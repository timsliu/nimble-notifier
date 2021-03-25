# update_users.py
#
# This program updates the user JSON using a google spreadsheet.

import drive_utils
import datetime as dt
import defs
import json

RANGE = "Responses!A:E"

def new_users(drive_service):
    '''read from the google spreadsheet and find new users'''
    # get last update time 
    last_tick = dt.datetime.now() - dt.timedelta(seconds=(defs.TICK_TIME + 1)) 
    #last_tick = dt.datetime(2018, 1, 1)  # uncomment to force update
    
    # open json file with document IDs
    with open("data/credentials/doc_ids.json", "r") as f:
        doc_ids = json.load(f)

    # access sheet with new users
    new_user_sheet = doc_ids["new_user_sheet"]
    sheet = drive_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=new_user_sheet, range=RANGE).execute()
    values = result.get('values', [])
    
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
        with open(state_json_path, "r") as f:
            state_list = json.load(f)
        
        # create a new user dictionary
        new_user = {}
        new_user["email"] = row[1]
        new_user["zip"] = int(row[2]) 
        new_user["search_radius"] = int(row[4])
        new_user["last_avail"] = []

        # see if this new user is in the dictionary
        existing_index = None
        for i, entry in enumerate(state_list):
            if entry["email"] == new_user["email"]:
                existing_index = i
                break
        
        # delete old entry
        if existing_index is not None:
            del state_list[existing_index]

        state_list.append(new_user)     # add new user

        # dump the updated json back
        state_data = json.dumps(state_list, indent = 4)
        with open(state_json_path, "w") as f:
            f.write(state_data)

def remove_users():
    pass
