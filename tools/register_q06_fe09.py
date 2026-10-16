# -*- coding: utf-8 -*-
"""登记 Q06，并把 FE-09 改成重点项目。

涉及的地方（这些「只加了一半」的漂移踩过两次，一并做完）：
    series_data.py        首页卡片 / 分组计数   ← Q06 新增 + FE-09 星标
    series-common.js      PAGES（页尾「本系列」/「全部系列」）← Q06 新增
    fe-data.js            SERIES_FILES（「全部系列」篇数与跳转）← Q06 新增
    add_lang_badges.py    语言徽章映射 ← Q06 新增
    各 FE 页的 __FE_PAGE__.series ← FE-09 的 star 由 build 时写入，不用改这里
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

Q6_FN, Q6_NUM, Q6_TITLE = "q06-components.html", "Q06", "组件化编程与解耦合"
Q6_DESC = "什么叫耦合、高耦合的代价、组件化的三条准则"


def insert_after(lines, needle, newline):
    for i, l in enumerate(lines):
        if needle in l:
            j = i
            while j < len(lines) and not re.search(r'[\)\}],\s*$', lines[j]):
                j += 1
            return lines[:j + 1] + [newline] + lines[j + 1:]
    return None


def main():
    dry = "--dry" in sys.argv
    n = 0

    # ---------- 1. series_data.py：加 Q06 ----------
    p = os.path.join(TOOLS, "series_data.py")
    t = io.open(p, encoding="utf-8").read()
    if Q6_FN in t:
        print("  1. series_data.py 已有 Q06")
    else:
        new = ('    ("%s",      "%s",\n'
               '     "Q", "%s", "%s", "%s", True),'
               % (Q6_FN, Q6_FN, Q6_NUM, Q6_TITLE, Q6_DESC))
        out = insert_after(t.split("\n"), '"q05-open-closed.html",', new)
        if out is None:
            print("  !! 1. series_data.py 找不到 q05 锚点")
        else:
            print("  1. series_data.py 追加 Q06")
            n += 1
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write("\n".join(out))

    # ---------- 2. series-common.js：加 Q06 ----------
    p = os.path.join(A, "series-common.js")
    t = io.open(p, encoding="utf-8").read()
    if Q6_FN in t:
        print("  2. series-common.js 已有 Q06")
    else:
        new = "    { f: '%s', n: '%s', t: '%s', s: 'Q' }," % (Q6_FN, Q6_NUM, Q6_TITLE)
        out = insert_after(t.split("\n"), "f: 'q05-open-closed.html'", new)
        if out is None:
            print("  !! 2. series-common.js 找不到 q05 锚点")
        else:
            print("  2. series-common.js 追加 Q06")
            n += 1
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write("\n".join(out))

    # ---------- 3. fe-data.js 的 SERIES_FILES ----------
    p = os.path.join(A, "fe-data.js")
    t = io.open(p, encoding="utf-8").read()
    if "'%s'" % Q6_FN in t:
        print("  3. fe-data.js 已有 Q06")
    else:
        old = "'q05-open-closed.html',"
        if old not in t:
            print("  !! 3. fe-data.js 找不到 q05 锚点")
        else:
            t = t.replace(old, old + "'%s'," % Q6_FN, 1)
            print("  3. fe-data.js SERIES_FILES 追加 Q06")
            n += 1
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t)

    # ---------- 4. add_lang_badges.py ----------
    p = os.path.join(TOOLS, "add_lang_badges.py")
    t = io.open(p, encoding="utf-8").read()
    if Q6_FN in t:
        print("  4. add_lang_badges.py 已有 Q06")
    else:
        old = '    "%s": ("C++", "cpp"),' % "q05-open-closed.html"
        if old not in t:
            print("  !! 4. add_lang_badges.py 找不到 q05 锚点")
        else:
            t = t.replace(old, old + '\n    "%s": ("C++", "cpp"),' % Q6_FN, 1)
            print("  4. add_lang_badges.py 追加 Q06")
            n += 1
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t)

    # ---------- 5. FE-09 标为星标 ----------
    # fe-data.js 的 SERIES_FILES 只管文件名，星标在 series_data 的 FE_PAGES 与
    # 各页 __FE_PAGE__.series 里。series_data 那条要改 False→True。
    p = os.path.join(TOOLS, "series_data.py")
    t = io.open(p, encoding="utf-8").read()
    old = ('("fe-09.html",     "FE-09",     "DOM 操作基础",'
           '           "getElementById / createElement / append；DOM 树与 Qt addWidget 的对照", "JS", False),')
    if old in t:
        t = t.replace(old, old.replace('"JS", False)', '"JS", True)'), 1)
        print("  5. series_data.py：FE-09 标为星标（重点项目）")
        n += 1
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t)
    elif 'q06-components.html' in t and '"JS", True)' in t:
        print("  5. FE-09 已是星标")
    else:
        print("  !! 5. series_data.py 里 fe-09 那行未匹配")

    print()
    print("  共改 %d 处  %s" % (n, "[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
