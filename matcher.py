# matcher.py
#
# This program opens the list of active users in each state and matches with
# the list of available sites

import os
import json
import util
from haversine import haversine, Unit
import copy
import defs
       
def users_this_tick(user_dict, tick):
    '''filters a user dictionary for users that should be updated this tick
    given the refresh period and random offset''' 
    
    # no tick indicates all users should be updated
    if tick is None:
        return user_dict

    # list of users to update this tick 
    user_dict_filtered = {} 
    for email in user_dict.keys():
        user = user_dict[email]

        # number of ticks between updates
        update_freq_ticks = max(1, int(user["refresh_interval"]/defs.TICK_TIME))
        # offset for which tick to update 
        rand_offset_wrapped = user["rand_offset"] % update_freq_ticks

        if tick % update_freq_ticks == rand_offset_wrapped:
            user_dict_filtered[email] = copy.deepcopy(user)

    return user_dict_filtered

def match_state(user_data, loc_data, state):
    '''match the people in a state with the available locations
    inputs: users - dictionary of users in a state
            locs - dictionary of availble locations in a state
            state - string state being matched
    output: list of users with nearby locations'''
    match_list = []

    # iterate through users, which are email addresses
    for user in user_data.keys():
        user_coor = util.zip_to_coors(user_data[user]["zip"])
        matched_user = {}
        matched_user["email"] = user
        matched_user["avail"] = []

        # for given user, search through all location looking for availability
        for loc in loc_data:
            distance = haversine(user_coor, loc["coordinates"], unit=Unit.MILES)
            if distance < user_data[user]["search_radius"]:
                matched_loc = copy.deepcopy(loc)          # deep copy the location
                matched_loc["distance"] = distance        # set the distance
                matched_user["avail"].append(matched_loc)

        # availability found for this user
        if len(matched_user["avail"]) > 0:
            # last availability emailed to user 
            last_available = user_data[user]["last_avail"]
            new_available = [loc["name"] for loc in matched_user["avail"]]
            
            # only mark a match and update the lastest availability if the
            # new list is not a subset of the last availability sent out
            if not set(new_available).issubset(set(last_available)):
                # copy thread_id and msg_id from user_data to be used in
                # sending the emails
                matched_user["state"] = state 
                if "thread_id" in user_data[user].keys():
                    matched_user["thread_id"] = user_data[user]["thread_id"] 
                    matched_user["msg_id"] = user_data[user]["msg_id"]
                else:
                    matched_user["thread_id"] = None 
                    matched_user["msg_id"] = None
                match_list.append(matched_user)
                # record latest availability
                user_data[user]["last_avail"] = new_available

    return match_list, user_data

def match_all(tick=None):
    '''loop through all states, opening JSON and matching with the available
    sites in that state

    inputs: tick (optional) - integer index of the current tick; used to
            determine which users to update
    output: list of emails and nearby locations'''
    
    all_matches = []        # list of all users w/ matches
    user_files = os.listdir(os.path.join(os.getcwd(), "data/user"))
    user_files = filter(lambda x: "_users.json" in x, user_files)

    for state_user in user_files:
        state = state_user[0:2]      # parse the state abbreviation
       
        # paths to the state location and state users
        state_loc = os.path.join("data/location", "{}_location.json".format(state))
        state_user_path = os.path.join("data/user", state_user)

        # load data for users and locations in the state
        with open(state_loc, "r") as f:
            loc_data = json.load(f)

        
        with open(state_user_path, "r") as f:
            # open user file, find matches, and update last availability 
            user_dict = json.load(f)
       
        # filter for only users who should be updated this tick
        user_dict = users_this_tick(user_dict, tick)
        
        # update list of all matches and dump the updated user data back
        matches, user_dict = match_state(user_dict, loc_data, state)
        all_matches += matches
        
        user_data = json.dumps(user_dict, indent = 4)
        with open(state_user_path, "w") as f:
            f.write(user_data)

    return all_matches

if __name__ == "__main__":
    match_all()
