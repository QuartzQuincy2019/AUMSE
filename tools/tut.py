# -*- coding: utf-8 -*-
"""生成教程页的公共外壳：复用已提取的 CSS/脚本，套上给定正文。"""
import io
import os

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
# 外壳缓存放在 tools 下，避免污染交付目录（教程目录只放 15 篇成品）
PARTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_shell_parts")


def _read(name):
    with io.open(os.path.join(PARTS, name), encoding="utf-8") as fh:
        return fh.read()


CSS = _read("css.html")
SCRIPTS = _read("scripts.html")

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@</title>
@@CSS@@
<style>@@EXTRA@@</style>
</head>
<body>
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
@@TOC@@
</nav>

<main>
@@BODY@@
</main>
</div>

@@SCRIPTS@@
</body>
</html>
"""


def build(filename, title, toc, body, extra=""):
    out = (PAGE.replace("@@TITLE@@", title)
               .replace("@@CSS@@", CSS)
               .replace("@@EXTRA@@", extra)
               .replace("@@TOC@@", toc)
               .replace("@@BODY@@", body)
               .replace("@@SCRIPTS@@", SCRIPTS))
    dest = os.path.join(ROOT, filename)
    with io.open(dest, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)
    print("已生成: %-46s %6d 字符 | 代码块 %2d | 输出块 %2d | 表格 %d"
          % (filename, len(out), out.count('class="code-wrap"'),
             out.count('class="out-wrap"'), out.count("<table")))
    return out
