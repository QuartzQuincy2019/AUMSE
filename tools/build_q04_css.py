# -*- coding: utf-8 -*-
"""生成 Q04 的样式表：以 q03 的样式表为基底（同系列、结构最接近）。

基底里已经带了 Q01~Q03 用过的展示块：
    .alias  键 → 说明对照
    .vs     逐项对照表
    .two    两份代码并排
    .mem    内存/结构示意格
    .cost   代价对照条
    .lay    成员布局表
    .take   一句话结论
Q04 只补一个：

    .iface  接口示意图（左边「外部能做什么」，右边「内部藏着什么」）
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
SRC = os.path.join(A, "q03_pointers_to_objects.css")
DST = os.path.join(A, "q04_interfaces.css")

EXTRA = """
/* =====================================================================
   Q04 专属：接口示意图
   ===================================================================== */

/* 左「对外」右「对内」两栏，中间一条分隔线 */
.iface{margin:18px 0;border:1px solid var(--line-2);border-radius:11px;
  overflow:hidden}
.iface .cols{display:flex;flex-wrap:wrap;align-items:stretch}
.iface .col{flex:1 1 210px;padding:12px 15px;border-right:1px solid var(--line-2)}
.iface .col:last-child{border-right:0}
.iface .col .hd{font-size:12.5px;font-weight:700;margin-bottom:8px}
.iface .col.out .hd{color:#0a6b52}
.iface .col.in .hd{color:#8a5a06}
.iface .col ul{margin:0;padding-left:20px}
.iface .col li{font-size:13px;line-height:1.85}
.iface .col.in{background:var(--bg-soft)}
.iface .col code{font-size:12.5px}
@media (max-width:720px){
  .iface .col{flex:1 1 100%;border-right:0;
    border-bottom:1px solid var(--line-2)}
  .iface .col:last-child{border-bottom:0}
}
"""


def main():
    src = io.open(SRC, encoding="utf-8").read()
    i = src.find("/* =====================================================================\n   Q04 专属")
    if i > 0:
        src = src[:i].rstrip() + "\n"
    out = src.rstrip() + "\n" + EXTRA
    io.open(DST, "w", encoding="utf-8", newline="\n").write(out)
    print("  ✓ q04_interfaces.css  %d B（基底 q03 %d B）" % (len(out), len(src)))


if __name__ == "__main__":
    main()
