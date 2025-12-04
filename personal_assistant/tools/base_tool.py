from __future__ import annotations

from abc import ABC
from types import SimpleNamespace

try:
    import google.generativeai as genai
except ModuleNotFoundError:  # pragma: no cover - exercised indirectly in tests
    class _MissingGenAI(SimpleNamespace):  # type: ignore[override]
        """Placeholder that raises a helpful error if the SDK is absent."""

        def __getattr__(self, item: str):
            raise RuntimeError(
                "google-generativeai is required. Install requirements.txt or "
                "monkeypatch `personal_assistant.tools.base_tool.genai` for tests."
            ) from None

    genai = _MissingGenAI()  # type: ignore[assignment]

try:
    import config
except Exception as exc:  # pragma: no cover - defensive, config validated at runtime
    _config_error: Exception | None = exc
    config = None  # type: ignore[assignment]
else:
    _config_error = None


class BaseTool(ABC):
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        if _config_error is not None or getattr(config, "api_key", None) is None:
            raise RuntimeError(
                "Missing GOOGLE_API_KEY configuration. Populate .env or "
                "export GOOGLE_API_KEY before instantiating BaseTool."
            ) from _config_error

        self.model_name = model_name
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(model_name=self.model_name)
