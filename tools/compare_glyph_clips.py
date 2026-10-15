"""Compare clipped first-glyph images to decide whether positional features
   (init/medi/fina/isol) are actually applied by the browser.

   If the browser honours the font's contextual shaping, MA rendered
   word-initially must differ from MA rendered in isolation.
"""
import sys
import os
import zlib
import struct

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "report")


def read_png(path):
    with open(path, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat = 8, b""
    w = h = nch = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        ch = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bitd, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", ch)
            nch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
            assert bitd == 8 and inter == 0
        elif typ == b"IDAT":
            idat += ch
        elif typ == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * nch
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if ft == 1:
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 0xFF
        elif ft == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                b = prev[i]
                c = prev[i - nch] if i >= nch else 0
                pp = a + b - c
                pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return w, h, nch, bytes(out)


def ink(path):
    w, h, nch, px = read_png(path)
    m = bytearray(w * h)
    for i in range(w * h):
        o = i * nch
        m[i] = 1 if (px[o] + px[o + 1] + px[o + 2]) < 384 else 0
    return w, h, m


def diff(a, b):
    n = sum(1 for i in range(len(a)) if a[i] != b[i])
    inter = sum(1 for i in range(len(a)) if a[i] and b[i])
    union = sum(1 for i in range(len(a)) if a[i] or b[i])
    return n, (inter / union if union else 0.0)


labels = {"ctx": "MA 词首 (init)", "iso": "MA 孤立 (init._isol)", "mid": "MA 词中 (medi)"}
imgs = {}
for k in labels:
    p = os.path.join(REP, "_clip_%s.png" % k)
    if not os.path.exists(p):
        print("missing", p); sys.exit(2)
    imgs[k] = ink(p)

print("裁剪尺寸:")
for k in labels:
    print("  %-22s %dx%d  ink=%d" % (labels[k], imgs[k][0], imgs[k][1], sum(imgs[k][2])))

print()
print("逐像素比较（HarfBuzz 地面真相：三个上下文应为三个不同字形）:")
pairs = [("ctx", "iso"), ("ctx", "mid"), ("iso", "mid")]
allzero = True
for x, y in pairs:
    if imgs[x][0] != imgs[y][0] or imgs[x][1] != imgs[y][1]:
        print("  %-26s vs %-26s 尺寸不同，无法逐像素比较" % (labels[x], labels[y]))
        allzero = False
        continue
    n, iou = diff(imgs[x][2], imgs[y][2])
    if n: allzero = False
    print("  %-22s vs %-22s  differ=%-6d IoU=%.4f  %s"
          % (labels[x], labels[y], n, iou, "不同" if n else "完全相同"))

print()
if allzero:
    print("结论: 浏览器渲染的三种上下文像素完全一致 ——")
    print("      位置形位特性 init/medi/fina/isol 未被应用（与 HarfBuzz 结果矛盾）。")
    sys.exit(1)
else:
    print("结论: 上下文确实改变了字形 —— 位置形位特性生效。")
    sys.exit(0)
