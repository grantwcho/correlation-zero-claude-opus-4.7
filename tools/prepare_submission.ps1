param(
  [string]$RepoDir = "."
)

$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "test_agent.ps1") $RepoDir
& (Join-Path $PSScriptRoot "validate_manifest.ps1") $RepoDir

$versionPath = Join-Path $RepoDir ".correlation-zero\version.json"
if (-not (Test-Path $versionPath)) {
  Write-Host "x Missing .correlation-zero/version.json"
  exit 1
}

Write-Host "Submission scaffold looks ready"
