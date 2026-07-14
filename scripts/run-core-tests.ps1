$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $repoRoot "backend"

Push-Location $backendRoot
try {
    python -m pytest -c pytest-core.ini
}
finally {
    Pop-Location
}
