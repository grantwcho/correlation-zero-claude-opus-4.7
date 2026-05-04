"""Heavily commented reference agent for contributors."""

from correlation_zero import Agent, AgentQuery


class ExampleAgent(Agent):
    # Keep this in sync with manifest.yaml.
    AGENT_ID = "example-agent-001"

    def freeform(self, query: AgentQuery) -> str:
        # In a real agent, this method would fetch data, compute signals,
        # and return the narrative answer the platform should display.
        topic = query.context.get("topic", "the user's request")
        return (
            f"Answering {topic}: {query.prompt} "
            "Replace this with your prompts, API calls, tools, business logic, "
            "or any other code your agent needs."
        )
