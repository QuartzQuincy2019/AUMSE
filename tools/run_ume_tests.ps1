# Extract the pure-logic sections (1 and 3) from web/UME.html and run Node regression tests.
# ASCII-only on purpose: Windows PowerShell 5.1 mis-decodes UTF-8 script files without a BOM.
#
# Section layout in UME.html's script:
#   1. MNG character set          <- pure data
#   2. state & helpers ($ = document.getElementById ...)  <- SKIPPED (DOM)
#   3. editor (sync/insert/palette)                        <- SKIPPED (DOM)
#   4. SVG/PNG export (measureLine / layoutDoc / buildSVGText) <- SKIPPED (DOM)
#   5. interactions                                        <- SKIPPED (DOM)
#   6. boot                                                <- SKIPPED (DOM)
# So only section 1 is extractable as pure logic; the DOM-dependent helpers
# (prop/graphemes/breakOpps) live in section 2 and are shimmed in the test body.
$ErrorActionPreference = 'Stop'
$node = 'C:\Users\lenovo\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe'
$root = 'E:\QKMansion\CSX10\w\UME'

$html = [System.IO.File]::ReadAllText("$root\web\UME.html", [System.Text.Encoding]::UTF8)
$m = [regex]::Match($html, '(?s)<script>\s*"use strict";(.*?)</script>')
if (-not $m.Success) { throw 'script block not found' }
$js = $m.Groups[1].Value
$lines = $js.Split([char]10)
Write-Host ("script lines: " + $lines.Count)

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

$s2 = Find-SectionLine $lines '2'
$s3 = Find-SectionLine $lines '3'
if ($s2 -lt 0 -or $s3 -lt 0) { throw "section markers missing: $s2/$s3" }
$b2 = Banner-Start $lines $s2
$b3 = Banner-Start $lines $s3
Write-Host ("s2=$s2 b2=$b2  line[b2]='" + $lines[$b2] + "'")

# 第 1 节：字符集数据（无 DOM 引用）
# 用显式数组累加，避免 PS 5.1 在脚本里对 $lines[0..n] 切片的不稳定行为
$head = @()
for ($k = 0; $k -lt $b2; $k++) { $head += $lines[$k] }
$part1 = $head -join "`n"
Write-Host ("part1 chars=" + $part1.Length + " hasGroups=" + $part1.Contains('const GROUPS'))
# 第 2 节里的纯算法（cpHex / isMong / PROPS / prop / graphemes / breakOpps）
# —— 都不含 DOM 引用，可以一起抽出来
$helperStart = -1
for ($k = $b2; $k -lt $lines.Count; $k++) {
    if ($lines[$k] -match '^const cpHex = ') { $helperStart = $k; break }
}
if ($helperStart -lt 0) {
    for ($k = $b2; $k -lt $lines.Count; $k++) {
        if ($lines[$k] -match '^const PROPS = \{') { $helperStart = $k; break }
    }
}
if ($helperStart -lt 0) { throw 'helper block not found' }
# breakOpps 结束：从函数头开始配平花括号
$fnStart = -1
for ($k = $helperStart; $k -lt $lines.Count; $k++) {
    if ($lines[$k] -match '^function breakOpps') { $fnStart = $k; break }
}
if ($fnStart -lt 0) { throw 'breakOpps not found' }
$depth = 0; $helperEnd = -1
for ($k = $fnStart; $k -lt $lines.Count; $k++) {
    $depth += ([regex]::Matches($lines[$k], '\{')).Count - ([regex]::Matches($lines[$k], '\}')).Count
    if ($depth -eq 0 -and $lines[$k] -match '^\}') { $helperEnd = $k; break }
}
if ($helperEnd -lt 0) { throw 'breakOpps end not found' }
$part3 = ($lines[$helperStart..$helperEnd] -join "`n")

$data = $part1 + "`n" + $part3
Write-Host ("logic: part1=" + $part1.Length + " helpers=" + $part3.Length + " total=" + $data.Length)

if ($data -match 'document\.') { throw 'DOM reference leaked into logic section' }
foreach ($needle in @('const GROUPS', 'const SAMPLES', 'const cpHex', 'const isMong', 'function prop',
                      'function graphemes', 'function breakOpps')) {
    if ($data.IndexOf($needle) -lt 0) { throw "missing required symbol: $needle" }
}

$test = [System.IO.File]::ReadAllText("$root\tools\_ume_test_body.js", [System.Text.Encoding]::UTF8)
$out = Join-Path $env:TEMP 'ume_test.mjs'
[System.IO.File]::WriteAllText($out, $data + "`n" + $test, (New-Object System.Text.UTF8Encoding($false)))
& $node $out
exit $LASTEXITCODE
