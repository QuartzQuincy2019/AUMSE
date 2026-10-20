# -*- coding: utf-8 -*-
"""在《书面语读音和键位图对照》扫描件上标注鲍培转写（Poppe）。

网格是实测出来的（见 tools/_grid_probe 的输出）：
    竖线 x：355 430 505 580 653 727 801 875 949 1023 1097 1172 1249 1326 1405
    左侧第一格（355..430）是空隔列，字母从 430 开始，共 13 列
    表一表头带 y 75..357；表二 y 1018..1302

鲍培转写（Poppe, Grammar of Written Mongolian）：
    ᠨ n   ᠪ b   ᠫ p   ᠬ q   ᠭ γ   ᠮ m   ᠯ l   ᠰ s   ᠱ š
    ᠲ t   ᠳ d   ᠴ č   ᠵ ǰ   ᠶ y   ᠷ r   ᠸ w   ᠩ ng  ᠹ f
    ᠺ k   ᠼ c   ᠽ z   ᠾ h   ᠿ ž   ᡀ lh  ᡁ zh  ᡂ ch
"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

REPO = r"E:\QKMansion\CSX10\w\UME"
SRC = REPO + r"\SharingGroup\tutorials\assets\ref\书面语读音和键位图对照.jpg"
DST = REPO + r"\SharingGroup\tutorials\assets\ref\书面语读音和键位图对照_鲍培.jpg"

COLS = [430, 505, 580, 653, 727, 801, 875, 949, 1023, 1097, 1172, 1249, 1326, 1405]

T1 = ["n", "b", "p", "q", "γ", "m", "l", "s", "š", "t", "d", "č", "ǰ"]
T2 = ["y", "r", "w", "ng", "f", "k", "c", "z", "h", "ž", "lh", "zh", "ch"]

T1_Y, T2_Y = 96, 1036          # 标注基线（表头带的上方空白处）
T1_MN = ["ᠨ", "ᠪ", "ᠫ", "ᠬ", "ᠭ", "ᠮ", "ᠯ", "ᠰ", "ᠱ",
         "ᠲ", "ᠳ", "ᠴ", "ᠵ"]
T2_MN = ["ᠶ", "ᠷ", "ᠸ", "ᠩ", "ᠹ", "ᠺ", "ᠼ", "ᠽ", "ᠾ",
         "ᠿ", "ᡀ", "ᡁ", "ᡂ"]

RED = (192, 57, 43)
DIM = (110, 110, 110)

im = Image.open(SRC).convert("RGB")
d = ImageDraw.Draw(im)

f_poppe = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 40)
f_cjk = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 30)
f_cjk_s = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 22)
# 蒙文字形要用蒙文字体，Segoe UI 里没有这些码位（第一版就印成了一排豆腐块）
f_mn = ImageFont.truetype(REPO + r"\font\NotoSansMongolian-Regular.ttf", 54)
f_hex = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 20)


def center(box, text, font):
    x0, x1 = box
    w = d.textlength(text, font=font)
    return (x0 + x1) / 2 - w / 2


def annotate(letters, mns, y, band_y=None):
    """只在表头空白处写鲍培转写。

    原先还想在表格底部补蒙文字形 + 码位，但实测底部那条带子是「词末」行，
    不是空白 —— 盖上去会压住手写字形，所以只保留红字。
    """
    for i, letter in enumerate(letters):
        x0, x1 = COLS[i], COLS[i + 1]
        d.text((center((x0, x1), letter, f_poppe), y), letter, font=f_poppe, fill=RED)


annotate(T1, T1_MN, T1_Y)
annotate(T2, T2_MN, T2_Y)

# 图例。注意：中西文与蒙文必须分段用不同字体画 ——
# 一开始整行用 msyh 写，蒙文字符全印成了豆腐块。
f_lat = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 28)
f_mn_s = ImageFont.truetype(REPO + r"\font\NotoSansMongolian-Regular.ttf", 30)


def draw_mixed(x, y, parts):
    for text, font, color in parts:
        d.text((x, y), text, font=font, fill=color)
        x += d.textlength(text, font=font)


draw_mixed(60, 1952, [("红字 = 鲍培转写（Poppe）", f_cjk, RED)])

PAIRS = [("q", "ᠬ"), ("γ", "ᠭ"), ("š", "ᠱ"), ("č", "ᠴ"), ("ǰ", "ᠵ"),
         ("ng", "ᠩ"), ("ž", "ᠿ"), ("lh", "ᡀ"), ("zh", "ᡁ"), ("ch", "ᡂ")]
f_mn_s = ImageFont.truetype(REPO + r"\font\NotoSansMongolian-Regular.ttf", 32)
x = 60
draw_mixed(x, 2000, [("转写规范：", f_cjk_s, DIM)])
x += d.textlength("转写规范：", font=f_cjk_s)
for lat, mn in PAIRS:
    draw_mixed(x, 2002, [(lat + " ", f_lat, RED)])
    x += d.textlength(lat + " ", font=f_lat)
    # 蒙文字形本身是竖排朝向，基线比拉丁字低，往上抬一点才对得齐
    draw_mixed(x, 1988, [(mn + " ", f_mn_s, (30, 30, 30))])
    x += d.textlength(mn + " ", font=f_mn_s)

im.save(DST, quality=95)
print("   已写 %s  (%d × %d)" % (DST, im.width, im.height))
