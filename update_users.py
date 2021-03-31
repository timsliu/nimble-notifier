# update_users.py
#
# This program updates the user JSON using a google spreadsheet.

import drive_utils
import datetime as dt
import util
import defs
import json
import os

BUFFER_TIME = 5   # extra seconds before last tick to check for new users

def total_users():
    '''return the total number of active users'''
    user_files = os.listdir(os.path.join(os.getcwd(), "data/user"))
    user_files = filter(lambda x: "_users.json" in x, user_files)
    total = 0
   
    # open each state user json file and count number of users
    for state_path in user_files:
        with open(os.path.join("data/user", state_path), "r") as f:
            state_dict = json.load(f)
        total += len(state_dict)

    return total

def all_states():
    '''create list of all states that there are users'''
    user_files = os.listdir(os.path.join(os.getcwd(), "data/user"))
    user_files = filter(lambda x: "_users.json" in x, user_files)
    states = []

    for state in user_files:
        states.append(state[0:2])

    return states

def new_entries(drive_service, sheet_name, last_tick=None):
    '''read from the google spreadsheet and find new users'''
    # get last update time 
    if last_tick is None:
        last_tick = dt.datetime.now() - dt.timedelta(seconds=(defs.TICK_TIME + BUFFER_TIME)) 

    # open json file with document IDs
    with open("data/credentials/doc_ids.json", "r") as f:
        doc_ids = json.load(f)

    # look up sheet id and sheet range
    sheet_id = doc_ids[sheet_name]["sheet_id"]
    sheet_range = doc_ids[sheet_name]["sheet_range"]
    
    # access sheet 
    sheets = drive_service.spreadsheets()
    result = sheets.values().get(
        spreadsheetId=sheet_id, 
        range=sheet_range
    ).execute()
    values = result.get('values', [])
   
    # filter out only the newest entries since the last tick
    values.reverse()   # reverse to parse latest first
    last_new = None 
    for i, row in enumerate(values):
        if row[0] == "Timestamp":
            last_new = i 
            break
        
        response_time = dt.datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S")
        
        # break on the column headers or previously seen rows 
        if response_time < last_tick:
            last_new = i 
            break

    return values[0:last_new]


def add_users(user_list):
    '''add new users to the appropriate JSON'''

    # TODO - sort by state and only open when the state changes

    for row in user_list:
        state = row[3]     # access state abbreviation
        state_json_path = "data/user/{}_users.json".format(state)
       
        # load state data if it exists; otherwise use empty list
        state_dict = None
        if os.path.exists(state_json_path):
            with open(state_json_path, "r") as f:
                state_dict = json.load(f)
        else:
            state_dict = {}
        
        # create a new user dictionary
        new_user = {}
        email_address = util.clean_email_address(row[1])
        print("Adding/updating user: {}, {}".format(email_address, state))
       
        # reject zip codes and search radii that are not integers
        try:
            new_user["zip"] = int(row[2]) 
            new_user["search_radius"] = int(row[4])
        except BaseException as e:
            new_user["zip"] = 0
            new_user["search_radius"] = 0

        new_user["last_avail"] = []         # last available locations
        new_user["thread_id"] = ""          # threadID for threading emails
        new_user["msg_id"] = ""             # message ID for threading
        
        state_dict[email_address] = new_user

        # dump the updated json back
        state_data = json.dumps(state_dict, indent = 4)
        with open(state_json_path, "w") as f:
            f.write(state_data)

def remove_users(user_list):
    '''remove a list of users from the user json'''

    for user in user_list:
        email_address = util.clean_email_address(user[1])
        state = user[2]
        state_json_path = "data/user/{}_users.json".format(state)

        print("Removing user: {}, {}".format(email_address, state))
        # open the json file of users
        with open(state_json_path, "r") as f:
            state_dict = json.load(f)
        
        # delete the user from the dictionary
        state_dict.pop(email_address, None)

        # dump the updated json back
        state_data = json.dumps(state_dict, indent = 4)
        with open(state_json_path, "w") as f:
            f.write(state_data)

    return
