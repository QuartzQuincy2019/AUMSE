# -*- coding: utf-8 -*-
"""重造 r04.css：以 r01.css 为基底 + 取色器规则。

上一版的问题
    我把 r04.css 写成了「R 系列主色块 + 取色器规则」（3.6 KB），
    但**每篇的页专属 CSS 里其实还带着一层基样式** ——
    比如 #toc a{display:block}（目录的竖排）并不在 genelayout.css 里，
    而是在各页自己的 CSS 里。丢掉它之后：
        · 左侧目录塌成一大段连排文字
        · 小节标题「1颜色…」的序号与标题粘在一起

正确做法
    r01 与 r04 同属 R 系列，r01.css（19 KB）本身就是「R 系列基样式 +
    R01 专有规则」的完整一份。直接以它为基底，再把 r04 需要的取色器
    规则（pk-* / cp2）追加在后面 —— 这样样式齐备，也没有多余改动。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"

r01 = io.open(os.path.join(A, "r01.css"), encoding="utf-8").read()
base = io.open(os.path.join(A, "fe_base.css"), encoding="utf-8").read()

WANT = ["cp2", "pk-ctl", "pk-note", "pk-out", "pk-sw", "pk-swatch",
        "pk-top", "pk-row", "pk-sl", "pk-hex", "picker", "val"]
picked = []
seen = set()
for mm in re.finditer(r"([^{}]+)\{([^{}]*)\}", base):
    sel, body = mm.group(1).strip(), mm.group(2).strip()
    if not body:
        continue
    if any(re.search(r"\." + re.escape(w) + r"(?![\w-])", sel) for w in WANT):
        if sel in seen:
            continue
        seen.add(sel)
        picked.append("%s{%s}" % (sel, body))
print("  从 fe_base.css 摘到取色器规则 %d 条" % len(picked))

OUT = r01.rstrip() + """

/* =====================================================================
   R04 专有：颜色拾取器
   ---------------------------------------------------------------------
   本页比 R 系列其它篇多一个「颜色拾取器」演示（pk-* 一组 class）。
   这些规则原来在 FE 系列的 fe_base.css 里 —— R04 从 FE 转过来后
   文档页不加载 fe_base.css，所以把用到的那几条复制到这里。
   ===================================================================== */
""" + "\n".join(picked) + """

/* 拾取器里的数值要等宽对齐，读数才不会跳动 */
.cp2{font-variant-numeric:tabular-nums}
"""

path = os.path.join(A, "r04.css")
io.open(path, "w", encoding="utf-8", newline="").write(OUT)
print("  已写入 r04.css（%d 字符）" % len(OUT))

# 复核关键规则在不在
for need in ("#toc a{display:block", ".n", "pk-swatch"):
    print("     含 %-22s %s" % (need, need in OUT))
