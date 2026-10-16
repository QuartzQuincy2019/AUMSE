# -*- coding: utf-8 -*-
"""核对首页语言标注与教程页语言徽章是否一致。

首页的卡片（JS 渲染）与 noscript 兜底列表，两处的语言都必须
与**该篇教程页自己的 .lang 徽章**相同 —— 否则同一个系列在两个地方
显示不同的语言，读者会以为看错了。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")

# ---- 1. 教程页各自的徽章 ----
page_lang = {}
for f in sorted(os.listdir(T)):
    if not f.endswith(".html"):
        continue
    t = io.open(os.path.join(T, f), encoding="utf-8").read()
    m = re.search(r'class=\\?"lang ([a-z]+)\\?"', t)
    if m:
        page_lang[f] = m.group(1)

CLS2LANG = {"html": "HTML", "css": "CSS", "js": "JS",
            "cpp": "C++", "c": "C", "sh": "Shell", "py": "Python"}

# ---- 2. 首页 noscript 列表 ----
home = io.open(os.path.join(R, "index.html"), encoding="utf-8").read()
ns = re.search(r'<noscript>(.*?)</noscript>', home, re.S).group(1)
home_lang = {}
for m in re.finditer(r'<li><span style="[^"]*background:(#[0-9a-f]{6})[^"]*">'
                     r'([^<]+)</span><a href="SharingGroup/tutorials/([^"]+)"',
                     ns):
    home_lang[m.group(3)] = m.group(2)

bad = 0
print("  教程页徽章 %d 篇，首页兜底列表 %d 条" % (len(page_lang), len(home_lang)))
print()
for f in sorted(page_lang):
    want = CLS2LANG[page_lang[f]]
    got = home_lang.get(f)
    if got is None:
        bad += 1
        print("  !! %-34s 首页兜底列表里没有这一条" % f)
    elif got != want:
        bad += 1
        print("  !! %-34s 教程页=%-6s 首页=%s" % (f, want, got))
for f in sorted(set(home_lang) - set(page_lang)):
    bad += 1
    print("  !! %-34s 首页有，教程页没有徽章（%s）" % (f, home_lang[f]))

print()
print("  不一致 %d 处 %s" % (bad, "OK" if bad == 0 else "FAIL"))
