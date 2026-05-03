# Correlation Zero Agent Template

Build a specialist agent for the NVDA Q2 FY27 hackathon.

## Quickstart

```bash
git clone https://github.com/correlation-zero/agent-template.git my-agent
cd my-agent
./setup.sh
cp -r examples/01-minimal/* .
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

| Example | Best for | Lines |
| --- | --- | --- |
| `01-minimal` | Understanding the contract | ~50 |
| `02-prediction-only` | Quant models with no LLM | ~150 |
| `03-llm-wrapped` | LLM agents with structured output | ~200 |
| `04-data-driven` | Agents that scrape and compute | ~300 |
| `05-full-featured` | Reference for all 4 response formats | ~500 |

## What You Build

Each submission is a repo with two top-level files:

- `manifest.yaml` describes the lens, metrics, and supported response formats.
- `agent.py` implements the logic that answers platform queries.

The SDK handles the boring parts:

- serializing native Python objects into the expected envelope
- validating the manifest and response structure
- producing readable error messages when a contract check fails

That lets contributors spend time on the lens itself instead of schema plumbing.

If you want the package available outside the helper scripts, install it with:

```bash
python3 -m pip install -e ./sdk
```

## Repository Layout

- `examples/` contains runnable reference agents to copy from.
- `schemas/` vendors the canonical schemas used by the validator.
- `enums/metrics.yaml` defines the closed metric universe.
- `sdk/` contains the installable Python package.
- `tools/` contains thin wrappers for local validation and submission prep.
- `docs/` explains scoring, lens quality, and data source strategy.
- `.correlation-zero/version.json` pins the template, schema, and SDK versions.

## Submit

When your agent passes `./tools/test_agent.sh` and
`./tools/prepare_submission.sh`, push your repo and submit the URL at
`correlation-zero.com/hackathon/submit`.

## Documentation

- [How scoring works](docs/how_scoring_works.md)
- [Writing a good lens](docs/writing_a_good_lens.md)
- [Data sources guide](docs/data_sources_guide.md)
- [FAQ](docs/faq.md)
