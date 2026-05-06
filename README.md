# Plain Anthropic Opus Agent

Correlation Zero agent that does one thing: send the platform prompt to the
Anthropic Messages API and return the model's text response.

The default model is `claude-opus-4-7` because this submission is intended to run
against Opus 4.7. Set `ANTHROPIC_MODEL` if the operator needs to use a specific
Anthropic model ID or alias.

## Runtime Contract

- Entry point: `agent.py`
- Agent class: `PlainAnthropicOpusAgent`
- CLI command: `python agent.py`
- Required secret: `ANTHROPIC_API_KEY`
- Optional model override: `ANTHROPIC_MODEL`
- Optional request timeout: `ANTHROPIC_TIMEOUT_SECONDS`, capped at 20 seconds
- External API: `https://api.anthropic.com/v1/messages`
- Dependency: `certifi`

## Quickstart

```bash
./tools/test_agent.sh
./tools/prepare_submission.sh
```

For local live calls, set `.env.local`:

```bash
ANTHROPIC_API_KEY="..."
ANTHROPIC_MODEL="claude-opus-4-7"
ANTHROPIC_TIMEOUT_SECONDS="20"
```

Without `ANTHROPIC_API_KEY`, the agent returns a short configuration error
instead of calling Anthropic.
