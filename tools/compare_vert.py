# -*- coding: utf-8 -*-
"""
用字体自带的 .vert 变体反推竖排旋转角：
把基础标点字形按 -90 / +90 旋转，与字体作者绘制的 .vert 字形比对。
与 .vert 一致的那个角度，就是该字体认定的竖排方向。
"""
import os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
OUT = os.path.join(ROOT, "report")
MSYH = r"C:\Windows\Fonts\msyh.ttc"

f = TTFont(FONT_PATH)
gs = f.getGlyphSet()
cmap = f.getBestCmap()
S = 160


def render_glyph(gname):
    """把某个字形按其轮廓渲染成 SxS 位图（upem 归一化）。"""
    upem = f["head"].unitsPerEm
    scale = S / upem
    img = Image.new("L", (S, S), 255)
    d = ImageDraw.Draw(img)
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    pen = DecomposingRecordingPen(gs)
    gs[gname].draw(pen)
    pts_polys = []
    cur = []
    start = None
    for op, args in pen.value:
        if op == "moveTo":
            if cur:
                pts_polys.append(cur)
            cur = [args[0]]
            start = args[0]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "qCurveTo":
            pts = list(args)
            # 二次曲线转采样
            if pts[-1] is None:
                pts = pts[:-1]
            p0 = cur[-1] if cur else pts[0]
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                for t in [j / 8.0 for j in range(9)]:
                    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * a[0] + t * t * b[0]
                    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * a[1] + t * t * b[1]
                    cur.append((x, y))
                p0 = b
        elif op == "curveTo":
            p0 = cur[-1] if cur else args[0]
            a, b, c = args[0], args[1], args[2]
            for j in range(13):
                t = j / 12.0
                x = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * a[0]
                     + 3 * (1 - t) * t * t * b[0] + t ** 3 * c[0])
                y = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * a[1]
                     + 3 * (1 - t) * t * t * b[1] + t ** 3 * c[1])
                cur.append((x, y))
        elif op == "closePath":
            if cur:
                pts_polys.append(cur)
            cur = []
    if cur:
        pts_polys.append(cur)

    # 统一平移居中：以所有点包围盒为准
    allp = [p for poly in pts_polys for p in poly]
    if not allp:
        return img
    minx = min(p[0] for p in allp); maxx = max(p[0] for p in allp)
    miny = min(p[1] for p in allp); maxy = max(p[1] for p in allp)
    cx, cy = (minx + maxx) / 2.0, (miny + maxy) / 2.0

    for poly in pts_polys:
        pix = [((p[0] - cx) * scale + S / 2, -(p[1] - cy) * scale + S / 2)
               for p in poly]
        if len(pix) >= 3:
            d.polygon(pix, fill=0)
    return img


def iou(a, b):
    """两幅二值图的交并比（前景=字）。"""
    pa = a.point(lambda v: 255 if v < 128 else 0)
    pb = b.point(lambda v: 255 if v < 128 else 0)
    inter = ImageChops.logical_and(pa.convert("1"), pb.convert("1"))
    union = ImageChops.logical_or(pa.convert("1"), pb.convert("1"))
    ni = sum(inter.point(lambda v: 1 if v else 0).getdata())
    nu = sum(union.point(lambda v: 1 if v else 0).getdata())
    return ni / nu if nu else 0.0


PAIRS = [("u2018", "u2018.vert"), ("u2019", "u2019.vert"),
         ("u201C", "u201C.vert"), ("u201D", "u201D.vert"),
         ("uni3001", "u3001.vert"), ("uni3002", "u3002.vert"),
         ("uni3008", "u3008.vert"), ("uni3009", "u3009.vert"),
         ("uniFF08", "uFF08.vert"), ("uniFF09", "uFF09.vert")]

names = set(f.getGlyphOrder())
print("%-14s %-14s  %-8s %-8s %-8s  判定" % ("基础字形", ".vert 字形", "0°", "-90°", "+90°"))
rows = []
for base, vert in PAIRS:
    if base not in names or vert not in names:
        print("跳过（缺字形）:", base, vert)
        continue
    ib = render_glyph(base)
    iv = render_glyph(vert)
    s0 = iou(ib, iv)
    sm = iou(ib.rotate(-90, expand=False), iv)
    sp = iou(ib.rotate(90, expand=False), iv)
    best = max([(s0, "0°"), (sm, "-90°"), (sp, "+90°")])
    print("%-14s %-14s  %-8.3f %-8.3f %-8.3f  -> %s" % (
        base, vert, s0, sm, sp, best[1]))
    rows.append((base, vert, s0, sm, sp, best[1], ib, iv))

if rows:
    from collections import Counter
    # 旋转不敏感的字形（引号/顿号等）：0° 与 ±90° 得分相同或极接近，无判别力
    sensitive = [r for r in rows if abs(r[3] - r[4]) > 0.05]
    c_all = Counter(r[5] for r in rows)
    print("\n[全部字形投票，含旋转不敏感者]", dict(c_all))
    if sensitive:
        c_s = Counter(r[5] for r in sensitive)
        print("[仅旋转敏感字形投票]  样本 %d 个 -> %s" % (len(sensitive), dict(c_s)))
        win = c_s.most_common(1)[0][0]
        mean = sum(max(r[3], r[4]) for r in sensitive) / len(sensitive)
        print("结论: 竖排取向 = %s（旋转敏感字形平均 IoU %.3f）" % (win, mean))
        print("      旋转不敏感字形: %s" % ", ".join(
            r[0] for r in rows if r not in sensitive))

    # 拼一张对照图
    CW, CH = 170, 200
    W = 60 + len(rows) * CW
    H = 60 + 4 * CH
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    fl = ImageFont.truetype(MSYH, 15)
    heads = ["基础字形 0°", "基础字形 -90°", "基础字形 +90°", "字体自带 .vert"]
    for i, h in enumerate(heads):
        d.text((10, 30 + i * CH), h, font=fl, fill="#333")
    for j, (base, vert, s0, sm, sp, best, ib, iv) in enumerate(rows):
        x = 60 + j * CW
        for i, im in enumerate([ib, ib.rotate(-90, expand=False),
                                ib.rotate(90, expand=False), iv]):
            canvas.paste(im.convert("RGB"), (x, 30 + i * CH))
        d.text((x, 6), base, font=fl, fill="#666")
    p = os.path.join(OUT, "vert-orientation-matrix.png")
    canvas.save(p)
    print("已写出:", p)
