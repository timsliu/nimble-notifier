# notifier
# 
# This program auto sends emails when a vaccine is found


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

    avail_locs = ""
    for loc in user["avail"]:
        avail_locs += "\nZip code: {}\n".format(loc['zip'])
        avail_locs += "{}\n".format(loc["url"])
        avail_locs += "Estimated distance: {} miles\n".format(loc["distance"])

    email_body = email_body.replace("<<appointments>>", avail_locs)

    return email_body



def send_all(match_list):
    '''send emails to all users with nearby vaccines'''

    for user in match_list:
        msg = format_msg(user)
