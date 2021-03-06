# notifier
# 
# This program auto sends emails when a vaccine is found

import gmail_utils
import util
import json
import time

SENDER_ADDRESS = "nimblenotifier@gmail.com"
SUBJECT = "Potential Covid-19 Vaccine Appointments in your Area"
EMAIL_WAIT = 0.5

def select_service(gmail_services, user):
    '''returns the gmail service to use for this user based on the user's
    random offset
    inputs: gmail_services - list of gmail services, one for each account
            user - dictionary of user data
    outputs: gmail_service - gmail service to use
             address - address corresponding to the gmail service'''

    rand_offset = user["rand_offset"]               # look up user random offset
    service_idx = rand_offset % len(gmail_services) # calculate index
    
    if service_idx != 0:
        suffix = service_idx
    else:
        suffix = ""
  
    address = "nimblenotifier{}@gmail.com".format(suffix)

    return gmail_services[service_idx], address

def set_thread_id(gmail_service, user, msg, sender_address):
    '''sets the thread ID for a user to enable replying to the same thread'''
   
    # msg failed - don't set the thread id
    if msg is None:
        return
    
    mime = gmail_utils.GetMimeMessage(
        gmail_service,
        sender_address,
        msg["id"]
    )
    
    # get msgid and threadid
    msg_id = util.parse_by_prefix(mime.as_string(), "Message-Id: ", end_char = [">"]) + ">"
    thread_id = msg["threadId"]

    state_json_path = "data/user/{}_users.json".format(user["state"])

    with open(state_json_path, "r") as f:
        state_dict = json.load(f)

    state_dict[user["email"]]["thread_id"] = thread_id
    state_dict[user["email"]]["msg_id"] = msg_id

    state_data = json.dumps(state_dict, indent = 4)
    with open(state_json_path, "w") as f:
        f.write(state_data)

    return

def format_msg(user):
    '''create a formatted user message with available appointments'''
    # construct path to email template
    template = "data/template/email.txt"
    
    with (open(template, "r")) as f:
        template_list = f.readlines()
  
    # single string with entire template email
    email_body = ""
    for line in template_list:
        email_body += line

    locations = user["avail"]
    locations.sort(key = lambda x: x["distance"])
    avail_locs = ""

    for loc in locations:
        avail_locs += "\nLocation: {}\n".format(loc['name'])
        avail_locs += "Zip code: {}\n".format(loc['zip'])
        avail_locs += "{}\n".format(loc["url"])
        avail_locs += "Estimated distance: {:.1f} miles\n".format(loc["distance"])
        avail_locs += "Additional details and restrictions: {}\n".format(loc["details"])

    email_body = email_body.replace("<<appointments>>", avail_locs)

    return email_body

def send_all(match_list, gmail_services, debug=None):
    '''send emails to all users with nearby vaccines'''
    sent_emails = 0               # total emails sent
    fail_emails = 0               # failed emails

    # loop through all users with nearby vaccines
    for user in match_list:
        msg_txt = format_msg(user)               # create message text
     
        if user["thread_id"] is None:            # add Re: for replies
            subject = SUBJECT
        else:
            subject = "Re: " + SUBJECT
        
        gmail_service, sender_address = select_service(gmail_services, user)

        # generate an email object
        email = gmail_utils.create_message(
            sender_address,
            user["email"],
            subject,
            msg_txt,
            thread_id=user["thread_id"],
            msg_id=user["msg_id"],
        )
        
        msg = None
        # debug mode - only email the debug address
        if debug is not None and user["email"] != debug:
            print("\n==== Recipient: {} ====\n{}".format(user["email"], msg_txt))
            continue
      
        msg = gmail_utils.send_message(gmail_service, sender_address, email)
       
        # save info required for threading if it's not saved
        if user["thread_id"] is None: 
            set_thread_id(gmail_service, user, msg, sender_address)

        # send succeeded
        if msg is not None:
            sent_emails += 1
            
            # save info required for threading if it's not saved
            if user["thread_id"] is None: 
                set_thread_id(gmail_service, user, msg, sender_address)
        # send failed 
        else:
            fail_emails += 1
        
        time.sleep(EMAIL_WAIT)    # wait before sending next email to prevent
                                  # exceeding usage limit

    return sent_emails, fail_emails
