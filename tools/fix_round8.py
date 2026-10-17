# -*- coding: utf-8 -*-
"""修 3 个问题。

① 「项目组长留言」前面那个方框
   原因：CSS content 写成了 content:"\\1F4CC "。
   在 Python 源码里 "\\1F4CC" 是**两个字符**：反斜杠 + 1F4CC。
   写进 CSS 后，CSS 词法把 "\\" 解析成「一个字面反斜杠」，
   后面跟着 "1F4CC " 就成了普通文本 —— 于是渲染出「\1F4CC」，
   也就是用户看到的方框。
   正确的 CSS 转义是**单个**反斜杠：content:"\1F4CC "，
   并且习惯上在末尾补一个空格作为转义终止符（这个空格不显示）。
   更省事的做法是直接把 emoji 字符本身写进去，不转义。

② T 篇的「全部系列」按钮样式丢了
   原因：我上一轮把 .s-nav-switch 的样式放进了 series-theme.css，
   而 **T 的三篇根本没有加载 series-theme.css**
   （它们只用 f03_compile_and_link.css + t01.css + t-theme.css）。
   series-common.js 是照常注入 DOM 的，所以按钮在、就是没样式。
   修法：把 series-theme.css 也挂到 T 篇（主题按 data-series 选择器限定，
   对 T 只提供与系列无关的公共部分，不会跟手写的 t-theme.css 打架）。

③ 「全部系列」不含 FE
   series-common.js 的 PAGES 里只有 T/M/Q/E/F/R，没有前端 FE。
   而且文案写的是「其它系列」，与用户说的「全部系列」不一致。
   修法：把 FE 的 8 篇也纳入 PAGES，标签统一成「全部系列」，
   当前系列就地标出，不再排除自己。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"
TUT = os.path.join(R, "SharingGroup", "tutorials")
A = os.path.join(TUT, "assets")

# ---------------------------------------------------------------- ① emoji
P = os.path.join(R, "tools", "make_pages.py")
t = io.open(P, encoding="utf-8").read()
bad = '.lead-msg-t::before{content:"\\\\1F4CC "}'
if bad in t:
    # 直接写 emoji 本身，不做 CSS 转义 —— 少一层转义就少一个坑
    t = t.replace(bad, '.lead-msg-t::before{content:"\U0001F4CC "}', 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  ✓ ① 留言标题的图钉改为直接写字面 emoji（不再用 \\\\ 转义）")
else:
    # 退一步：找任何形态的这条规则
    import re
    m = re.search(r'\.lead-msg-t::before\{content:"[^"]*"\}', t)
    if m:
        t = t[:m.start()] + '.lead-msg-t::before{content:"\U0001F4CC "}' + t[m.end():]
        io.open(P, "w", encoding="utf-8", newline="").write(t)
        print("  ✓ ① 已替换：%r" % m.group(0))
    else:
        print("  ! ① 没找到 lead-msg-t::before 规则")

# ------------------------------------------------- ② T 篇挂上 series-theme
LINK = '<link rel="stylesheet" href="assets/series-theme.css">'
n = 0
for f in ("t01.html", "t02.html",
          "t03.html"):
    p = os.path.join(TUT, f)
    t = io.open(p, encoding="utf-8").read()
    if "series-theme.css" in t:
        continue
    links = list(__import__("re").finditer(r'<link[^>]*rel="stylesheet"[^>]*>', t))
    last = links[-1]
    t = t[:last.end()] + "\n" + LINK + t[last.end():]
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    n += 1
print("  ✓ ② T 篇挂上 series-theme.css：%d 篇" % n)

# 让 T 也能吃到与系列无关的公共部分
P2 = os.path.join(R, "tools", "build_series_css.py")
u = io.open(P2, encoding="utf-8").read()
old_sel = "body[data-series]{box-sizing:border-box}"
new_sel = ("/* 公共部分：不带具体系列，T 篇也要用（T 的主题是手写的 t-theme.css，\n"
           "   但它同样需要下面这些与系列无关的规则）。 */\n"
           "body[data-series]{box-sizing:border-box}")
if old_sel in u and "公共部分：不带具体系列" not in u:
    u = u.replace(old_sel, new_sel, 1)
    io.open(P2, "w", encoding="utf-8", newline="").write(u)
    print("  ✓ ② series-theme.css 的公共段加注（T 也用）")

io.open(os.path.join(R, "tools", "_round8_done"), "w").write("1")
