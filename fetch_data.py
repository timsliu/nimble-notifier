#!/usr/bin/env
#
# fetch_data.py
#
# This program calls APIs to fetch vaccine availability data from vaccine
# spotter and covidWA

import requests
import json
from datetime import datetime
from pyzipcode import ZipCodeDatabase
import util


def fill_coordinates(avail_loc):
    '''helper function writes in the coordinates of a location using the
    center of the zip code and other info if the actual coordinates aren't
    available'''
    
    if avail_loc["coordinates"][0] is None and avail_loc["zip"] is not None:
        # look up zip code
        avail_loc["coordinates"] = util.zip_to_coors(int(avail_loc["zip"]))

    return avail_loc

def fetch_state(state):
    '''fetch the data for a single state'''
    # data for API call 
    api_url = 'https://www.vaccinespotter.org/api/v0/states/{}.json'.format(state)
    headers = {
        'if-modified-since': "<DATE_STRING>"
    }

    # get time and fill in the header
    now = datetime.utcnow()
    time_string = now.strftime("%a, %d %B %Y %H:%M:%S GMT")
    headers['if-modified-since'] = time_string

    # make request
    r = requests.get(api_url, headers=headers)
    locations = r.json()
    available = []
    
    for loc in locations["features"]:
        # appointments are available 
        if loc["properties"]["appointments_available"]:
            # copy over relevant information 
            avail_loc = {}
            avail_loc["coordinates"] = loc["geometry"]["coordinates"]
            avail_loc["zip"] = loc["properties"]["postal_code"]
            avail_loc["url"] = loc["properties"]["url"]
            avail_loc["name"] = "{} {} {}".format(
                loc["properties"]["name"],
                loc["properties"]["city"],
                loc["properties"]["address"]
            )

            # try to fill in coordinates if they're not available
            avail_loc = fill_coordinates(avail_loc)
            
            # add to full list only if there are coordinates
            if avail_loc["coordinates"][0] is not None:
                available.append(avail_loc)
    
    
    # convert to json and dump it 
    json_object = json.dumps(available, indent = 4)
    with open("data/location/{}_location.json".format(state), "w") as f:
        f.write(json_object)

    return available

if __name__ == "__main__":
    vaccine_spotter = fetch_vaccine_spotter()
    vaccine_spotter.fetch()
        
