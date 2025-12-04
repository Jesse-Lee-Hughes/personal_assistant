from __future__ import annotations

from typing import Optional

from .base_tool import BaseTool
from ..resources.google_workspace import GoogleWorkspace

scopes = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

_workspace: Optional[GoogleWorkspace] = None


def get_workspace() -> GoogleWorkspace:
    global _workspace
    if _workspace is None:
        _workspace = GoogleWorkspace(scopes)
    return _workspace


class GoogleTools(BaseTool):

    def summarize_emails(self):
        workspace = get_workspace()
        messages = workspace.list_gmail_messages()
        if not messages:
            return "Communicate to the user that there are no email messages to be summarized. This may be an error."
        resp = self.model.generate_content(
            f"Summarize all of the provided emails concisely in bullet points.  :\n\n{messages}"
        )
        return resp.text

    def send_email_summary(self, summary: str):
        workspace = get_workspace()
        to = 'jessesaddress@gmail.com'
        subject = "An AI summary of Jesse's emails'"
        resp = self.model.generate_content(
            f"Format the email into an eloquently styled message to my "
            f"wife 'Irene' with love from Jesse via AI Personal Assistant:\n\n{summary}."
        )
        if not resp.text:
            raise RuntimeError("Unable to get a valid response from LLM.")
        sent_message = workspace.send_email(to=to, subject=subject, body_text=resp.text)
        return sent_message

    def read_files(self):
        workspace = get_workspace()
        files = workspace.list_drive_files()
        assert files
        resp = self.model.generate_content("Give me an overall summary of how many files, the file size and contents")
        return resp.text
