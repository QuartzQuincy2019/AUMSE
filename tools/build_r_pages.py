# -*- coding: utf-8 -*-
"""R 系列页面生成器：把「正文片段」套上通用外壳，输出完整 HTML。

目录从正文的 <h2> **自动推导**，不再手写
----------------------------------------
上一轮在 Q01 上踩过这个坑：目录和正文分别维护，
插入一节后目录写成了 s8 标准库地图 / s9 ::，
而正文是 s8 :: / s9 标准库地图 —— 两处对不上，锚点全指错。

这里改成：正文只写一次（<h2 id="sN"><span class="n">N</span>标题</h2>），
目录由正则从正文里抓出来生成。正文顺序就是目录顺序，物理上不可能漂移。

同时校验：
  · id 必须是 s1..sN 连续
  · <span class="n"> 里的编号必须与序位一致
  · 目录条数必须等于 h2 条数
任何一条不过就报错退出，不写文件。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_r_shell import shell  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

PAGES = [
    dict(body="_r01_body.html", out="r01-font-design-metrics.html",
         num="R01", title="字体设计里的几个基本概念",
         sub="了解即可，不必深究", css="r01_font_design_metrics.css",
         foot="UME 项目组内部教程 · R01《字体设计里的几个基本概念》<br>\n"
              "示意图片来自公开的字体度量说明图；文字说明由项目组整理。"),
    dict(body="_r02_body.html", out="r02-bubble-sort.html",
         num="R02", title="冒泡排序与算法复杂度",
         sub="从「把一排数字排好」说起", css="r02_bubble_sort.css",
         foot="UME 项目组内部教程 · R02《冒泡排序与算法复杂度》<br>\n"
              "文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）"
              "实际编译运行核对；代码示例以 <b>Consolas</b> 等宽字体呈现。"),
    dict(body="_r03_body.html", out="r03-collation.html",
         num="R03", title="字典序、自然序与 QCollator",
         sub="字符串怎么比大小，中文怎么排才对", css="r03_collation.css",
         foot="UME 项目组内部教程 · R03《字典序、自然序与 QCollator》<br>\n"
              "文中所有输出与报错，均使用 g++ 13.1.0（<code>-std=c++17</code>）"
              "与 Qt 6.5 实际编译运行核对；代码示例以 <b>Consolas</b> 等宽字体呈现。"),
]


def build(one):
    bp = os.path.join(HERE, one["body"])
    if not os.path.exists(bp):
        print("  ! 找不到正文片段 %s，跳过" % one["body"])
        return False
    body = io.open(bp, encoding="utf-8").read()

    # 从正文抓 h2，生成目录
    heads = re.findall(
        r'<h2[^>]*id="(s\d+)"[^>]*>(?:<span class="key-mark"[^>]*>[^<]*</span>)?<span class="n">(\d+)</span>(?:<span class="key-mark"[^>]*>[^<]*</span>)?(.*?)</h2>', body, re.S)
    if not heads:
        print("  ! %s 里没有 <h2>，跳过" % one["body"])
        return False

    toc_items = [(h[0], h[2].strip()) for h in heads]

    # ---- 校验 ----
    ids = [h[0] for h in heads]
    nos = [int(h[1]) for h in heads]
    expect_ids = ["s%d" % i for i in range(1, len(ids) + 1)]
    errs = []
    if ids != expect_ids:
        errs.append("id 不是 s1..sN 连续：%s" % ids)
    if nos != list(range(1, len(ids) + 1)):
        errs.append("编号与序位不一致：%s" % nos)
    if errs:
        print("  !! %s 校验失败：" % one["out"])
        for e in errs:
            print("       " + e)
        return False

    p, size = shell(one["num"], one["title"], one["sub"], one["css"],
                    toc_items, body, one["foot"], one["out"])
    print("  ✓ %-34s %2d 节  目录 %2d 条  %6d B"
          % (one["out"], len(ids), len(toc_items), size))
    return True


def main():
    n = 0
    for one in PAGES:
        if build(one):
            n += 1
    print("\n  生成 %d / %d 篇" % (n, len(PAGES)))


if __name__ == "__main__":
    main()
