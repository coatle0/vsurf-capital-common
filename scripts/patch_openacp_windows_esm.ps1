$ErrorActionPreference = 'Stop'

$cliPath = Join-Path $env:APPDATA 'npm\node_modules\@openacp\cli\dist\cli.js'
if (-not (Test-Path -LiteralPath $cliPath)) {
    throw "OpenACP CLI bundle not found at '$cliPath'."
}

$source = [System.IO.File]::ReadAllText($cliPath)
$old = 'const mod = await import(modulePath);'
$new = 'const mod = await import(pathToFileURL(modulePath).href);'

if (-not $source.Contains($new)) {
    if (-not $source.Contains($old)) {
        throw 'OpenACP plugin loader no longer matches the known Windows ESM issue; review before patching.'
    }
    $source = $source.Replace($old, $new)
    [System.IO.File]::WriteAllText($cliPath, $source, [System.Text.UTF8Encoding]::new($false))
}

& node --check $cliPath
if ($LASTEXITCODE -ne 0) {
    throw 'Patched OpenACP CLI failed node syntax validation.'
}

if ($env:OPENACP_WORKSPACE) {
    $slackDist = Join-Path $env:OPENACP_WORKSPACE '.openacp\plugins\node_modules\@openacp\slack-adapter\dist'
}
else {
    $slackDist = 'C:\lab\.openacp\plugins\node_modules\@openacp\slack-adapter\dist'
}
$activityPath = Join-Path $slackDist 'activity-tracker.js'
$adapterPath = Join-Path $slackDist 'adapter.js'

foreach ($path in @($activityPath, $adapterPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "OpenACP Slack adapter file not found at '$path'."
    }
}

$activity = [System.IO.File]::ReadAllText($activityPath)
$activity = $activity.Replace('text: "Processing...",', 'text: "ACK — received; starting work.",')
[System.IO.File]::WriteAllText($activityPath, $activity, [System.Text.UTF8Encoding]::new($false))

$adapter = [System.IO.File]::ReadAllText($adapterPath)
$renameMarker = '    async renameSessionThread(sessionId, newName) {'
$renameDisabled = "    async renameSessionThread(sessionId, newName) {`n        // VSURF: keep the shared Slack control channel name stable.`n        return;"
if (-not $adapter.Contains('VSURF: keep the shared Slack control channel name stable.')) {
    if (-not $adapter.Contains($renameMarker)) {
        throw 'Slack adapter rename method no longer matches the known implementation.'
    }
    $adapter = $adapter.Replace($renameMarker, $renameDisabled)
    [System.IO.File]::WriteAllText($adapterPath, $adapter, [System.Text.UTF8Encoding]::new($false))
}

foreach ($path in @($activityPath, $adapterPath)) {
    & node --check $path
    if ($LASTEXITCODE -ne 0) {
        throw "Patched OpenACP Slack adapter failed node syntax validation: $path"
    }
}
