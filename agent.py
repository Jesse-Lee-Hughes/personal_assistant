"""Compatibility wrapper for `personal_assistant.agent`.

This ensures tooling that expects `agent` at the project root continues to
work after reorganizing the package structure.
"""

from __future__ import annotations

from pathlib import Path
import sys

# Ensure local packages (e.g., `personal_assistant`) stay importable even when the
# agent is loaded from outside the repository root.
REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from personal_assistant.agent import *  # noqa: F401,F403
