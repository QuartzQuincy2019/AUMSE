# -*- coding: utf-8 -*-
"""核对两种页尾「全部系列」显示的篇数与真实篇数是否一致。

真实篇数以 tools/series_data.py 为准。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = r"E:\QKMansion\CSX10\w\UME"
A = os.path.join(R, "SharingGroup", "tutorials", "assets")

# 真实篇数
ns = {}
exec(compile(io.open(os.path.join(R, "tools", "series_data.py"),
                     encoding="utf-8").read(), "series_data.py", "exec"), ns)
truth = {k: len(ns["pages_of"](k)) for k in ns["ORDER"]}
truth["FE"] = len(ns["FE_PAGES"])

print("  series_data.py 的真实篇数：")
for k, v in truth.items():
    print("      %-4s %d" % (k, v))

print()
print("  fe-data.js（FE 页尾用）：")
d = io.open(os.path.join(A, "fe-data.js"), encoding="utf-8").read()
# 只从 SERIES_FILES 这个数组里取文件名。
# 不能对全文做 'xxx.html' 匹配 —— helper 的注释里也有文件名样例，
# 会多数出一条，第一版就是这么误报的。
mf = re.search(r'(?s)var SERIES_FILES\s*=\s*\[(.*?)\];', d)
files = re.findall(r"'([^']+)'", mf.group(1)) if mf else []
print("      现算用的文件清单 %d 条" % len(files))
for key in ("T", "F", "M", "R", "Q", "E", "FE"):
    n = sum(1 for f in files if (("FE" if f.startswith("fe-")
                                  else f[0].upper()) == key))
    mark = "OK " if n == truth.get(key) else "!! "
    print("      %s %-4s 现算 %d  真实 %d" % (mark, key, n, truth.get(key, -1)))
print("      渲染处是现算的吗（filesOfSeries）: %s"
      % ("filesOfSeries(k)" in d))
# fe-data.js 已经从「手写 ALL_SERIES + 写死的 n」改成「SERIES + ORDER
# + SERIES_FILES 现算」。这里不能再去找 ALL_SERIES —— 它已经不存在了，
# 之前那句 re.search(...).group(1) 会直接 AttributeError。
print("      已无手写 ALL_SERIES（改成数据驱动）: %s"
      % ("var ALL_SERIES" not in d))
_mo = re.search(r'(?s)var ORDER\s*=\s*\[([^\]]*)\]', d)
print("      ORDER: %s" % (_mo.group(1).strip() if _mo else "（找不到）"))

print()
print("  series-common.js（非 FE 页尾用）：")
s = io.open(os.path.join(A, "series-common.js"), encoding="utf-8").read()
m = re.search(r'(?s)var PAGES\s*=\s*\[(.*?)\n  \];', s)
body = m.group(1) if m else ""
# 每条按 s: 'X' 分组
keys = re.findall(r"s:\s*'([^']*)'", body)
import collections
cnt = collections.Counter(keys)
for key in ("T", "F", "M", "R", "Q", "E", "FE"):
    n = cnt.get(key, 0)
    mark = "OK " if n == truth.get(key) else "!! "
    print("      %s %-4s 表里 %d  真实 %d" % (mark, key, n, truth.get(key, -1)))
print("      渲染处是现算的吗: %s"
      % ("count" in s.lower() or "length" in s))
