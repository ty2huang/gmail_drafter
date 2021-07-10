from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
import base64

import yaml
import csv
import re


### Global variables/parameters from files ###

with open('cfgs/job_context.yaml', 'r') as f:
    job_context = yaml.safe_load(f)

email_contents_file = job_context['email_contents']
with open('cfgs/' + email_contents_file, 'r') as f:
    email_contents = yaml.safe_load(f)

parameters_file = job_context['parameters']
with open('cfgs/' + parameters_file, 'r') as f:
    context = yaml.safe_load(f)

recipients_file = job_context['recipients']
with open('cfgs/' + recipients_file, 'r') as f:
    recipients_parms = [parms for parms in csv.DictReader(f) if parms['enable'] == '1']


### Class definitions for Text, DraftEmail, and DraftEmailIterator ###

class Text:
    def __init__(self, text):
        self.val = text

    def fill_text(self, parms):
        for k, v in parms.items():
            self.val = self.val.replace('{' + k + '}', v)
        return self

    def compress_whitespaces(self):
        self.val = re.sub(' +', ' ', self.val)
        self.val = re.sub('\n\n+', '\n\n', self.val)
        return self

class DraftEmail:
    def __init__(self, parms_dict):
        self.parms = parms_dict
        self.parms.update(context)
        self.recipient = parms_dict['email']
        self.subject = self.parameterize(email_contents['subject'])
        self.body = self.parameterize(email_contents['body'])

    def parameterize(self, text):
        text_obj = Text(text).fill_text(self.parms).fill_text(context)
        return text_obj.compress_whitespaces().val

    def get_contents(self):
        return self.recipient, self.subject, self.body

class DraftEmailIterator:
    def __init__(self):
        self.guests = [DraftEmail(parms) for parms in recipients_parms]
        self.next_idx = 0

    def next(self):
        if self.next_idx >= len(self.guests):
            return None
        self.next_idx += 1
        return self.guests[self.next_idx - 1]


### Functions for creating the email drafting service and writing draft emails ###

def create_message(sender, to, subject, message_text):
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
  return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

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

    print ('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

    return draft
  except Exception as error:
    print ('An error occurred: %s' % error)
    return None

def init_gmail_service():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.compose']
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service


# Triggering email drafting service for all recipients
if __name__ == "__main__":
    service = init_gmail_service()
    session = DraftEmailIterator()
    draft_email = session.next()
    while draft_email:
        (recipient, subject, body) = draft_email.get_contents()
        create_draft(service, 'me', create_message('me', recipient, subject, body))
        draft_email = session.next()
