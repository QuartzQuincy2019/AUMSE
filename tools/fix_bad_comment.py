# -*- coding: utf-8 -*-
"""修：16 份样式表里一个坏注释把后面的规则全吞了。

症状
----
`tools/check_docs.py` 早就报过 `e02_batch_and_cmd.css` 花括号不配平
（{ 305 } 304），我当时判定为「既有问题、浏览器能容忍，先不动」——
这个判断是错的，它**确实造成了可见的破坏**：

    e02 的 .mnemonic 在暗色下仍是琥珀浅底 rgb(253,244,227)，
    配近白的字 rgb(232,216,242) —— 对比度 1.24，几乎看不见。
    我第 12 轮明明给它加过暗色覆盖，却完全没生效。

根因
----
第 476 行（e01 在 522、f01 在 798…… 共 16 份都有）写成了：

    /* ===== 移动端：长路径字符串断行 =====
    /* 长且无空格的串（路径、命令、变量名）在窄屏上必须允许内部断行，
       否则会把表格和终端块撑得比视口还宽。 */
    @media (max-width:980px){ ... }

CSS 的注释**不能嵌套**。第一个 `/*` 开始注释，
中间那个 `/*` 只是注释内容，于是**第一个 `*/` 就把注释结束了** ——
本来想注释掉两行，实际只注释了一行，紧接着的
`@media (max-width:980px)` 反倒被当成了……不，更糟：
`/* ... /*` 之后到 `*/` 之间的内容被吃掉，
真正被吞的是**再往后**的东西 —— 这里正好吞掉了一个 `}`，
于是 `@media` 一路开到文件末尾，把后面所有规则（含我加的暗色覆盖）
都变成了窄屏专用。

修法
----
把标题行末尾多余的 ` /*` 去掉，让它成为一条完整注释：

    /* ===== 移动端：长路径字符串断行 =====
    /* 长且…  */        ← 改成下面这样
    /* ===== 移动端：长路径字符串断行 =====
       长且… */         ← 更好：合并成一条

这里采取最小改动：把 `===== /*` 换成 `=====`，
并把紧随其后那行单独成一条注释，语义完全不变。
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

BAD = "/* ===== 移动端：长路径字符串断行 =====\n/* "
GOOD = "/* ===== 移动端：长路径字符串断行 =====\n   "

n = 0
fixed = []
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    p = os.path.join(A, f)
    c = io.open(p, encoding="utf-8").read()
    if BAD not in c:
        continue
    c2 = c.replace(BAD, GOOD)
    io.open(p, "w", encoding="utf-8", newline="\n").write(c2)
    n += 1
    fixed.append(f)
print("  ✓ 修好 %d 份样式表的坏注释" % n)
for f in fixed:
    print("      " + f)

# ---------------- 复查：未闭合注释与括号都要归零 ----------------
print()
bad = 0
for f in sorted(os.listdir(A)):
    if not f.endswith(".css"):
        continue
    e = io.open(os.path.join(A, f), encoding="utf-8").read()
    i = 0
    opens = []
    while i < len(e) - 1:
        if e[i:i + 2] == "/*":
            opens.append(i); i += 2; continue
        if e[i:i + 2] == "*/":
            if opens:
                opens.pop()
            i += 2; continue
        i += 1
    br = e.count("{") - e.count("}")
    if opens or br:
        bad += 1
        print("  !! %-30s 未闭合注释 %d  括号差 %+d" % (f, len(opens), br))
print("  复查：未闭合注释/括号不配平的文件 %d 个 %s" % (bad, "✅" if bad == 0 else "❌"))
