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

python 'C:\lab\vsurf_capital\common\scripts\slack_bolt_listener.py'
exit $LASTEXITCODE
