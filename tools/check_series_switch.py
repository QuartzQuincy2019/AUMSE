# -*- coding: utf-8 -*-
"""检查页尾「全部系列」的每个系列是否都能点 —— 也就是没有该有却没有的灰项。

背景（这次踩的两个坑）
    ① fe-data.js 手写的 ALL_SERIES 里 R 的跳转目标是 f: null，
       于是 FE 页尾的「相关 · R」永远是灰色点不动的 ss-empty，
       而 R 其实有 3 篇。这份列表是**手抄的**，和 series-common.js
       的 SERIES+ORDER+PAGES 是两套数据，抄的时候 R 还没写。
    ② 各 FE 页的 window.__FE_PAGE__.series 长度不一致：
       fe-01~fe-07 是 8 条（FE-08 建出来之前生成的，之后没人补），
       fe-08 是 9 条。于是同一系列在不同页上显示的篇数不一样。

这个脚本把这两类漂移都挡住：
    · 每个 FE 页的 series 条数必须相同，且必须等于 FE_PAGES 的篇数
    · FE 页的 series 必须列出全部 FE 篇目
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")

ns = {}
exec(compile(io.open(os.path.join(R, "tools", "series_data.py"),
                     encoding="utf-8").read(), "series_data.py", "exec"), ns)
fe_truth = [p[0] for p in ns["FE_PAGES"]]

ok = bad = 0


def chk(cond, msg):
    global ok, bad
    if cond:
        ok += 1
        print("  OK   %s" % msg)
    else:
        bad += 1
        print("  !!   %s" % msg)


def bracket_span(s, start):
    depth = 0
    i = start
    while i < len(s):
        if s[i] == "[":
            depth += 1
        elif s[i] == "]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


print("1. 每个 FE 页的 __FE_PAGE__.series")
for f in sorted(os.listdir(T)):
    if not f.startswith("fe-") or not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    m = re.search(r'"series"\s*:\s*\[', t)
    if not m:
        chk(False, "%s 没有 series" % f)
        continue
    b = t.index("[", m.start())
    e = bracket_span(t, b)
    files = re.findall(r'"file"\s*:\s*\\?"([^"\\]+)', t[b:e])
    missing = [x for x in fe_truth if x not in files]
    extra = [x for x in files if x not in fe_truth]
    chk(len(files) == len(fe_truth) and not missing and not extra,
        "%-18s %d 条%s%s" % (f, len(files),
                             ("  缺 %s" % missing) if missing else "",
                             ("  多 %s" % extra) if extra else ""))

print()
print("2. fe-data.js 的「全部系列」必须每个系列都有跳转目标")
d = io.open(os.path.join(A, "fe-data.js"), encoding="utf-8").read()
# 数据驱动写法：SERIES / ORDER / SERIES_FILES；不再有手写 ALL_SERIES
chk("var ALL_SERIES" not in d, "不再手写 ALL_SERIES（已改成数据驱动）")
chk("var ORDER = ['T', 'F', 'M', 'R', 'Q', 'E', 'FE'];" in d,
    "ORDER 与 series_data.py 一致")
mf = re.search(r'(?s)var SERIES_FILES\s*=\s*\[(.*?)\];', d)
sflags = re.findall(r"'([^']+)'", mf.group(1)) if mf else []
for key in ("T", "F", "M", "R", "Q", "E"):
    n = sum(1 for f in sflags
            if (("FE" if f.startswith("fe-") else f[0].upper()) == key))
    chk(n > 0, "系列 %s 有 %d 篇 → 会渲染成可点链接（不是灰项）" % (key, n))

print()
print("3. series-common.js 的 ORDER 与系列定义")
s = io.open(os.path.join(A, "series-common.js"), encoding="utf-8").read()
chk("var ORDER = ['T', 'F', 'M', 'R', 'Q', 'E', 'FE'];" in s,
    "ORDER 一致")
for key in ("T", "F", "M", "R", "Q", "E", "FE"):
    chk(re.search(r"\b%s:\s*\{\s*label:" % key, s) is not None,
        "SERIES 里有 %s 的标签" % key)

print()
print("  通过 %d 项，未过 %d 项 %s" % (ok, bad, "OK" if bad == 0 else "FAIL"))
