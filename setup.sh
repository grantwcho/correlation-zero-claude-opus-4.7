#!/usr/bin/env bash
set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_cmd() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] $*"
    return 0
  fi
  "$@"
}

install_npm_cli() {
  local command_name="$1"
  local package_name="$2"
  local label="$3"

  if have_cmd "$command_name"; then
    echo "$label already installed."
    return 0
  fi

  if ! have_cmd npm; then
    echo "Skipping $label: npm was not found. Install Node.js 18+ and rerun ./setup.sh."
    return 0
  fi

  echo "Installing $label..."
  run_cmd npm install -g "$package_name"
}

install_cursor_agent() {
  if have_cmd cursor-agent; then
    echo "Cursor Agent already installed."
    return 0
  fi

  if ! have_cmd curl; then
    echo "Skipping Cursor Agent: curl was not found."
    return 0
  fi

  echo "Installing Cursor Agent..."
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] bash -lc 'curl -fsS https://cursor.com/install | bash'"
  else
    bash -lc 'curl -fsS https://cursor.com/install | bash'
  fi
}

print_cursor_shell_hint() {
  if have_cmd cursor; then
    echo "Cursor shell command already installed."
    return 0
  fi

  cat <<'EOF'
The `cursor` shell command is not installed yet.
Official setup is done from the Cursor desktop app:
  1. Open Cursor
  2. Open the Command Palette
  3. Run: Install 'cursor' to shell
EOF
}

install_npm_cli codex "@openai/codex" "Codex CLI"
install_npm_cli claude "@anthropic-ai/claude-code" "Claude Code"
install_cursor_agent
print_cursor_shell_hint

echo
echo "Bootstrap complete."
echo "Available commands:"
echo "  - codex"
echo "  - claude"
if have_cmd cursor; then
  echo "  - cursor"
else
  echo "  - cursor-agent"
fi

