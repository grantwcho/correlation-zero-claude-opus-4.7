from .schemas import AgentQuery, ResponseFormat


class Agent:
    AGENT_ID = "replace-me"
    SUPPORTED_FORMATS = [ResponseFormat.FREEFORM.value]

    def freeform(self, query: AgentQuery) -> str:
        raise NotImplementedError("Implement freeform(query) in your agent.")
