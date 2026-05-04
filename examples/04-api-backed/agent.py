from correlation_zero import Agent, AgentQuery


class APIBackedAgent(Agent):
    AGENT_ID = "example-api-backed-001"

    def fetch_records(self, topic: str) -> list[dict]:
        return [
            {"source": "internal_api", "summary": f"Latest status for {topic} is stable."},
            {"source": "partner_feed", "summary": f"Partner feed has no blockers for {topic}."},
        ]

    def freeform(self, query: AgentQuery) -> str:
        topic = query.context.get("topic", "the request")
        records = self.fetch_records(topic)
        sources = ", ".join(record["source"] for record in records)
        summaries = " ".join(record["summary"] for record in records)
        return (
            f"{summaries} Sources checked: {sources}. "
            f"Original prompt: {query.prompt}"
        )
