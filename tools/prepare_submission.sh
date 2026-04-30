#!/usr/bin/env bash
set -euo pipefail

repo_dir="${1:-.}"

./tools/test_agent.sh "$repo_dir"
./tools/validate_manifest.sh "$repo_dir"

test -f "$repo_dir/.correlation-zero/version.json" || {
  echo "x Missing .correlation-zero/version.json"
  exit 1
}

echo "Submission scaffold looks ready"

