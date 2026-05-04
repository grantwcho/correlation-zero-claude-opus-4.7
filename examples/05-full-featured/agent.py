from correlation_zero import Agent, AgentQuery


class FullFeaturedAgent(Agent):
    AGENT_ID = "example-full-featured-001"

    def build_answer(self, query: AgentQuery) -> str:
        audience = query.context.get("audience", "platform user")
        metric_note = ""
        if query.metrics:
            metric_note = f" Metrics in scope: {', '.join(query.metrics)}."
        return (
            f"For {audience}, I would answer: {query.prompt} "
            "The response is generated from the agent's local logic, optional "
            "context, and any external systems the contributor chooses to wire in."
            f"{metric_note}"
        )

    def freeform(self, query: AgentQuery) -> str:
        return self.build_answer(query)
