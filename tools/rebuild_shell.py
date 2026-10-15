# -*- coding: utf-8 -*-
"""从已有文档里重建共享外壳（css / scripts），并生成 tut.py 需要的缓存。

背景：之前用 extract_shell.py 抽出的 _shell_parts/ 在清理时删掉了。
外壳本身并没有变，所以直接从一篇现有文档里再抽一次即可。

用法：
    python rebuild_shell.py                 # 重建缓存
    python rebuild_shell.py <doc.html>      # 指定作为模板的文档
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
PARTS = os.path.join(ROOT, "_shell_parts")

# 用 07 做模板：它没有 F 系列主题、没有额外样式，是最干净的正文结构
DEFAULT_TEMPLATE = "_ds_07_作用域、全局与局部变量.html"


def extract(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()

    # ---- 1. 所有 <style> 块：第一个是基础样式，其余是页面专属，需剔除 ----
    styles = re.findall(r"(?s)<style>(.*?)</style>", t)
    if not styles:
        raise SystemExit("没找到 <style> 块")
    base_css = styles[0]
    extra_css = styles[1:]

    # ---- 2. 所有 <script> 块（含外链）----
    scripts = re.findall(r"(?s)<script\b[^>]*>.*?</script>", t)
    scripts_html = "\n".join(scripts)

    # ---- 3. 正文 ----
    m = re.search(r"(?s)<main>(.*?)</main>", t)
    if not m:
        raise SystemExit("没找到 <main>")
    body = m.group(1)

    # ---- 4. 目录 ----
    m = re.search(r"(?s)<nav id=\"toc\">.*?</nav>", t)
    toc = m.group(0) if m else ''

    # ---- 5. body 上挂的 class ----
    m = re.search(r"<body([^>]*)>", t)
    body_attr = m.group(1).strip() if m else ""

    return {
        "css": base_css,
        "scripts": scripts_html,
        "body": body,
        "toc": toc,
        "extra": "\n".join(extra_css),
        "body_attr": body_attr,
        "has_parts": (body, toc),
    }


def main():
    tpl = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEMPLATE
    path = os.path.join(ROOT, tpl)
    if not os.path.exists(path):
        raise SystemExit("模板不存在: " + path)

    d = extract(path)
    os.makedirs(PARTS, exist_ok=True)

    with io.open(os.path.join(PARTS, "css.html"), "w", encoding="utf-8", newline="") as fh:
        fh.write("<style>" + d["css"] + "</style>")
    with io.open(os.path.join(PARTS, "scripts.html"), "w", encoding="utf-8", newline="") as fh:
        fh.write(d["scripts"])

    print("模板: %s" % tpl)
    print("  css.html      %6d 字符" % len(d["css"]))
    print("  scripts.html  %6d 字符" % len(d["scripts"]))
    print("  <script> 块   %d 个" % (d["scripts"].count("<script") if d["scripts"] else 0))
    print("  body 属性     %r" % d["body_attr"])
    print("  页面专属样式  %d 块（不写入缓存，由各文档自己带）" % len(d["extra"].split("</style>")) if d["extra"] else "  页面专属样式  0 块")

    # 顺手报告基础样式里是否已含移动端增强与断行规则
    for key, label in [("max-width:980px", "移动端断点"),
                       ("tocToggle", "目录按钮"),
                       ("overflow-wrap:anywhere", "长串断行")]:
        print("  基础样式含 %-10s : %s" % (label, "是" if key in d["css"] else "否"))


if __name__ == "__main__":
    main()
