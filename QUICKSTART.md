# Quickstart

This is the 5-minute path from clone to first valid response.

## 1. Install the common AI CLIs

```bash
./setup.sh
```

This bootstraps:

- `codex`
- `claude`
- `cursor-agent`

If you use the Cursor desktop app, the script also prints the official
one-time step for enabling the `cursor` shell command.

On Windows Git Bash/MSYS/Cygwin, the script skips Cursor Agent because Cursor's
bash installer does not support that shell environment. Install Cursor Desktop
for Windows, or run `./setup.sh` from WSL/Linux/macOS if you need
`cursor-agent`.

## 2. Copy the smallest runnable example

```bash
cp examples/01-minimal/agent.py examples/01-minimal/manifest.yaml .
```

## 3. Run the local checks

```bash
./tools/test_agent.sh
```

That gives you a root-level `agent.py` and `manifest.yaml` to edit.

This script validates:

- `manifest.yaml` exists and has the required fields
- `agent.py` defines an `Agent` subclass
- `freeform(query)` returns a string

## 4. Edit the two files that matter

- `manifest.yaml`: name the agent and describe what it does
- `agent.py`: implement your prompt engineering, API calls, functions, tools, or
  other logic inside `freeform(query)`

## 5. Prepare the submission

```bash
./tools/prepare_submission.sh
```

If you want a different starting point, copy one of the other example folders
instead of `01-minimal`.

If you want the SDK importable outside the helper scripts, install it with:

```bash
python3 -m pip install -e ./sdk
```
