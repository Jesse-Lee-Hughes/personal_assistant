from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from google.adk.agents import SequentialAgent

from .factory import AgentFactory, AgentSpec


@dataclass(slots=True)
class WorkflowStep:
    """Declarative representation of a single agent step."""

    spec: AgentSpec
    overrides: dict[str, Any] = field(default_factory=dict)


class WorkflowBuilder:
    """Helper for composing sequential agent workflows."""

    def __init__(self, factory: AgentFactory):
        self.factory = factory

    def build(
        self,
        name: str,
        steps: Sequence[WorkflowStep],
        *,
        description: str = "",
    ) -> SequentialAgent:
        """Create a `SequentialAgent` by materializing each declared `WorkflowStep`."""
        sub_agents = [self.factory.create(step.spec, **step.overrides) for step in steps]
        return SequentialAgent(
            name=name,
            sub_agents=sub_agents,
            description=description or name,
        )

    def inline(
        self,
        name: str,
        step_specs: Iterable[AgentSpec],
        *,
        description: str = "",
    ) -> SequentialAgent:
        """Convenience for building a workflow from specs without overrides."""
        steps = [WorkflowStep(spec=spec) for spec in step_specs]
        return self.build(name, steps, description=description)
