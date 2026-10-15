# -*- coding: utf-8 -*-
"""给**后端** 16 篇加「返回 home」+ 页尾系列小目录。

做法：脚本注入，不改动原有任何样式与结构 ——
  * 小目录插在页脚 <footer> 之前（没有 footer 就追加到 <main> 末尾）
  * 返回按钮是固定定位的悬浮按钮
  * 用 <!-- NAV-AUTO --> 标记，重复运行会先清掉旧块，保证幂等

小目录由 make_pages.py 的 META 表生成 —— 与 home 导航页单一数据源，
以后加篇目只改那一处。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
TUT = os.path.join(REPO, "SharingGroup", "tutorials")

sys.path.insert(0, os.path.join(REPO, "tools"))
import make_pages as MP          # 复用 META / FE 两张表

MARK_A = "<!-- NAV-AUTO -->"
MARK_B = "<!-- /NAV-AUTO -->"

CSS = """
/* ================= 自动注入：返回 home + 系列小目录 ================= */
.home-fab{position:fixed;left:11px;bottom:11px;z-index:65;display:inline-flex;
  align-items:center;gap:6px;padding:8px 14px;border-radius:999px;
  background:#fff;border:1px solid var(--line-2);color:var(--fg-2);
  text-decoration:none;font:600 13px/1 var(--sans);
  box-shadow:0 4px 16px rgba(20,30,50,.16);transition:transform .14s,box-shadow .14s,color .14s}
.home-fab:hover{transform:translateY(-2px);color:var(--blue);
  box-shadow:0 8px 22px rgba(30,60,120,.24)}
.home-fab::before{content:"⌂";font-size:15px}
.series-nav{margin:34px 0 0;padding:14px 18px;border:1px solid var(--line-2);
  border-radius:12px;background:var(--bg-soft);font-size:13.5px}
.series-nav b{color:var(--fg)}
.series-nav a{display:inline-block;margin:3px 8px 3px 0;padding:3px 11px;border-radius:999px;
  background:#fff;border:1px solid var(--line-2);text-decoration:none;color:var(--fg-2);
  transition:border-color .14s,color .14s}
.series-nav a:hover{border-color:var(--blue);color:var(--blue)}
.series-nav a.cur{background:var(--blue);border-color:var(--blue);color:#fff;font-weight:600}
@media (max-width:560px){
  .series-nav{font-size:12.5px;padding:12px 13px}
  .series-nav a{font-size:12px;margin:2px 5px 2px 0;padding:2px 9px}
  .home-fab{left:9px;bottom:9px;padding:7px 12px;font-size:12.5px}
}
"""

FAB = ('<a class="home-fab" href="../../index.html" '
       'title="返回教程总目录">返回 home</a>')


def series_nav(cur_file, entries):
    out = ['<div class="series-nav"><b>本系列</b>　']
    for fn, num, title, desc, kind, star in entries:
        cls = ' class="cur"' if fn == cur_file else ''
        s = ' <span style="color:#c8901a">*</span>' if star else ''
        label = ("%s %s" % (num, title)) if num else title
        out.append('<a href="%s"%s>%s%s</a>' % (fn, cls, label, s))
    out.append('</div>')
    return "".join(out)


def main():
    backend = [m for m in MP.META]
    n = 0
    for idx, (fn, num, title, desc, kind, star) in enumerate(backend):
        p = os.path.join(TUT, fn)
        if not os.path.exists(p):
            print("  !! 找不到 %s" % fn)
            continue
        t = io.open(p, encoding="utf-8").read()

        # ① 幂等：先清掉旧的注入块
        t = re.sub(re.escape(MARK_A) + r'.*?' + re.escape(MARK_B), "", t, flags=re.S)
        t = t.replace(FAB, "")

        # ② 样式：插在最后一个 </style> 之前（后端是外链 css，所以插 <head> 末尾）
        if ".home-fab{" not in t:
            if "</head>" in t:
                t = t.replace("</head>", "<style>%s</style>\n</head>" % CSS, 1)
            else:
                print("  !! %s 没有 </head>" % fn)
                continue

        block = MARK_A + "\n" + FAB + "\n" + series_nav(fn, backend) + "\n" + MARK_B

        # ③ 位置：<footer> 之前
        i = t.find("<footer")
        if i > 0:
            t = t[:i] + block + "\n" + t[i:]
        else:
            j = t.rfind("</main>")
            if j < 0:
                j = t.rfind("</body>")
            t = t[:j] + block + "\n" + t[j:]

        io.open(p, "w", encoding="utf-8", newline="").write(t)
        n += 1
        print("  ✔ %-34s %s" % (fn, num))
    print("\n  处理 %d 篇" % n)


if __name__ == "__main__":
    main()
