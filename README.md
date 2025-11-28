### Quickstart

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Run the default personal assistant workflow (file summary → email digest):

```bash
API_KEY=<your key> .venv/bin/adk run .
```

### Workflows & Agents

- Agent definitions live in `agent.py` via reusable `AgentSpec` entries.
- Compose new workflows by instantiating `WorkflowStep` objects and passing them to `WorkflowBuilder`.
- Existing workflows are exposed through the `WORKFLOWS` map (`content_creator`, `email_digest`, `personal_assistant`).
- `agent.py` ensures the repository root is on `sys.path` so local packages such as `personal_assistant` stay importable when the ADK loader changes the working directory.
