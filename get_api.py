import requests
import json
import prettytable
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

def fetch_bls_data(series_ids, start_year, end_year):
    api_key = os.getenv('BLS_API_KEY')
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": series_ids, 
        "startyear": start_year, 
        "endyear": end_year, 
        "registrationkey": api_key
    })

    response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    return json.loads(response.text)

def save_to_file(json_data):
    # Ensure the downloads directory exists
    output_folder = 'downloads'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for series in json_data['Results']['series']:
        table = prettytable.PrettyTable(["series id", "year", "period", "value", "footnotes"])
        series_id = series['seriesID']
        
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes = ""
            for footnote in item['footnotes']:
                if footnote:
                    footnotes += footnote['text'] + ','
                    
            if 'M01' <= period <= 'M12':  # Limiting to monthly periods
                table.add_row([series_id, year, period, value, footnotes.rstrip(',')])
        
        with open(os.path.join(output_folder, f'{series_id}.txt'), 'w') as output_file:
            output_file.write(table.get_string())

# Example usage
series_ids = ['CUUR0000SA0']
start_year = '2020'
end_year = '2024'

json_response = fetch_bls_data(series_ids, start_year, end_year)
save_to_file(json_response)