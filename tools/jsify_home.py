# -*- coding: utf-8 -*-
"""把 home.html / index.html 改成「数据 + JS 动态生成」。

模板放在 tools/home_template.html，卡片脚本放在 tools/home-cards.js ——
都作为**独立文件**存在，不再往 Python 字符串里塞大段 HTML/JS
（之前那样反复被引号和三引号咬到）。

生成结果：
  index.html / home.html
    ├─ <style>…</style>            首页自己的样式（保持自包含，不走 tutorial.css）
    ├─ 内联 window.__HOME__ 数据   加篇目只改 META / FE
    ├─ 内联 home-cards.js          渲染卡片
    └─ <noscript> 静态链接列表      关掉 JS 也能用，搜索引擎也读得到
"""
import io
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
TOOLS = os.path.join(REPO, "tools")
P = os.path.join(TOOLS, "make_pages.py")

# ---------- 新函数体（从文件读模板与脚本，避免引号地狱） ----------
NEW_FUNC = '''
# 首页模板与卡片脚本放在独立文件里 —— 不再往 Python 字符串里塞 HTML/JS
_HOME_TPL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "home_template.html")
_HOME_JS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "home-cards.js")


def build_html():
    """首页也由数据驱动 —— 与篇目单一数据源（META / FE）。

    数据内联在页面里（不 fetch），所以本地双击也能看。
    同时输出一份 noscript 静态列表兜底：关掉 JS 仍能看到全部链接，
    搜索引擎也读得到。
    """
    n_star = sum(1 for m in META if m[5]) + sum(1 for m in FE if m[5])
    total = len(META) + len(FE)

    def pack(items):
        return [{"file": a, "num": b, "title": c, "desc": d,
                 "kind": e, "star": bool(f)} for a, b, c, d, e, f in items]

    main_items = [m for m in META if m[4] in ("C", "C++")]
    more_items = [m for m in META if m[4] in ("Extra", "File")]

    data = {"main": pack(main_items), "more": pack(more_items), "fe": pack(FE)}
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    def plain(items):
        out = ["<ul>"]
        for a, b, c, d, e, f in items:
            s = " <b>&#9733;</b>" if f else ""
            out.append('<li><a href="SharingGroup/tutorials/%s">%s %s</a>%s</li>'
                       % (a, b, c, s))
        out.append("</ul>")
        return "".join(out)

    noscript = ('<noscript><div class="note"><h3>请开启 JavaScript</h3>'
                '<p>上面的卡片列表由脚本生成。你也可以用这份静态列表进入各篇：</p>'
                '<h3>正文 · 01 ~ 10</h3>' + plain(main_items) +
                '<h3>Extra · File</h3>' + plain(more_items) +
                '<h3>前端 · FE</h3>' + plain(FE) +
                '</div></noscript>')

    tpl = io.open(_HOME_TPL, encoding="utf-8").read()
    cardjs = io.open(_HOME_JS, encoding="utf-8").read()

    return (tpl.replace("@@STYLE@@", STYLE)
               .replace("@@TOTAL@@", str(total))
               .replace("@@NFE@@", str(len(FE)))
               .replace("@@NSTAR@@", str(n_star))
               .replace("@@NOSCRIPT@@", noscript)
               .replace("@@DATA@@", js)
               .replace("@@CARDJS@@", cardjs))


'''

t = io.open(P, encoding="utf-8").read()

# 先清掉上次那次失败的改动残留（若有）
if "CARD_JS = r\"\"\"" in t:
    a = t.find("CARD_JS = r\"\"\"")
    b = t.find("def build_html():", a)
    if b > a:
        t = t[:a] + t[b:]

start = t.find("def build_html():")
end = t.find("def main():")
assert start > 0 and end > start, (start, end)

t = t[:start] + NEW_FUNC.lstrip("\n") + t[end:]

if "\nimport json\n" not in t:
    t = t.replace("import io\nimport os\n", "import io\nimport json\nimport os\n", 1)

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  OK make_pages.py: build_html 改为读 home_template.html + home-cards.js")
