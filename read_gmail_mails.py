from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from dao_email_metadata import store_mail_metadata_in_database


SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

# The credentials.json file should be added to run google api.
# The credentials can be obtained of the offical site: https://developers.google.com/gmail/api/guides/
GMAIL_CREDENTIALS_FILE = 'credentials.json'


# The raw dictionary is transformed into a dictionary so later we can search for information.
# As the payload is stored in a list, storing is the most efficient way in time to check
# if the message is needed.
def transform_gmail_to_message_metadata(msg):
    message_metadata = {'body_content': msg['snippet']}
    payloads = msg['payload']['headers']
    for payload in payloads:
        if payload['name'] == 'From':
            message_metadata['from'] = payload['value']
        if payload['name'] == 'Date':
            message_metadata['date'] = payload['value']
        if payload['name'] == 'Subject':
            message_metadata['subject'] = payload['value']
    return message_metadata


# Using the credentials of gmail api, we can fetch the gmail mails.
# The messages that in the body or in the subject contain the word 'devops'
# are send to the database through the dao function.
def fetch_gmail_account():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(GMAIL_CREDENTIALS_FILE, SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            message_metadata = transform_gmail_to_message_metadata(msg)
            if 'devops' in message_metadata['body_content'].lower() or 'devops' in message_metadata['subject'].lower():
                store_mail_metadata_in_database(message_metadata['date'], message_metadata['from'],
                                                message_metadata['subject'])
