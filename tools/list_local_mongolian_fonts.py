"""列出本机所有含蒙文字形的字体族，并算出光学缩放系数。

缩放口径：以项目内置 Noto 的「U+1820 A 的墨迹高度 / upem」为 1.0，
其余字体按同一指标做等墨迹换算 —— scale = REF / inkH(font)。
"""
import glob
import os

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTO = os.path.join(PROJECT_DIR, 'font', 'NotoSansMongolian-Regular.ttf')
DIRS = [r'C:\Windows\Fonts',
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts')]


def ink(path, cp=0x1820):
    font = TTFont(path, lazy=True)
    cmap = font.getBestCmap()
    if not cmap or cp not in cmap:
        return None
    upem = font['head'].unitsPerEm
    gs = font.getGlyphSet()
    pen = BoundsPen(gs)
    gs[cmap[cp]].draw(pen)
    if not pen.bounds:
        return None
    return (pen.bounds[3] - pen.bounds[1]) / upem


def scan():
    ref = ink(NOTO)
    seen = {}
    for d in DIRS:
        for p in glob.glob(os.path.join(d, '*.ttf')):
            try:
                font = TTFont(p, lazy=True)
                cmap = font.getBestCmap()
            except Exception:
                continue
            if not cmap:
                continue
            if sum(1 for c in cmap if 0x1800 <= c <= 0x18AF) < 50:
                continue
            fam = font['name'].getDebugName(1)
            sub = font['name'].getDebugName(2) or ''
            if not fam or (sub and sub != 'Regular'):
                continue
            seen.setdefault(fam, []).append(
                (p, font['name'].getDebugName(5) or '', ink(p)))
    rows = []
    for fam, v in seen.items():
        p, ver, h = max(v, key=lambda x: x[1])
        rows.append((fam, ver, h, len(v)))
    rows.sort(key=lambda r: r[0].lower())
    return ref, rows


def main():
    ref, rows = scan()
    tig = [r for r in rows if 'StdEx' not in r[0]]
    std = [r for r in rows if 'StdEx' in r[0]]
    print('# REF inkH(A) of project Noto = %.4f; families = %d (Tig %d / StdEx %d)'
          % (ref, len(rows), len(tig), len(std)))
    for title, group in (('TIG', tig), ('STDEX', std)):
        print('## %s' % title)
        for fam, ver, h, n in group:
            scale = round(ref / h, 2) if h else 1.0
            print('    { f:%-26s s:%.2f },   // %s%s'
                  % ('"%s",' % fam, scale, (ver or '').split(';')[0][:22],
                     '' if n == 1 else '  (x%d 同名文件)' % n))


if __name__ == '__main__':
    main()
