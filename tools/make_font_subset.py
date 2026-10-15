# -*- coding: utf-8 -*-
"""为 SVG 文本模式生成内嵌用的字体子集（WOFF2 + base64）。

为什么需要：SVG 作为 <img> 加载时是隔离环境，**不能加载外部字体**，
所以 <text> 会回退到系统字体 —— 蒙文没有字形就变成豆腐块。
把字体子集内嵌成 data: URL 才能保证任何环境都正确。

子集只保留实际用得到的码位，体积远小于原字体。
"""
import base64
import io
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
OUT = os.path.join(ROOT, "web", "vendor", "font-subset.js")

# 保留：蒙文主区段 + 补充区段 + 基本拉丁/数字/常用标点
unicodes = []
unicodes += list(range(0x1800, 0x18B0))      # 蒙文主区段
unicodes += list(range(0x11660, 0x11680))    # 蒙文补充区段
unicodes += list(range(0x0020, 0x007F))      # 基本拉丁
unicodes += [0x200B, 0x200C, 0x200D, 0x2060, 0x00A0,
             0x2018, 0x2019, 0x201C, 0x201D, 0x2014, 0x2026,
             0x3001, 0x3002, 0xFF01, 0xFF08, 0xFF09, 0xFF0C,
             0xFF1A, 0xFF1B, 0xFF1F]

opts = subset.Options()
opts.flavor = "woff2"
opts.desubroutinize = False
opts.layout_features = ["*"]      # 保留全部 OpenType 特性（rclt 必须留）
opts.name_IDs = ["*"]
opts.notdef_outline = True
opts.recalc_bounds = False
opts.drop_tables = []
opts.retain_gids = False
# 关键：允许裁剪 GSUB/GPOS，只保留子集码位真正用得上的替换规则。
# 否则 rclt 会把整个字体的 3715 个字形全部拖住，子集毫无收益。
opts.layout_closure = True
opts.hinting = False
opts.glyph_names = False

font = subset.load_font(SRC, opts)
sub = subset.Subsetter(options=opts)
sub.populate(unicodes=unicodes)
sub.subset(font)

buf = io.BytesIO()
font.save(buf)
data = buf.getvalue()

b64 = base64.b64encode(data).decode("ascii")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("/* Noto Sans Mongolian 3.103 子集（WOFF2）—— SIL Open Font License 1.1\n")
    fh.write("   Copyright 2023 The Noto Project Authors. https://scripts.sil.org/OFL\n")
    fh.write("   用于把字体内嵌进导出的 SVG：SVG 作为 <img> 加载时无法引用外部字体，\n")
    fh.write("   不内嵌就会回退到系统字体、蒙文显示成豆腐块。\n")
    fh.write("   由 tools/make_font_subset.py 生成，请勿手改。 */\n")
    fh.write('window.UME_FONT_SUBSET = "%s";\n' % b64)

orig = os.path.getsize(SRC)
print("原始 TTF : %d 字节 (%.1f KB)" % (orig, orig / 1024))
print("WOFF2 子集: %d 字节 (%.1f KB)  —— 压缩到 %.1f%%"
      % (len(data), len(data) / 1024, 100.0 * len(data) / orig))
print("base64   : %d 字符 (%.1f KB)" % (len(b64), len(b64) / 1024))
print("输出     : %s (%d 字节)" % (OUT, os.path.getsize(OUT)))

# 校验子集仍含蒙文字形与关键特性
chk = TTFont(io.BytesIO(data))
cmap = chk.getBestCmap()
print("子集码位数:", len(cmap), " 字形数:", chk["maxp"].numGlyphs)
for cp in (0x182E, 0x1823, 0x182D):
    print("  U+%04X -> %s" % (cp, "OK" if cp in cmap else "缺失"))
if "GSUB" in chk:
    tags = sorted({fr.FeatureTag for fr in chk["GSUB"].table.FeatureList.FeatureRecord})
    print("GSUB 特性:", " ".join(tags))
    print("含 rclt:", "rclt" in tags)
