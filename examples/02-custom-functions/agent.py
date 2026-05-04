from correlation_zero import Agent, AgentQuery


def summarize_text(text: str) -> str:
    words = text.split()
    if len(words) <= 12:
        return text
    return " ".join(words[:12]) + "..."


def classify_request(prompt: str) -> str:
    lowered = prompt.lower()
    if "risk" in lowered:
        return "risk review"
    if "summarize" in lowered or "summary" in lowered:
        return "summary"
    return "general analysis"


class CustomFunctionsAgent(Agent):
    AGENT_ID = "example-custom-functions-001"

    def freeform(self, query: AgentQuery) -> str:
        request_type = classify_request(query.prompt)
        prompt_summary = summarize_text(query.prompt)
        return f"Handled as {request_type}. Prompt summary: {prompt_summary}"
