param(
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

function Test-Command {
  param([string]$Name)
  return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-Step {
  param(
    [string]$File,
    [string[]]$Arguments = @()
  )

  if ($DryRun) {
    Write-Host "[dry-run] $File $($Arguments -join ' ')"
    return
  }

  & $File @Arguments
}

function Get-PythonRunner {
  if (Test-Command "python") {
    return @{ File = "python"; Arguments = @() }
  }
  if (Test-Command "py") {
    return @{ File = "py"; Arguments = @("-3") }
  }
  return $null
}

function Invoke-Python {
  param(
    [hashtable]$Runner,
    [string[]]$Arguments
  )

  Invoke-Step $Runner["File"] ($Runner["Arguments"] + $Arguments)
}

function Setup-PythonVenv {
  if (-not (Test-Path "requirements.txt")) {
    return
  }

  $runner = Get-PythonRunner
  if ($null -eq $runner) {
    Write-Host "Skipping Python dependencies: Python was not found. Install Python 3.10+ and rerun .\setup.ps1."
    return
  }

  $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"

  if ($DryRun) {
    if (-not (Test-Path ".venv")) {
      Invoke-Python $runner @("-m", "venv", ".venv")
    }
    Invoke-Step $venvPython @("-m", "pip", "install", "-r", "requirements.txt")
    return
  }

  if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment in .venv..."
    Invoke-Python $runner @("-m", "venv", ".venv")
  }

  if (-not (Test-Path $venvPython)) {
    Write-Host "Skipping Python dependencies: expected $venvPython was not found."
    return
  }

  Write-Host "Installing Python dependencies..."
  Invoke-Step $venvPython @("-m", "pip", "install", "-r", "requirements.txt")
}

function Install-NpmCli {
  param(
    [string]$CommandName,
    [string]$PackageName,
    [string]$Label
  )

  if (Test-Command $CommandName) {
    Write-Host "$Label already installed."
    return
  }

  if (-not (Test-Command "npm")) {
    Write-Host "Skipping ${Label}: npm was not found. Install Node.js 18+ and rerun .\setup.ps1."
    return
  }

  Write-Host "Installing $Label..."
  Invoke-Step "npm" @("install", "-g", $PackageName)
}

function Print-CursorHint {
  if (Test-Command "cursor") {
    Write-Host "Cursor shell command already installed."
  } else {
    Write-Host "The 'cursor' shell command is not installed yet."
    Write-Host "Official setup is done from the Cursor desktop app:"
    Write-Host "  1. Open Cursor"
    Write-Host "  2. Open the Command Palette"
    Write-Host "  3. Run: Install 'cursor' to shell"
  }

  if (-not (Test-Command "cursor-agent")) {
    Write-Host "Cursor Agent is not installed by this Windows PowerShell setup."
    Write-Host "Use WSL/Linux/macOS for Cursor Agent, or use Cursor Desktop on Windows."
  }
}

function Print-CommandStatus {
  param(
    [string]$CommandName,
    [string]$Label
  )

  if (Test-Command $CommandName) {
    Write-Host "  - $Label"
  } else {
    Write-Host "  - $Label (not installed)"
  }
}

function Print-PythonStatus {
  $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
  if (Test-Path $venvPython) {
    Write-Host "  - Python dependencies (.venv)"
  } else {
    Write-Host "  - Python dependencies (.venv not installed)"
  }
}

Setup-PythonVenv
Install-NpmCli "codex" "@openai/codex" "Codex CLI"
Install-NpmCli "claude" "@anthropic-ai/claude-code" "Claude Code"
Print-CursorHint

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "Command status:"
Print-PythonStatus
Print-CommandStatus "codex" "codex"
Print-CommandStatus "claude" "claude"
Print-CommandStatus "cursor" "cursor"
Print-CommandStatus "cursor-agent" "cursor-agent"
