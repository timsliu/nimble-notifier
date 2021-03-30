# Helper functions and wrappers around the google APIs

from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.encoders
import mimetypes

import os
import base64
import html2text
import pickle
import email


# If modifying these scopes, delete the file data/credentials/token_gmail.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive.activity']


def GetService():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file data/credentials/token_gmail.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('data/credentials/token_gmail.pickle'):
        with open('data/credentials/token_gmail.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/credentials/credentials_gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('data/credentials/token_gmail.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service

def GetMessage(service, user_id, msg_id):
      """Get a Message with given ID.
    
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.
    
      Returns:
        A Message.
      """
      try:
          message = service.users().messages().get(userId=user_id, id=msg_id).execute()
      
          return message["payload"]
      except errors.HttpError as error:
          print('An error occurred: %s' % error)

def GetMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.
  
    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.
  
    Returns:
      A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                 format='raw').execute()
    
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(str(msg_str))
        return mime_msg

    except errors.HttpError as error:
        print("Error {}".format(error))
        raise("Error {}".format(error))
 
def create_message(sender, to, subject, message_text, threadid=None, msgid=None):
    """Create a message for an email.
  
    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
  
    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    if threadid is not None:
        print("threadid: ", threadid) 
        #print("msgid: ", msgid) 
        message['threadId'] = threadid
        message['References'] = msgid
        message['In-Reply-To'] = msgid
    print(message)
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    
    #if threadid is not None: 
    #    body["threadID"] = threadid
    return body

def create_message_with_attachment(
    sender, to, subject, message_text, file):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.
      file: The path to the file to be attached.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    # encode the email 
    email.encoders.encode_base64(msg)
    message.attach(msg)
    
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    return body


def create_draft(service, user_id, message_body):
    """Create and insert a draft email. Print the returned draft's message and id.
  
    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      message_body: The body of the email message, including headers.
  
    Returns:
      Draft object, including draft id and message meta data.
    """
    try:
        message = {'message': message_body}
        draft = service.users().drafts().create(userId=user_id, body=message).execute()
  
        #print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))
  
        return draft
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return None




def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    return message
  except errors.HttpError as error:
    print('An error occurred: %s' % error)
