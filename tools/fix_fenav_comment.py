# -*- coding: utf-8 -*-
"""把 fe-dark.css 里那段 series-nav 注释的因果关系写准确，并复查明暗两模式。

原注释说「浅色主题给它们留了 var(--sfc-2) 之类的浅底」—— 不准确：
真实原因是 fe_base.css 给 .series-nav a 定死了
background:rgba(255,255,255,.82)，而 FE 没有暗色覆盖。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets\fe-dark.css"
c = io.open(P, encoding="utf-8").read()

OLD = ("/* 问题：div.series-nav 里的 a（非 .cur）在暗色模式下背景是白的。\n"
       "     浅色主题给它们留了 var(--sfc-2) 之类的浅底，fe-dark.css 没有覆盖到，\n"
       "     于是浅色值漏了过来。这里把非当前项统一压成深底。 */")

NEW = ("/* 用户报的问题：div.series-nav 里的 a（非 .cur）在暗色下背景是白的。\n"
       "     真实原因：fe_base.css 给 .series-nav a 定死了\n"
       "       background:rgba(255,255,255,.82)   ← 写死的白底\n"
       "     其它系列各有一套 body[data-series=\"X\"] 的暗色规则，\n"
       "     只有 FE 的外观自成体系、没走那套生成，于是白底漏到了暗色模式。\n"
       "     这里把非当前项统一压成深底。\n"
       "     ⚠ 本块必须在 @media (prefers-color-scheme: dark) 里 ——\n"
       "       亮色下 .series-nav a 就该是那个白底，不能一起压深。 */")

if OLD in c:
    c = c.replace(OLD, NEW, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(c)
    print("  已把注释里的因果关系写准确")
elif "真实原因" in c:
    print("  注释已是新内容")
else:
    print("  !! 未匹配，原文如下：")
    i = c.find("系列导航：暗色下的链接底色")
    print(repr(c[i:i + 300]))
