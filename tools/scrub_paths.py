# -*- coding: utf-8 -*-
"""把文档里出现的私人路径与用户名换成通用占位符。

  E:\\QKMansion\\…        → D:\\Path\\To\\…
  E:/QKMansion/…          → D:/Path/To/…
  C:\\Users\\lenovo       → C:\\Users\\Your_Username
  lenovo（其他位置）        → Your_Username
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

# 顺序有讲究：先换长的，再换短的
RULES = [
    (r"E:\QKMansion\CSX10\w\UME\tools\_c_check\path1.cpp",
     r"D:\Path\To\project\build\path1.cpp"),
    (r"E:\QKMansion\CSX10\w\UME", r"D:\Path\To\UME"),
    (r"E:\QKMansion", r"D:\Path\To"),
    (r"E:/QKMansion/UME", r"D:/Path/To/UME"),
    (r"E:/QKMansion", r"D:/Path/To"),
    (r"C:\Users\lenovo", r"C:\Users\Your_Username"),
    (r"C:/Users/lenovo", r"C:/Users/Your_Username"),
    (r"lenovo", r"Your_Username"),          # 兜底
    (r"\\Users\\Your_Username", r"\\Users\\Your_Username"),
]

total = 0
for name in sorted(os.listdir(ROOT)):
    if not name.endswith(".html"):
        continue
    path = os.path.join(ROOT, name)
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    orig = t
    hits = []
    for old, new in RULES:
        n = t.count(old)
        if n:
            t = t.replace(old, new)
            hits.append("%s→%s ×%d" % (old[:34], new[:34], n))
    if t != orig:
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(t)
        print("%-46s %s" % (name, "; ".join(hits)))
        total += 1

print("")
print("共修改 %d 个文件" % total)

# 复核
print("")
print("=== 复核：是否还有残留 ===")
bad = 0
for name in sorted(os.listdir(ROOT)):
    if not name.endswith(".html"):
        continue
    with io.open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        t = fh.read()
    for pat in ["QKMansion", "lenovo"]:
        n = t.count(pat)
        if n:
            print("  !! %s 里还有 %s ×%d" % (name, pat, n))
            bad += n
if not bad:
    print("  无残留")
