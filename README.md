# Correlation Zero Agent Template

Build a specialist agent that contributors can customize and submit to the
Correlation Zero platform.

## Quickstart

```bash
git clone https://github.com/correlation-zero/agent-template.git my-agent
cd my-agent
./setup.sh
cp examples/01-minimal/agent.py examples/01-minimal/manifest.yaml .
./tools/test_agent.sh
```

If that prints `All checks passed`, you're set up. Edit `agent.py`
and `manifest.yaml`, then run `./tools/test_agent.sh` again.

More detail lives in [QUICKSTART.md](QUICKSTART.md).

`./setup.sh` installs the common AI CLIs contributors may want:
`codex`, `claude`, and Cursor Agent. If you use the Cursor desktop app,
it also prints the official one-time step for adding the `cursor` shell
command to your PATH.

## Pick a starting example

We ship five reference agents. Copy the one closest to what you're building:

| Example | Best for |
| --- | --- |
| `01-minimal` | Understanding the contract |
| `02-custom-functions` | Agents built from local code and helpers |
| `03-llm-wrapped` | LLM agents with freeform output |
| `04-api-backed` | Agents that call APIs or read external data |
| `05-full-featured` | Polished freeform reference |

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
