import base64
import os
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

project_root = Path(__file__).parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)
credential_file = project_root / 'credentials.json'
token_file = project_root / 'token.json'


class GoogleWorkspace:
    def __init__(self, scopes: list[str]):
        self.scopes = scopes
        self.creds = self._authenticate()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def _authenticate(self) -> dict:
        creds = None
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(str(token_file), self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(credential_file), self.scopes)
                creds = flow.run_local_server(port=0)
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        return creds

    def list_drive_files(self) -> list[str]:
        results = self.drive_service.files().list(
            pageSize=10,
            fields="files(id, name)"
        ).execute()
        return results.get('files', [])

    def list_gmail_subjects(self, max_results: int = 5) -> list[str]:
        messages = self.gmail_service.users().messages().list(
            userId='me', labelIds=['INBOX'],
            maxResults=max_results).execute().get('messages', [])
        subjects = []
        for msg in messages:
            msg_detail = self.gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_detail.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            subjects.append(subject)
        return subjects

    def list_gmail_messages(self) -> list[dict]:
        messages_data = []
        try:
            messages = self.gmail_service.users().messages().list(userId='me', labelIds=['INBOX'],
                                                                  maxResults=5).execute().get('messages', [])
            for msg in messages:
                msg_detail = self.gmail_service.users().messages().get(userId='me', id=msg['id'],
                                                                       format='full').execute()
                headers = msg_detail.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                message_id = msg_detail.get('id')

                # Extract the body text (supports plain text emails)
                body = ""
                payload = msg_detail.get('payload', {})
                if 'parts' in payload:
                    # Multipart message - find the text/plain part
                    for part in payload['parts']:
                        if part.get('mimeType') == 'text/plain':
                            data = part.get('body', {}).get('data')
                            if data:
                                body = base64.urlsafe_b64decode(data).decode('utf-8')
                                break
                else:
                    # Single part message
                    data = payload.get('body', {}).get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')

                messages_data.append({
                    'message_id': message_id,
                    'subject': subject,
                    'body': body
                })

        except Exception as e:
            raise Exception(f"Failed to fetch Gmail messages: {e}")

        return messages_data

    def send_email(self, to: str, subject: str, body_text: str) -> dict[str, Any]:
        message = EmailMessage()
        message.set_content(body_text)
        message['To'] = to
        message['From'] = "me"
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': encoded_message}

        send_result = self.gmail_service.users().messages().send(userId="me", body=create_message).execute()
        return {'message_id': send_result['id']}
