# -*- coding: utf-8 -*-
"""生成 Q05 的样式表：以 q04 的样式表为基底（同系列、结构最接近）。

Q05 的正文只用已经有的展示块：.card / .code-wrap / .out-wrap /
.alias / .vs / .mnemonic / .mem / .two / table / .steps / .take …
这些在 q04_interfaces.css 里都已经定义过，所以基底直接复用，
不新增任何规则 —— 这一篇是短篇，没必要再引入新的视觉元素。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
SRC = os.path.join(A, "q04_interfaces.css")
DST = os.path.join(A, "q05_open_closed.css")

HEAD = """/* =====================================================================
   q05_open_closed.css —— Q05《开闭原则》页专属样式
   ---------------------------------------------------------------------
   本篇没有专属的视觉元素：正文只用了各页通用的展示块
   （.card / .code-wrap / .out-wrap / .alias / .vs / .mnemonic /
     .mem / .two / .steps / .take / 各种 table）。

   保留这个文件是为了让 Q05 的 <link> 结构与 Q02~Q04 一致
   （genelayout → 本页 → series-theme → tg_L → tg_D），
   以后要给这一页加专属样式，直接往下写即可。

   基底取自 q04_interfaces.css（同系列、结构最接近）。
   ===================================================================== */

"""


def main():
    src = io.open(SRC, encoding="utf-8").read()
    # 去掉 q04 自己的文件头注释，换成 Q05 的
    i = src.find("*/")
    body = src[i + 2:].lstrip("\n") if i > 0 else src
    out = HEAD + body
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("  ✓ q05_open_closed.css  %d B（基底 q04 %d B）" % (len(out), len(src)))


if __name__ == "__main__":
    main()
