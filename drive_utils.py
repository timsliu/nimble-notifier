from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

from apiclient import errors
from apiclient import http

import pickle
import os.path
import io


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive']

def GetDriveCredentials():
    '''returns the credentials for google drive'''
    creds = None
    # The file data/credentials/token_drive.pickle stores the user's
    # access and refresh tokens, and is created automatically when the
    # authorization flow completes for the first time.
    if os.path.exists('data/credentials/token_drive.pickle'):
        with open('data/credentials/token_drive.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'data/credentials/credentials_drive.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('data/credentials/token_drive.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def GetDriveService():
    '''Returns service for google drive''' 
    creds = GetDriveCredentials()
    service = build('drive', 'v3', credentials=creds)

    return service

def GetSheetService():
    '''Returns service for google sheet''' 
    creds = GetDriveCredentials()
    service = build('sheets', 'v4', credentials=creds)

    return service

def GetFiles(service):
    # Call the Drive v3 API
    results = service.files().list(
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))


def print_file_metadata(service, file_id):
    """Print a file's metadata.
  
    Args:
      service: Drive API service instance.
      file_id: ID of the file to print metadata for.
    """
    try:
        file = service.files().get(fileId=file_id).execute()
  
        print('Title: %s' % file['title'])
        print('MIME type: %s' % file['mimeType'])
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def print_file_content(service, file_id):
    """Print a file's content.

    Args:
      service: Drive API service instance.
      file_id: ID of the file.

    Returns:
      File's content if successful, None otherwise.
    """
    try:
        print(service.files().get_media(fileId=file_id).execute())
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def download_file(service, file_id, local_fd):
    """Download a Drive file's content to the local filesystem.
  
    Args:
      service: Drive API Service instance.
      file_id: ID of the Drive file that will downloaded.
      local_fd: io.Base or file object, the stream that the Drive file's
          contents will be written to.
    """
    request = service.files().get_media(fileId=file_id)
    media_request = http.MediaIoBaseDownload(local_fd, request)
  
    while True:
        try:
            download_progress, done = media_request.next_chunk()
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
            return
        if download_progress:
            print('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
            print('Download Complete')
            return



def download_google_file(service, file_id, mimeType):
    '''downloads a google doc file from google drive and returns 
    a file handle to the download
    service - authentication
	file_id - file id corresponding to file
    mimeType - descriptor of download format'''

    request = service.files().export_media(fileId=file_id,
                                                 mimeType=mimeType)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    return fh


def create_file(drive_service, name, parent_id, file_path,
    mimetype='text/plain', gdoc=False):
    '''creates a new file and uploads to google drive
    name - name of new file
    parent_id - parent_id of the parent folder
    file_path - path to the file to upload
    mimetype - file format
    gdoc - convert to google doc format'''

    file_metadata = {
        'name': name,
        'parents': [parent_id]
    }

    # optionally convert to google doc format
    if gdoc:
        file_metadata['mimeType'] = 'application/vnd.google-apps.document'

    media = MediaFileUpload(file_path,
                            mimetype=mimetype,
                            resumable=True)
    # create the file 
    new_file = drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()

    # print("File uploaded to drive: {}".format(name))
    return new_file.get('id')

def update_sheet(sheet_service, sheet_id, sheet_range, data):
    '''appends a row to the bottom of a sheet
    drive_service - service credentials for sheets
    sheet_id - file id of sheet to append
    sheet_range - A1 notation of table to start at''' 

    # construct data
    value_range_body = {
        "range": sheet_range,
        "majorDimension": "ROWS", 
        "values": [data]
    }
   
    # generate request to append to spreadsheet 
    request = sheet_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=sheet_range,
        body=value_range_body,
        valueInputOption="RAW"
    )

    # execute request
    response = request.execute()
    return

