# kbd_probe.ps1  --  show what each key produces under an installed keyboard layout
#
# Why: Mongolian layouts put FVS / MVS on modifier combos, and the positions differ
#      between layouts. Guessing is useless -- ask the OS.
#
# How: LoadKeyboardLayout + ToUnicodeEx (wFlags 0x04 = do not touch key state),
#      walking VK 8..254 across five modifier states.
#
# Usage:
#     powershell -NoProfile -ExecutionPolicy Bypass -File tools\kbd_probe.ps1
#     $env:KBD_WANT = '1820,182C,180E'        # optional: only these codepoints
#     powershell -NoProfile -ExecutionPolicy Bypass -File tools\kbd_probe.ps1
#
# Note: keep this file ASCII-only. Windows PowerShell 5.1 reads .ps1 without a BOM
#       as ANSI, so Chinese comments get mangled and the whole script fails to parse.

$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public class KbdProbe
{
    [DllImport("user32.dll")]
    public static extern IntPtr LoadKeyboardLayout(string pwszKLID, uint Flags);

    [DllImport("user32.dll")]
    public static extern int ToUnicodeEx(uint wVirtKey, uint wScanCode, byte[] lpKeyState,
        [Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pwszBuff, int cchBuff,
        uint wFlags, IntPtr dwhkl);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKeyEx(uint uCode, uint uMapType, IntPtr dwhkl);

    public static string Probe(IntPtr hkl, uint vk, byte[] state)
    {
        StringBuilder sb = new StringBuilder(8);
        uint sc = MapVirtualKeyEx(vk, 0, hkl);
        int n = ToUnicodeEx(vk, sc, state, sb, sb.Capacity, 0x04, hkl);
        if (n <= 0) return "";
        string s = sb.ToString();
        if (s.Length > n) s = s.Substring(0, n);
        return s;
    }
}
"@

function KeyState([bool]$shift, [bool]$ctrl, [bool]$alt) {
    $st = New-Object byte[] 256
    if ($shift) { $st[0x10] = 0x80 }
    if ($ctrl)  { $st[0x11] = 0x80 }
    if ($alt)   { $st[0x12] = 0x80 }
    return $st
}

$layouts = @(
    @{ Id = '00000850'; Name = 'Mongolian (Mongolian Script)' },
    @{ Id = '00010850'; Name = 'Traditional Mongolian (Standard)' },
    @{ Id = '00020850'; Name = 'Traditional Mongolian (MNS)' }
)

$states = @(
    @{ L = 'plain';     S = $false; C = $false; A = $false },
    @{ L = 'shift';     S = $true;  C = $false; A = $false },
    @{ L = 'ctrl';      S = $false; C = $true;  A = $false },
    @{ L = 'ctrlshift'; S = $true;  C = $true;  A = $false },
    @{ L = 'altgr';     S = $false; C = $true;  A = $true  }
)

# default: the whole Mongolian block; KBD_WANT narrows it
$want = 0x1800..0x18AF
if ($env:KBD_WANT) {
    $parsed = @()
    foreach ($part in ($env:KBD_WANT -split '[,;\s]+')) {
        if ($part -match '^(0x)?([0-9A-Fa-f]{2,6})$') {
            $parsed += [Convert]::ToInt32($matches[2], 16)
        }
    }
    if ($parsed.Count -gt 0) { $want = $parsed }
}

foreach ($lay in $layouts) {
    $hkl = [KbdProbe]::LoadKeyboardLayout($lay.Id, 0x00000001)
    "=== {0}  (KLID {1}) ===" -f $lay.Name, $lay.Id
    $hit = 0
    foreach ($s in $states) {
        $ks = KeyState $s.S $s.C $s.A
        foreach ($vk in 8..254) {
            # skip the modifier keys themselves
            if ($vk -eq 0x10 -or $vk -eq 0x11 -or $vk -eq 0x12 -or $vk -eq 0x14) { continue }
            if ($vk -ge 0x5B -and $vk -le 0x5D) { continue }
            $res = [KbdProbe]::Probe($hkl, [uint32]$vk, $ks)
            if ([string]::IsNullOrEmpty($res)) { continue }
            $cp = [int][char]$res[0]
            if ($want -contains $cp) {
                $hit++
                "   VK 0x{0:X2}  {1,-9} -> U+{2:X4}" -f $vk, $s.L, $cp
            }
        }
    }
    if ($hit -eq 0) { "   (no hit)" }
    ""
}
