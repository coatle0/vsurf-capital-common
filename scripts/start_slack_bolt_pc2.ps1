$ErrorActionPreference = 'Stop'

$pcId = [Environment]::GetEnvironmentVariable('CODEX_PC_ID', 'User')
if ($pcId -ne 'codex-pc2') {
    throw "slack_bolt_listener is restricted to codex-pc2; current CODEX_PC_ID='$pcId'."
}
$token = [Environment]::GetEnvironmentVariable('OPENACP_SLACK_BOT_TOKEN', 'User')
if ([string]::IsNullOrWhiteSpace($token)) {
    throw 'OPENACP_SLACK_BOT_TOKEN is not configured.'
}
$appToken = [Environment]::GetEnvironmentVariable('OPENACP_SLACK_APP_TOKEN', 'User')
if ([string]::IsNullOrWhiteSpace($appToken)) {
    throw 'OPENACP_SLACK_APP_TOKEN is not configured.'
}
[Environment]::SetEnvironmentVariable('CODEX_PC_ID', $pcId, 'Process')
[Environment]::SetEnvironmentVariable('OPENACP_SLACK_BOT_TOKEN', $token, 'Process')
[Environment]::SetEnvironmentVariable('OPENACP_SLACK_APP_TOKEN', $appToken, 'Process')

# slack_bolt_listener.py logs its own INFO/exception events to
# logs\slack_bolt_listener.log. This capture is only for anything outside
# that (import errors, uncaught tracebacks before logging is configured,
# a crash at process start).
$logDir = 'C:\lab\vsurf_capital\common\logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$startupLog = Join-Path $logDir 'slack_bolt_listener_startup.log'

# Self-healing loop: Task Scheduler's restart-on-failure only reliably
# applies to instances started by its own trigger, not ones started
# on-demand (Start-ScheduledTask / "Run"), so retry logic lives here
# instead of relying on that. Task Scheduler's job is just "start this
# once at logon"; any exit of the python process (crash or kill) is
# retried after a short delay, indefinitely.
#
# $ErrorActionPreference = 'Stop' above is global to this scope, so a
# non-terminating error anywhere inside the loop body (e.g. a transient
# Add-Content sharing violation) would otherwise propagate as terminating
# and kill the *outer* while loop too -- silently ending "self-healing"
# altogether (verified: this happened to the consumer's copy of this
# script, 2026-08-12). Wrap the whole loop body so nothing but an
# explicit exit of this script can stop it.
while ($true) {
    try {
        "$(Get-Date -Format o) START pid=$PID" | Add-Content -LiteralPath $startupLog -Encoding UTF8
        python 'C:\lab\vsurf_capital\common\scripts\slack_bolt_listener.py' 2>&1 |
            Add-Content -LiteralPath $startupLog -Encoding UTF8
        $code = $LASTEXITCODE
        "$(Get-Date -Format o) EXIT code=$code -- restarting in 5s" | Add-Content -LiteralPath $startupLog -Encoding UTF8
    }
    catch {
        try {
            "$(Get-Date -Format o) WRAPPER ERROR: $($_.Exception.Message) -- restarting in 5s" |
                Add-Content -LiteralPath $startupLog -Encoding UTF8
        } catch {}
    }
    Start-Sleep -Seconds 5
}
