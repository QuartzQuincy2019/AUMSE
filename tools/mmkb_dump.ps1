# mmkb_dump.ps1 -- dump the Mongolian layout's VK -> character mapping as JSON
#
# Output: %TEMP%\mmkb_dump.json   [{ "vk": 65, "plain": 6176, "shift": null }, ...]
#         codepoints are decimal; null means the key produces nothing (or a dead key).
#
# ASCII only: Windows PowerShell 5.1 reads .ps1 without BOM as ANSI.

$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @"
using System;
using System.Text;
using System.Runtime.InteropServices;

public class KbdDump
{
    [DllImport("user32.dll")]
    public static extern IntPtr LoadKeyboardLayout(string pwszKLID, uint Flags);

    [DllImport("user32.dll")]
    public static extern int ToUnicodeEx(uint wVirtKey, uint wScanCode, byte[] lpKeyState,
        [Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder pwszBuff, int cchBuff,
        uint wFlags, IntPtr dwhkl);

    [DllImport("user32.dll")]
    public static extern uint MapVirtualKeyEx(uint uCode, uint uMapType, IntPtr dwhkl);

    public static int One(IntPtr hkl, uint vk, byte[] state)
    {
        StringBuilder sb = new StringBuilder(8);
        uint sc = MapVirtualKeyEx(vk, 0, hkl);
        int n = ToUnicodeEx(vk, sc, state, sb, sb.Capacity, 0x04, hkl);
        if (n <= 0) return -1;
        string s = sb.ToString();
        if (s.Length == 0) return -1;
        return (int)s[0];
    }
}
"@

$KLID = if ($env:KBD_KLID) { $env:KBD_KLID } else { '00000850' }
$hkl = [KbdDump]::LoadKeyboardLayout($KLID, 0x00000001)

$plain = New-Object byte[] 256
$shift = New-Object byte[] 256
$shift[0x10] = 0x80

$out = @()
foreach ($vk in 8..254) {
    $p = [KbdDump]::One($hkl, [uint32]$vk, $plain)
    $s = [KbdDump]::One($hkl, [uint32]$vk, $shift)
    if ($p -lt 0 -and $s -lt 0) { continue }
    $out += [pscustomobject]@{
        vk    = $vk
        plain = $(if ($p -lt 0) { $null } else { $p })
        shift = $(if ($s -lt 0) { $null } else { $s })
    }
}

$path = Join-Path $env:TEMP 'mmkb_dump.json'
$out | ConvertTo-Json -Compress | Set-Content -Path $path -Encoding UTF8
"wrote {0} keys to {1}" -f $out.Count, $path
