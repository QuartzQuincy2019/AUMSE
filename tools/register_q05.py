# -*- coding: utf-8 -*-
"""把 Q05 登记进 series_data.py / series-common.js / add_lang_badges.py。

用「按行找锚点」而不是复杂正则 —— 前两次都栽在正则的多行匹配上
（q04 那条是两行元组，结尾写在第二行）。
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")

FN = "q05-open-closed.html"
NUM, TITLE = "Q05", "开闭原则"


def insert_after(lines, needle, newline):
    """在包含 needle 的那一「条」之后插入 newline。

    条目可能跨两行（series_data 的元组就是），所以：
    找到 needle 后，从该行往下找到第一个以 '),' 或 '},' 结尾的行，
    在它之后插入。
    """
    for i, l in enumerate(lines):
        if needle in l:
            j = i
            while j < len(lines) and not re.search(r'[\)\}],\s*$', lines[j]):
                j += 1
            return lines[:j + 1] + [newline] + lines[j + 1:]
    return None


def main():
    dry = "--dry" in sys.argv

    # ---------- 1. series_data.py ----------
    p = os.path.join(R, "tools", "series_data.py")
    t = io.open(p, encoding="utf-8").read()
    if FN in t:
        print("  1. series_data.py 已有 Q05")
    else:
        lines = t.split("\n")
        new = ('    ("%s",      "%s",\n'
               '     "Q", "%s", "%s", "为什么不能什么都塞进一个类；只给方向不给代码", True),'
               % (FN, FN, NUM, TITLE))
        out = insert_after(lines, '"q04-interfaces.html",', new)
        if out is None:
            print("  !! 1. series_data.py 找不到 q04 锚点")
        else:
            print("  1. series_data.py 追加 Q05")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write("\n".join(out))

    # ---------- 2. series-common.js ----------
    p = os.path.join(T, "assets", "series-common.js")
    t = io.open(p, encoding="utf-8").read()
    if FN in t:
        print("  2. series-common.js 已有 Q05")
    else:
        lines = t.split("\n")
        new = ("    { f: '%s', n: '%s', t: '%s', s: 'Q' }," % (FN, NUM, TITLE))
        out = insert_after(lines, "f: 'q04-interfaces.html'", new)
        if out is None:
            print("  !! 2. series-common.js 找不到 q04 锚点")
        else:
            print("  2. series-common.js 追加 Q05")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write("\n".join(out))

    # ---------- 3. fe-data.js 的 SERIES_FILES ----------
    # 第一版漏了这一处 —— check_series_counts.py 报「Q 现算 4 真实 5」才抓到。
    # 「全部系列」里 Q 的篇数与跳转目标都取自这个数组。
    p = os.path.join(T, "assets", "fe-data.js")
    t = io.open(p, encoding="utf-8").read()
    if "'%s'" % FN in t:
        print("  3. fe-data.js 已有 Q05")
    else:
        old = "'q04-interfaces.html',"
        if old not in t:
            print("  !! 3. fe-data.js 找不到 q04 锚点")
        else:
            t = t.replace(old, old + "'%s'," % FN, 1)
            print("  3. fe-data.js 的 SERIES_FILES 追加 Q05")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t)

    # ---------- 4. add_lang_badges.py ----------
    p = os.path.join(R, "tools", "add_lang_badges.py")
    t = io.open(p, encoding="utf-8").read()
    if FN in t:
        print("  4. add_lang_badges.py 已有 Q05")
    else:
        old = '    "q04-interfaces.html": ("C++", "cpp"),'
        if old not in t:
            print("  !! 4. add_lang_badges.py 找不到锚点")
        else:
            t = t.replace(old, old + '\n    "%s": ("C++", "cpp"),' % FN, 1)
            print("  4. add_lang_badges.py 追加 Q05")
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t)

    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
