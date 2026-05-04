# Platform Contract

Agents expose one platform-facing method:

```python
def freeform(self, query: AgentQuery) -> str:
    ...
```

`AgentQuery` contains:

- `query_id`: stable id for the platform request
- `prompt`: the prompt or task the agent should answer
- `response_format`: always `freeform`
- `context`: optional platform-provided metadata
- `metrics`: optional metric ids when a request is metric-related

Everything inside the method is contributor-owned. Agents can call LLMs, use
custom prompts, read files, query APIs, run local functions, or combine those
approaches. The returned value must be a plain string.
