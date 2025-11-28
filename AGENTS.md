# Repository Guidelines

## Project Structure & Module Organization
- Core orchestration lives in `agent.py`; agents are composed using `google_tools` and `text_tools`.
- Shared tooling sits in `tools/` (LLM wrappers, Google utilities) and `resources/` (Google Workspace client helpers).
- Configuration artifacts (`config.py`, `.env`, OAuth `credentials.json`, `token.json`) stay at repo root; do not commit regenerated tokens.
- Tests and runnable diagnostics belong in `tests/`; mirror the source layout (e.g., `tests/test_google_workspace.py` exercises `resources/google_workspace.py`).

## Setup, Build & Run
- Create a virtualenv (optional but recommended) and install dependencies: `pip install -r requirements.txt`.
- Run the primary agent chain locally with `adk run .`; it loads `agent.root_agent`.
- Export or define `API_KEY` in `.env` before invoking any command to avoid runtime auth failures.

## Coding Style & Naming Conventions
- Python modules use snake_case (`google_tools.py`), classes are CapWords (`GoogleWorkspace`, `GoogleTools`), and functions/methods are snake_case.
- Adhere to 4-space indentation and keep line length ≤ 100 chars to match existing files.
- Configure `ruff` or `black --line-length 100` locally before committing; format touchpoints and fix lint warnings.

## Testing Guidelines
- Prefer pytest-style unit tests under `tests/`, named `test_<module>.py`; structure assertions around public behavior (e.g., email summaries, Drive listings).
- To run the current diagnostics: `python -m tests.test_google_workspace` (uses live Google APIs; supply credentials).
- Add mocks or fixtures for Google services where possible to keep CI offline and reproducible.

## Commit & Pull Request Guidelines
- Follow imperative, present-tense commit messages (e.g., `Add Drive folder caching`) consistent with the existing concise history.
- Scope each PR to one feature or fix; include a summary of behavior, manual test notes (`adk run .`, key scripts), and link related issues.
- Provide screenshots or terminal snippets when changes affect Google Workspace flows to help reviewers validate auth-dependent behavior.

## Security & Configuration Tips
- Keep OAuth secrets (`credentials.json`, `token.json`) out of version control; refresh tokens locally and rotate when compromised.
- Avoid logging raw email bodies or tokens; redact sensitive payloads before storing or sharing debugging output.
