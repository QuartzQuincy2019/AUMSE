# -*- coding: utf-8 -*-
"""清掉全站残留的旧编号（08-F0x / 08-E0x / 09-F04）。

用户指出 M08/M09 的「下一讲预告」不符合实际项目，已改。
顺手全站扫了一遍，发现同一类问题还有 20 处 —— 都是**旧编号**没跟上：

    08-F01 → F01        08-F02 → F02        08-F03 → F03
    08-E01 → E01        08-E02 → E02
    09-F04 → T02        （Unicode 那篇现在是 T02；
                          旧写法还标着「File」系列，双错 —— 它属于 Theory）

出现位置：e01 / e02 / f01 / f02 / f03 / m07 / m08 / t02 的正文与页脚。

注意两处要顺句子改，不能只换编号：
    m07  「第 08-F03 讲会专门讲」   → 「F03 篇会专门讲」
    m08  「那是第 09-F04 讲的内容」 → 「那是 T02 那篇的内容」
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# 先处理要顺句子的两处（必须在批量替换之前）
SENTENCE = [
    ("m07.html", "第 08-F03 讲会专门讲", "F03 篇会专门讲"),
    ("m08.html", "那是第 09-F04 讲的内容", "那是 T02 那篇的内容"),
    ("m08.html", "第 09-F04 讲的内容", "T02 那篇的内容"),
]

for fn, old, new in SENTENCE:
    p = os.path.join(T, fn)
    if not os.path.exists(p):
        continue
    t = io.open(p, encoding="utf-8").read()
    if old in t:
        t = t.replace(old, new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("  %-10s 顺句子：%s → %s" % (fn, old, new))

# 再批量换编号
MAP = [
    (r"09-F04（File）", "T02（Theory）"),   # t02 页脚，系列也标错了
    ("09-F04", "T02"),
    ("08-F01", "F01"),
    ("08-F02", "F02"),
    ("08-F03", "F03"),
    ("08-E01", "E01"),
    ("08-E02", "E02"),
]

total = 0
for fn in sorted(os.listdir(T)):
    if not fn.endswith(".html"):
        continue
    p = os.path.join(T, fn)
    t = io.open(p, encoding="utf-8").read()
    orig = t
    n = 0
    for old, new in MAP:
        c = t.count(old)
        if c:
            t = t.replace(old, new)
            n += c
    if t != orig:
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        total += n
        print("  %-10s 换旧编号 %d 处" % (fn, n))

print()
print("  合计 %d 处" % total)

# ---------------- 自检 ----------------
print()
pat = re.compile(r"(?:09|08|10)-(?:F0\d|E0\d|A0\d)")
left = 0
for fn in sorted(os.listdir(T)):
    if not fn.endswith(".html"):
        continue
    t = io.open(os.path.join(T, fn), encoding="utf-8").read()
    hits = pat.findall(t)
    if hits:
        left += len(hits)
        print("  !! %-10s 仍有 %s" % (fn, hits))
print("  旧编号残留：%d 处 %s" % (left, "OK" if left == 0 else "FAIL"))
