import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from personal_assistant.tools import text_tools as text_tools_module  # noqa: E402
from personal_assistant.tools.text_tools import TextTools  # noqa: E402


def test_persist_procurement_results_writes_json(tmp_path, monkeypatch):
    target = tmp_path / "motorcycle.json"
    monkeypatch.setattr(
        text_tools_module, "_PROCUREMENT_RESULTS_PATH", target, raising=False
    )

    payload = json.dumps({"scraped_at": "2024-01-01T00:00:00Z"})

    TextTools._persist_procurement_results(payload)

    assert target.exists()
    saved = json.loads(target.read_text())
    assert saved == {"scraped_at": "2024-01-01T00:00:00Z"}


def test_persist_procurement_results_ignores_invalid_json(tmp_path, monkeypatch):
    target = tmp_path / "motorcycle.json"
    monkeypatch.setattr(
        text_tools_module, "_PROCUREMENT_RESULTS_PATH", target, raising=False
    )

    TextTools._persist_procurement_results("", "not-json")

    assert target.exists()
    assert target.read_text() == "not-json"


def test_finalize_motorcycle_results_writes_to_file(tmp_path, monkeypatch):
    target = tmp_path / "motorcycle.json"
    monkeypatch.setattr(
        text_tools_module, "_PROCUREMENT_RESULTS_PATH", target, raising=False
    )

    payload = json.dumps({"scraped_at": "2024-01-01T00:00:00Z"})

    class DummyModel:
        def generate_content(self, prompt: str):
            return type("Resp", (), {"text": f"```json\n{payload}\n```"})()

    def fake_init(self, model_name: str = ""):
        self.model_name = model_name
        self.model = DummyModel()

    monkeypatch.setattr(
        text_tools_module.BaseTool, "__init__", fake_init, raising=False
    )

    tool = TextTools()
    result = tool.finalize_motorcycle_results("{}")

    assert target.exists()
    file_content = target.read_text()
    assert "```" not in file_content
    data = json.loads(file_content)
    assert data == {"scraped_at": "2024-01-01T00:00:00Z"}
    assert json.loads(result) == data
