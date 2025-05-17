from google.adk.agents import LlmAgent, SequentialAgent

from .tools.google_tools import GoogleTools
from .tools.text_tools import TextTools

text_tools = TextTools()
google_tools = GoogleTools()

topic_agent = LlmAgent(
    name="IdeaAgent",
    model="gemini-2.0-flash",
    description="Brainstorms blog post ideas.",
    instruction=(
        "Call generate_ideas(topic) with the exact topic string you receive "
        "and return only the ideas."
    ),
    tools=[text_tools.generate_ideas],
    output_key="ideas"
)

draft_agent = LlmAgent(
    name="WriterAgent",
    model="gemini-2.0-flash",
    description="Writes a blog post draft from ideas.",
    instruction=(
        "Call write_content(ideas), where `ideas` is the output from the prior step, "
        "and return only the draft text."
    ),
    tools=[text_tools.write_content],
    output_key="draft"
)

format_agent = LlmAgent(
    name="FormatterAgent",
    model="gemini-2.0-flash",
    description="Formats the draft into Markdown.",
    instruction=(
        "Call format_draft(draft), where `draft` is the previous output, "
        "and return only the final Markdown."
    ),
    tools=[text_tools.format_draft],
    output_key="formatted"
)

email_summary_agent = LlmAgent(
    name="EmailSummaryAgent",
    model="gemini-2.0-flash",
    description="Summarizes emails.",
    instruction=(
        "Call summarize_emails() function and ensure the result is correctly formatted"
        " and adequately summarizes the emails."
    ),
    tools=[google_tools.summarize_emails],
    output_key="summary"
)

email_sending_agent = LlmAgent(
    name="EmailSendAgent",
    model="gemini-2.0-flash",
    description="Send the summarized emails.",
    instruction=(
        "Call send_email_summary(summary) function where `summary` is the previous output text, "
        "and return the response"
    ),
    tools=[google_tools.send_email_summary],
    output_key="sent_message"
)

root_agent = SequentialAgent(
    name="personal_assistant",
    sub_agents=[email_summary_agent, email_sending_agent],
    description="Performs an email analyses and returns a summary of the results."
)
