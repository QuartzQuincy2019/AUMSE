# -*- coding: utf-8 -*-
"""核对首页语言标注与教程页徽章一致 —— 支持一篇多个语言。

三处都要一致
    ① 教程页自己的 .lang 徽章（可能多个，保序）
    ② 首页 noscript 兜底列表
    ③ 首页卡片（JS 渲染）—— 数据在 window.__HOME__ 的 kinds 里

期望值来自 series_data.LANG_OF（列表），不手写。

为什么要管「多个」
    FE-09 现在同时是 Qt 和 JS。原来的判定一律假设「一篇 1 个徽章」，
    多处会漏判或误判，所以这里全部改成**序列**比对。
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import LANG_OF  # noqa: E402

NO_BADGE = {fn for fn, v in LANG_OF.items() if not v}

# 两种写法都要认：文档页 class="lang xx"、FE 页 class=\"lang xx\"
BADGE = re.compile(r'<span class=\\?"lang ([a-z]+)\\?">([^<]*)')

# ---- 1. 教程页各自的徽章（序列）----
page_lang = {}
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    hits = [(m.group(2), m.group(1)) for m in BADGE.finditer(t)]
    if hits:
        page_lang[f] = hits

# ---- 2. 首页 noscript 兜底列表 ----
home = io.open(os.path.join(R, "index.html"), encoding="utf-8").read()
ns = re.search(r"<noscript>(.*?)</noscript>", home, re.S).group(1)
home_lang = {}
# 一行里可能有好几个徽章 span，所以先按 <li> 切开再取该行的全部徽章
for li in re.findall(r"<li>.*?</li>", ns, re.S):
    m = re.search(r'<a href="SharingGroup/tutorials/([^"]+)"', li)
    if not m:
        continue
    names = re.findall(r'<span style="[^"]*(?:background|background-image):'
                       r'[^"]*">([^<]+)</span>', li)
    if names:
        home_lang[m.group(1)] = names

bad = 0
print("  教程页有徽章 %d 篇，首页兜底列表 %d 条"
      % (len(page_lang), len(home_lang)))
print()

for f in sorted(page_lang):
    want = [n for n, _ in page_lang[f]]
    got = home_lang.get(f)
    if got is None:
        bad += 1
        print("  !! %-34s 首页兜底列表里没有这一条" % f)
    elif got != want:
        bad += 1
        print("  !! %-34s 教程页=%-12s 首页=%s"
              % (f, " ".join(want), " ".join(got)))

for f in sorted(set(home_lang) - set(page_lang)):
    if f in NO_BADGE:      # T 系列本来就无徽章，首页也不给，正常
        continue
    bad += 1
    print("  !! %-34s 首页有徽章，教程页没有（%s）"
          % (f, " ".join(home_lang[f])))

for f in sorted(set(page_lang) - set(home_lang)):
    bad += 1
    print("  !! %-34s 教程页有徽章，首页兜底列表里没有" % f)

# ---- 3. 首页卡片（JS 渲染）----
m = re.search(r"window\.__HOME__ = (\{.*?\});", home, re.S)
if not m:
    print("  !! 找不到 window.__HOME__")
    bad += 1
else:
    data = json.loads(m.group(1))
    langs = data.get("langs", {})
    card_bad = 0
    n_card = 0
    for g in data["groups"]:
        for c in g["cards"]:
            n_card += 1
            fn = c["file"]
            # kinds 是 [[名, cls], …]；老数据只有单个 kind 字符串
            kinds = c.get("kinds") or []
            names = [k[0] for k in kinds]
            if not kinds and c.get("kind"):
                names = [c["kind"]]

            if fn in NO_BADGE:
                if names:
                    card_bad += 1
                    print("  !! %-34s 卡片不该有语言，却是 %s"
                          % (fn, " ".join(names)))
                continue
            if not names:
                card_bad += 1
                print("  !! %-34s 卡片没有语言" % fn)
                continue
            for nm in names:
                if nm not in langs:
                    card_bad += 1
                    print("  !! %-34s 语言 %s 在 langs 表里没有 class"
                          % (fn, nm))
            page_names = [n for n, _ in page_lang.get(fn, [])]
            if names != page_names:
                card_bad += 1
                print("  !! %-34s 教程页=%-12s 卡片=%s"
                      % (fn, " ".join(page_names) or "无", " ".join(names)))

    print("  首页卡片 %d 张，langs 表 %d 种语言"
          % (n_card, len(langs)))
    if card_bad:
        bad += card_bad
        print("  卡片语言不一致 %d 处" % card_bad)
    else:
        print("  卡片语言一致 OK")

print()
print("  不一致 %d 处 %s" % (bad, "OK" if bad == 0 else "FAIL"))
