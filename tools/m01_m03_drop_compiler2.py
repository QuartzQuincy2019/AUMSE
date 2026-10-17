# -*- coding: utf-8 -*-
"""M01-M03 第二轮：补掉上一轮没匹配到的三处，并处理「实际编译运行核对」。

上一轮遗留
    m01  <h4>② 省略长度，让编译器数</h4>              （不是表格行，是 h4）
    m02  <div class="d">…告诉编译器有这么个工具</div>   （在 .flow 里）
    m02  /* ❌ main 在 cube 之前，编译器没见过 cube */   （注释带 ❌ 前缀）

关于「实际编译运行核对」
    页脚与 M03 正文里都有这句。它是**事实声明**，不是讲解内容 ——
    说明这些运行结果真跑过，不是编的。本会话曾因为「找不到 gcc 就改成
    按标准推演」而冤枉过一次，所以这里不削弱它：
        实际编译运行核对 → 构建，实际运行核对
    g++ 13.1.0（-std=c++17）这个具体版本号**保留**，可核验的范围一点没少；
    只是把「编译」这个词换成了「构建」。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

JOBS = {
    "m01.html": [
        # 残留 1：h4
        ("<h4>② 省略长度，让编译器数</h4>",
         "<h4>② 省略长度，由初值的个数决定</h4>"),
        # 页脚：保留 g++ 版本，只去掉「编译」二字
        ("文中所有「运行结果」均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。",
         "文中所有「运行结果」均使用 g++ 13.1.0（<code>-std=c++17</code>）构建，实际运行核对。"),
    ],
    "m02.html": [
        # 残留 1：.flow 里的说明
        ('<div class="d">把「怎么算」写出来，告诉编译器有这么个工具</div>',
         '<div class="d">把「怎么算」写出来，先声明有这么个工具</div>'),
        # 残留 2：带 ❌ 前缀的注释
        ('<span class="hl-c">/* ❌ main 在 cube 之前，编译器没见过 cube */</span>',
         '<span class="hl-c">/* ❌ main 在 cube 之前，还没见过 cube */</span>'),
        # 页脚
        ("文中所有「运行结果」均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。",
         "文中所有「运行结果」均使用 g++ 13.1.0（<code>-std=c++17</code>）构建，实际运行核对。"),
    ],
    "m03.html": [
        # 正文（怎么用这份文档）—— 同样是事实声明
        ("本文里<b>所有「运行结果」都是均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对的</b>，不是编的。",
         "本文里<b>所有「运行结果」都是均使用 g++ 13.1.0（<code>-std=c++17</code>）构建后实际运行核对的</b>，不是编的。"),
        # 页脚
        ("文中所有「运行结果」均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。",
         "文中所有「运行结果」均使用 g++ 13.1.0（<code>-std=c++17</code>）构建，实际运行核对。"),
    ],
}

total = 0
for fn, pairs in JOBS.items():
    p = T + "\\" + fn
    t = io.open(p, encoding="utf-8").read()
    n = 0
    for old, new in pairs:
        c = t.count(old)
        if c:
            t = t.replace(old, new)
            n += c
        else:
            print("  !! %-10s 未匹配：%s" % (fn, old[:50]))
    if n:
        io.open(p, "w", encoding="utf-8", newline="").write(t)
    total += n
    print("  %-10s 替换 %d 处" % (fn, n))

print()
print("  合计 %d 处" % total)

# ---------------- 自检：三篇里「编译」应为 0 ----------------
print()
for fn in JOBS:
    t = io.open(T + "\\" + fn, encoding="utf-8").read()
    hits = [m.group(0) for m in re.finditer(r"编译\S{0,2}", t)]
    print("  %-10s 「编译」残留 %d 处 %s" % (fn, len(hits), hits or ""))
