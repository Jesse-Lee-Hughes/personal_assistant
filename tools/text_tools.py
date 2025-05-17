from .base_tool import BaseTool


class TextTools(BaseTool):
    def generate_ideas(self, topic: str) -> str:
        """Ask Gemini to brainstorm blog post idea for a topic."""
        resp = self.model.generate_content(
            f"Brainstorm 4–6 creative blog post ideas for the topic:\n\n{topic}"
        )
        return resp.text

    def write_content(self, ideas: str) -> str:
        """Ask Gemini to expand an outline into a ~300-word draft."""
        resp = self.model.generate_content(
            "Expand the following outline into a cohesive ~300-word blog post:\n\n"
            f"{ideas}"
        )
        return resp.text

    def format_draft(self, draft: str) -> str:
        """Ask Gemini to format the draft as clean Markdown."""
        resp = self.model.generate_content(
            "Format this draft as clean Markdown with headings, sub-headings, and bullet lists:\n\n"
            f"{draft}"
        )
        return resp.text
