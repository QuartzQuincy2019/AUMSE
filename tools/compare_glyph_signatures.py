# -*- coding: utf-8 -*-
"""比较「HarfBuzz 应选字形」与「导出器误选字形」的签名，
   用来找出能区分它们的判据。"""
import sys
import os

from fontTools.ttLib import TTFont

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
f = TTFont(os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf"))
order = f.getGlyphOrder()
hmtx = f["hmtx"]
glyf = f["glyf"]


def sig(name):
    g = glyf[name]
    if g.numberOfContours == 0:
        return None
    coords, endPts, flags = g.getCoordinates(glyf)
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    return (max(xs) - min(xs), max(ys) - min(ys), hmtx[name][0])


CORRECT = ['u182E.M.init', 'u1823.O.medi', 'u1829.AG.medi',
           'u182D_u1823.GO.medi', 'u182F.L.fina']
WRONG = ['u182E.M.init._isol', 'u1829.AG.medi._init', 'u182C.Hx.init._isol',
         'u182F.L.init._isol', 'u182A.B.init._isol', 'u1834.Ch.init._isol',
         'u1828.N.init._isol', 'u1832.T.init._isol', 'uni1823', 'uni1822']

print("== HarfBuzz 对 ᠮᠣᠩᠭᠣᠯ 的实际输出 ==")
print("%-24s %-6s %-12s %s" % ("字形名", "gid", "bbox w×h", "advance"))
print("-" * 58)
for n in CORRECT:
    w, h, a = sig(n)
    print("%-24s %-6d %-12s %d" % (n, order.index(n), "%dx%d" % (w, h), a))

print()
print("== 导出器误选的近似字形（bbox 相同或极近，但 advance 不同）==")
print("%-24s %-6s %-12s %s" % ("字形名", "gid", "bbox w×h", "advance"))
print("-" * 58)
for n in WRONG:
    s = sig(n)
    if not s:
        print("%-24s %-6s (无轮廓)" % (n, order.index(n)))
        continue
    w, h, a = s
    print("%-24s %-6d %-12s %d" % (n, order.index(n), "%dx%d" % (w, h), a))

print()
print("== 结论判据 ==")
for n in CORRECT:
    w, h, a = sig(n)
    same_box = []
    for other in order:
        if other == n:
            continue
        s2 = sig(other)
        if s2 and s2[0] == w and s2[1] == h:
            same_box.append((other, s2[2]))
    if same_box:
        advs = sorted({a2 for _, a2 in same_box})
        print("  %-24s bbox %dx%d 有 %d 个同框字形，其 advance 取值 %s （本字形 %d）"
              % (n, w, h, len(same_box), advs, a))
    else:
        print("  %-24s bbox %dx%d 唯一" % (n, w, h))
