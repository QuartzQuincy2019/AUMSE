# -*- coding: utf-8 -*-
"""A01 收尾：页尾换成与实际验证方式相符的说明。

**每次重建 a01.html 之后都要跑**
    build_page.py 的 TAIL 里写死了「均使用 g++ 13.1.0 实际编译运行核对」。
    A01 一个 C++ 程序都没跑（本机没装 HarfBuzz 开发库），
    声称 g++ 核对是假话 —— 项目里有「页尾不许虚报」的规矩。

本篇实际做过的事
    · uharfbuzz 14.6.0（HarfBuzz 14.6.0）+ fontTools 4.67.0
    · Noto Sans Mongolian（UPEM 1000）、Segoe UI、Arial、Times New Roman
    · 实测项：字形序列、推进量、簇号、ttb 的 −1750、guess 与显式 mong 等价
    · 第 15 节的圣书体：MdCRndr + New Gardiner 3.06 实际渲染（OFL 1.1）
    · C++ 片段：按 API 签名写，未编译
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\a01.html"
t = io.open(P, encoding="utf-8").read()

OLD = """<footer>
UME 项目组内部教程 · A01《HarfBuzz 及其基础用法》<br>
文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

NEW = """<footer>
UME 项目组内部教程 · A01《HarfBuzz 及其基础用法》<br>
文中的字形序列、推进量、簇号与方向对照，均由
<b>uharfbuzz 14.6.0</b>（HarfBuzz 14.6.0）配合 <b>fontTools 4.67.0</b>，
在 <code>Noto Sans Mongolian</code>（UPEM 1000）、<code>Segoe UI</code>、
<code>Arial</code>、<code>Times New Roman</code> 上实际运行得出。<br>
第 15 节的圣书体示例由 <b>MdCRndr</b> 配 <b>New Gardiner 3.06</b>
（Mark-Jan Nederhof，OFL 1.1）实际渲染。<br>
C++ 片段是按接口签名写的说明性代码，<b>本机未安装 HarfBuzz 开发库，未编译</b>；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

if NEW in t:
    print("  · 页尾已是正确版本")
elif OLD in t:
    t = t.replace(OLD, NEW, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  ✓ 页尾已换成 uharfbuzz + MdCRndr 口径")
else:
    print("  !! 页尾未匹配 —— 请检查 build_page.py 的 TAIL 是否又改了")
