# -*- coding: utf-8 -*-
"""HarfBuzz 对拍：浏览器默认整形 vs UME.html 里显式开启的特性。

关键问题：浏览器对蒙文会默认启用哪些特性？
若浏览器默认已经启用 init/medi/fina/isol/rclt，则显式声明是多余但无害的；
若默认不启用，则显式声明是必需的。
另外验证：显式声明是否会把字形选错（例如漏掉 rclt 的连字）。
"""
import sys
import os

import uharfbuzz as hb

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
OUT = os.path.join(ROOT, "report")

with open(FONT, "rb") as fh:
    data = fh.read()
face = hb.Face(data)
font = hb.Font(face)

# UME.html 当前使用的特性集合
UME_FEATURES = {"rclt": 1, "ccmp": 1, "init": 1, "medi": 1, "fina": 1,
                "isol": 1, "calt": 1, "liga": 1}


def shape(text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features)
    return [(font.glyph_to_string(i.codepoint), p.x_advance)
            for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


WORDS = [
    ("mongol", "\u182E\u1823\u1829\u182D\u1823\u182F"),
    ("sayin",  "\u1830\u1820\u1836\u1822\u1828"),
    ("bichig", "\u182A\u1822\u1834\u1822\u182D"),
    ("MA 单独", "\u182E"),
    ("MA 词首", "\u182E\u1823"),
    ("MA 词中", "\u1820\u182E\u1820"),
    ("MA 词尾", "\u1820\u182E"),
]

L = []
A = L.append
A("=" * 96)
A("HarfBuzz 对拍：默认整形 vs UME 显式特性")
A("=" * 96)
A("")

A("%-10s %-46s %s" % ("用例", "默认（不传 features）", "UME 显式特性"))
A("-" * 96)
same_all = True
for nm, txt in WORDS:
    d = shape(txt)
    u = shape(txt, UME_FEATURES)
    same = (d == u)
    if not same:
        same_all = False
    A("%-10s %-46s %s" % (
        nm,
        " ".join(g for g, _ in d),
        " ".join(g for g, _ in u)))
    if not same:
        A("%-10s %-46s %s" % ("", " ".join(str(a) for _, a in d),
                              " ".join(str(a) for _, a in u)))
A("")
A("默认 == UME 显式 : %s" % ("是（显式声明是冗余但无害的）" if same_all
                            else "否 —— 两者选了不同字形！"))
A("")

A("-- 若只关掉 rclt，会丢什么 --")
A("%-10s %-46s %s" % ("用例", "rclt=0", "默认"))
A("-" * 96)
for nm, txt in WORDS:
    noR = shape(txt, {"rclt": 0})
    d = shape(txt)
    A("%-10s %-46s %s" % (nm,
                          " ".join(g for g, _ in noR),
                          " ".join(g for g, _ in d)))
A("")

A("-- 关掉全部位置特性 --")
A("%-10s %-46s %s" % ("用例", "init/medi/fina/isol=0", "默认"))
A("-" * 96)
for nm, txt in WORDS:
    off = shape(txt, {"init": 0, "medi": 0, "fina": 0, "isol": 0,
                      "rclt": 0, "ccmp": 0})
    d = shape(txt)
    A("%-10s %-46s %s" % (nm,
                          " ".join(g for g, _ in off),
                          " ".join(g for g, _ in d)))

text = "\n".join(L)
print(text)
with open(os.path.join(OUT, "harfbuzz-features-compare.txt"), "w",
          encoding="utf-8") as fh:
    fh.write(text)
print("\n已写出: report/harfbuzz-features-compare.txt")
