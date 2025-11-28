from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from google.adk.agents import LlmAgent


@dataclass(slots=True)
class AgentSpec:
    """Declarative configuration for constructing an LLM-backed agent."""

    name: str
    description: str
    instruction: str
    tools: Sequence[Callable[..., Any]]
    output_key: str
    model: str | None = None
    agent_kwargs: Mapping[str, Any] = field(default_factory=dict)


class AgentFactory:
    """Factory that materializes `LlmAgent` instances from reusable specs."""

    def __init__(self, default_model: str = "gemini-2.0-flash"):
        self.default_model = default_model

    def create(self, spec: AgentSpec, **overrides: Any) -> LlmAgent:
        """
        Instantiate an `LlmAgent` using the provided spec and optional overrides.

        Overrides can include any field present on `AgentSpec`, along with
        `agent_kwargs` for additional constructor keyword arguments.
        """
        model = overrides.get("model", spec.model or self.default_model)
        tools = overrides.get("tools", spec.tools)
        if not tools:
            raise ValueError(f"Agent '{spec.name}' requires at least one tool.")

        agent_kwargs: dict[str, Any] = {}
        agent_kwargs.update(spec.agent_kwargs or {})
        agent_kwargs.update(overrides.get("agent_kwargs", {}))

        return LlmAgent(
            name=overrides.get("name", spec.name),
            model=model,
            description=overrides.get("description", spec.description),
            instruction=overrides.get("instruction", spec.instruction),
            tools=tools,
            output_key=overrides.get("output_key", spec.output_key),
            **agent_kwargs,
        )
