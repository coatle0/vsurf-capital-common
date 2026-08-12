$ErrorActionPreference = 'Stop'

$pcId = [Environment]::GetEnvironmentVariable('CODEX_PC_ID', 'User')
if ($pcId -ne 'codex-pc2') {
    throw "order_inbox_consumer is restricted to codex-pc2; current CODEX_PC_ID='$pcId'."
}
$token = [Environment]::GetEnvironmentVariable('OPENACP_SLACK_BOT_TOKEN', 'User')
if ([string]::IsNullOrWhiteSpace($token)) {
    throw 'OPENACP_SLACK_BOT_TOKEN is not configured.'
}
[Environment]::SetEnvironmentVariable('CODEX_PC_ID', $pcId, 'Process')
[Environment]::SetEnvironmentVariable('OPENACP_SLACK_BOT_TOKEN', $token, 'Process')

# order_inbox_consumer.py logs its own INFO/exception events to
# logs\inbox_consumer\inbox_consumer.log. This capture is only for anything
# outside that (import errors, uncaught tracebacks before logging is
# configured, a crash at process start).
$logDir = 'C:\lab\vsurf_capital\common\logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$startupLog = Join-Path $logDir 'inbox_consumer_startup.log'

# Self-healing loop, same rationale as start_slack_bolt_pc2.ps1. NOTE: if
# the crash happened while ConsumerLock (.runtime/inbox/consumer.lock)
# was held, this will keep retrying every 5s but keep failing fast on
# "already holds consumer.lock" -- that is intentional (ORDER_PROTOCOL
# 2-3 / this work order's prohibition on auto-clearing stale locks): a
# crash mid-lock requires a human to clear the lock file before this
# loop can actually resume. A crash that never touched the lock (e.g.
# transient startup failure) recovers with no human action needed.
while ($true) {
    "$(Get-Date -Format o) START pid=$PID" | Add-Content -LiteralPath $startupLog -Encoding UTF8
    python 'C:\lab\vsurf_capital\common\scripts\order_inbox_consumer.py' 2>&1 |
        Add-Content -LiteralPath $startupLog -Encoding UTF8
    $code = $LASTEXITCODE
    "$(Get-Date -Format o) EXIT code=$code -- restarting in 5s" | Add-Content -LiteralPath $startupLog -Encoding UTF8
    Start-Sleep -Seconds 5
}
