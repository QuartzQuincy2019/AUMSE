# -*- coding: utf-8 -*-
"""把字体编码为 base64 并写成 JS 模块，供 UME.html 离线内联使用。

为什么需要：file:// 协议下 fetch/XHR 都无法读取本地字体文件
（实测 fetch 抛 TypeError、XHR 抛 NetworkError），
但 <script src> 与 @font-face 可以。
为了在导出 SVG 时用 opentype.js 解析字体轮廓，必须拿到字体字节，
因此把字体 base64 内联进来。
"""
import base64
import hashlib
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "font", "NotoSansMongolian-Regular.ttf")
OUT = os.path.join(ROOT, "web", "vendor", "font-b64.js")

os.makedirs(os.path.dirname(OUT), exist_ok=True)

with open(SRC, "rb") as fh:
    data = fh.read()

b64 = base64.b64encode(data).decode("ascii")
sha = hashlib.sha256(data).hexdigest()[:16]

header = (
    "/* Noto Sans Mongolian Regular 3.103\n"
    "   Copyright 2023 The Noto Project Authors (https://github.com/notofonts/mongolian)\n"
    "   Licensed under the SIL Open Font License, Version 1.1\n"
    "   https://scripts.sil.org/OFL\n"
    "\n"
    "   字体以 base64 内联：file:// 下 fetch/XHR 读不到本地字体文件，\n"
    "   而 SVG 导出需要用 opentype.js 解析字体轮廓，因此必须内联。\n"
    "\n"
    "   由 tools/embed_vendor.py 生成，请勿手改。\n"
    "   sha256(前16位)=%s  size=%d\n"
    "*/\n" % (sha, len(data))
)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(header)
    fh.write('window.UME_FONT_B64 = "%s";\n' % b64)

print("ttf      : %d 字节" % len(data))
print("base64   : %d 字符" % len(b64))
print("输出     : %s (%d 字节)" % (OUT, os.path.getsize(OUT)))
print("sha256   : %s..." % sha)
