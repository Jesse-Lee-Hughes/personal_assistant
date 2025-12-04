from google.adk.agents import SequentialAgent

from .agents import AgentFactory, AgentSpec, WorkflowBuilder, WorkflowStep
from .tools.assistant_tools import AssistantTools
from .tools.google_tools import GoogleTools
from .tools.marketplace_tools import MarketplaceTools
from .tools.text_tools import TextTools

DEFAULT_MODEL = "gemini-2.0-flash"

text_tools = TextTools()
google_tools = GoogleTools()
marketplace_tools = MarketplaceTools()
assistant_tools = AssistantTools(
    google_tools=google_tools,
    marketplace_tools=marketplace_tools,
    text_tools=text_tools,
)

factory = AgentFactory(default_model=DEFAULT_MODEL)
workflow_builder = WorkflowBuilder(factory=factory)

STATIC_AGENT_SPECS: dict[str, AgentSpec] = {
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
    "find_motorcycles": AgentSpec(
        name="MotorcycleResearchAgent",
        description=(
            "Aggregates marketplace listings for qualifying 2-stroke dirt bikes."
        ),
        instruction=(
            "Call search_motorcycles() and return only the JSON payload of listings."
        ),
        tools=[marketplace_tools.search_motorcycles],
        output_key="raw_motorcycle_listings",
    ),
    "output_summarization": AgentSpec(
        name="MotorcycleValidationAgent",
        description="Validates and normalises the motorcycle procurement results.",
        instruction=(
            "Call finalize_motorcycle_results(raw_motorcycle_listings) where "
            "`raw_motorcycle_listings` is the previous output and respond with only "
            "the cleaned JSON report."
        ),
        tools=[text_tools.finalize_motorcycle_results],
        output_key="motorcycle_report",
    ),
}

WORKFLOWS: dict[str, SequentialAgent] = {}

WORKFLOWS["content_creator"] = workflow_builder.build(
    name="content_creator",
    description="Generates ideas, drafts, and formatted Markdown for content creation.",
    steps=[
        WorkflowStep(STATIC_AGENT_SPECS["idea_generator"]),
        WorkflowStep(STATIC_AGENT_SPECS["draft_writer"]),
        WorkflowStep(STATIC_AGENT_SPECS["markdown_formatter"]),
    ],
)

WORKFLOWS["email_digest"] = workflow_builder.build(
    name="email_digest",
    description="Summarizes inbox activity and emails it to the recipient.",
    steps=[
        WorkflowStep(STATIC_AGENT_SPECS["email_summarizer"]),
        WorkflowStep(STATIC_AGENT_SPECS["email_sender"]),
    ],
)

WORKFLOWS["personal_assistant"] = workflow_builder.build(
    name="personal_assistant",
    description="Summarizes files and delivers a daily email digest.",
    steps=[
        WorkflowStep(STATIC_AGENT_SPECS["file_summary"]),
        WorkflowStep(STATIC_AGENT_SPECS["email_summarizer"]),
        WorkflowStep(STATIC_AGENT_SPECS["email_sender"]),
    ],
)

WORKFLOWS["procurement_assistant"] = workflow_builder.build(
    name="procurement_assistant",
    description="Searches the web for motorcycles of a specific criteria",
    steps=[
        WorkflowStep(STATIC_AGENT_SPECS["find_motorcycles"]),
        WorkflowStep(STATIC_AGENT_SPECS["output_summarization"]),
    ],
)

ROOT_AGENT_SPEC = AgentSpec(
    name="LifeAssistant",
    description="Handles user requests by invoking the Life project toolset.",
    instruction=(
        "You are the primary assistant for the Life project. Identify the user's task and call the "
        "relevant tools to complete it. For Google Drive questions, call read_files() and summarise "
        "the result. For email digests, call summarize_emails() and provide the structured summary; "
        "only call send_email_summary(summary) if the user explicitly asks to send it. For "
        "motorcycle procurement requests, call procure_motorcycle(requirements) once, passing the "
        "user's requirements verbatim. That tool already runs the full workflow and returns the "
        "cleaned JSON. You may ask concise clarifying questions when the request is ambiguous."
    ),
    tools=[
        text_tools.generate_ideas,
        text_tools.write_content,
        text_tools.format_draft,
        google_tools.read_files,
        google_tools.summarize_emails,
        google_tools.send_email_summary,
        assistant_tools.procure_motorcycle,
    ],
    output_key="assistant_response",
)

root_agent = factory.create(ROOT_AGENT_SPEC)
