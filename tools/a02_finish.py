# -*- coding: utf-8 -*-
"""A02 收尾：页尾换成实际验证方式。

**每次重建 a02.html 之后都要跑**

build_page.py 的默认页尾写的是「均使用 g++ 13.1.0 实际编译运行核对」。
A02 这一次**这句话是真的** —— 本机用 MinGW GCC 13.1.0 + Qt 6.12.0 真编真跑了
（tools/qt/a02/main.cpp），但光说「g++ 核对」还不够，得把怎么跑的说清楚：
offscreen 平台、哪个字体、哪几个数字是从这次运行里读出来的。
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\a02.html"
t = io.open(P, encoding="utf-8").read()

OLD = """<footer>
UME 项目组内部教程 · A02《如何利用 HarfBuzz 在 Qt 上绘制字形》<br>
文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

NEW = """<footer>
UME 项目组内部教程 · A02《如何利用 HarfBuzz 在 Qt 上绘制字形》<br>
文中的字形号、位置、行宽、逐像素比较结果与路径元素数，均由
<b>MinGW GCC 13.1.0</b>（<code>-std=c++17</code>）＋ <b>Qt 6.12.0</b>
编译 <code>tools/qt/a02/main.cpp</code>、在 <code>QT_QPA_PLATFORM=offscreen</code>
下实际运行读出，字体为 <code>font/NotoSansMongolian-Regular.ttf</code>
（Noto Sans Mongolian，UPEM 1000）。<br>
第 4 节的推进量对照取自 <b>uharfbuzz 14.6.0</b>（A01 的实测数据），
按 64px ÷ UPEM 换算后与 Qt 的输出现场比对。<br>
第 7 节的插图是那次运行直接画出来的 PNG（<code>.shots/a02-*.png</code>），未再修图；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

if NEW in t:
    print("  · 页尾已是正确版本")
elif OLD in t:
    t = t.replace(OLD, NEW, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  ✓ 页尾已换成「真编译真运行」口径")
else:
    print("  !! 页尾未匹配 —— 检查 build_page.py 的 TAIL")
