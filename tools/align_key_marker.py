# -*- coding: utf-8 -*-
"""把重点小节的 ★ 统一放到**数字徽标之前**。

为什么
    .key-mark 自带 margin-right:8px，那是为「★ 在数字前」设计的：
        ★ 3 为什么需要命名空间
    而 Q05/Q01 先写成了「数字在前、★ 在后」：
        3 ★ 为什么需要命名空间
    于是 8px 的留白跑到了标题前面，而数字徽标和 ★ 之间反而没有间隔，
    两处都不好看（Q05 之前是靠一条页面专属规则把 margin 反过来补的）。

    更关键的是：**手工页 T02 / F01 用的就是「★ 在前」**，
    脚本生成的是「★ 在后」—— 同一个标记两种排法，本来就不该有两个。

    统一到「★ 在前」：既合 .key-mark 的默认样式，也与 T02/F01 一致。

改动
    1. Q05 与 Q01 的正文片段：★ 挪到数字之前
    2. 删掉 Q05 样式表里那条「把 margin 反过来」的补丁 —— 不再需要
    3. build_q01_body.py 里生成 s2/s3 标题的地方同步改
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

# 允许 ★ 在数字前或后，统一换成「前」
PAT = re.compile(
    r'(<h2 id="s\d+" class="key-h"><span class="n">\d+</span>)'
    r'<span class="key-mark" title="重点内容">★</span>')

TARGETS = [
    r"tools\_q05_body.html",
    r"tools\_q01_body.html",
]


def main():
    dry = "--dry" in sys.argv
    for rel in TARGETS:
        p = os.path.join(R, rel)
        if not os.path.exists(p):
            print("  !! 找不到 %s" % rel)
            continue
        t = io.open(p, encoding="utf-8").read()
        n = len(PAT.findall(t))
        if not n:
            print("  %-24s 无需调整" % rel)
            continue
        t2 = PAT.sub(lambda m: '<span class="key-mark" title="重点内容">★</span>'
                     + m.group(1), t)
        print("  %-24s 调整 %d 处（★ 移到数字前）" % (rel, n))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)

    # 生成器里的标题模板
    p = os.path.join(R, "tools", "build_q01_body.py")
    t = io.open(p, encoding="utf-8").read()
    pat2 = re.compile(
        r"(<h2 id=\"s[23]\" class=\"key-h\"><span class=\"n\">\d</span>)"
        r"(<span class=\"key-mark\" title=\"重点内容\">★</span>)")
    if pat2.search(t):
        t = pat2.sub(lambda m: m.group(2) + m.group(1), t)
        print("  %-24s 模板同步（★ 移到数字前）" % "build_q01_body.py")
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t)
    else:
        print("  %-24s 模板无需调整" % "build_q01_body.py")

    # 删掉 Q05 里那条补丁规则
    p = os.path.join(R, "SharingGroup", "tutorials", "assets",
                     "q05_open_closed.css")
    c = io.open(p, encoding="utf-8").read()
    i = c.find("/* ---------- 重点小节的 ★ 位置 ---------- */")
    if i >= 0:
        c2 = c[:i].rstrip() + "\n"
        print("  删除 q05_open_closed.css 里的 ★ margin 补丁（%d 字符）"
              % (len(c) - len(c2)))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="\n").write(c2)
    else:
        print("  q05_open_closed.css 已无该补丁")

    print()
    print("  %s" % ("[dry-run]" if dry else "已写入"))


if __name__ == "__main__":
    main()
