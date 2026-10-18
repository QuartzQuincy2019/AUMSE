# -*- coding: utf-8 -*-
"""核对语言徽章：一篇可以有**多个**，逐个比对。

为什么重写
    原来的判定建立在「一篇恰好 1 个徽章」上：
        if len(hits) != 1: 异常
    而 FE-09 现在有 2 个（Qt + JS）—— 那不是异常，是新需求。
    所以改成「**序列**比对」：页面上找到的徽章顺序必须与期望的完全一致。

期望值仍然来自 series_data.LANG_OF（列表），不手写。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
A = os.path.join(T, "assets")

# ---- assets 已按类型分到 css/ img/ js/，这里统一兜底找 ----
def resolve(name):
    """先找 assets/<name>，再找 assets/{css,js,img}/<name>。"""
    p = os.path.join(A, name)
    if os.path.exists(p):
        return p
    for sub in ("css", "js", "img", "fonts"):
        q = os.path.join(A, sub, name)
        if os.path.exists(q):
            return q
    return p

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import LANG_OF  # noqa: E402

# 文件名 → 期望的 [(显示名, class), …]；空列表 = 这篇不该有徽章
EXPECT = dict(LANG_OF)

# 两种写法都要认：文档页 class="lang xx"、FE 页 class=\"lang xx\"
BADGE = re.compile(r'<span class=\\?"lang ([a-z]+)\\?">([^<]*)')


def badges(html):
    return [(m.group(2), m.group(1)) for m in BADGE.finditer(html)]


bad = 0
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    if f not in EXPECT:
        print("  %-34s （LANG_OF 里没有，跳过）" % f)
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    got = badges(t)
    want = EXPECT[f]

    if not want:
        if got:
            bad += 1
            print("  !! %-32s 不应有徽章，却有 %d 个 %s"
                  % (f, len(got), [n for n, _ in got]))
        else:
            print("  OK %-32s （无徽章，符合预期）" % f)
        continue

    got_cls = [c for _, c in got]
    want_cls = [c for _, c in want]
    if got_cls == want_cls:
        print("  OK %-32s %s" % (f, " ".join(n for n, _ in got)))
    else:
        bad += 1
        print("  !! %-32s 徽章 %-14s 期望 %s"
              % (f, " ".join(n for n, _ in got) or "无",
                 " ".join(n for n, _ in want)))

print()
print("  异常 %d 篇 %s" % (bad, "OK" if bad == 0 else "FAIL"))

# 样式表侧：每个出现过的 class 都要有规则
print()
need = sorted({c for v in EXPECT.values() for _, c in v})
for fn in ("tg_L.css", "tg_D.css"):
    c = io.open(resolve(fn), encoding="utf-8").read()
    squashed = c.replace(" ", "")
    missing = [k for k in need if (".lang.%s{" % k) not in squashed]
    print("  %-10s 需 %d 条规则，缺: %s"
          % (fn, len(need), missing if missing else "无 OK"))
