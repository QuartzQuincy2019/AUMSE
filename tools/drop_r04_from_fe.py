# -*- coding: utf-8 -*-
"""从 FE 各页的 __FE_PAGE__.series 里去掉 r04（它已不在 FE 系列）。

每个 FE 页的 JSON 里有一份 `series` 数组，列出 FE 系列的篇目
（用于页内上一页 / 下一页、以及系列切换的篇数）。
fe-03-F01 改成 R04 之后，它必须从这些数组里消失 ——
否则 FE 篇数会显示 10（实际 9），且「下一篇」会跳到 R 系列的一页。
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
RE = re.compile(r'(window\.__FE_PAGE__\s*=\s*)(\{.*?\})(;\s*\n</script>)', re.S)

n_page = 0
for f in sorted(os.listdir(T)):
    if not f.startswith("fe-") or not f.endswith(".html"):
        continue
    p = os.path.join(T, f)
    t = io.open(p, encoding="utf-8").read()
    m = RE.search(t)
    if not m:
        print("  %-14s !! 找不到 __FE_PAGE__" % f)
        continue
    d = json.loads(m.group(2))
    ser = d.get("series") or []
    before = len(ser)
    keep = [s for s in ser if s.get("file") != "r04.html"
            and s.get("num") != "FE-03-F01"]
    if len(keep) == before:
        print("  %-14s series %d 条，已无 r04，跳过" % (f, before))
        continue
    d["series"] = keep
    js = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")
    t2 = t[:m.start(2)] + js + t[m.end(2):]
    io.open(p, "w", encoding="utf-8", newline="").write(t2)
    n_page += 1
    print("  %-14s series %d → %d" % (f, before, len(keep)))

print()
print("  处理 %d 页" % n_page)

# 复核：每页 series 都应恰好 9 条、且不含 r04
print()
bad = 0
for f in sorted(os.listdir(T)):
    if not f.startswith("fe-") or not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    d = json.loads(RE.search(t).group(2))
    ser = d.get("series") or []
    files = [s["file"] for s in ser]
    ok = len(ser) == 9 and "r04.html" not in files
    if not ok:
        bad += 1
        print("  !! %-14s %d 条 %s" % (f, len(ser), files))
print("  复核：%s" % ("全部 9 条且无 r04 OK" if bad == 0 else "%d 页异常" % bad))
