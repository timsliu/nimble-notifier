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
import argparse


def init():
    '''initializer - creates services for gmail and drive'''
    gmail_service = gmail_utils.GetService()                   # get gmail service
    drive_service = drive_utils.GetSheetService()              # get drive service

    return gmail_service, drive_service

def update_users_list(drive_service, last_tick=None):
    # find new users and update sheet
    new_users = update_users.new_entries(
        drive_service, "new_user_sheet", last_tick=last_tick
    )
    update_users.add_users(new_users)
    
    # find users who unsubscribed and update sheet
    unsub_users = update_users.new_entries(
        drive_service, "unsub_user_sheet", last_tick=last_tick
    )
    update_users.remove_users(unsub_users) 


def run_single(gmail_service, drive_service, debug=None):
    '''main loop for testing all processes - updates vaccine data, searches
    for matches, and emails users'''
    
    update_users_list(drive_service, last_tick=None)

    user_states = update_users.all_states()            # get list of states 
    print("Total users: {}".format(update_users.total_users()))

    # update all states with users
    for state in user_states:
        fetch_data.fetch_state(state)                       # update vaccine data
    print("Updated availability data for {}".format(user_states))
    
    match_list = matcher.match_all()                             # match users w/ nearby vaccines
    sent, failed = notifier.send_all(match_list, gmail_service, debug=debug)  # send emails
    print("Tick ending; sent {} out of {} attempted emails at {}".format(
        sent, 
        failed + sent, 
        datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    ))


def run_continuous(gmail_service, drive_service):
    '''run all processes and continually loop''' 
    
    while True:
        print("\n=== Starting tick at time: {} ===".format(
            datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        ))
        run_time = 0 
        try:
            start = datetime.now()
            run_single(gmail_service, drive_service) 
            end = datetime.now()
            run_time = (end - start).seconds
        except BaseException as e:
            print("Failed: {}".format(e))
        
        time.sleep(defs.TICK_TIME - run_time)

def get_parser():
    '''create argument parser'''
    parser = argparse.ArgumentParser(description='Run Vaccine Notifier')

    parser.add_argument('-s', action='store_true', help='run single time')
    parser.add_argument('-u', action='store_true', help='update user')
    parser.add_argument('-n', action='store_true', help='no send')
    parser.add_argument('-d', action='store_true', help='debug mode')

    return parser
if __name__ == "__main__":
    parser = get_parser()
    gmail_service, drive_service = init()

    # parse arguments
    args = parser.parse_args()

    # only update users 
    if args.u:
        print("=== Only updating users ===")
        print("Enter time to start updating users from: ")
        month  = int(input("Month: "))
        day    = int(input("Day: "))
        hour   = int(input("Hour: "))
        minute = int(input("Minute: "))
        
        last_tick = datetime(
            year=2021, 
            month=month, 
            day=day,
            hour=hour, 
            minute=minute
        )  
        
        update_users_list(drive_service, last_tick=last_tick)
        exit()
  
    # run in test mode
    if args.d:
        print("=== Running in debug mode ===")
        address = str(input("Debug address: "))
        run_single(gmail_service, drive_service, debug=address) 
        exit()

    # run a single iteration
    if args.s:
        run_single(gmail_service, drive_service)
    
    # run continuously 
    else:
        run_continuous(gmail_service, drive_service)
