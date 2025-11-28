from types import SimpleNamespace

import pytest

from personal_assistant.tools import base_tool
from personal_assistant.tools.google_tools import GoogleTools


class FakeWorkspace:
    def __init__(self):
        self.drive_calls = 0
        self.last_drive_folder = None
        self.drive_files = []

        self.gmail_list_calls = 0
        self.gmail_messages: list[dict] = []

        self.sent_messages: list[dict] = []

    def list_drive_files(self, folder_id=None):
        self.drive_calls += 1
        self.last_drive_folder = folder_id
        return list(self.drive_files)

    def list_gmail_messages(self):
        self.gmail_list_calls += 1
        return list(self.gmail_messages)

    def send_email(self, *, to: str, subject: str, body_text: str):
        payload = {"to": to, "subject": subject, "body_text": body_text}
        self.sent_messages.append(payload)
        return {"message_id": "abc-123"}


@pytest.fixture
def fake_genai(monkeypatch):
    prompts: list[str] = []

    class FakeModel:
        def __init__(self, _model_name):
            self.prompts = prompts

        def generate_content(self, prompt: str):
            prompts.append(prompt)
            return SimpleNamespace(text=f"LLM_RESPONSE::{prompt}")

    monkeypatch.setattr(base_tool.genai, "configure", lambda api_key=None: None)
    monkeypatch.setattr(
        base_tool.genai,
        "GenerativeModel",
        lambda model_name: FakeModel(model_name),
    )

    fake_config = SimpleNamespace(api_key="test-api-key")
    monkeypatch.setattr(base_tool, "config", fake_config, raising=False)
    monkeypatch.setattr(base_tool, "_config_error", None, raising=False)

    return prompts


@pytest.fixture
def google_tools(fake_genai, monkeypatch):
    workspace = FakeWorkspace()
    monkeypatch.setattr("personal_assistant.tools.google_tools.get_workspace", lambda: workspace)
    tool = GoogleTools()
    return tool, workspace, fake_genai


def test_summarize_emails_generates_summary(google_tools):
    tool, workspace, prompts = google_tools
    workspace.gmail_messages = [
        {"subject": "Hello", "body": "Message body"},
        {"subject": "Updates", "body": "Another message"},
    ]

    summary = tool.summarize_emails()

    assert summary.startswith("LLM_RESPONSE::")
    assert "Summarize all of the provided emails" in prompts[0]
    assert workspace.gmail_list_calls == 1


def test_summarize_emails_returns_notice_when_empty_inbox(google_tools):
    tool, workspace, prompts = google_tools
    workspace.gmail_messages = []

    summary = tool.summarize_emails()

    assert summary.startswith("Communicate to the user")
    assert prompts == []
    assert workspace.gmail_list_calls == 1


def test_send_email_summary_formats_and_sends(google_tools):
    tool, workspace, prompts = google_tools

    result = tool.send_email_summary("Daily summary text")

    assert result == {"message_id": "abc-123"}
    # Ensure the LLM formatted the email content.
    assert len(prompts) == 1
    assert "Format the email" in prompts[0]
    assert workspace.sent_messages[0]["body_text"].startswith("LLM_RESPONSE::")
    assert workspace.sent_messages[0]["to"] == "jessesaddress@gmail.com"


def test_read_files_requests_drive_listing_and_summary(google_tools):
    tool, workspace, prompts = google_tools
    workspace.drive_files = [{"id": "1", "name": "doc"}]

    summary = tool.read_files()

    assert summary.startswith("LLM_RESPONSE::")
    assert workspace.drive_calls == 1
    assert prompts[-1] == "Give me an overall summary of how many files, the file size and contents"
