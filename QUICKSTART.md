# Quickstart

This is the 5-minute path from clone to first valid response.

## 1. Bootstrap the repo

macOS, Linux, or WSL:
```bash
./setup.sh
```

Windows PowerShell:
```powershell
.\setup.ps1
```

This creates a local `.venv`, installs Python dependencies from
`requirements.txt`, and installs the npm-based CLIs when Node.js/npm is
available:

- `codex`
- `claude`

It also prints Cursor setup guidance and command status. Cursor Agent's bash
installer does not support Windows Git Bash/MSYS/Cygwin; use WSL/Linux/macOS for
`cursor-agent`, or use Cursor Desktop on Windows.

If `codex` or `claude` are skipped, install Node.js 18+ and rerun the setup
script.

## 2. Copy the smallest runnable example

macOS, Linux, WSL, or Git Bash:
```bash
cp examples/01-minimal/agent.py examples/01-minimal/manifest.yaml .
```

Windows PowerShell:
```powershell
Copy-Item examples/01-minimal/agent.py, examples/01-minimal/manifest.yaml .
```

## 3. Run the local checks

macOS, Linux, WSL, or Git Bash:
```bash
./tools/test_agent.sh
```

Windows PowerShell:
```powershell
.\tools\test_agent.ps1
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

macOS, Linux, WSL, or Git Bash:
```bash
./tools/prepare_submission.sh
```

Windows PowerShell:
```powershell
.\tools\prepare_submission.ps1
```

If you want a different starting point, copy one of the other example folders
instead of `01-minimal`.

If you want the SDK importable outside the helper scripts, install it with:

```bash
python3 -m pip install -e ./sdk
```
