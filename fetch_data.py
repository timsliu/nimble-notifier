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

def parse_covidwa(locations):
    '''parse the data fetched from covidwa
    inputs: locations - dictionary style JSON of all availability data
    output: available - list of available locations
    '''

    available = []

    for loc in locations["data"]:
        if loc["Availability"] == "Yes" or loc["Availability"] == "Limited":
            avail_loc = {} 
            try: 
                avail_loc["coordinates"] = [None, None]
                avail_loc["zip"] = loc["address"][-5:]
                avail_loc["url"] = loc["url"]
                avail_loc["name"] = "{} {}".format(
                    loc["name"],
                    loc["address"]
                )
            except KeyError as e:
                continue
            
            if "restrictions" in loc.keys():
                avail_loc["details"] = loc["restrictions"]
            
            else:
                avail_loc["details"] = ""
            
            try:
                avail_loc = fill_coordinates(avail_loc)
            except BaseException as e:
                continue
            
            # add to full list only if there are coordinates
            if avail_loc["coordinates"][0] is not None:
                available.append(avail_loc)
    return available    

def parse_vaccine_spotter(locations):
    '''parse the data fetched from vaccine_spotter
    inputs: locations - dictionary style JSON of all availability data
    output: available - list of available locations
    '''
    SKIP_LIST = ['safeway', 'riteaid', 'albert']    # list of pharmacies to skip
    
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
            avail_loc["details"] = ""

            # try to fill in coordinates if they're not available
            avail_loc = fill_coordinates(avail_loc)
            
            # add to full list only if there are coordinates
            if avail_loc["coordinates"][0] is not None:
                available.append(avail_loc)

    return available


def fetch_state(state):
    '''fetch the data for a single state'''
   
    # dictionary of which API to call for each state
    state_sources = {
        "WA": {
            "api_url": "https://api.covidwa.com/v1/get", 
            "parser": parse_covidwa,
        }, 
        "default":{
            "api_url":'https://www.vaccinespotter.org/api/v0/states/{}.json'.format(state),
            "parser": parse_vaccine_spotter,
        }
    }

    # make request
    if state in state_sources.keys(): 
        api_url = state_sources[state]["api_url"]
        state_parser = state_sources[state]["parser"]
    else:
        api_url = state_sources["default"]["api_url"]
        state_parser = state_sources["default"]["parser"]
    
    r = requests.get(api_url)
    locations = r.json()
    available = state_parser(locations) 
    
    # convert to json and dump it 
    json_object = json.dumps(available, indent = 4)
    with open("data/location/{}_location.json".format(state), "w") as f:
        f.write(json_object)

