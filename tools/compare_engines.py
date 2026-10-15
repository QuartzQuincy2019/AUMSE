"""Compare the two vertical engines' rendering pixel by pixel.

Both engines are supposed to produce the SAME Mongolian glyphs (one via
writing-mode, one via rotate(90deg)). Any large difference means one of them
is shaping/orienting differently.
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
    pos, idat = 8, b""
    w = h = nch = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        ch = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bitd, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", ch)
            nch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
            assert bitd == 8 and inter == 0, (bitd, inter)
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
        m[i] = 1 if (px[o] + px[o + 1] + px[o + 2]) > 330 else 0
    return w, h, m


pa = os.path.join(REP, "_cmp_a.png")
pb = os.path.join(REP, "_cmp_b.png")
for f in (pa, pb):
    if not os.path.exists(f):
        print("missing", f); sys.exit(2)

wa, ha, a = ink(pa)
wb, hb, b = ink(pb)
print(f"A (writing-mode)  : {wa}x{ha}  ink={sum(a)}")
print(f"B (rotate 90deg)  : {wb}x{hb}  ink={sum(b)}")

if (wa, ha) != (wb, hb):
    print("尺寸不同，无法逐像素比较")
    sys.exit(1)

n = sum(1 for i in range(wa * ha) if a[i] != b[i])
inter = sum(1 for i in range(wa * ha) if a[i] and b[i])
union = sum(1 for i in range(wa * ha) if a[i] or b[i])
print(f"差异像素 = {n} / {wa*ha}  ({100.0*n/(wa*ha):.3f}%)")
print(f"IoU = {inter/union:.4f}" if union else "IoU n/a")


def bbox(m, w, h):
    minx, maxx, miny, maxy = w, -1, h, -1
    for i in range(w * h):
        if m[i]:
            x, y = i % w, i // w
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
    return minx, miny, maxx, maxy


ba, bb = bbox(a, wa, ha), bbox(b, wb, hb)
print(f"A 墨迹包围盒 = x[{ba[0]}..{ba[2]}] y[{ba[1]}..{ba[3]}]  "
      f"尺寸 {ba[2]-ba[0]+1}x{ba[3]-ba[1]+1}")
print(f"B 墨迹包围盒 = x[{bb[0]}..{bb[2]}] y[{bb[1]}..{bb[3]}]  "
      f"尺寸 {bb[2]-bb[0]+1}x{bb[3]-bb[1]+1}")
dx, dy = bb[0] - ba[0], bb[1] - ba[1]
print(f"位移 dx={dx} dy={dy}")

# 按该位移把 B 平移回去再比一次 —— 若差异归零，说明两者字形完全相同
if (ba[2] - ba[0], ba[3] - ba[1]) == (bb[2] - bb[0], bb[3] - bb[1]):
    shift_ok = True
    for i in range(wa * ha):
        x, y = i % wa, i // wa
        sx, sy = x + dx, y + dy
        if 0 <= sx < wa and 0 <= sy < ha:
            if a[i] != b[sy * wa + sx]:
                shift_ok = False
                break
        elif a[i]:
            shift_ok = False
            break
    print()
    if shift_ok:
        print("结论：两者墨迹包围盒尺寸相同，且按 dx,dy 平移后逐像素完全一致 ——")
        print("      两种引擎渲染出的字形是同一个，只是起点偏移了几像素。")
        sys.exit(0)
    else:
        print("结论：平移后仍有差异 —— 字形本身不同。")
        sys.exit(1)

print()
print("结论：包围盒尺寸不同 —— 字形或取向确有差异。")
sys.exit(1)
