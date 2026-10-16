# -*- coding: utf-8 -*-
"""生成 Q03 的样式表：以 q02 的样式表为基底（同系列、结构最接近）。

基底里已经带了 Q02 专属的几个展示块（.alias / .vs / .mem / .two / .steps），
Q03 要继续用其中的 .alias / .vs / .two / .mem，另外补两个新的：

    .cost   性能代价对照条（左「按值」右「按引用」，突出相差多少倍）
    .lay    类成员的内存布局表
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
SRC = os.path.join(A, "q02_references.css")
DST = os.path.join(A, "q03_pointers_to_objects.css")

EXTRA = """
/* =====================================================================
   Q03 专属：内存开销的几个对照件
   ===================================================================== */

/* 性能代价对照：左「按值」右「按引用」，中间一个「省掉多少」 */
.cost{margin:18px 0;border:1px solid var(--line-2);border-radius:11px;
  overflow:hidden}
.cost .hd{padding:8px 14px;font-size:13px;font-weight:700;color:var(--fg-2);
  background:var(--bg-soft);border-bottom:1px solid var(--line-2)}
.cost .bd{display:flex;flex-wrap:wrap;align-items:stretch}
.cost .side{flex:1 1 180px;padding:12px 15px;border-right:1px solid var(--line-2)}
.cost .side:last-child{border-right:0}
.cost .side .lb{font-size:12px;color:var(--fg-3);margin-bottom:5px}
.cost .side .nb{font-family:var(--mono);font-size:22px;font-weight:700;
  line-height:1.25;color:var(--fg)}
.cost .side .nb.bad{color:#b4232f}
.cost .side .nb.good{color:#0a6b52}
.cost .side .nt{font-size:12.5px;color:var(--fg-3);margin-top:3px}
@media (max-width:720px){
  .cost .side{flex:1 1 100%;border-right:0;
    border-bottom:1px solid var(--line-2)}
  .cost .side:last-child{border-bottom:0}
}

/* 类成员的内存布局 */
.lay{margin:16px 0;border:1px solid var(--line-2);border-radius:11px;
  overflow:hidden}
.lay table{margin:0;width:100%;border-collapse:collapse}
.lay th,.lay td{padding:8px 12px;font-size:13px;text-align:left;
  border-bottom:1px solid var(--line-2)}
.lay th{background:var(--bg-soft);font-weight:700}
.lay tr:last-child td{border-bottom:0}
.lay td.m{font-family:var(--mono);font-size:12.5px}
.lay td.r{text-align:right;font-family:var(--mono);font-weight:700;
  white-space:nowrap}
.lay tr.sum td{background:var(--bg-soft);font-weight:700}

/* 一句话结论（比 .take 更醒目，用于每节的落点） */
.take{margin:14px 0;padding:11px 15px;border-left:5px solid var(--s-main,#0c8261);
  border-radius:0 9px 9px 0;background:var(--s-soft,var(--bg-soft));
  font-size:14px;line-height:1.75;color:var(--fg)}
"""


def main():
    src = io.open(SRC, encoding="utf-8").read()
    i = src.find("/* =====================================================================\n   Q03 专属")
    if i > 0:
        src = src[:i].rstrip() + "\n"
    out = src.rstrip() + "\n" + EXTRA
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("  ✓ q03_pointers_to_objects.css  %d B（基底 q02 %d B）"
          % (len(out), len(src)))


if __name__ == "__main__":
    main()
