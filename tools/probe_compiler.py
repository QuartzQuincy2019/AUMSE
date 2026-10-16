# -*- coding: utf-8 -*-
"""把 .exe 里 GCC 的版本字符串抠出来，确认教程 footer 里写的 13.1.0 是否属实。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

D = r"E:\QKMansion\CSX10\w\UME\tools\_c_check"

for f in sorted(os.listdir(D)):
    if not f.lower().endswith(".exe"):
        continue
    b = io.open(os.path.join(D, f), "rb").read()
    found = set()
    # GCC 的 .comment 段里会有 "GCC: (…) 13.1.0" 这种串
    for pat in (rb'GCC:\s*\([^)]{0,80}\)\s*[0-9][0-9.]{1,12}',
                rb'GCC\s+[0-9]+\.[0-9]+\.[0-9]+',
                rb'x86_64-w64-mingw32[ -~]{0,40}',
                rb'GNU C[0-9+]{0,3} [0-9][0-9.]{1,12}',
                rb'[0-9]+\.[0-9]+\.[0-9]+-win32'):
        for m in re.finditer(pat, b):
            s = m.group(0).decode("ascii", "replace").strip()
            if len(s) < 90:
                found.add(s)
    print("  %-16s %s" % (f, " | ".join(sorted(found)[:5]) or "(未找到版本串)"))
