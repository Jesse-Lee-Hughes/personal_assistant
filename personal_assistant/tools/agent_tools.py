from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING

from ..agents import AgentSpec, WorkflowBuilder, WorkflowStep
from ..tools.text_tools import TextTools

if TYPE_CHECKING:  # pragma: no cover - used only for typing
    from google.adk.agents import SequentialAgent


class AgentOrchestrationError(RuntimeError):
    """Raised when a generated agent blueprint is invalid."""


@dataclass(slots=True)
class GeneratedAgentConfig:
    """Normalized representation of a dynamically generated agent."""

    key: str
    name: str
    description: str
    task_prompt: str
    instruction: str | None
    output_key: str


@dataclass(slots=True)
class GeneratedWorkflowPlan:
    """Structured plan produced from a goal description."""

    name: str
    description: str
    agents: list[GeneratedAgentConfig]


def _require_text(payload: dict[str, object], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AgentOrchestrationError(
            f"Agent planner response is missing a non-empty string for '{key}'."
        )
    return value.strip()


def _slugify(source: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", source).strip("_")
    return cleaned.lower() or "agent"


def _escape_quotes(text: str) -> str:
    return text.replace('"', '\\"')


class AgentOrchestrationTools:
    """
    Utilities that translate LLM plans into runnable SequentialAgent workflows.
    """

    def __init__(
        self,
        *,
        workflow_builder: WorkflowBuilder,
        workflow_registry: dict[str, "SequentialAgent"],
        text_tools: TextTools,
    ):
        self.workflow_builder = workflow_builder
        self.workflow_registry = workflow_registry
        self.text_tools = text_tools
        self._static_workflow_keys = set(workflow_registry)

    def register_goal_workflow(self, plan_json: str) -> str:
        """
        Materialize and register a new workflow from a planner's JSON output.
        """
        plan = self._parse_plan(plan_json)
        steps = [WorkflowStep(spec=spec) for spec in self._build_agent_specs(plan)]
        workflow = self.workflow_builder.build(
            name=plan.name,
            description=plan.description,
            steps=steps,
        )
        self.workflow_registry[plan.name] = workflow
        agent_names = ", ".join(agent.name for agent in plan.agents)
        return (
            f"Registered workflow '{plan.name}' with agents: {agent_names}. "
            "Use workflow_registry[workflow_name] to run the new chain."
        )

    def list_goal_workflows(self) -> str:
        """
        Summarize dynamically created workflows using this tool instance.
        """
        dynamic = {
            name: workflow
            for name, workflow in self.workflow_registry.items()
            if name not in self._static_workflow_keys
        }
        if not dynamic:
            return "No goal-driven workflows have been registered yet."
        rows = [f"- {name}: {workflow.description}" for name, workflow in dynamic.items()]
        return "Goal-driven workflows:\n" + "\n".join(rows)

    def _build_agent_specs(self, plan: GeneratedWorkflowPlan) -> Iterable[AgentSpec]:
        for agent in plan.agents:
            instruction = agent.instruction or (
                "Call perform_task(task_prompt=\""
                f"{_escape_quotes(agent.task_prompt)}"
                "\", context=<summarize prior outputs as needed>) and return only the "
                "finished deliverable."
            )
            yield AgentSpec(
                name=agent.name,
                description=agent.description,
                instruction=instruction,
                tools=[self.text_tools.perform_task],
                output_key=agent.output_key,
            )

    def _parse_plan(self, plan_json: str) -> GeneratedWorkflowPlan:
        try:
            payload = json.loads(plan_json)
        except json.JSONDecodeError as exc:
            raise AgentOrchestrationError(
                "Agent planner did not return valid JSON. "
                "Re-run the planner or refine the goal."
            ) from exc

        if not isinstance(payload, dict):
            raise AgentOrchestrationError("Planner payload must be a JSON object.")

        raw_name = _require_text(payload, "workflow_name")
        workflow_name = _slugify(raw_name)
        description = _require_text(payload, "workflow_description")

        agents_payload = payload.get("agents")
        if not isinstance(agents_payload, list) or not agents_payload:
            raise AgentOrchestrationError(
                "Planner response must include a non-empty 'agents' list."
            )

        agents: list[GeneratedAgentConfig] = []
        seen_keys: set[str] = set()
        for idx, raw_agent in enumerate(agents_payload, start=1):
            if not isinstance(raw_agent, dict):
                raise AgentOrchestrationError(
                    "Each agent entry must be a JSON object with descriptive fields."
                )
            name = _require_text(raw_agent, "name")
            description_text = _require_text(raw_agent, "description")
            task_prompt = _require_text(raw_agent, "task_prompt")
            instruction = raw_agent.get("instruction")
            if isinstance(instruction, str):
                instruction = instruction.strip() or None
            key_source = (
                raw_agent.get("output_key")
                or raw_agent.get("key")
                or name
            )
            candidate_key = _slugify(str(key_source))
            if candidate_key in seen_keys:
                candidate_key = f"{candidate_key}_{idx}"
            seen_keys.add(candidate_key)
            agents.append(
                GeneratedAgentConfig(
                    key=candidate_key,
                    name=name,
                    description=description_text,
                    task_prompt=task_prompt,
                    instruction=instruction,
                    output_key=candidate_key,
                )
            )

        return GeneratedWorkflowPlan(
            name=workflow_name,
            description=description,
            agents=agents,
        )
