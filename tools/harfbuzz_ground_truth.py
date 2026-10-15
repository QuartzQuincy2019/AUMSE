# -*- coding: utf-8 -*-
"""
用 HarfBuzz（浏览器所用的同一个整形引擎）取得地面真相：
字体在蒙文上下文中究竟选用了哪些字形。

这一步独立于浏览器，因此可以判定：
  - 浏览器「应该」渲染出什么
  - 位置形位特性 init/medi/fina/isol 在该字体下是否真的存在且可用
"""
import sys
import os
import json

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
upem = face.upem


def shape(text, features=None, script=None, lang=None, direction=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    if script:
        buf.script = script
    if lang:
        buf.language = lang
    if direction:
        buf.direction = direction
    hb.shape(font, buf, features)
    infos = buf.glyph_infos
    poss = buf.glyph_positions
    out = []
    for i, p in zip(infos, poss):
        out.append({
            "gid": i.codepoint,
            "name": font.glyph_to_string(i.codepoint),
            "cluster": i.cluster,
            "x_adv": p.x_advance,
            "y_adv": p.y_advance,
            "x_off": p.x_offset,
            "y_off": p.y_offset,
        })
    return out


L = []
A = L.append
A("=" * 92)
A("HarfBuzz 地面真相：Noto Sans Mongolian 在蒙文上下文中的字形选择")
A("=" * 92)
A("upem = %d" % upem)
A("")

# 关键对照：MA(U+182E) 在词首 / 单独 / 词中 / 词尾
CASES = [
    ("MA 单独",            "\u182E",                    "mn", "MNG "),
    ("MA 词首 (MA+A)",     "\u182E\u1823",              "mn", "MNG "),
    ("MA 词中 (A+MA+A)",   "\u1820\u182E\u1820",        "mn", "MNG "),
    ("MA 词尾 (A+MA)",     "\u1820\u182E",              "mn", "MNG "),
    ("mongol 整词",        "\u182E\u1823\u1829\u182D\u1823\u182F", "mn", "MNG "),
    ("MA 空格 MA",         "\u182E \u182E",             "mn", "MNG "),
    ("A 单独",             "\u1820",                    "mn", "MNG "),
    ("A 词首 (A+MA)",      "\u1820\u182E",              "mn", "MNG "),
    ("A 词中 (MA+A+MA)",   "\u182E\u1820\u182E",        "mn", "MNG "),
    ("A 词尾 (MA+A)",      "\u182E\u1820",              "mn", "MNG "),
]

A("-- 默认（guess_segment_properties）--")
A("%-20s %-9s %-9s %-26s %s" % ("用例", "script", "dir", "字形序列", "x_advance"))
A("-" * 92)
for nm, txt, lang, _ in CASES:
    b = hb.Buffer(); b.add_str(txt); b.guess_segment_properties()
    gs = shape(txt)
    A("%-20s %-9s %-9s %-26s %s" % (
        nm, b.script, b.direction,
        " ".join(g["name"] for g in gs),
        " ".join(str(g["x_adv"]) for g in gs)))

A("")
A("-- 显式指定 script=mong, lang=MNG --")
A("%-20s %-26s %s" % ("用例", "字形序列", "x_advance"))
A("-" * 92)
for nm, txt, _, lng in CASES:
    gs = shape(txt, script="mong", lang=lng)
    A("%-20s %-26s %s" % (
        nm, " ".join(g["name"] for g in gs),
        " ".join(str(g["x_adv"]) for g in gs)))

A("")
A("-- 关键判定：MA 的词首形与单独形是否不同？ --")
g_isol = shape("\u182E", script="mong", lang="MNG ")
g_init = shape("\u182E\u1823", script="mong", lang="MNG ")
A("  MA 单独  -> %s" % " ".join(g["name"] for g in g_isol))
A("  MA 词首  -> %s" % " ".join(g["name"] for g in g_init))
diff = g_isol[0]["name"] != g_init[0]["name"]
A("  首字形不同: %s" % ("是 —— HarfBuzz 确实会按位置换形" if diff else "否 —— 该字体不做位置换形"))
A("")
A("  注：若两者字形名不同，则任何「整形正常工作的渲染器」都应显示出差异；")
A("      若浏览器两者像素一致，说明浏览器没有应用该字体的位置形位特性。")

A("")
A("-- 关闭位置特性后 --")
gs = shape("\u182E\u1823", script="mong", lang="MNG ",
           features={"init": 0, "medi": 0, "fina": 0, "isol": 0, "rclt": 0})
A("  MA+A (init/medi/fina/isol/rclt=0) -> %s" % " ".join(g["name"] for g in gs))

A("")
A("-- 只关 rclt --")
gs = shape("\u182E\u1823", script="mong", lang="MNG ", features={"rclt": 0})
A("  MA+A (rclt=0) -> %s" % " ".join(g["name"] for g in gs))

A("")
A("-- 蒙文常用词整体成形 --")
for nm, txt in [("mongol", "\u182E\u1823\u1829\u182D\u1823\u182F"),
                ("sayin", "\u1830\u1820\u1836\u1822\u1828"),
                ("bichig", "\u182A\u1822\u1834\u1822\u182D")]:
    gs = shape(txt, script="mong", lang="MNG ")
    A("  %-8s %s" % (nm, " ".join(g["name"] for g in gs)))

text = "\n".join(L)
print(text)
with open(os.path.join(OUT, "harfbuzz-ground-truth.txt"), "w", encoding="utf-8") as fh:
    fh.write(text)
print("\n已写出: report/harfbuzz-ground-truth.txt")
