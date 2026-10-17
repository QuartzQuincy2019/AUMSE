# -*- coding: utf-8 -*-
"""把「每篇用什么语言」的定义收进 series_data.py，并让 add_lang_badges.py 从它派生。

为什么
    add_lang_badges.py 里有一张**手写**的 38 行映射表
    （文件名 → (显示名, class)）。而同样的信息本来就在
    series_data.py 里、或者在别处已经定过一次：

        PAGES     第 3 项 = 系列 key（"M" / "Q" / "R" …）
        FE_PAGES  第 5 项 = **语言**（"HTML" / "CSS" / "JS"），本来就是现成的
        非 FE 各篇的语言可以由系列推出（M/Q/R 基本是 C++，
        但 T 是 HTML、F 是 Shell、e02 是 Shell、r01 是 CSS）

    手写那张表的代价本会话已经付过：加 Q07 时要记得同步它，
    加 FE-09 时也要 —— 漏一处，那一篇就没有语言徽章。

做法
    1. 在 series_data.py 里定义 SERIES_LANG（按系列给）+ PAGE_LANG（单篇覆盖），
       并导出 LANG_OF 字典：文件名 → (显示名, class)。
       FE 各篇的语言直接取 FE_PAGES 的第 5 项。
    2. add_lang_badges.py 改成读 LANG_OF，不再自带映射表。

    这是一次「把副本换成派生」的重构，和 gen_series_tables.py 同一思路。
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
TOOLS = os.path.join(R, "tools")

BLOCK = '''

# ------------------------------------------------------------ 语言标注
# 每篇教程「用的是什么语言」，供语言徽章（.lang）与首页卡片使用。
#
#   SERIES_LANG  按系列给默认语言（这几组的主线语言各自统一）
#   PAGE_LANG    单篇覆盖（系列默认不合适时）
#   LANG_CLS     语言 → CSS 类名
#   LANG_OF      导出的**权威表**：文件名 → (显示名, class)
#
# FE 各篇的语言不在上表里 —— 它本来就写在 FE_PAGES 的第 5 项，
# 直接从那里取，避免又造一份副本。
SERIES_LANG = {
    "T": "HTML",    # 理论三篇：示例都是 HTML
    "F": "Shell",   # F01/F02 命令提示符、F03 编译与链接的工具链
    "M": "C++",
    "Q": "C++",
    "R": "C++",
    "E": "C++",     # E01/E03 是 C++，E02 见下面的单篇覆盖
}
PAGE_LANG = {
    # E02 是批处理（.bat），与 E 系列默认的 C++ 不同
    "e02.html": "Shell",
    # R01 只讲字体度量（EM Square / x 字高 / 行高），一个编程语言例子都没有；
    # 它讲的东西正是 CSS 关心的，所以归 CSS（与首页卡片一致）。
    "r01.html": "CSS",
}
LANG_CLS = {"HTML": "html", "CSS": "css", "JS": "js",
            "C++": "cpp", "C": "c", "Shell": "sh", "Python": "py"}


def _lang_of_pages():
    out = {}
    for key in PAGE_ORDER:
        if key == "FE":
            continue
        for p in pages_of(key):
            fn = p[1]
            out[fn] = PAGE_LANG.get(fn, SERIES_LANG[key])
    for p in FE_PAGES:
        out[p[0]] = p[4]          # FE_PAGES 的第 5 项就是语言
    return out


# 文件名 → (显示名, class)
LANG_OF = {fn: (lang, LANG_CLS[lang]) for fn, lang in _lang_of_pages().items()}
'''


def main():
    dry = "--dry" in sys.argv

    # ---------- 1. series_data.py：追加语言定义 ----------
    p = os.path.join(TOOLS, "series_data.py")
    t = io.open(p, encoding="utf-8").read()
    if "LANG_OF" in t:
        print("  1. series_data.py 已有 LANG_OF")
    else:
        t = t.rstrip("\n") + "\n" + BLOCK
        print("  1. series_data.py 追加 SERIES_LANG / PAGE_LANG / LANG_OF")
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t)

    # ---------- 2. add_lang_badges.py：改成读 LANG_OF ----------
    p2 = os.path.join(TOOLS, "add_lang_badges.py")
    t2 = io.open(p2, encoding="utf-8").read()
    if "LANG_OF" in t2:
        print("  2. add_lang_badges.py 已改成读 LANG_OF")
    else:
        # 把整个 LANG = { … } 字面量换成从 series_data 取
        m = re.search(r"(?ms)^LANG = \{.*?^\}\n", t2)
        if not m:
            print("  !! 2. 找不到 LANG 字面量")
        else:
            new = (
                "# 语言映射不再手写 —— 权威定义在 tools/series_data.py 里\n"
                "# （SERIES_LANG 按系列给 + PAGE_LANG 单篇覆盖，FE 各篇取自\n"
                "#   FE_PAGES 的语言字段），这里只做导入。\n"
                "# 手写那张 38 行的表已经因为漏同步出过问题（加 Q07 / FE-09 时）。\n"
                "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
                "from series_data import LANG_OF as LANG  # noqa: E402\n")
            t2 = t2[:m.start()] + new + t2[m.end():]
            print("  2. add_lang_badges.py 的 LANG 改为 from series_data import LANG_OF")
            if not dry:
                io.open(p2, "w", encoding="utf-8", newline="").write(t2)

    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))

    # ---------- 自检：与旧表逐条对照 ----------
    if not dry:
        sys.path.insert(0, TOOLS)
        import series_data as S
        print()
        print("  自检：LANG_OF 共 %d 条" % len(S.LANG_OF))
        for k in ("t01.html", "f03.html",
                  "r01.html", "e02.html",
                  "q07.html", "fe-09.html", "r04.html"):
            print("      %-36s %s" % (k, S.LANG_OF.get(k, "** 缺 **")))


if __name__ == "__main__":
    main()
