# -*- coding: utf-8 -*-
"""R04 重建后的固定收尾：标签行（无语言徽章）+ 页脚（不声称编译核对）。

build_page.py 每次重建都会：
  · 把标签行写成「要求 (无)|语音|IPA」那一套
  · 把页脚写回 g++ 的通用说明
R04 讲的是语音，两处都得改，所以每次重建后都要跑这个。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\r04.html"
t = io.open(P, encoding="utf-8").read()
changed = []

# ---------- ① 标签行：只有「语音」「IPA」，不要语言徽章 ----------
FIX = '<p><span class="tag">语音</span> <span class="tag b">IPA</span></p>'
m = re.search(r'<p>(?:<span class="(?:lang|tag)[^>]*>.*?)</p>', t, re.S)
if m and m.group(0) != FIX:
    t = t.replace(m.group(0), FIX, 1)
    changed.append("标签行")

# ---------- ② 页脚 ----------
OLD = '''文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对；
代码示例以 <b>Consolas</b> 等宽字体呈现。'''
NEW = '''本篇不含代码运行结果，没有经过编译器核对的内容；
音标图与符号名称参考 <b>2015 修订版</b>的 IPA 官方全图
（<code>assets/img/IPA_Deja_2015.pdf</code>，DejaVu Sans + Doulos SIL 排版），
中文术语与分区名参考 <a href="https://toipa.org/zh/ipa-chart">toIPA 的中文音标表</a>；
元音位置图是按舌位示意重画的，不是从官方图上截的。'''
if OLD in t:
    t = t.replace(OLD, NEW, 1)
    changed.append("页脚")

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  已处理：%s" % ("、".join(changed) if changed else "无（本来就是对的）"))
print("  字数：%d" % len(t))

# ---------- 自检 ----------
print("  含 lang 徽章：%s" % ("是" if 'class="lang' in t else "否"))
print("  含「g++ 13.1.0」：%s" % ("是" if "g++ 13.1.0" in t else "否"))
print("  小节数：%d" % t.count("<h2 "))
