# -*- coding: utf-8 -*-
"""实验：把一个蒙文词从不同的位置切成两个 run，看字形怎么变。

动机
    「像 Word 一样实时渲染用户指定的格式」意味着同一段文字里可以有多种格式
    （字号、颜色、加粗…）。而排版的规矩是：**属性不同的地方必须切成不同 run**
    （A01 第 3 节引的手册原话：HarfBuzz expects to shape a run of characters
    that all share the same properties）。

    问题：蒙文的连写是由**邻居**决定的。一旦在词中间切 run，
    两半各自找不到邻居，会不会退化成孤立形？

    若会 —— 那么「字级格式」与「蒙文连写」在架构上就是冲突的，
    Word 式编辑器必须把格式与整形解耦（格式画在字形上，不切进 buffer）。
"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import uharfbuzz as hb
except ImportError:
    print("  没有 uharfbuzz，改用 fontTools 不可行 —— 跳过")
    sys.exit(0)

FONT = r"E:\QKMansion\CSX10\w\UME\font\NotoSansMongolian-Regular.ttf"
WORD = "\u182E\u1823\u1829\u182D\u1823\u182F"   # ᠮᠣᠩᠭᠣᠯ

blob = hb.Blob.from_file_path(FONT)
face = hb.Face(blob)
font = hb.Font(face)
font.scale = (64 * 64, 64 * 64)
font.ppem = (64, 64)


def shape(text):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf)
    out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = font.glyph_to_string(info.codepoint)
        out.append((name, pos.x_advance, info.cluster))
    return out


def show(segs, label):
    total = 0
    names = []
    for s in segs:
        for name, adv, _c in shape(s):
            names.append(name)
            total += adv
    print("   %-22s 字形 %d 个  总推进 %5d  %s"
          % (label, len(names), total, " | ".join(names)))


print("  词：ᠮᠣᠩᠭᠣᠯ（6 码位）")
print()
show([WORD], "整词一个 run")
print()
for cut in range(1, 6):
    show([WORD[:cut], WORD[cut:]], "在 %d 与 %d 之间切" % (cut, cut + 1))
print()
show([WORD[:2], WORD[2:4], WORD[4:]], "切成三段")
print()
show([c for c in WORD], "每码位一个 run")
