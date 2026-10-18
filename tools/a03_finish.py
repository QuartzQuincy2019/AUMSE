# -*- coding: utf-8 -*-
"""A03 收尾：页尾换成与实际来源相符的说明。

**每次重建 a03.html 之后都要跑**

build_page.py 的默认页尾写的是「均使用 g++ 13.1.0 实际编译运行核对」。
A03 是架构篇，一半的数字来自**别的途径**：

    · 字形号、推进量、切分对照     → uharfbuzz 14.6.0（tools/probe_run_split.py）
    · Qt 的行为（3 个 glyph run 等）→ Qt 6.12.0 实测（tools/qt/a02/main.cpp）
    · 浏览器跨 span 的行为         → Edge 155（web/span-probe.html）
    · 3000 段的代价估算            → 按实测单段耗时外推，**不是跑出来的**

最后一条必须说清楚是估算，不能写成实测。
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\a03.html"
t = io.open(P, encoding="utf-8").read()

OLD = """<footer>
UME 项目组内部教程 · A03《懒惰的落榜美术生——文本编辑器》<br>
文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

NEW = """<footer>
UME 项目组内部教程 · A03《懒惰的落榜美术生——文本编辑器》<br>
文中的字形号、推进量、切分对照，由 <b>uharfbuzz 14.6.0</b> 配合
<code>NotoSansMongolian-Regular.ttf</code>（UPEM 1000）实测；Qt 侧的行为
（词内改字号切成 3 个 glyph run、行宽 186 → 206）由 <b>Qt 6.12.0</b>
在 <code>tools/qt/a02/main.cpp</code> 中实测；浏览器跨 span 的数据
（185.61 / 200.34 / 281.19）由 <b>Edge 155</b> 实测。<br>
第 5、15 节里「3000 段 ≈ 600 ms」「单段 ≈ 200 µs」是按实测的**单段耗时外推的估算**，
不是跑出来的数字，量级可信、绝对值仅供比较。<br>
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

if NEW in t:
    print("  · 页尾已是正确版本")
elif OLD in t:
    t = t.replace(OLD, NEW, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  ✓ 页尾已换成「实测 + 外推」口径")
else:
    print("  !! 页尾未匹配 —— 检查 build_page.py 的 TAIL 与标题")
