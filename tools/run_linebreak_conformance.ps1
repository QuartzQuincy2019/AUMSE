# Run the official UCD LineBreakTest.txt against the breakOpps() in web/UME.html.
# ASCII-only (Windows PowerShell 5.1 mis-decodes UTF-8 script files without a BOM).
$ErrorActionPreference = 'Stop'
$node = 'C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe'
$root = 'E:\QKMansion\CSX10\w\UME'

$html = [System.IO.File]::ReadAllText("$root\web\UME.html", [System.Text.Encoding]::UTF8)
$m = [regex]::Match($html, '(?s)<script>\s*"use strict";(.*?)</script>')
if (-not $m.Success) { throw 'script block not found' }
$js = $m.Groups[1].Value
$lines = $js.Split([char]10)

function Find-SectionLine([string[]]$L, [string]$num) {
    $rx = '^\s{3}' + [regex]::Escape($num) + '\.\s'
    for ($k = 0; $k -lt $L.Count; $k++) { if ($L[$k] -match $rx) { return $k } }
    return -1
}
function Banner-Start([string[]]$L, [int]$idx) {
    $s = $idx
    while ($s -gt 0 -and $L[$s] -notmatch '/\*') { $s-- }
    return $s
}

$b2 = Banner-Start $lines (Find-SectionLine $lines '2')
$b3 = Banner-Start $lines (Find-SectionLine $lines '3')
$b4 = Banner-Start $lines (Find-SectionLine $lines '4')
if ($b2 -lt 0 -or $b3 -lt 0 -or $b4 -lt 0) { throw "section markers missing" }

$data = ($lines[0..($b2 - 1)] -join "`n") + "`n" + ($lines[$b3..($b4 - 1)] -join "`n")
if ($data -match 'document\.') { throw 'DOM reference leaked into logic section' }

$conform = [System.IO.File]::ReadAllText("$root\tools\_ume_linebreaktest.js", [System.Text.Encoding]::UTF8)
$out = Join-Path $env:TEMP 'ume_conform.cjs'
[System.IO.File]::WriteAllText($out, $data + "`n" + $conform, (New-Object System.Text.UTF8Encoding($false)))
& $node $out
exit $LASTEXITCODE
