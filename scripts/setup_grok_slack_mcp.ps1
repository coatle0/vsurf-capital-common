# Setup Grok Slack MCP from the shared git tree.
# Does not print token values. Does not start PC2 listeners.
$ErrorActionPreference = 'Stop'

$common = 'C:\lab\vsurf_capital\common'
$server = Join-Path $common 'tools\slack-toolkit\slack_mcp_server.py'
$reqs = Join-Path $common 'tools\slack-toolkit\requirements.txt'
$patcher = Join-Path $common 'tools\slack-toolkit\patch_grok_config.py'
$grokConfig = Join-Path $env:USERPROFILE '.grok\config.toml'

if (-not (Test-Path -LiteralPath $server)) {
    throw "Missing $server. Run: git -C $common pull --ff-only"
}

function Resolve-Python {
    foreach ($candidate in @(
        'C:\Python314\python.exe',
        'C:\Python313\python.exe',
        'C:\Python312\python.exe'
    )) {
        if (Test-Path -LiteralPath $candidate) { return $candidate }
    }
    $cmd = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    throw 'python.exe not found. Install Python or add it to PATH.'
}

$python = Resolve-Python
Write-Output "python=$python"
Write-Output "server=$server"

& $python -m pip install -r $reqs
if ($LASTEXITCODE -ne 0) { throw 'pip install mcp failed' }

& $python $patcher --config $grokConfig --python $python --server $server
if ($LASTEXITCODE -ne 0) { throw 'failed to patch ~/.grok/config.toml' }

function Token-State([string]$name) {
    $user = [Environment]::GetEnvironmentVariable($name, 'User')
    $proc = [Environment]::GetEnvironmentVariable($name, 'Process')
    if (-not [string]::IsNullOrWhiteSpace($user) -or -not [string]::IsNullOrWhiteSpace($proc)) {
        return '<set>'
    }
    return '<not set>'
}

$pcId = [Environment]::GetEnvironmentVariable('CODEX_PC_ID', 'User')
if ([string]::IsNullOrWhiteSpace($pcId)) { $pcId = '<not set>' }
$bot = Token-State 'OPENACP_SLACK_BOT_TOKEN'
$app = Token-State 'OPENACP_SLACK_APP_TOKEN'
$sig = Token-State 'OPENACP_SLACK_SIGNING_SECRET'

Write-Output "CODEX_PC_ID=$pcId"
Write-Output "OPENACP_SLACK_BOT_TOKEN=$bot"
Write-Output "OPENACP_SLACK_APP_TOKEN=$app"
Write-Output "OPENACP_SLACK_SIGNING_SECRET=$sig"
Write-Output "grok_config=$grokConfig"
Write-Output "listener=not_started"

if ($bot -eq '<not set>') {
    Write-Output "HALT: set User env OPENACP_SLACK_BOT_TOKEN, then restart Grok. Do not put the value in Git."
    exit 2
}

Write-Output "OK: Slack MCP config written. Restart the Grok session so slack_* tools load."
