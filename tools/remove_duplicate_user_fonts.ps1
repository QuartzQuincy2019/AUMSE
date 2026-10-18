# =====================================================================
#  remove_duplicate_user_fonts.ps1
#  ---------------------------------------------------------------------
#  清理「同一族名装了两份」里的**用户级**那一份。
#
#  背景：Windows 允许同一族名同时注册在
#    HKLM（系统级，C:\Windows\Fonts）
#    HKCU（当前用户级，%LOCALAPPDATA%\Microsoft\Windows\Fonts）
#  两份族名相同、文件不同。DirectWrite 只会挑一份，实测有浏览器两边都匹配
#  不上、直接回退到别的字体。本机蒙科立那套就是这样：系统级 8103 +
#  用户级 8102 同名（Menk Qagan Tig 是 MQG8103 + MQG8F02）。
#
#  默认**只列出**要动什么，不删任何东西。确认无误再加 -Apply。
#
#  用法：
#    powershell -NoProfile -ExecutionPolicy Bypass -File tools/remove_duplicate_user_fonts.ps1
#    powershell -NoProfile -ExecutionPolicy Bypass -File tools/remove_duplicate_user_fonts.ps1 -Apply
#
#  撤销：被删的用户级字体重新装一遍即可（文件已先备份到 -BackupTo）。
# =====================================================================
[CmdletBinding()]
param(
  [switch]$Apply,
  [string]$BackupTo = "$env:USERPROFILE\Desktop\ume-duplicate-fonts-backup",
  [string]$Filter   = 'Menk'
)

$ErrorActionPreference = 'Stop'
$sysKey = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
$usrKey = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
$usrDir = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'

function Read-FontKey($key) {
  $out = @{}
  if (-not (Test-Path $key)) { return $out }
  $item = Get-ItemProperty $key
  foreach ($p in $item.PSObject.Properties) {
    if ($p.Name -like 'PS*' -or $p.Name -like '*Path') { continue }
    $fam = $p.Name -replace ' \((TrueType|OpenType|All res)\)$', ''
    $out[$fam.Trim()] = [string]$p.Value
  }
  return $out
}

$sys = Read-FontKey $sysKey
$usr = Read-FontKey $usrKey

# 只挑「两边都有、族名以 -Filter 开头、且不是同一个文件」的
$dup = foreach ($fam in ($usr.Keys | Sort-Object)) {
  if ($fam -notlike "$Filter*") { continue }
  if (-not $sys.ContainsKey($fam)) { continue }
  $uFile = $usr[$fam]
  $sFile = $sys[$fam]
  if ((Split-Path $uFile -Leaf) -eq (Split-Path $sFile -Leaf)) { continue }  # 同一份，跳过
  [pscustomobject]@{
    Family    = $fam
    UserFile  = $uFile
    SysFile   = $sFile
    Exists    = Test-Path $uFile
  }
}

if (-not $dup) {
  Write-Host "没有发现「族名以 $Filter 开头且系统级/用户级撞名」的字体。"
  exit 0
}

Write-Host ""
Write-Host ("要处理 {0} 个撞名族（用户级那份会被移除，系统级那份保留）：" -f @($dup).Count) -ForegroundColor Cyan
$dup | Format-Table Family, @{n='保留(系统级)';e={Split-Path $_.SysFile -Leaf}},
                            @{n='移除(用户级)';e={Split-Path $_.UserFile -Leaf}}, Exists -AutoSize

if (-not $Apply) {
  Write-Host "以上只是预演，什么都没有改。" -ForegroundColor Yellow
  Write-Host "确认无误后加 -Apply 参数重跑一次：" -ForegroundColor Yellow
  Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File tools/remove_duplicate_user_fonts.ps1 -Apply"
  exit 0
}

New-Item -ItemType Directory -Force -Path $BackupTo | Out-Null
Write-Host ""
Write-Host "备份目录：$BackupTo"

$n = 0
foreach ($d in $dup) {
  $leaf = Split-Path $d.UserFile -Leaf
  if ($d.Exists) {
    Copy-Item $d.UserFile (Join-Path $BackupTo $leaf) -Force
    Write-Host ("  备份 {0}" -f $leaf)
  }
  # 先删注册项，再删文件：反过来的话 Windows 会留着一条指向不存在文件的记录
  $regName = "$($d.Family) (TrueType)"
  $item = Get-ItemProperty $usrKey
  $real = ($item.PSObject.Properties |
           Where-Object { ($_.Name -replace ' \((TrueType|OpenType|All res)\)$','') -eq $d.Family } |
           Select-Object -First 1)
  if ($real) {
    Remove-ItemProperty -Path $usrKey -Name $real.Name -Force
    Write-Host ("  移出注册表 {0}" -f $real.Name)
  }
  if ($d.Exists) {
    Remove-Item $d.UserFile -Force
    Write-Host ("  删除文件 {0}" -f $leaf)
  }
  $n++
}

Write-Host ""
Write-Host ("完成：处理了 {0} 个族。接下来请完全退出浏览器再打开（让它重新拉一次系统字体列表）。" -f $n) -ForegroundColor Green
Write-Host "如需撤销：把备份目录里的字体重新安装即可。"
