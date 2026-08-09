$ErrorActionPreference = 'Stop'

$cliPath = Join-Path $env:APPDATA 'npm\node_modules\@openacp\cli\dist\cli.js'
if (-not (Test-Path -LiteralPath $cliPath)) {
    throw "OpenACP CLI bundle not found at '$cliPath'."
}

$source = [System.IO.File]::ReadAllText($cliPath)
$old = 'const mod = await import(modulePath);'
$new = 'const mod = await import(pathToFileURL(modulePath).href);'

if ($source.Contains($new)) {
    exit 0
}
if (-not $source.Contains($old)) {
    throw 'OpenACP plugin loader no longer matches the known Windows ESM issue; review before patching.'
}

$updated = $source.Replace($old, $new)
[System.IO.File]::WriteAllText($cliPath, $updated, [System.Text.UTF8Encoding]::new($false))
& node --check $cliPath
if ($LASTEXITCODE -ne 0) {
    throw 'Patched OpenACP CLI failed node syntax validation.'
}
