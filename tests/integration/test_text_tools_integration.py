from types import SimpleNamespace

import pytest

from personal_assistant.tools import base_tool
from personal_assistant.tools.text_tools import TextTools


@pytest.fixture
def fake_genai(monkeypatch):
    prompts: list[str] = []

    class FakeModel:
        def __init__(self, _model_name):
            self.prompts = prompts

        def generate_content(self, prompt: str):
            prompts.append(prompt)
            return SimpleNamespace(text=f"LLM::{len(prompts)}")

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
def text_tools(fake_genai):
    tool = TextTools()
    return tool, fake_genai


def test_generate_ideas_invokes_model_with_topic(text_tools):
    tool, prompts = text_tools

    ideas = tool.generate_ideas("backend automation")

    assert ideas == "LLM::1"
    assert "backend automation" in prompts[0]


def test_write_content_expands_outline(text_tools):
    tool, prompts = text_tools

    draft = tool.write_content("- idea A")

    assert draft.startswith("LLM::")
    assert "- idea A" in prompts[0]


def test_format_draft_requests_markdown(text_tools):
    tool, prompts = text_tools

    formatted = tool.format_draft("plain draft")

    assert formatted.startswith("LLM::")
    assert "Format this draft as clean Markdown" in prompts[0]
