# -*- coding: utf-8 -*-
"""为 process.html 提取真实数据：把每个码位在两种特性设置下的字形名与宽度导出为 JSON。

文档里的示意图不手绘字形，全部用这些真实数据驱动，并由浏览器现场渲染字体。
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
    face = hb.Face(fh.read())
font = hb.Font(face)
UPEM = face.upem

# 演示用词：ᠮᠣᠩᠭᠣᠯ / ᠪᠢᠴᠢᠭ / ᠰᠠᠶᠢᠨ
WORDS = [
    ("mongol", "\u182E\u1823\u1829\u182D\u1823\u182F", "蒙古"),
    ("bichig", "\u182A\u1822\u1834\u1822\u182D", "文字·书"),
    ("sayin",  "\u1830\u1820\u1836\u1822\u1828", "好"),
]

# 故意把位置特性强制打开 —— 复现曾经的 bug
BROKEN = {"rclt": 1, "ccmp": 1, "init": 1, "medi": 1, "fina": 1, "isol": 1,
          "calt": 1, "liga": 1}


def shape(text, features=None):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features)
    out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append({
            "gid": info.codepoint,
            "name": font.glyph_to_string(info.codepoint),
            "cluster": info.cluster,
            "adv": pos.x_advance,
        })
    return out


data = {
    "upem": UPEM,
    "fontName": "Noto Sans Mongolian Regular",
    "fontVersion": "3.103",
    "words": [],
}

for key, text, gloss in WORDS:
    good = shape(text)
    bad = shape(text, BROKEN)
    data["words"].append({
        "key": key,
        "gloss": gloss,
        "text": text,
        "codepoints": ["U+%04X" % ord(c) for c in text],
        "chars": list(text),
        "good": good,
        "goodTotal": sum(g["adv"] for g in good),
        "bad": bad,
        "badTotal": sum(g["adv"] for g in bad),
    })

# 单字母在各位置的形态（用于展示位置形位体系）
POS = [
    ("MA 单独", "\u182E"),
    ("MA 词首", "\u182E\u1823"),
    ("MA 词中", "\u1820\u182E\u1820"),
    ("MA 词尾", "\u1820\u182E"),
]
data["positions"] = [{
    "label": lab, "text": txt,
    "glyphs": shape(txt),
} for lab, txt in POS]

# 少量单位换算供图例使用
data["em"] = UPEM

path = os.path.join(OUT, "process-data.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=1)

# 同时写一个 JS 版本：process.html 用 <script src> 加载它。
# 原因：file:// 协议下 fetch/XHR 读同级 JSON 会被 CORS 拦，
# 而 <script src> 不受限制 —— 这样文档双击即可打开。
jspath = os.path.join(OUT, "process-data.js")
with open(jspath, "w", encoding="utf-8") as fh:
    fh.write("/* 由 tools/extract_process_data.py 生成，请勿手改。 */\n")
    fh.write("window.UME_PROCESS_DATA = ")
    json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    fh.write(";\n")

print("upem =", UPEM)
for w in data["words"]:
    print("%-8s 默认 %d 字形 总宽 %4d (%.2f em) | 干预后 %d 字形 总宽 %4d (%.2f em)"
          % (w["key"], len(w["good"]), w["goodTotal"], w["goodTotal"] / UPEM,
             len(w["bad"]), w["badTotal"], w["badTotal"] / UPEM))
print()
for p in data["positions"]:
    print("%-9s -> %s" % (p["label"], " ".join(g["name"] for g in p["glyphs"])))
print()
print("已写出:", path, "(%d 字节)" % os.path.getsize(path))
print("已写出:", jspath, "(%d 字节)" % os.path.getsize(jspath))
