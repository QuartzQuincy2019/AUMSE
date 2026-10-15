# -*- coding: utf-8 -*-
"""校验导出的 SVG：把每条 <path> 的包围盒与「HarfBuzz 应选字形」的
   轮廓包围盒对比（按变换缩放/旋转换算），从而确认字形身份正确。

   这一步不依赖浏览器，只用 fontTools 的权威字形数据。
"""
import os
import re
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
SVG = os.path.join(ROOT, "report", "_export-test.svg")

f = TTFont(FONT)
order = f.getGlyphOrder()
glyf = f["glyf"]
gs = f.getGlyphSet()

# 样例文本 ᠮᠣᠩᠭᠣᠯ ᠪᠢᠴᠢᠭ ᠤᠨ ᠲᠣᠯᠢ 的 HarfBuzz 期望字形序列
EXPECT = [
    "u182E.M.init", "u1823.O.medi", "u1829.AG.medi",
    "u182D_u1823.GO.medi", "u182F.L.fina",
    "u182A_u1822.BI.init", "u1834.Ch.medi", "u1822.I.medi", "u182D.G.fina",
    "u1824.U.isol", "u1828.N.fina",
    "u1832.T.init", "u1823.O.medi", "u182F.L.fina", "u1822.I.fina",
]


def glyph_bbox(name):
    pen = BoundsPen(gs)
    gs[name].draw(pen)
    return pen.bounds  # (xMin, yMin, xMax, yMax) or None


def svg_path_bounds(d):
    """从 path 的 d 字符串里取所有绝对坐标点的包围盒（近似但足够比较）。"""
    nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
    xs = nums[0::2]
    ys = nums[1::2]
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


if not os.path.exists(SVG):
    print("缺少", SVG, "—— 请先运行导出测试")
    sys.exit(2)

svg = open(SVG, encoding="utf-8").read()
paths = re.findall(r'<path transform="([^"]+)" d="([^"]+)"', svg)
print("SVG 中 path 数 =", len(paths))
print("HarfBuzz 期望字形数 =", len(EXPECT))
print()

# 从 transform 取平移量（ty = pad + localX，应随字形逐个递增）
tys = []
for tf, _ in paths:
    v = [float(x) for x in re.findall(r"-?\d+\.?\d*", tf)]
    if len(v) >= 6:
        tys.append(v[5])
if tys:
    print("各字形沿行方向的起点 ty:", " ".join("%.1f" % t for t in tys[:8]), "…")
    print("是否单调递增:", all(tys[i] <= tys[i+1] + 1e-6 for i in range(len(tys)-1)))
print()

# 用「归一化包围盒比例」比对：与缩放、平移都无关，只反映字形形状
print("%-3s %-24s %-18s %-18s %s" % ("#", "期望字形", "字形 bbox 比例",
                                     "path bbox 比例", "判定"))
print("-" * 90)
ok = 0
for i, (tf, d) in enumerate(paths):
    pb = svg_path_bounds(d)
    if pb is None or i >= len(EXPECT):
        continue
    sw = pb[2] - pb[0]
    sh = pb[3] - pb[1]
    sratio = sw / sh

    name = EXPECT[i]
    gb = glyph_bbox(name)
    if gb is None:
        print("%-3d %-24s %s" % (i, name, "(空轮廓)"))
        continue
    gw = gb[2] - gb[0]
    gh = gb[3] - gb[1]
    gratio = gw / gh

    # 比例相对误差 < 4%
    err = abs(sratio - gratio) / gratio
    match = err < 0.04
    if match:
        ok += 1
    print("%-3d %-24s %-18s %-18s %s" % (
        i, name,
        "%.0f×%.0f = %.3f" % (gw, gh, gratio),
        "%.0f×%.0f = %.3f" % (sw, sh, sratio),
        "OK" if match else "<-- 不符 (%.1f%%)" % (err * 100)))

print()
print("字形身份匹配 %d / %d" % (ok, min(len(paths), len(EXPECT))))
sys.exit(0 if ok == min(len(paths), len(EXPECT)) else 1)
