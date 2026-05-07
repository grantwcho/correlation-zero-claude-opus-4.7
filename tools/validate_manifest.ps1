param(
  [string]$RepoDir = "."
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

function Get-PythonRunner {
  $venvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
  if (Test-Path $venvPython) {
    return @{ File = $venvPython; Arguments = @() }
  }

  $unixVenvPython = Join-Path $RepoRoot ".venv/bin/python"
  if (Test-Path $unixVenvPython) {
    return @{ File = $unixVenvPython; Arguments = @() }
  }

  if (Get-Command "python" -ErrorAction SilentlyContinue) {
    return @{ File = "python"; Arguments = @() }
  }

  if (Get-Command "py" -ErrorAction SilentlyContinue) {
    return @{ File = "py"; Arguments = @("-3") }
  }

  throw "Python was not found. Run .\setup.ps1 or install Python 3.10+."
}

$sdkPath = Join-Path $RepoRoot "sdk"
if ($env:PYTHONPATH) {
  $env:PYTHONPATH = "$sdkPath;$env:PYTHONPATH"
} else {
  $env:PYTHONPATH = $sdkPath
}

$validator = @'
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
'@

$runner = Get-PythonRunner
$pythonFile = $runner["File"]
$pythonArgs = $runner["Arguments"] + @("-c", $validator, $RepoDir)
& $pythonFile @pythonArgs
