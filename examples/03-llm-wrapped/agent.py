from correlation_zero import Agent, AgentQuery


def model_stub(prompt: str, context: dict) -> str:
    topic = context.get("topic", "the requested task")
    return f"Example LLM response about {topic}: {prompt}"


class LLMWrappedAgent(Agent):
    AGENT_ID = "example-llm-wrapped-001"

    def freeform(self, query: AgentQuery) -> str:
        return model_stub(query.prompt, query.context)
