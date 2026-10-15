# -*- coding: utf-8 -*-
"""最后一处：HTML 里**内联**的 background:#fff。

内联样式优先级最高，样式表里的暗色规则压不过它 ——
这正是「用户报一个、我补一个」最容易漏掉的一类。

实测 5 处：
  t02-unicode-and-encoding.html  x4   流程图的节点（.pipeline 的子 div）
  fe-07.html                     x1

修法：内联的 #fff 改成 var(--sfc)。
      变量在样式表里已有暗色值，所以内联也能跟着变 ——
      这是「内联 + 变量」组合的好处：保留内联的优先级，
      但不写死颜色。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

n = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    p = os.path.join(T, f)
    t = io.open(p, encoding="utf-8").read()
    # 只改内联样式里的 background/background-color 值，不碰别的
    before = t
    t = re.sub(r'(background(?:-color)?\s*:\s*)#(?:fff|ffffff)\b', r'\1var(--sfc)', t)
    # JSON 转义形态（__FE_PAGE__ 里的 body 字符串）
    t = re.sub(r'(background(?:-color)?\\?"\s*:\s*)#(?:fff|ffffff)\\?"', r'\1var(--sfc)', t)
    if t != before:
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        k = len(re.findall(r'background(?:-color)?\s*:\s*var\(--sfc\)', t))
        n += 1
        print("  ✓ %-34s 已改" % f)

print("\n  共 %d 篇" % n)

# 复查
left = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    m = re.findall(r'background(?:-color)?\s*:\s*#(?:fff|ffffff)\b', t)
    if m:
        left += len(m)
        print("     !! %s 还剩 %d 处" % (f, len(m)))
print("  复查：HTML 内联 background:#fff 剩 %d 处 %s"
      % (left, "✅" if left == 0 else "❌"))
