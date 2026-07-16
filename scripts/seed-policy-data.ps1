param(
    [string]$PythonEnvFile = "backend/.env",
    [string]$PolicyFile = "data/seed/policy_documents.json"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

function Read-DotEnvValue {
    param(
        [string]$Path,
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    foreach ($line in Get-Content -LiteralPath $Path -Encoding UTF8) {
        if ($line -match "^\s*$([regex]::Escape($Name))\s*=\s*(.+?)\s*$") {
            $value = $Matches[1].Trim()
            if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                return $value.Substring(1, $value.Length - 2)
            }
            return $value
        }
    }
    return $null
}

Push-Location $RepoRoot
try {
    $psql = Get-Command psql -ErrorAction Stop
    $envPath = Join-Path $RepoRoot $PythonEnvFile
    $databaseUrl = $env:DATABASE_URL
    if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
        $databaseUrl = Read-DotEnvValue -Path $envPath -Name "DATABASE_URL"
    }
    if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
        $databaseUrl = Read-DotEnvValue -Path (Join-Path $RepoRoot ".env") -Name "DATABASE_URL"
    }
    if ([string]::IsNullOrWhiteSpace($databaseUrl)) {
        throw "DATABASE_URL was not found in the environment or configured .env files."
    }

    $psqlUrl = $databaseUrl -replace '^postgresql\+psycopg://', 'postgresql://'
    $uri = [Uri]$psqlUrl
    if ($uri.Scheme -notin @("postgresql", "postgres")) {
        throw "DATABASE_URL must use the PostgreSQL protocol."
    }

    $userInfo = $uri.UserInfo -split ':', 2
    if ($userInfo.Length -lt 1 -or [string]::IsNullOrWhiteSpace($userInfo[0])) {
        throw "DATABASE_URL does not contain a database username."
    }
    $env:PGUSER = [Uri]::UnescapeDataString($userInfo[0])
    if ($userInfo.Length -eq 2) {
        $env:PGPASSWORD = [Uri]::UnescapeDataString($userInfo[1])
    }
    $env:PGHOST = $uri.Host
    $env:PGPORT = if ($uri.Port -gt 0) { [string]$uri.Port } else { "5432" }
    $env:PGDATABASE = [Uri]::UnescapeDataString($uri.AbsolutePath.TrimStart('/'))
    $env:PGCONNECT_TIMEOUT = "8"

    $resolvedPolicyFile = Resolve-Path (Join-Path $RepoRoot $PolicyFile)
    $payloadBase64 = [Convert]::ToBase64String([IO.File]::ReadAllBytes($resolvedPolicyFile))
    $expectedCount = (Get-Content -Raw -Encoding UTF8 -LiteralPath $resolvedPolicyFile | ConvertFrom-Json).Count
    $sql = @'
WITH source AS (
    SELECT jsonb_array_elements(
        convert_from(decode(:'payload_base64', 'base64'), 'UTF8')::jsonb
    ) AS item
), upserted AS (
    INSERT INTO policy_documents (
        document_code,
        title,
        category,
        source_path,
        version,
        is_active,
        metadata_json
    )
    SELECT
        item ->> 'document_code',
        item ->> 'title',
        item ->> 'category',
        item ->> 'source_path',
        item ->> 'version',
        COALESCE((item ->> 'is_active')::boolean, true),
        COALESCE(item -> 'metadata_json', '{}'::jsonb)
    FROM source
    ON CONFLICT (document_code) DO UPDATE SET
        title = EXCLUDED.title,
        category = EXCLUDED.category,
        source_path = EXCLUDED.source_path,
        version = EXCLUDED.version,
        is_active = EXCLUDED.is_active,
        metadata_json = EXCLUDED.metadata_json,
        updated_at = now()
    RETURNING document_code
)
SELECT count(*) FROM upserted;
'@

    $sql | & $psql.Source --no-password --no-psqlrc --quiet --set=ON_ERROR_STOP=1 --set="payload_base64=$payloadBase64" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "The psql policy import failed."
    }

    $verifySql = @'
WITH expected AS (
    SELECT item ->> 'document_code' AS document_code
    FROM jsonb_array_elements(
        convert_from(decode(:'payload_base64', 'base64'), 'UTF8')::jsonb
    ) AS item
)
SELECT count(*)
FROM policy_documents AS policy
JOIN expected USING (document_code)
WHERE policy.is_active IS true;
'@
    $verification = $verifySql | & $psql.Source --no-password --no-psqlrc --quiet --tuples-only --no-align --set=ON_ERROR_STOP=1 --set="payload_base64=$payloadBase64"
    if ($LASTEXITCODE -ne 0) {
        throw "The psql policy verification query failed."
    }
    $count = [int](($verification | Select-Object -Last 1).Trim())
    if ($count -ne $expectedCount) {
        throw "Policy verification failed: expected $expectedCount active records, found $count."
    }
    Write-Output "[seed-policy] Completed; inserted or updated $count policies."
}
finally {
    Pop-Location
}
