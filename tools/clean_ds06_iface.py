# -*- coding: utf-8 -*-
"""收尾：把 _ds_06 里剩下的「接口」这个说法也换掉。

这些不是「接口」那一节的内容，而是顺手用到的词。既然要求
「删除对接口的所有阐述」，这里统一改成更朴素的说法，避免读者
以为还有一节在讲接口。
"""
import io
import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
PATH = os.path.join(ROOT, "_ds_06_类、结构体.html")

with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()

SUB = [
    ("你按按钮（接口），它给你饮料。",
     "你按按钮，它给你饮料。"),
    ("你踩油门（接口），发动机按规则响应。",
     "你踩油门，发动机按规则响应。"),
    ("<span class=\"hl-c\">/* 只读接口 */</span>",
     "<span class=\"hl-c\">/* 只读：只给看不给改 */</span>"),
    ('<span class="hl-s">"从接口读 HP: "</span>',
     '<span class="hl-s">"通过公开函数读 HP: "</span>'),
    ("从接口读 HP: 60",
     "通过公开函数读 HP: 60"),
    ("<div class=\"d\">通过公开接口<br>读写、调用成员函数</div>",
     "<div class=\"d\">通过公开的函数<br>读写、调用成员函数</div>"),
    ("先把本讲的接口与封装用熟",
     "先把本讲的私有保护与构造函数用熟"),
    ("<span class=\"hl-c\">/* ✅ 数据私有，只通过接口改 */</span>",
     "<span class=\"hl-c\">/* ✅ 数据私有，只通过公开函数改 */</span>"),
]

for old, new in SUB:
    n = t.count(old)
    if n != 1:
        print("  !! 命中 %d 次（应为 1）: %s" % (n, old[:50]))
        continue
    t = t.replace(old, new, 1)
    print("  ✓ %s" % old[:48])

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("")
print("残留「接口」次数: %d" % t.count("接口"))
for m in re.finditer("接口", t):
    print("   ..." + t[max(0, m.start() - 70):m.start() + 30].replace("\n", " ").strip()[-95:])
