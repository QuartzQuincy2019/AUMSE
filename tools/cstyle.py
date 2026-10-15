# -*- coding: utf-8 -*-
"""把 09 之前的文档改写为 C 风格，并在必须用 C++ 的地方加显眼标识。

背景：教程 01~08 原本按 C 讲。但我在 06/07/08/E01 里混入了 iostream /
cout / class / string 等 C++ 内容，与「09 之前用 C」的要求冲突。

本脚本：
  1. 注入 .cpp-badge 样式与「C++」标记的辅助函数
  2. 逐块把 cout/iostream 版本改写成 printf/stdio.h 版本
  3. 对确实无法避免的 C++（类的成员函数、private/public），
     在代码块标题栏加醒目的 C++ 徽标，并在正文里说明
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

BADGE_CSS = """
/* ===== C++ 内容标识：09 之前尽量用 C，不得已用 C++ 时必须显眼 ===== */
.cpp-badge{
  display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;
  font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.04em;
  background:#7c3aed;color:#fff;vertical-align:1px;
}
.cpp-note{
  border:1px solid #ded0f7;border-left:4px solid #7c3aed;background:var(--violet-soft);
  border-radius:0 9px 9px 0;padding:11px 16px;margin:14px 0;font-size:14px;
}
.cpp-note b{color:#7c3aed}
.cpp-note .t{font-weight:700;color:#7c3aed;margin-bottom:4px;display:flex;
  align-items:center;gap:8px}
.cpp-note p:last-child{margin-bottom:0}
"""

MARK = "/* ===== C++ 内容标识"


def ensure_badge_css(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    if MARK in t:
        return t, False
    t = t.replace("</head>", "<style>" + BADGE_CSS + "</style>\n</head>", 1)
    return t, True


def mark_cpp(t, block_name, label="C++"):
    """给某个代码块的标题栏加 C++ 徽标（按标题文字定位）"""
    old = '<span class="name">%s</span>' % block_name
    new = ('<span class="name">%s</span>'
           '<span class="cpp-badge">%s</span>' % (block_name, label))
    if old not in t:
        print("    !! 找不到标题：%s" % block_name)
        return t
    return t.replace(old, new, 1)


def repl(t, pairs, tag):
    for old, new in pairs:
        n = t.count(old)
        if n != 1:
            print("    !! [%s] 命中 %d 次: %s" % (tag, n, old[:56].replace("\n", " ")))
            continue
        t = t.replace(old, new, 1)
    return t


# =====================================================================
# 通用：把 cout 版代码块整体换成 printf 版
# =====================================================================
def convert_all_cout(t, doc):
    """把最简单的 `cout << ... << endl;` 形式换成 printf"""
    # iostream / using namespace 头两行
    t = t.replace(
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n'
        '<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n',
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>\n')
    t = t.replace(
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n'
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>\n'
        '<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;\n',
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>\n'
        '<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>\n')
    return t


if __name__ == "__main__":
    print("本脚本为辅助模块，具体改写见各 build_* 脚本。")
