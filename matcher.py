# matcher.py
#
# This program opens the list of active users in each state and matches with
# the list of available sites

import os
import json
import util
from haversine import haversine, Unit

def match_state(user_data, loc_data):
    '''match the people in a state with the available locations
    inputs: users - dictionary of users in a state
            locs - dictionary of availble locations in a state
    output: list of users with nearby locations'''
    match_list = []

    for user in user_data:
        user_coor = util.zip_to_coors(user["zip"])
        matched_user = {}
        matched_user["email"] = user["email"]
        matched_user["avail"] = []

        for loc in loc_data:
            distance = haversine(user_coor, loc["coordinates"], unit=Unit.MILES)
            if distance < user["search_radius"]:
                loc["distance"] = distance
                matched_user["avail"].append(loc)

        if len(matched_user["avail"]) > 0:
            match_list.append(matched_user)

    return match_list

def match_all():
    '''loop through all states, opening JSON and matching with the available
    sites in that state

    inputs: None
    output: list of emails and nearby locations'''
    
    all_matches = []        # list of all users w/ matches
    user_files = os.listdir(os.path.join(os.getcwd(), "data/user"))
    user_files = filter(lambda x: "_users.json" in x, user_files)

    for state_user in user_files:
        state = state_user[0:2]      # parse the state abbreviation
       
        # paths to the state location and state users
        state_loc = os.path.join("data/location", "{}_location.json".format(state))
        state_user = os.path.join("data/user", state_user)

        # load data for users and locations in the state
        with open(state_user, "r") as f:
            user_data = json.load(f)

        with open(state_loc, "r") as f:
            loc_data = json.load(f)
    
        all_matches += match_state(user_data, loc_data)

    return all_matches

if __name__ == "__main__":
    match_all()
