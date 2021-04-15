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

SKIP_LIST = ['safeway', 'riteaid', 'albert']    # list of pharmacies to skip

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

    # make request
    r = requests.get(api_url)
    locations = r.json()
    available = []
    
    for loc in locations["features"]:
       
        # skip unreliable pharmacies
        if True in [pharmacy in str(loc["properties"]["url"]) for pharmacy in SKIP_LIST]:
            continue

        # appointments are available 
        if loc["properties"]["appointments_available"]:
            # copy over relevant information 
            avail_loc = {}
            # vaccine spotter stores coordinates backwards from convention - 
            # flip to standard lat, lon coordinates
            avail_loc["coordinates"] = list(reversed(loc["geometry"]["coordinates"]))
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

