# -*- coding: utf-8 -*-
"""把 fe_theme.css 同步进各篇已生成的 fe_*.css。

前端现在每篇的 css 是「主题 + 组件 + 本篇专属」合并而成，
主题单独放在 tools/fe_theme.css 里方便调。
改完主题后跑这个脚本同步 —— 不用重跑整套生成流程
（重跑会覆盖掉已经改成数据驱动的 .html）。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
AS = os.path.join(REPO, "SharingGroup", "tutorials", "assets")
THEME = os.path.join(REPO, "tools", "fe_theme.css")

HEAD = re.compile(r'^/\* ====.*?==== \*/\s*', re.S)
THEME_MARK = "/* @@FE-THEME-START@@ */"
THEME_END = "/* @@FE-THEME-END@@ */"


def main():
    theme = io.open(THEME, encoding="utf-8").read().strip()
    n = 0
    for f in sorted(os.listdir(AS)):
        if not f.startswith("fe_") or not f.endswith(".css"):
            continue
        p = os.path.join(AS, f)
        t = io.open(p, encoding="utf-8").read()

        head = ""
        m = HEAD.match(t)
        if m:
            head, t = m.group(0), t[m.end():]

        # 去掉上一次同步进去的主题段
        if THEME_MARK in t:
            a = t.index(THEME_MARK)
            b = t.index(THEME_END) + len(THEME_END)
            t = (t[:a] + t[b:]).strip()

        out = head + THEME_MARK + "\n" + theme + "\n" + THEME_END + "\n\n" + t.strip() + "\n"
        io.open(p, "w", encoding="utf-8", newline="\n").write(out)
        n += 1
        print("  ✔ %-18s %6d 字符" % (f, len(out)))
    print("\n  同步 %d 篇" % n)


if __name__ == "__main__":
    main()
