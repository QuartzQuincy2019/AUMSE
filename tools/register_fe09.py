# -*- coding: utf-8 -*-
"""把 FE-09 登记进所有需要它的地方。

涉及四处：
  1. tools/series_data.py            FE_PAGES（首页卡片 + 分组计数）
  2. assets/js/series-common.js         PAGES（非 FE 页尾的「本系列」用不到 FE，
                                     但「全部系列」的 FE 计数要用）
  3. assets/js/fe-data.js               SERIES_FILES（「全部系列」篇数与跳转目标）
  4. 各 FE 页的 __FE_PAGE__.series     「本系列」小目录

第 4 项单独由 add_fe08_to_series.py 的同类逻辑处理；
这里统一做，避免又出现「新篇目只加进了一半地方」的漂移
（上一轮 R 按钮点不动就是这类问题）。

用法：
    python register_fe09.py --dry
    python register_fe09.py
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(T, "assets")
TOOLS = os.path.join(R, "tools")

NUM, FN = "FE-09", "fe-09.html"
TITLE = "DOM 操作基础"
DESC = ("getElementById / createElement / append；DOM 树与 Qt addWidget 的对照",
        "getElementById / createElement / append、DOM 树、与 Qt addWidget 的对照")

# 页面数据里 series 条目的格式（与既有各页一致）
SERIES_ENTRY = ('{"file":"fe-09.html","num":"FE-09",'
                '"title":"DOM 操作基础","star":false}')


def bracket_span(s, start):
    depth = 0
    i = start
    while i < len(s):
        if s[i] == "[":
            depth += 1
        elif s[i] == "]":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def main():
    dry = "--dry" in sys.argv
    n_ok = 0

    # ---------- 1. series_data.py ----------
    p = os.path.join(TOOLS, "series_data.py")
    t = io.open(p, encoding="utf-8").read()
    if FN in t:
        print("  1. series_data.py 已有 FE-09")
    else:
        # fe-08 那条是**单行**结尾的：
        #   ("fe-08.html", …, "JS", False),\n]
        # 第一版照着别的条目写成「"…",\s*False\),\n」，多要求了一个引号，
        # 而这里 False 前面是 "JS" 之后的逗号，于是匹配不上。
        m = re.search(r'(?m)^(\s*\("fe-08\.html".*?\n)', t)
        if not m:
            print("  !! 1. series_data.py 找不到 fe-08 条目")
        else:
            ind = re.match(r"\s*", m.group(1)).group(0)
            add = (ind + '("%s",     "%s",     "%s",\n'
                   % (FN, NUM, TITLE) + ind +
                   ' "%s", "JS", False),\n' % DESC[0])
            t2 = t[:m.end()] + add + t[m.end():]
            print("  1. series_data.py  追加 FE-09")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t2)
            n_ok += 1

    # ---------- 2. series-common.js 的 PAGES ----------
    p = os.path.join(A, "series-common.js")
    t = io.open(p, encoding="utf-8").read()
    if "fe-09.html" in t:
        print("  2. series-common.js 已有 FE-09")
    else:
        m = re.search(r"(?m)^(\s*\{ f: 'fe-08\.html'[^\n]*)$", t)
        if not m:
            print("  !! 2. series-common.js 找不到 fe-08 那行")
        else:
            ind = re.match(r"\s*", m.group(1)).group(0)
            add = ("\n" + ind +
                   "{ f: 'fe-09.html', n: 'FE-09', t: 'DOM 操作基础', s: 'FE' },")
            t2 = t[:m.end()] + add + t[m.end():]
            print("  2. series-common.js  追加 FE-09")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t2)
            n_ok += 1

    # ---------- 3. fe-data.js 的 SERIES_FILES ----------
    p = os.path.join(A, "fe-data.js")
    t = io.open(p, encoding="utf-8").read()
    if "'fe-09.html'" in t:
        print("  3. fe-data.js 已有 FE-09")
    else:
        old = "'fe-07.html','fe-08.html'"
        if old in t:
            t2 = t.replace(old, "'fe-07.html','fe-08.html','fe-09.html'", 1)
            print("  3. fe-data.js  SERIES_FILES 追加 FE-09")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t2)
            n_ok += 1
        else:
            print("  !! 3. fe-data.js 找不到 SERIES_FILES 的 anchor")

    # ---------- 4. 各 FE 页的 __FE_PAGE__.series ----------
    pages = 0
    for f in sorted(os.listdir(T)):
        if not re.match(r"^fe-0[1-9](-F\d+)?\.html$", f):
            continue
        fp = os.path.join(T, f)
        s = io.open(fp, encoding="utf-8").read()
        m = re.search(r'"series"\s*:\s*\[', s)
        if not m:
            print("  !! 4. %s 无 series" % f)
            continue
        b = s.index("[", m.start())
        e = bracket_span(s, b)
        seg = s[b:e + 1]
        if '"fe-09.html"' in seg:
            continue
        newseg = seg[:-1].rstrip() + "," + SERIES_ENTRY + "]"
        n1 = len(re.findall(r'"file"\s*:', seg))
        n2 = len(re.findall(r'"file"\s*:', newseg))
        if n2 != n1 + 1:
            print("  !! 4. %s 条数不对 %d → %d" % (f, n1, n2))
            continue
        if not dry:
            io.open(fp, "w", encoding="utf-8", newline="").write(
                s[:b] + newseg + s[e + 1:])
        pages += 1
        print("  4. %-18s series %d → %d 条" % (f, n1, n2))
    if not pages:
        print("  4. 各 FE 页的 series 都已有 FE-09")

    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
