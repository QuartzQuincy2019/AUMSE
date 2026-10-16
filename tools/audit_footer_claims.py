# -*- coding: utf-8 -*-
"""找出全文里所有「声称实际编译/运行核对」的句子（不只是 footer）。

为什么要查全文
    这类声明不只写在 footer 里 —— 正文的「开始之前」卡片、小节说明里
    也常有（例如 M04 的「本讲的代码与输出全部经过实际编译运行核对」）。
    只改 footer 会留下不一致的说法。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

KEY = re.compile(r'(实际编译|实际运行核对|实际验证|编译运行核对|经过实际|'
                 r'本机[^。<]{0,40}核对|实际编译产生)')

total = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    hits = []
    for m in KEY.finditer(t):
        seg = re.sub(r'\s+', ' ', t[max(0, m.start() - 70):m.end() + 50])
        seg = re.sub(r'<[^>]+>', '', seg)
        hits.append(seg.strip())
    if hits:
        total += len(hits)
        print("=" * 78)
        print("%s  （%d 处）" % (f, len(hits)))
        for h in hits:
            print("   …%s…" % h)
print()
print("=" * 78)
print("合计 %d 处" % total)
