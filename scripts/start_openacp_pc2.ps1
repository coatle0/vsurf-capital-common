param(
    [string]$Workspace = $(if ($env:OPENACP_WORKSPACE) { $env:OPENACP_WORKSPACE } else { 'C:\lab' })
)

$ErrorActionPreference = 'Stop'

$pcId = [Environment]::GetEnvironmentVariable('CODEX_PC_ID', 'User')
if ($pcId -ne 'codex-pc2') {
    throw "OpenACP startup is restricted to codex-pc2; current CODEX_PC_ID='$pcId'."
}

$openAcp = Join-Path $env:APPDATA 'npm\openacp.cmd'
if (-not (Test-Path -LiteralPath $openAcp)) {
    throw "OpenACP CLI not found at '$openAcp'."
}

$configPath = Join-Path $Workspace '.openacp\config.json'
$logDir = Join-Path $env:LOCALAPPDATA 'VSURF\OpenACP'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$startupLog = Join-Path $logDir 'startup.log'

if (-not (Test-Path -LiteralPath $configPath)) {
    "$(Get-Date -Format o) BLOCKED config missing: $configPath" |
        Add-Content -LiteralPath $startupLog -Encoding UTF8
    exit 2
}

Push-Location -LiteralPath $Workspace
try {
    & $openAcp start --json 2>&1 |
        Add-Content -LiteralPath $startupLog -Encoding UTF8
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
