param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

Push-Location $RepoRoot
try {
    & $Python "scripts/build-demo-data.py"
}
finally {
    Pop-Location
}
