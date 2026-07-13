param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

Push-Location $RepoRoot
try {
    & $Python "scripts/seed_dev_data.py"
}
finally {
    Pop-Location
}
