"""Measure whether UME.html's feature toggle changes Mongolian shaping.

Compares two browser screenshots of the SAME text, one with
font-feature-settings enabled and one with them disabled. Canvas cannot be used
for this: Chromium never implemented ctx.fontFeatureSettings, so only the real
DOM/CSS rendering path is meaningful.
"""
import sys
import zlib
import struct
import os
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "report")


def read_png(path):
    """Minimal PNG reader (8-bit RGB/RGBA, non-interlaced)."""
    with open(path, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8
    idat = b""
    w = h = bitd = ctype = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, bitd, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", chunk)
            assert bitd == 8 and inter == 0, f"unsupported PNG {bitd}bpp interlace={inter}"
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    nch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    stride = w * nch
    out = bytearray(h * stride)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if ft == 1:      # Sub
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 0xFF
        elif ft == 2:    # Up
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:    # Average
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ft == 4:    # Paeth
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


def ink_map(path):
    w, h, nch, px = read_png(path)
    # 前景=暗像素；背景是深色主题 #12151b 与面板 #171a21，
    # 所以用「明显亮于背景」判定为文字
    ink = bytearray(w * h)
    for i in range(w * h):
        o = i * nch
        r, g, b = px[o], px[o + 1], px[o + 2]
        ink[i] = 1 if (r + g + b) > 330 else 0
    return w, h, ink


def main():
    on = os.path.join(REP, "_feat_on.png")
    off = os.path.join(REP, "_feat_off.png")
    for f in (on, off):
        if not os.path.exists(f):
            print("missing:", f); return 1

    w1, h1, a = ink_map(on)
    w2, h2, b = ink_map(off)
    print(f"on : {w1}x{h1}   off: {w2}x{h2}")
    if (w1, h1) != (w2, h2):
        print("size mismatch"); return 1

    diff = sum(1 for i in range(w1 * h1) if a[i] != b[i])
    ink_on, ink_off = sum(a), sum(b)
    inter = sum(1 for i in range(w1 * h1) if a[i] and b[i])
    union = sum(1 for i in range(w1 * h1) if a[i] or b[i])
    print(f"ink pixels  ON={ink_on}  OFF={ink_off}")
    print(f"pixels differing = {diff}")
    print(f"IoU = {inter/union:.4f}" if union else "IoU n/a")

    # 差异的边界框，确认差异集中在文本列上
    if diff:
        minx, maxx, miny, maxy = w1, -1, h1, -1
        for i in range(w1 * h1):
            if a[i] != b[i]:
                x, y = i % w1, i // w1
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
        print(f"diff bbox = x[{minx}..{maxx}] y[{miny}..{maxy}]")

    print()
    if diff > 0:
        print("RESULT: 连字特性开关 确实改变成形结果（DOM+CSS 渲染路径）。")
        return 0
    print("RESULT: 两态像素完全一致 —— 开关无效，或该字体/浏览器组合未受影响。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
