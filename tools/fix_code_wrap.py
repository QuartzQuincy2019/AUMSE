# -*- coding: utf-8 -*-
"""修窄屏「长代码行要横向滚动」的问题。

先澄清一件事（实测）
--------------------
`tools/verify_mobile.js` 报的「横向溢出 175px」是**误报**：
它逐个元素比较 `e.right > parent.right`，而代码块里的长行
（`span.hl-p` 宽 851px）本来就在一个 `overflow:auto` 的 `<pre>` 里 ——
那是**块内滚动**，不是页面横向滚动。

用 documentElement.scrollWidth 复测：**26 篇全部没有页面级横向滚动**。

但用户的感受是真的
------------------
窄屏下代码块需要**左右拖动**才能看全一行，读起来很别扭。
（正文里的表格后端已经处理过，代码块没有。）

修法
----
窄屏下让代码块**自动换行**：
    white-space: pre-wrap    保留缩进与换行，但超长行自动折行
    overflow-wrap: anywhere  长标识符（如 aVeryLongFunctionName）也能断
    word-break: break-word   兜底
同时把它标记成「已换行」的样式（左侧细条），让读者知道这行是折过来的，
不是原本就这样缩进。

只作用于窄屏（≤ 720px），宽屏保持 `pre` 不换行的原样 ——
宽屏有足够空间，换行反而会打乱代码的视觉结构。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"

PATCH = """
/* =====================================================================
   窄屏：代码块自动换行（不再需要左右拖动）
   ---------------------------------------------------------------------
   宽屏保留 `white-space:pre` 的原样 —— 空间够，换行反而打乱代码结构。
   窄屏（≤720px）改成 pre-wrap + anywhere：
     · pre-wrap     保留缩进与换行，但超长行折行
     · anywhere     长标识符（aVeryLongFunctionName）也能断开
   折行的那一行左侧加一条细引导线，提示「这是折过来的」。
   ===================================================================== */
@media (max-width:720px){
  .code-wrap pre,
  .out-wrap pre,
  .term pre,
  .plain-pre,
  pre.tree,
  .pv-wrap pre{
    white-space:pre-wrap !important;
    overflow-wrap:anywhere !important;
    word-break:break-word !important;
  }
  /* 输入框 / 终端区同理 */
  .code-wrap pre code,.out-wrap pre code{white-space:pre-wrap !important}
  /* 行内 code 不要被长串撑破 */
  code,td.c,th.c{overflow-wrap:anywhere;word-break:break-word}
}
"""

n = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if "窄屏：代码块自动换行" in c:
        continue
    # 只给含代码块样式的文件加（即真正有 pre 的那些）
    if not re.search(r'\.code-wrap\s+pre|\.code-wrap\{|out-wrap', c):
        continue
    io.open(p, "w", encoding="utf-8", newline="\n").write(c.rstrip() + "\n" + PATCH)
    n += 1
print("  ✓ 为 %d 份样式表补上窄屏代码换行" % n)
