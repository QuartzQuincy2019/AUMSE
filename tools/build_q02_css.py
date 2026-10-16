# -*- coding: utf-8 -*-
"""生成 Q02 的样式表：以 q01 的样式表为基底。

为什么不从零写
   每篇教程的样式表是「公共层 + 本篇专属」合并而成的一整份。
   公共部分（.card / .code-wrap / .out-wrap / #toc / 表格 …）已经在
   genelayout.css 里了，但**字体、基础排版、窄屏细节**仍散落在各页的
   样式表里，从零写必然漏掉，页面会塌。

   所以沿用 R 系列的做法：拿一份结构最接近的样式表当基底，
   只改需要改的地方。Q01 与 Q02 同属 Q 系列，最合适。

Q 系列的配色由 series-theme.css 按 series_data.py 生成，
所以这里不需要写任何系列色 —— 只需保证基础排版齐全。
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
SRC = os.path.join(A, "q01_std_and_namespace.css")
DST = os.path.join(A, "q02_references.css")

EXTRA = """
/* =====================================================================
   Q02 专属：引用一节的几个小展示块
   ===================================================================== */

/* 「同一份数据、两个名字」的对照图 */
.alias{margin:18px 0;border:1px solid var(--line-2);border-radius:11px;
  overflow:hidden;background:var(--sfc)}
.alias .row{display:flex;align-items:stretch;border-bottom:1px solid var(--line-2)}
.alias .row:last-child{border-bottom:0}
.alias .row .k{flex:0 0 148px;padding:10px 14px;font-family:var(--mono);
  font-size:13px;font-weight:700;color:var(--fg-2);
  background:var(--bg-soft);border-right:1px solid var(--line-2)}
.alias .row .v{padding:10px 14px;font-size:13.5px;color:var(--fg-2);line-height:1.7}
.alias .row .v code{font-size:12.5px}

/* 引用 vs 指针 的逐项对照 */
.vs{margin:18px 0;border:1px solid var(--line-2);border-radius:11px;overflow:hidden}
.vs table{margin:0;width:100%;border-collapse:collapse}
.vs th,.vs td{padding:9px 13px;font-size:13.5px;text-align:left;
  border-bottom:1px solid var(--line-2)}
.vs th{background:var(--r-chiplight,var(--bg-soft));font-weight:700}
.vs tr:last-child td{border-bottom:0}
.vs td.c{font-family:var(--mono);font-size:12.5px}

/* 内存示意：一行小格子，标出名字与地址 */
.mem{margin:16px 0;display:flex;gap:0;flex-wrap:wrap;
  border:1px solid var(--line-2);border-radius:10px;overflow:hidden}
.mem .slot{flex:1 1 96px;padding:9px 11px;border-right:1px solid var(--line-2);
  background:var(--sfc);font-size:12.5px;line-height:1.6}
.mem .slot:last-child{border-right:0}
.mem .slot .a{font-family:var(--mono);color:var(--fg-3);font-size:11.5px}
.mem .slot .n{font-family:var(--mono);font-weight:700;color:var(--fg-2)}

/* 两份代码并排对照（左边「复制的代价」，右边「引用的做法」） */
.two{margin:18px 0;display:grid;grid-template-columns:1fr 1fr;gap:12px}
.two .side{border:1px solid var(--line-2);border-radius:11px;overflow:hidden;
  background:var(--sfc)}
.two .side .hd{padding:8px 13px;font-size:12.5px;font-weight:700;
  color:var(--fg-2);background:var(--bg-soft);
  border-bottom:1px solid var(--line-2)}
.two .side .hd.bad{color:#b4232f}
.two .side .hd.good{color:#0a6b52}
.two .side pre{margin:0;padding:11px 13px;overflow:auto;
  font-family:var(--mono);font-size:12.5px;line-height:1.75;
  background:#1d1530;color:#e8e3f5}
.two .side pre code{background:none;color:inherit}
@media (max-width:720px){.two{grid-template-columns:1fr}}

/* 「三步走」流程：绑定 → 存地址 → 自动解引用 */
.steps{margin:16px 0;display:flex;flex-wrap:wrap;gap:0;align-items:stretch}
.steps .st{flex:1 1 150px;padding:11px 13px;border:1px solid var(--line-2);
  border-right:0;background:var(--sfc);font-size:13px;line-height:1.65}
.steps .st:first-child{border-radius:9px 0 0 9px}
.steps .st:last-child{border-right:1px solid var(--line-2);
  border-radius:0 9px 9px 0}
.steps .st .i{display:inline-block;min-width:18px;height:18px;line-height:18px;
  margin-right:6px;border-radius:5px;text-align:center;
  font:700 11px/18px var(--mono);background:var(--s-main,#0f9d76);color:#fff}
.steps .st .t{font-weight:700;color:var(--fg-2);display:block;margin-bottom:3px}
@media (max-width:720px){
  .steps{display:block}
  .steps .st{border-right:1px solid var(--line-2);border-bottom:0;border-radius:0}
  .steps .st:first-child{border-radius:9px 9px 0 0}
  .steps .st:last-child{border-bottom:1px solid var(--line-2);
    border-radius:0 0 9px 9px}
}
"""


def main():
    src = io.open(SRC, encoding="utf-8").read()
    # 基底里若已有 Q02 专属段，先去掉，保证可重复运行
    i = src.find("/* =====================================================================\n   Q02 专属")
    if i > 0:
        src = src[:i].rstrip() + "\n"
    out = src.rstrip() + "\n" + EXTRA
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("  ✓ q02_references.css  %d B（基底 q01 %d B）"
          % (len(out), len(src)))


if __name__ == "__main__":
    main()
