# -*- coding: utf-8 -*-
"""给 fe_base.css 的 :root 补上 --bg-soft（以及暗色覆盖）。

问题
----
FE-09 的 .domtree 用了 background:var(--bg-soft)，实测背景是透明的 ——
因为 **fe_base.css 的 :root 里根本没有 --bg-soft**：

    :root{ --bg --surface --surface-solid --line --line-2
           --fg --fg-2 --fg-3 --blue --blue-soft --green --green-soft
           --red --red-soft --amber --amber-soft --violet --violet-soft
           --teal --teal-soft --gold --pink --coral --mono --sans }

它只出现在 tg_D.css 的**暗色** @media 块里（--bg-soft:#161d26），
所以亮色模式下 var(--bg-soft) 是无效值 → 整个 background 声明失效。

为什么不换成 --surface / --sfc-2
    --bg-soft 是**全站**在用的名字（genelayout.css 里到处都是）。
    只在 FE 换个名字，这一页就与其它 34 篇不一致了，以后搬样式必踩坑。
    正确做法是把 FE 缺的那一个变量补齐。

改动
    1. :root 里加 --bg-soft（值取与 --bg #fdf7fb 协调的淡紫灰，
       也就是全站文档页 --bg-soft 的角色）。
    2. 已有的暗色 @media 块里加覆盖，值取 tg_D.css 的 #161d26
       —— 让 FE 的暗色与文档页完全一致，而不是我自己另挑一个颜色。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets\fe_base.css"

c = io.open(P, encoding="utf-8").read()

# ---------- 1. :root 补 --bg-soft ----------
if "--bg-soft" in c.split("@media")[0]:
    print("  :root 里已有 --bg-soft")
else:
    i = c.index(":root{")
    k = c.index("}", i)
    blk = c[i:k]
    # 插在 --surface-solid 之后，语义上挨着表面色
    anchor = "--surface-solid  #ffffff;"
    if anchor not in blk:
        # 退而求其次：找 --surface
        m = re.search(r'--surface\s*:[^;]+;', blk)
        if not m:
            print("  !! 找不到可插入的位置")
            raise SystemExit(1)
        pos = m.end()
    else:
        pos = blk.index(anchor) + len(anchor)
    add = "\n  /* 表单/卡片里的浅底块（文档页一直有这个变量，FE 侧原先漏了 ——\n     fe_09.css 的 .domtree 用它，缺了就整条 background 失效） */\n  --bg-soft       #f5f1f8;"
    c = c[:i + pos] + add + c[i + pos:]
    print("  :root 已补 --bg-soft: #f5f1f8")

# ---------- 2. 暗色块补覆盖 ----------
m = re.search(r'@media\s*\(prefers-color-scheme:\s*dark\)\s*\{', c)
if not m:
    print("  !! 找不到暗色 @media")
    raise SystemExit(1)
# 该块的闭合位置（括号配平）
j = c.index("{", m.start())
depth = 0
close = None
for x in range(j, len(c)):
    if c[x] == "{":
        depth += 1
    elif c[x] == "}":
        depth -= 1
        if depth == 0:
            close = x
            break
if "--bg-soft" in c[j:close]:
    print("  暗色块里已有 --bg-soft 覆盖")
else:
    add2 = "\n  :root{--bg-soft:#161d26}"
    c = c[:close] + add2 + c[close:]
    print("  暗色块已补 --bg-soft:#161d26（与 tg_D.css 取值一致）")

io.open(P, "w", encoding="utf-8", newline="\n").write(c)
print()
print("  已写入 fe_base.css  %d B" % len(c))
