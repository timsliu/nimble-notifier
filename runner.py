# runner.py
#
# This program periodically runs all other programs and acts as the main loop

import util
import matcher
import fetch_data
import notifier
import gmail_utils
import drive_utils
import time
from datetime import datetime
import defs
import update_users

def init():
    '''initializer - creates services for gmail and drive'''
    gmail_service = gmail_utils.GetService()                   # get gmail service
    drive_service = drive_utils.GetSheetService()              # get drive service

    return gmail_service, drive_service

def run_single(gmail_service, drive_service):
    '''main loop for testing all processes - updates vaccine data, searches
    for matches, and emails users'''
    
    try:
        # find new users and update sheet
        new_users = update_users.new_entries(
            drive_service, "new_user_sheet"
        )
        update_users.add_users(new_users)
        
        # find users who unsubscribed and update sheet
        #unsub_users = update_users.new_entries(
        #    drive_service, "unsub_user_sheet"
        #)
        #update_users.remove_users(unsub_users) 

        user_states = update_users.all_states()            # get list of states 

        # update all states with users
        for state in user_states:
            fetch_data.fetch_state(state)                       # update vaccine data
        
        match_list = matcher.match_all()                             # match users w/ nearby vaccines
        sent, failed = notifier.send_all(match_list, gmail_service)  # send emails
        now = datetime.now() 
        print("Sent {} out of {} attempted emails at {}".format(
            sent, 
            failed + sent, 
            now.strftime("%d/%m/%Y %H:%M:%S")
        ))
    except BaseException as e:
        print("Failed: {}".format(e))


def run_continuous(gmail_service, drive_service):
    '''run all processes and continually loop''' 
    
    while True:
        run_single(gmail_service, drive_service) 
        time.sleep(defs.TICK_TIME)

if __name__ == "__main__":
    gmail_service, drive_service = init()
    run_continuous(gmail_service, drive_service)
    #run_single(gmail_service, drive_service)
