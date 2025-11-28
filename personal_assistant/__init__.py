"""Utilities for defining agents and workflows within the personal assistant project."""

from .agents import AgentFactory, AgentSpec, WorkflowBuilder, WorkflowStep

__all__ = [
    "AgentFactory",
    "AgentSpec",
    "WorkflowBuilder",
    "WorkflowStep",
    "agent",
]


def __getattr__(name: str):
    if name == "agent":
        from . import agent as agent_module

        return agent_module
    raise AttributeError(name)
