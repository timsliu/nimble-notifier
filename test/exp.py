# file for experimenting with code and functionality

import runner
import gmail_utils
import util

SENDER_ADDRESS = "nimblenotifier@gmail.com"


def reply_thread(gmail_service):
    '''test replying to a thread'''
    
    test_email = str(input("Test email: "))      # get email to test with

    # create first email
    email = gmail_utils.create_message(
        SENDER_ADDRESS, 
        test_email,
        "Testing thread reply",
        "Hello, this is a test",
    )

    # send messages
    msg = gmail_utils.send_message(gmail_service, SENDER_ADDRESS, email)
    mime = gmail_utils.GetMimeMessage(gmail_service, SENDER_ADDRESS, msg["id"]) 

    # get msgid and threadid
    msgid = util.parse_by_prefix(mime.as_string(), "Message-Id: ", end_char = [">"]) + ">"
    threadid = msg["threadId"]

    # print the thread and message id
    print(msgid)
    print(threadid)

    # create the new message
    email = gmail_utils.create_message(
        SENDER_ADDRESS, 
        test_email,
        "Re: Testing thread reply", 
        "I'm doing great! This is another reply",
        thread_id = threadid,
        msg_id = msgid,
    )
   
    # send reply message
    msg = gmail_utils.send_message(gmail_service, SENDER_ADDRESS, email)

if __name__ == "__main__":
    gmail_service, drive_servie = runner.init()
    reply_thread(gmail_service)
