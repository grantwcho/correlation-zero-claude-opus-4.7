from correlation_zero import Agent, AgentQuery


class MinimalAgent(Agent):
    AGENT_ID = "example-minimal-001"

    def freeform(self, query: AgentQuery) -> str:
        return f"Minimal response for {query.query_id}: {query.prompt}"
