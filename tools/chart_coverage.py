# -*- coding: utf-8 -*-
"""
UME 字体字符分布可视化：
  1) coverage.png  —— 按 Unicode 区段的覆盖率直方图
  2) mongolian-grid.png —— 蒙文区段逐码位字形总表（旋转 90° 以符合竖排书写观感）
"""
import os
import sys
import unicodedata
from collections import Counter, OrderedDict

from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
OUT = os.path.join(ROOT, "report")
os.makedirs(OUT, exist_ok=True)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Windows 中文字体，用于图内中文标签
CJK_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc",
]


def cjk_font(size):
    for p in CJK_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def get_cmap():
    f = TTFont(FONT_PATH)
    return f.getBestCmap()


def draw_coverage(cmap):
    """区段覆盖率直方图。"""
    BLOCKS = [
        ("Mongolian\n蒙文主区段", 0x1800, 0x18AF, 176),
        ("Mongolian Suppl.\n蒙文补充", 0x11660, 0x1167F, 32),
        ("Basic Latin\n基本拉丁", 0x0000, 0x007F, 128),
        ("Latin-1 Suppl.", 0x0080, 0x00FF, 128),
        ("Latin Ext-A", 0x0100, 0x017F, 128),
        ("Latin Ext-B", 0x0180, 0x024F, 208),
        ("Spacing Modifier", 0x02B0, 0x02FF, 80),
        ("Combining Diacr.", 0x0300, 0x036F, 112),
        ("General Punct.", 0x2000, 0x206F, 112),
        ("CJK Symbols", 0x3000, 0x303F, 64),
        ("Halfwidth/Full.", 0xFF00, 0xFFEF, 240),
    ]
    rows = []
    for name, lo, hi, total in BLOCKS:
        n = sum(1 for c in range(lo, hi + 1) if c in cmap)
        rows.append((name, n, total, 100.0 * n / total))

    W, rowh, pad_t, pad_b = 1040, 46, 90, 40
    H = pad_t + rowh * len(rows) + pad_b
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    fb = cjk_font(20)
    fs = cjk_font(15)
    ft = cjk_font(26)

    d.text((30, 24), "UME 字体字符分布 — 按 Unicode 区段覆盖率", font=ft, fill="#111")
    d.text((30, 58), "Noto Sans Mongolian Regular v3.103  (共 517 个 Unicode 码位)",
           font=fs, fill="#666")

    barx = 250
    maxw = W - barx - 130
    for i, (name, n, total, pct) in enumerate(rows):
        y = pad_t + i * rowh
        d.text((30, y + 4), name, font=fs, fill="#222")
        d.rectangle([barx, y + 10, barx + maxw, y + 30], fill="#eef1f5",
                    outline="#d7dce3")
        w = int(maxw * pct / 100.0)
        color = "#2f6fd0" if pct >= 90 else ("#3f9e5a" if pct >= 50 else "#c9803a")
        if pct == 0:
            color = "#ccc"
        if w:
            d.rectangle([barx, y + 10, barx + w, y + 30], fill=color)
        d.text((barx + maxw + 10, y + 5), "%d/%d  %.0f%%" % (n, total, pct),
               font=fs, fill="#333")
    p = os.path.join(OUT, "coverage.png")
    img.save(p)
    print("已写出:", p)
    return rows


def draw_mongolian_grid(cmap):
    """蒙文区段字形总表。

    字形旋转 -90°（逆时针）：已用字体自带 GSUB 'vert' 变体验证——
    基础括号 U+3008/3009/FF08/FF09 逆时针转 90° 后与作者绘制的 .vert
    字形 IoU 达 0.95~0.98，而顺时针仅 0.08~0.09，故该字体竖排取向为逆时针。
    """
    cps = sorted(c for c in cmap if 0x1800 <= c <= 0x18AF)
    cps += sorted(c for c in cmap if 0x11660 <= c <= 0x1167F)

    COLS, CELL, GAP = 12, 130, 10
    PAD = 30
    HEAD = 104
    FOOT = 26
    W = PAD * 2 + COLS * (CELL + GAP) - GAP
    rows = (len(cps) + COLS - 1) // COLS
    H = HEAD + rows * (CELL + GAP + FOOT) + PAD

    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    ft = cjk_font(26)
    fs = cjk_font(14)
    fx = cjk_font(11)

    d.text((PAD, 24), "UME — 蒙文区段字形总表 (U+1800–U+18AF + U+11660–U+1167F)",
           font=ft, fill="#111")
    d.text((PAD, 60), "共 %d 个码位 · 蓝底=字母  绿底=数字  灰底=标点/格式符  ·  "
                      "字形已按字体自身竖排取向旋转 90°（逆时针）" % len(cps),
           font=fs, fill="#666")

    pf = ImageFont.truetype(FONT_PATH, 76)
    for i, cp in enumerate(cps):
        r, c = divmod(i, COLS)
        x = PAD + c * (CELL + GAP)
        y = HEAD + r * (CELL + GAP + FOOT)
        cat = unicodedata.category(chr(cp))
        is_letter = cat.startswith("L")
        is_digit = cat == "Nd"
        bg = "#e8f0fd" if is_letter else ("#eaf7ec" if is_digit else "#f3f4f6")
        bd = "#c3d6f5" if is_letter else ("#cbe8d1" if is_digit else "#dfe3e8")
        d.rectangle([x, y, x + CELL, y + CELL], fill=bg, outline=bd)

        tmp = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        ch = chr(cp)
        try:
            bb = td.textbbox((0, 0), ch, font=pf)
            gw, gh = bb[2] - bb[0], bb[3] - bb[1]
            if gw and gh:
                td.text(((CELL - gw) / 2 - bb[0], (CELL - gh) / 2 - bb[1]),
                        ch, font=pf, fill="#14181f")
        except Exception:
            pass
        rot = tmp.rotate(-90, expand=False, resample=Image.BICUBIC)
        img.paste(rot, (x, y), rot)

        d.text((x + 3, y + CELL + 3), "U+%04X" % cp, font=fx, fill="#444")
        try:
            nm = unicodedata.name(ch)
            short = (nm.replace("MONGOLIAN ", "")
                       .replace("LETTER ", "")
                       .replace("FREE VARIATION SELECTOR ", "FVS")
                       .replace("ALI GALI ", ""))
        except ValueError:
            short = "?"
        if len(short) > 17:
            short = short[:16] + "…"
        d.text((x + 3, y + CELL + 14), short, font=fx, fill="#999")

    p = os.path.join(OUT, "mongolian-grid.png")
    img.save(p)
    print("已写出:", p, img.size)


def main():
    cmap = get_cmap()
    rows = draw_coverage(cmap)
    draw_mongolian_grid(cmap)
    print("\n区段覆盖率汇总:")
    for name, n, total, pct in rows:
        print("  %-20s %4d/%-4d %5.1f%%" % (name.replace("\n", " "), n, total, pct))


if __name__ == "__main__":
    main()
