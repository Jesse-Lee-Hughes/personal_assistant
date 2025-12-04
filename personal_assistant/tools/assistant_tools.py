from __future__ import annotations

from .google_tools import GoogleTools
from .marketplace_tools import MarketplaceTools
from .text_tools import TextTools


class AssistantTools:
    """Composite helpers that bundle multi-step agent workflows into single tools."""

    def __init__(
        self,
        *,
        google_tools: GoogleTools,
        marketplace_tools: MarketplaceTools,
        text_tools: TextTools,
    ):
        self.google_tools = google_tools
        self.marketplace_tools = marketplace_tools
        self.text_tools = text_tools

    def procure_motorcycle(self, requirements: str | None = None) -> str:
        """
        Run the motorcycle procurement flow end-to-end and return the validated JSON report.

        `requirements` may include user-specific preferences that should act as soft filters.
        """
        raw_results = self.marketplace_tools.search_motorcycles(
            requirements=requirements or ""
        )
        return self.text_tools.finalize_motorcycle_results(raw_results)
