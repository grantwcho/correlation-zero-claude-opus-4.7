#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
export PYTHONPATH="$repo_root/sdk${PYTHONPATH:+:$PYTHONPATH}"

python3 - <<'PY' "${1:-.}"
from pathlib import Path
import sys

from correlation_zero.validator import load_manifest, validate_manifest_data

repo_dir = Path(sys.argv[1]).resolve()
manifest = load_manifest(repo_dir)
errors = validate_manifest_data(manifest)

if errors:
    for error in errors:
        print(f"x {error}")
    raise SystemExit(1)

print("Manifest looks valid")
PY
