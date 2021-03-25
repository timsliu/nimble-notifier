# notifier
# 
# This program auto sends emails when a vaccine is found

import gmail_utils

SENDER_ADDRESS = "nimblenotifier@gmail.com"
SUBJECT = "Potential Covid-19 Vaccine Appointments in your Area"


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

    email_body = email_body.replace("<<appointments>>", avail_locs)

    return email_body

def send_all(match_list, gmail_service):
    '''send emails to all users with nearby vaccines'''
    sent_emails = 0               # total emails sent
    fail_emails = 0               # failed emails

    # loop through all users with nearby vaccines
    for user in match_list:
        msg_txt = format_msg(user)               # create message text
        
        # generate an email object
        email = gmail_utils.create_message(
            SENDER_ADDRESS,
            user["email"],
            SUBJECT,
            msg_txt
        )
        # attempt to send the email
        #status = gmail_utils.send_message(gmail_service, SENDER_ADDRESS, email)
        status = None 
        # track number of successful emails
        if status is not None:
            sent_emails += 1
        else:
            fail_emails += 1

    return sent_emails, fail_emails
