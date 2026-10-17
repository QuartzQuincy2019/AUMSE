# -*- coding: utf-8 -*-
"""检查 DejaVu Serif 2.35 是否覆盖 R04 里用到的全部音标字符。

做法：自己解析 TTF 的 cmap（不装 fontTools）——
优先 format 12（全 Unicode），退回 format 4（BMP）。
然后拿正文里出现的每个非 ASCII 字符 + 一批 ASCII 音标字母去比对。
"""
import io
import re
import struct
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FONT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets\fonts\DejaVuSerif.ttf"
BODY = r"E:\QKMansion\CSX10\w\UME\tools\_r04_body.html"

d = io.open(FONT, "rb").read()
num = struct.unpack(">H", d[4:6])[0]
tables = {}
for i in range(num):
    off = 12 + i * 16
    tag = d[off:off + 4].decode("latin-1")
    o, l = struct.unpack(">II", d[off + 8:off + 16])
    tables[tag] = (o, l)

cmap_off = tables["cmap"][0]
n_sub = struct.unpack(">H", d[cmap_off + 2:cmap_off + 4])[0]
best = None
for i in range(n_sub):
    b = cmap_off + 4 + i * 8
    pid, eid, sub = struct.unpack(">HHI", d[b:b + 8])
    so = cmap_off + sub
    fmt = struct.unpack(">H", d[so:so + 2])[0]
    if fmt == 12 and (best is None or best[0] != 12):
        best = (12, so)
    elif fmt == 4 and best is None:
        best = (4, so)

covered = set()
if best and best[0] == 12:
    so = best[1]
    n_groups = struct.unpack(">I", d[so + 12:so + 16])[0]
    for i in range(n_groups):
        b = so + 16 + i * 12
        start, end, _gid = struct.unpack(">III", d[b:b + 12])
        covered.update(range(start, end + 1))
    print("  cmap format 12，%d 个区间，覆盖 %d 个码位" % (n_groups, len(covered)))
else:
    so = best[1]
    segx2 = struct.unpack(">H", d[so + 6:so + 8])[0]
    seg = segx2 // 2
    ends = [struct.unpack(">H", d[so + 14 + i * 2:so + 16 + i * 2])[0] for i in range(seg)]
    starts_off = so + 16 + segx2
    starts = [struct.unpack(">H", d[starts_off + i * 2:starts_off + i * 2 + 2])[0]
              for i in range(seg)]
    for s, e in zip(starts, ends):
        if s != 0xFFFF:
            covered.update(range(s, e + 1))
    print("  cmap format 4，%d 段，覆盖 %d 个码位" % (seg, len(covered)))

# ---------- 正文里出现的字符 ----------
t = io.open(BODY, encoding="utf-8").read()
text = re.sub(r"<[^>]+>", "", t)
text = re.sub(r"&[a-z]+;", " ", text)

nonascii = sorted({ch for ch in text if ord(ch) > 127 and ord(ch) < 0x3000})
# 再加一批正文里作为音标用的 ASCII（大小写字母在 IPA 里是有意义的）
extra = list("/[]{}()ʰːˑˈˌaeiouɛɔəɪʊɑɐʌɤɯɨøœyɥɜɞɘɵɚæɶɒɜɹɻɾʀʁʐʂʈɖɟɢɦɧɬɮɭɳɲɴɸɹʀʙʜʕʢʔβθðʃʒçʝɣχħʕʜʡʕʢʦʧʨʩʪʫʬʭʮʯ")

miss_n = [ch for ch in nonascii if ord(ch) not in covered]
miss_e = [ch for ch in extra if ord(ch) not in covered]

print()
print("  正文非 ASCII 字符 %d 个（不含中文），缺字形 %d 个：%s"
      % (len(nonascii), len(miss_n), "、".join(miss_n) if miss_n else "无"))
print()
print("  音标专用字符检查：")
show = "".join(extra)
print("      " + show)
print("      缺失：%s" % ("、".join(miss_e) if miss_e else "无 —— 全部覆盖"))

# 逐类统计
groups = {
    "IPA 扩展 U+0250–02AF": range(0x250, 0x2B0),
    "修饰字母 U+02B0–02FF": range(0x2B0, 0x300),
    "组合符号 U+0300–036F": range(0x300, 0x370),
}
print()
for name, rng in groups.items():
    have = [c for c in rng if c in covered]
    print("      %-22s 覆盖 %d / %d" % (name, len(have), len(list(rng))))
