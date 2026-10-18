# -*- coding: utf-8 -*-
"""检查教程页正文里用到的 class，是否都在**该页实际加载的样式表**里有定义。

为什么需要这个检查
------------------
每篇教程的样式表是**各自成篇**的（公共层 genelayout + 该页样式表 + 主题层）。
所以「Q02 里定义了 .mem」**不等于**「E03 里能用 .mem」——
E03 没定义，浏览器就按普通 div 渲染：格子变成一竖列纯文字，
页面不报错、结构检查也过，只有肉眼看渲染结果才发现不对。

E03 写的时候就这么栽了两次（.mem 和 .alias）。
这个脚本把这类问题变成一条命令能查出来的东西。

用法：
    python check_page_classes.py                  # 检查全部有正文片段的页
    python check_page_classes.py --slug e03       # 只查一页
"""
import io
import os
import re
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import all_rules  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"

# ---- assets 已按类型分到 css/ img/ js/，这里统一兜底找 ----
def resolve(name):
    p = os.path.join(A, name)
    if os.path.exists(p):
        return p
    for sub in ("css", "js", "img", "fonts"):
        q = os.path.join(A, sub, name)
        if os.path.exists(q):
            return q
    return p
T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
TOOLS = os.path.dirname(os.path.abspath(__file__))

COMMON = ["genelayout.css", "series-theme.css", "tg_L.css", "tg_D.css"]


def selectors_of(files):
    """把若干样式表里出现过的选择器收集起来（去掉空白，便于子串匹配）。"""
    out = set()
    for f in files:
        p = resolve(f)
        if not os.path.exists(p):
            print("     !! 缺样式表 %s" % f)
            continue
        c = io.open(p, encoding="utf-8").read()
        for _conds, nd in all_rules(c):
            for part in nd.prelude.split(","):
                out.add(re.sub(r"\s+", "", part))
    return out


def jobs():
    """正文片段 → 该页的样式表。样式表从生成的 HTML 里读，最可靠。"""
    out = []
    for fn in sorted(os.listdir(TOOLS)):
        m = re.match(r"^_(.+)body\.html$", fn)
        if not m:
            continue
        slug = m.group(1).rstrip("_")
        body = Io(os.path.join(TOOLS, fn))
        out.append((slug, fn, body))
    return out


def Io(p):
    return io.open(p, encoding="utf-8").read()


# 教程页是纯 HTML，不解析 markdown。正文里留下 **…** 会**原样显示**出来
# （Q03 初稿就漏了一处：「它是**语法上的别名**」）。
#
# 只查 `**` 这一种，而且必须剔掉代码区之后再查。理由：
#   · <pre> / <code> 里本来就满是 * 和 `：
#       C++ 的 `*p`、`**ptr`；JavaScript 模板字符串 `hi ${n}`；
#       Shell 的引号。这些**不是** markdown，报了全是噪音。
#     第一版没剔代码区，R03 的 `coll.compare(a, b) < 0` 被误报一百多条；
#     第二版只剔 <pre>，E03 表格里的 `hi ${n}` 又被误报。
#   · 反引号在正文里也可能**故意**用作示例（E03 那格就是 JS 语法），
#     所以不查反引号 —— 只查 `**`，它没有任何正当用途。
MD = "**"


def check_markdown(slug, body):
    """扫一遍正文片段，看有没有误写的 `**`（跳过 <pre> 与 <code>）。"""
    prose = re.sub(r'<pre[\s\S]*?</pre>', '', body)
    prose = re.sub(r'<code[\s\S]*?</code>', '', prose)
    n = prose.count(MD)
    return ["**（markdown 粗体）%d 处 —— 会原样显示出来" % n] if n else []


def page_css_for(slug):
    """从已生成的页面里找出它的样式表（排除全局层）。"""
    htmls = [f for f in os.listdir(T)
             if f.endswith(".html") and slug in f]
    for h in htmls:
        t = Io(os.path.join(T, h))
        for m in re.finditer(r'<link[^>]*href="assets/((?:css/)?[^"]+\.css)"', t):
            fn = m.group(1)
            # 链接现在一律是 css/xxx.css；COMMON 里存的是不带前缀的名字，
            # 所以比较前先剥掉子目录，否则 genelayout 会被当成「本页样式表」。
            if fn.rsplit('/', 1)[-1] not in COMMON:
                return fn, h
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    a = ap.parse_args()

    bad_total = 0
    for slug, fn, body in jobs():
        if a.slug and slug != a.slug:
            continue
        css, html = page_css_for(slug)
        if not css:
            print("  %-6s 找不到对应页面（跳过）" % slug)
            continue
        S = selectors_of(COMMON + [css])
        used = set()
        for m in re.finditer(r'class="([^"]+)"', body):
            used.update(m.group(1).split())
        missing = sorted(k for k in used
                         if not any(("." + k) in s for s in S))
        flag = "✅" if not missing else "❌"
        print("  %-6s 正文 %-22s 样式表 %-26s 用到 %2d 个 class  缺定义 %d 个 %s"
              % (slug, fn, css, len(used), len(missing), flag))
        if missing:
            bad_total += len(missing)
            print("         缺：%s" % ", ".join(missing))
            print("         （这些 class 会按普通元素渲染 —— 不报错，但样子不对）")
        md = check_markdown(slug, body)
        if md:
            bad_total += len(md)
            print("         !! 正文里有 markdown 记号，会原样显示出来：%s"
                  % "、".join(md))
    print()
    print("  合计缺定义 %d 个 %s" % (bad_total, "✅" if bad_total == 0 else "❌"))


if __name__ == "__main__":
    main()
