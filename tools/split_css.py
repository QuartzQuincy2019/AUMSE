# -*- coding: utf-8 -*-
"""把教程文档的 CSS 分离出来（第二版：按「规则在多少篇里出现」判定通用性）。

第一版的毛病：只把带标记注释的两块当通用，结果基础设计系统那 13 KB
被复制进了每一篇的专属 css（100~200 条规则），完全没有瘦身。

这一版的做法：
  1. 先扫一遍全部 15 篇，把每篇的 CSS 切成一条条规则
  2. 统计每条规则出现在多少篇里
  3. 出现在 ≥80% 篇里的 → 通用，进 tutorial.css
     其余 → 该篇专属，进 assets/dsNN.css
  4. 文档里的所有 <style> 换成两个 <link>

顺序也保留：通用规则按首次出现的顺序写入，专属规则保持原文顺序。
"""
import io
import os
import re
import sys
from collections import OrderedDict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
ASSETS = os.path.join(ROOT, "assets")
THRESHOLD = 0.8          # 出现比例达到这个值就算通用


def split_rules(css):
    """把 CSS 切成 [(comment, rule), ...]，正确处理 @media 嵌套。"""
    out, i, n = [], 0, len(css)
    while i < n:
        while i < n and css[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        comment = None
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            if j < 0:
                break
            comment = css[i:j + 2]
            i = j + 2
            while i < n and css[i] in " \t\r\n":
                i += 1
        if i >= n:
            break
        if css[i] == "@":
            k = css.find("{", i)
            if k < 0:
                break
            depth, j = 1, k + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            rule, i = css[i:j], j
        else:
            j = css.find("}", i)
            if j < 0:
                break
            rule, i = css[i:j + 1], j + 1
        out.append((comment, rule))
    return out


def norm(s):
    """归一化：压掉空白差异，用于跨文档比对同一条规则。"""
    return re.sub(r'\s+', ' ', s).strip()


def strip_header(css):
    m = re.match(r'\s*/\* =+\s*\n(.*?)\n\s*=+ \*/', css, re.S)
    return (m.group(0), css[m.end():]) if m else ("", css)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    docs = sorted(f for f in os.listdir(ROOT)
                  if f.startswith("_ds_") and f.endswith(".html"))

    # ---------- 第一遍：收集 ----------
    per_doc = OrderedDict()      # name -> [(comment, rule)]
    header = None
    for name in docs:
        with io.open(os.path.join(ROOT, name), encoding="utf-8") as fh:
            t = fh.read()
        styles = re.findall(r'(?s)<style>(.*?)</style>', t)
        if not styles:
            print("  !! %s 没有 <style>" % name)
            continue
        items = []
        for idx, css in enumerate(styles):
            if idx == 0:
                h, body = strip_header(css)
                if header is None:
                    header = re.sub(r'UME 项目组内部教程 · [^\n]*',
                                    'UME 项目组内部教程 · 共用样式表', h).strip()
            else:
                body = css
            items.extend(split_rules(body))
        per_doc[name] = items

    # ---------- 统计每条规则出现在多少篇 ----------
    count = {}
    for name, items in per_doc.items():
        for _, rule in items:
            k = norm(rule)
            count.setdefault(k, set()).add(name)

    n_docs = len(per_doc)
    need = max(2, int(n_docs * THRESHOLD))

    # ---------- 第二遍：分配 ----------
    common_order, common_seen = [], set()
    report = []
    for name, items in per_doc.items():
        page = []
        for comment, rule in items:
            k = norm(rule)
            if len(count[k]) >= need:
                if k not in common_seen:
                    common_seen.add(k)
                    common_order.append(((comment or "") + rule).strip())
            else:
                page.append(((comment or "") + rule).strip())

        stem = re.sub(r'[^A-Za-z0-9]+', '_',
                      os.path.splitext(name)[0]).strip('_')
        per_file = stem + ".css"
        if page:
            with io.open(os.path.join(ASSETS, per_file), "w",
                         encoding="utf-8", newline="\n") as fh:
                fh.write("/* ==== %s\n       本篇专属样式（通用部分见 tutorial.css）==== */\n\n"
                         % name)
                fh.write("\n\n".join(page) + "\n")

        # 文档里换 link
        path = os.path.join(ROOT, name)
        with io.open(path, encoding="utf-8") as fh:
            t = fh.read()
        link = '<link rel="stylesheet" href="assets/tutorial.css">'
        if page:
            link += '\n<link rel="stylesheet" href="assets/%s">' % per_file
        t = re.sub(r'(?s)<style>.*?</style>\s*', '', t)
        t = t.replace("</head>", link + "\n</head>", 1)
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(t)

        report.append((name, per_file if page else "(无)", len(page), len(t)))

    with io.open(os.path.join(ASSETS, "tutorial.css"), "w",
                 encoding="utf-8", newline="\n") as fh:
        if header:
            fh.write(header + "\n\n")
        fh.write("\n\n".join(common_order) + "\n")

    print("通用规则 %d 条（出现在 >=%d/%d 篇），写入 tutorial.css"
          % (len(common_order), need, n_docs))
    print("")
    print("%-46s %-26s %s" % ("文档", "专属样式", "专属规则数"))
    print("-" * 92)
    for name, per, cnt, ln in report:
        print("%-46s %-26s %d" % (name, per, cnt))
    print("")
    print("tutorial.css : %d 字符" % os.path.getsize(os.path.join(ASSETS, "tutorial.css")))
    tot = sum(os.path.getsize(os.path.join(ASSETS, f))
              for f in os.listdir(ASSETS) if f.endswith(".css"))
    print("assets 全部 css: %d 字符" % tot)


if __name__ == "__main__":
    main()
