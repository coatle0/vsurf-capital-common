$ErrorActionPreference = 'Stop'
if (-not $env:CODEX_PC_ID) { throw 'CODEX_PC_ID is required.' }
$common = 'C:\lab\vsurf_capital\common'
$python = 'C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe'
$wrapper = Join-Path $common 'scripts\neo4j_mcp_wrapper.py'
$codex = Join-Path $env:APPDATA 'npm\codex.cmd'
foreach ($path in @($python, $wrapper, $codex)) {
    if (-not (Test-Path -LiteralPath $path)) { throw "Missing required path: $path" }
}
if (-not [Environment]::GetEnvironmentVariable('NEO4J_PASSWORD', 'User')) {
    throw 'NEO4J_PASSWORD user environment variable is required.'
}
& $codex mcp remove neo4j-official 2>$null
& $codex mcp add neo4j-official -- $python $wrapper
& $codex mcp get neo4j-official
Write-Output "Configured neo4j-official read/write on $env:CODEX_PC_ID"
