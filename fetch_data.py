#
# fetch_data.py
#
# This program calls APIs to fetch vaccine availability data from vaccine
# spotter and covidWA

import requests
import json
from datetime import datetime


class fetch_vaccine_spotter():

    def __init__(self):
        self.api_url = 'https://www.vaccinespotter.org/api/v0/states/CA.json'
        self.headers = {
            'if-modified-since': "<DATE_STRING>"
        }

    def fetch(self):
        now = datetime.utcnow()
        time_string = now.strftime("%a, %d %B %Y %H:%M:%S GMT")

        self.headers['if-modified-since'] = time_string

        r = requests.get(self.api_url, headers=self.headers)
        locations = r.json()
        for loc in locations["features"]:
            print(loc)
            print("\n\n")
        for key in locations.keys():
            print(key)
            print("\n\n")

        #print(locations)




if __name__ == "__main__":
    vaccine_spotter = fetch_vaccine_spotter()
    vaccine_spotter.fetch()
        
