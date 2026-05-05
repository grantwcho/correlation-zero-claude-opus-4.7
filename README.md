# Semiconductor Language Shift Agent

Correlation Zero agent for semiconductor disclosure review. It reads earnings
calls, 10-Ks, 10-Qs, investor decks, and guidance updates, then flags changes in
language around AI demand, inventory, gross margin, capex, lead times, and
customer concentration.

The agent uses Claude Opus 4.7 as its baseline model through the Anthropic
Messages API when `ANTHROPIC_API_KEY` is set. Without a key, it returns a
deterministic local pre-scan so the platform harness still works.

Runtime metadata is declared in `manifest.yaml` and `runtime.yaml` so submission
intake can extract the Python entry point, package dependencies, external API,
and operator-managed secret.

## Quickstart

```bash
./setup.sh
./tools/test_agent.sh
```

Fill in `.env.local` when you are ready to make live model calls:

```bash
ANTHROPIC_API_KEY="..."
```

Optionally set `ANTHROPIC_MODEL` in the environment to override the default
`claude-opus-4-7` model id.

## Runtime Contract

- Entry point: `agent.py`
- Agent class: `SemiconductorLanguageShiftAgent`
- CLI command: `python agent.py`
- Required secret: `ANTHROPIC_API_KEY`
- External API: `https://api.anthropic.com/v1/messages`
- Dependencies: `requirements.txt`

## Supplying Documents

The platform can pass documents through `query.context["documents"]`. Each item
can be raw text, a local path, or an object:

```python
{
    "title": "NVDA FY2026 Q1 earnings call",
    "type": "earnings call",
    "date": "2026-05-20",
    "text": "... transcript or extracted filing/deck text ..."
}
```

Plain text, Markdown, JSON, HTML, DOCX, PPTX, and PDF paths are supported where
the local Python/runtime has the needed text extraction libraries available.

## What You Build

Each submission is a repo with two top-level files:

- `manifest.yaml` describes the agent and declares the freeform response format.
- `agent.py` implements `freeform(query)` and can use prompts, APIs, tools,
  functions, local files, or any other contributor code.

The platform calls:

```python
agent.freeform(query) -> str
```

`query` includes the platform prompt, request id, optional context, and optional
metric ids. The only output type the platform expects from the agent is a string.

The SDK handles the boring parts:

- keeping the agent interface small
- validating the manifest and freeform response structure
- producing readable error messages when a contract check fails

That lets contributors spend time on their agent logic instead of schema plumbing.

If you want the package available outside the helper scripts, install it with:

```bash
python3 -m pip install -e ./sdk
```

## Repository Layout

- `examples/` contains runnable reference agents to copy from.
- `schemas/` vendors the canonical schemas used by the validator.
- `enums/metrics.yaml` contains optional example metric ids.
- `sdk/` contains the installable Python package.
- `tools/` contains thin wrappers for local validation and submission prep.
- `docs/` explains the platform contract, submission expectations, scoring, and
  data source strategy.
- `.correlation-zero/version.json` pins the template, schema, and SDK versions.

## Submit

When your agent passes `./tools/test_agent.sh` and
`./tools/prepare_submission.sh`, push your repo and submit it through the URL
provided by the Correlation Zero team.

## Documentation

- [How scoring works](docs/how_scoring_works.md)
- [Platform contract](docs/platform_contract.md)
- [Submission guide](docs/submission_guide.md)
- [Writing a good agent](docs/writing_a_good_agent.md)
- [Data sources guide](docs/data_sources_guide.md)
- [FAQ](docs/faq.md)
