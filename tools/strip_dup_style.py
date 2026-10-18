# -*- coding: utf-8 -*-
"""删掉 15 篇后端教程里**冗余**的 head 内嵌 <style>。

那一段是早先 fix_fab_overlap.py 注入的（返回 home 按钮 +
抽屉遮罩的 pointer-events 规避）。这些规则现在都已经在
assets/css/series-theme.css 与 assets/css/t-theme.css 里了，
留着就是同一批选择器在两处定义 —— 迟早会分叉。

删之前先确认：
  · 它确实以「自动注入：返回 home + 系列小目录」开头
  · series-theme.css 或 t-theme.css 里确实已经有 .home-fab 与
    body.toc-open::after 的规则
两个条件都满足才删。
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
A = os.path.join(T, "assets")

# 先确认外部样式表里已经有这些规则
have = {}
for f in ("series-theme.css", "t-theme.css", "f01_command_prompt.css"):
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    have[f] = (".home-fab" in c, "toc-open::after" in c)
print("  series-theme.css  .home-fab=%s  toc-open::after=%s" % have["series-theme.css"])
print("  t-theme.css       .home-fab=%s  toc-open::after=%s" % have["t-theme.css"])
assert have["series-theme.css"][0] and have["series-theme.css"][1], "外部样式表还没接管，先别删"
print()

MARK = "自动注入：返回 home + 系列小目录"
n = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    p = os.path.join(T, f)
    t = io.open(p, encoding="utf-8").read()
    head = t[:t.find("</head>")]
    m = re.search(r'(?s)<style[^>]*>(.*?)</style>', head)
    if not m or MARK not in m.group(1):
        continue
    # 只删这一个（head 里的），body 里的注入块不动
    t2 = t[:m.start()] + t[m.end():]
    io.open(p, "w", encoding="utf-8", newline="").write(t2)
    n += 1
print("  ✓ 删掉 %d 篇的冗余 head 内嵌 style" % n)
