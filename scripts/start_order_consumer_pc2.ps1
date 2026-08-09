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

python 'C:\lab\vsurf_capital\common\scripts\order_inbox_consumer.py'
exit $LASTEXITCODE
