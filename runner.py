# runner.py
#
# This program periodically runs all other programs and acts as the main loop

import util
import matcher
import fetch_data
import notifier
import gmail_utils
import time
from datetime import datetime

SLEEP_TIME = 400      # sleep time in seconds


def run_test():
    '''main loop for testing all processes - updates vaccine data, searches
    for matches, and emails users'''
    
    gmail_service = gmail_utils.GetService()                     # get gmail service

    vaccine_spotter = fetch_data.fetch_vaccine_spotter()         # update vaccine data
    vaccine_spotter.fetch()                                      # update vaccine data
    match_list = matcher.match_all()                             # match users w/ nearby vaccines
    sent, failed = notifier.send_all(match_list, gmail_service)  # send emails
    
    print("Sucessfully sent {} out of {} attempted emails".format(sent, failed + sent))


def run_all():
    '''run all processes and continually loop''' 
    
    gmail_service = gmail_utils.GetService()                         # get gmail service
    vaccine_spotter = fetch_data.fetch_vaccine_spotter()             # update vaccine data
    
    while True: 
        vaccine_spotter.fetch()                                      # update vaccine data
        match_list = matcher.match_all()                             # match users w/ nearby vaccines
        sent, failed = notifier.send_all(match_list, gmail_service)  # send emails
       
        now = datetime.now() 
        print("Sent {} out of {} attempted emails at {}".format(
            sent, 
            failed + sent, 
            now.strftime("%d/%m/%Y %H:%M:%S")
        ))
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    run_all()
