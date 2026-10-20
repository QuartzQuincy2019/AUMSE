# -*- coding: utf-8 -*-
"""在《蒙古文元音字母表》上标注鲍培转写 + 码位。

和辅音表那次不同的是：元音的鲍培转写（a e i o u ö ü）和原表印的字**完全一致**，
所以单纯标红字没有增量。这里额外把每列的蒙文字母与码位补上。

网格实测（列黑度投影）：
    竖线 x：378 456 531 616 702 787 873 960 1047 1135
      378..456 与 456..531 是两小格标签（书面语读音 / 拉丁转写），
      字母列是 531..1135 共 7 列 —— 第一版从 456 起算，整体左移了一列
    横线 y：149 505 779 1052 1327 1600 1871
      149..505 = 书面语读音 + KBD 两行；505..779 = 标准音
"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from PIL import Image, ImageDraw, ImageFont

REPO = r"E:\QKMansion\CSX10\w\UME"
SRC = REPO + r"\SharingGroup\tutorials\assets\ref\元音版本.jpg"
DST = REPO + r"\SharingGroup\tutorials\assets\ref\元音版本_鲍培.jpg"

COLS = [531, 616, 702, 787, 873, 960, 1047, 1135]

VOWELS = [
    ("a",  "ᠠ", 0x1820),
    ("e",  "ᠡ", 0x1821),
    ("i",  "ᠢ", 0x1822),
    ("o",  "ᠣ", 0x1823),
    ("u",  "ᠤ", 0x1824),
    ("ö",  "ᠥ", 0x1825),
    ("ü",  "ᠦ", 0x1826),
]

TOP_Y = 358          # 行1 字母与 KBD 行之间的空白带（365..425）
RED = (192, 57, 43)
DIM = (110, 110, 110)
INK = (25, 25, 25)

im = Image.open(SRC).convert("RGB")
d = ImageDraw.Draw(im)

f_poppe = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 30)
f_mn = ImageFont.truetype(REPO + r"\font\NotoSansMongolian-Regular.ttf", 28)
f_cjk = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 28)
f_cjk_s = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 20)
f_small = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 17)


for i, (lat, mn, cp) in enumerate(VOWELS):
    x0, x1 = COLS[i], COLS[i + 1]
    cx = (x0 + x1) / 2

    # 红字 + 蒙文字母：先量总宽再整体居中，别让第一个字挤进左侧标签列
    w_lat = d.textlength(lat, font=f_poppe)
    w_mn = d.textlength(mn, font=f_mn)
    total = w_lat + 6 + w_mn
    x = cx - total / 2
    d.text((x, TOP_Y), lat, font=f_poppe, fill=RED)
    d.text((x + w_lat + 6, TOP_Y - 2), mn, font=f_mn, fill=INK)

    # 码位放在下一行（小字），不压到 KBD 行
    hexs = "U+%04X" % cp
    w2 = d.textlength(hexs, font=f_small)
    d.text((cx - w2 / 2, TOP_Y + 40), hexs, font=f_small, fill=DIM)

# 图例。只排两行、宽度控制在 440px 以内 —— 页码「4」在 x≈540, y≈1930，
# 排三行就会和它撞在一起。
d.text((60, 1888), "红字 = 鲍培转写（Poppe）", font=f_cjk, fill=RED)
d.text((60, 1932), "原表转写与鲍培一致；黑=字母 灰=码位", font=f_cjk_s, fill=DIM)

im.save(DST, quality=95)
print("   已写 %s  (%d × %d)" % (DST, im.width, im.height))
