#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
export PYTHONPATH="$repo_root/sdk${PYTHONPATH:+:$PYTHONPATH}"

find_python() {
  if [[ -x "$repo_root/.venv/bin/python" ]]; then
    echo "$repo_root/.venv/bin/python"
    return 0
  fi
  if [[ -x "$repo_root/.venv/Scripts/python.exe" ]]; then
    echo "$repo_root/.venv/Scripts/python.exe"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}

python_bin="$(find_python)" || {
  echo "x Python was not found. Run ./setup.sh or install Python 3.10+."
  exit 1
}

"$python_bin" -m correlation_zero.test_harness "${1:-.}"
