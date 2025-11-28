from google.adk.agents import SequentialAgent

from .agents import AgentFactory, AgentSpec, WorkflowBuilder, WorkflowStep
from .tools.google_tools import GoogleTools
from .tools.text_tools import TextTools

DEFAULT_MODEL = "gemini-2.0-flash"

text_tools = TextTools()
google_tools = GoogleTools()

factory = AgentFactory(default_model=DEFAULT_MODEL)
workflow_builder = WorkflowBuilder(factory=factory)

AGENT_SPECS: dict[str, AgentSpec] = {
    "file_summary": AgentSpec(
        name="FileAgent",
        description="Summarizes files stored in Google Drive.",
        instruction="Call read_files() and return only a concise bullet summary of the files.",
        tools=[google_tools.read_files],
        output_key="files",
    ),
    "idea_generator": AgentSpec(
        name="IdeaAgent",
        description="Brainstorms fresh content ideas from a topic string.",
        instruction="Call generate_ideas(topic) using the provided topic and respond with the ideas only.",
        tools=[text_tools.generate_ideas],
        output_key="ideas",
    ),
    "draft_writer": AgentSpec(
        name="WriterAgent",
        description="Expands an outline or idea list into a full draft.",
        instruction="Call write_content(ideas) where `ideas` is the previous output and return only the draft text.",
        tools=[text_tools.write_content],
        output_key="draft",
    ),
    "markdown_formatter": AgentSpec(
        name="FormatterAgent",
        description="Formats a draft into polished Markdown.",
        instruction="Call format_draft(draft) where `draft` is the previous output and return only the final Markdown.",
        tools=[text_tools.format_draft],
        output_key="formatted",
    ),
    "email_summarizer": AgentSpec(
        name="EmailSummaryAgent",
        description="Summarizes recent Gmail messages.",
        instruction="Call summarize_emails() and return a structured summary ready for delivery.",
        tools=[google_tools.summarize_emails],
        output_key="summary",
    ),
    "email_sender": AgentSpec(
        name="EmailSendAgent",
        description="Delivers a prepared summary via Gmail.",
        instruction="Call send_email_summary(summary) with the previous summary text and return the send confirmation.",
        tools=[google_tools.send_email_summary],
        output_key="sent_message",
    ),
}

WORKFLOWS: dict[str, SequentialAgent] = {
    "content_creator": workflow_builder.build(
        name="content_creator",
        description="Generates ideas, drafts, and formatted Markdown for content creation.",
        steps=[
            WorkflowStep(AGENT_SPECS["idea_generator"]),
            WorkflowStep(AGENT_SPECS["draft_writer"]),
            WorkflowStep(AGENT_SPECS["markdown_formatter"]),
        ],
    ),
    "email_digest": workflow_builder.build(
        name="email_digest",
        description="Summarizes inbox activity and emails it to the recipient.",
        steps=[
            WorkflowStep(AGENT_SPECS["email_summarizer"]),
            WorkflowStep(AGENT_SPECS["email_sender"]),
        ],
    ),
}

root_agent = workflow_builder.build(
    name="personal_assistant",
    description="Summarizes files and delivers a daily email digest.",
    steps=[
        WorkflowStep(AGENT_SPECS["file_summary"]),
        WorkflowStep(AGENT_SPECS["email_summarizer"]),
        WorkflowStep(AGENT_SPECS["email_sender"]),
    ],
)
