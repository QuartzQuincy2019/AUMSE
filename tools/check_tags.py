# -*- coding: utf-8 -*-
"""检查页面里成对标签的开关是否配平。

为什么需要
    纯 HTML 里，忘记写 </code> 浏览器**不会报错**，它会默默把后面的内容
    一直包进那个标签里 —— 版式因此错位，但结构检查、样式检查、
    JS 检查全都看不出来。F04 第 7 节就出过这一处：
    「（因为 <code>-G` 选的是 MinGW 系）」把反引号写进了 code 里、
    并且漏了 </code>，是用户肉眼发现的。

检查范围
    SharingGroup/tutorials/*.html（成品页）
    tools/_*_body.html（正文片段，重新生成页面时会把错误带回去）

检查哪些标签
    只查**必须成对**且本站真在用的那些；<br> <img> <hr> <meta> <link>
    这类空元素不查（它们本来就没有闭合）。

用法
    python check_tags.py          # 查全部
    python check_tags.py --slug f04
"""
import argparse
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(os.path.dirname(ROOT), "SharingGroup", "tutorials")

# 只查「内容级」标签。
# div / main / nav / footer 不查：页面外壳模板本身每页都多出两个 </div>，
# 每页相同、浏览器忽略，查了只会一片红，把真问题淹掉。
PAIRED = ["code", "pre", "b", "i", "span", "a", "p", "li", "ul", "ol",
          "table", "thead", "tbody", "tr", "td", "th",
          "h1", "h2", "h3", "h4", "strong", "em", "small", "kbd"]


def count_tag(t, name):
    """开标签算 <name> 与 <name ...>；闭标签算 </name>。"""
    opens = len(re.findall(r"<%s(?=[\s>])" % re.escape(name), t))
    closes = len(re.findall(r"</%s\s*>" % re.escape(name), t))
    return opens, closes


def check_file(path):
    t = io.open(path, encoding="utf-8", errors="replace").read()
    bad = []
    for name in PAIRED:
        o, c = count_tag(t, name)
        if o != c:
            bad.append((name, o, c))
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    a = ap.parse_args()

    targets = []
    for fn in sorted(os.listdir(T)):
        if not fn.endswith(".html"):
            continue
        # FE 系列的正文是运行时由 assets/fe-data.js 生成的，
        # 静态 HTML 里本来就没有内容标签，查了必然全红。
        if fn.startswith("fe-"):
            continue
        if not a.slug or fn == a.slug + ".html":
            targets.append(os.path.join(T, fn))
    for fn in sorted(os.listdir(ROOT)):
        m = re.match(r"^_(.+)_body\.html$", fn)
        if m and (not a.slug or m.group(1).rstrip("_") == a.slug):
            targets.append(os.path.join(ROOT, fn))

    bad_total = 0
    for p in targets:
        bad = check_file(p)
        name = os.path.basename(p)
        if bad:
            bad_total += len(bad)
            print("  ✗ %-24s %d 个标签不配平" % (name, len(bad)))
            for tag, o, c in bad:
                print("        <%s> 开 %d / 闭 %d" % (tag, o, c))
        elif a.slug:
            print("  OK %-24s 全部配平" % name)

    print()
    if bad_total:
        print("  合计 %d 处不配平 ✗" % bad_total)
        sys.exit(1)
    print("  共 %d 个文件，成对标签全部配平 OK" % len(targets))


if __name__ == "__main__":
    main()
