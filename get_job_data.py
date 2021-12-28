import requests
import json
import pandas as pd
import os

'''
Using series ID for job
"L" suffix gives level in thousands of quits "QU" in series id
For more info, look here: 
    https://download.bls.gov/pub/time.series/jt/jt.txt

API Example here: https://www.bls.gov/developers/api_python.htm
'''

headers = {'Content-type': 'application/json'}
api_key = os.environ.get('bls_api_key') # make env var


def get_job_data(seriesid='JTU000000000000000QUL', start_year="2000", end_year="2021"):
    '''
    Gets job data for a specific BLS data code

    parameters:
        seriesid : str; code for the BLS job data desired,
                    this code is made up of the type of job statistic,
                        as well as the industry and location.
                    For more info, look here: https://download.bls.gov/pub/time.series/jt/jt.txt
        start_year, end_year: str or int; start and end years for which data is desired
    '''
    # Pinging the BLS API and converting to JSON
    data = json.dumps({"seriesid": [seriesid], "startyear": str(start_year),
                       "endyear": str(end_year), "registrationkey": api_key})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/',
                      data=data, headers=headers)

    json_data = json.loads(p.text)

    # Grabbing relevant data, stripping response status codes
    jolts_data = json_data['Results']['series'][0]['data']
    print(jolts_data)

    # Generating a nice pandas df
    print('##############################################')
    df = pd.concat([pd.DataFrame(j) for j in jolts_data])
    df['value'] = df.value.astype(int)

    df['total_quits'] = df.value * 1000

    print(df)
    return df


def format_jobs_data(path='data/job_quits.csv'):
    '''Re-formats job_quits.csv file to match api response formatting'''
    # Data found here: https://data.bls.gov/pdq/SurveyOutputServlet
    df = pd.read_csv(path)
    df['value'] = df.value.astype(int)
    df['total_quits'] = df['value'] * 1000

    return df


if __name__ == "__main__":
    df = get_job_data(seriesid='JTU000000000000000QUL',
                      start_year="2000", end_year="2021")
    df.to_csv(os.path.join('data', "jobs_data_quits.csv"))

    # Using Survery response formatted data
    data = format_jobs_data(os.path.join('data', 'job_quits.csv'))
    data.to_csv(os.path.join('data', 'job_quits_formatted.csv'))
