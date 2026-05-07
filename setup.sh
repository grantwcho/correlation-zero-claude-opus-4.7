#!/usr/bin/env bash
set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

host_os() {
  if [[ -n "${SETUP_HOST_OS:-}" ]]; then
    echo "$SETUP_HOST_OS"
    return 0
  fi
  uname -s 2>/dev/null || echo "unknown"
}

is_windows_bash() {
  case "$(host_os)" in
    MINGW*|MSYS*|CYGWIN*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

python_cmd() {
  if have_cmd python3; then
    echo "python3"
    return 0
  fi
  if have_cmd python; then
    echo "python"
    return 0
  fi
  return 1
}

venv_python() {
  if is_windows_bash; then
    echo ".venv/Scripts/python.exe"
  else
    echo ".venv/bin/python"
  fi
}

run_cmd() {
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] $*"
    return 0
  fi
  "$@"
}

setup_python_venv() {
  if [[ ! -f requirements.txt ]]; then
    return 0
  fi

  local python
  if ! python="$(python_cmd)"; then
    echo "Skipping Python dependencies: python3/python was not found."
    return 0
  fi

  local venv_bin
  venv_bin="$(venv_python)"

  if [[ "$DRY_RUN" == "1" ]]; then
    if [[ ! -d .venv ]]; then
      run_cmd "$python" -m venv .venv
    fi
    run_cmd "$venv_bin" -m pip install -r requirements.txt
    return 0
  fi

  if [[ ! -d .venv ]]; then
    echo "Creating Python virtual environment in .venv..."
    if ! "$python" -m venv .venv; then
      echo "Skipping Python dependencies: could not create .venv."
      return 0
    fi
  fi

  if [[ ! -x "$venv_bin" ]]; then
    echo "Skipping Python dependencies: expected $venv_bin was not found."
    return 0
  fi

  echo "Installing Python dependencies..."
  run_cmd "$venv_bin" -m pip install -r requirements.txt
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
    if is_windows_bash; then
      echo "Skipping $label: npm was not found. Install Node.js 18+ for Windows and rerun ./setup.sh, or run .\\setup.ps1 from PowerShell."
      return 0
    fi
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

  if is_windows_bash; then
    cat <<EOF
Skipping Cursor Agent: Cursor's bash installer does not support Git Bash/MSYS on Windows ($(host_os)).
Run .\setup.ps1 from PowerShell for native Windows setup, install Cursor Desktop for Windows, or rerun ./setup.sh from WSL/Linux/macOS if you need cursor-agent.
EOF
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

print_command_status() {
  local command_name="$1"
  local label="$2"

  if have_cmd "$command_name"; then
    echo "  - $label"
  else
    echo "  - $label (not installed)"
  fi
}

print_python_status() {
  local venv_bin
  venv_bin="$(venv_python)"

  if [[ -x "$venv_bin" ]]; then
    echo "  - Python dependencies (.venv)"
  else
    echo "  - Python dependencies (.venv not installed)"
  fi
}

setup_python_venv
install_npm_cli codex "@openai/codex" "Codex CLI"
install_npm_cli claude "@anthropic-ai/claude-code" "Claude Code"
install_cursor_agent
print_cursor_shell_hint

echo
echo "Bootstrap complete."
echo "Command status:"
print_python_status
print_command_status codex "codex"
print_command_status claude "claude"
print_command_status cursor "cursor"
print_command_status cursor-agent "cursor-agent"
