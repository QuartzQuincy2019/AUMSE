# -*- coding: utf-8 -*-
"""把前端 8 篇改成「数据 + JS 动态生成 DOM」。

目标（按用户要求降低维护成本）：
  每一页 .html 缩成一个小壳：内联一份页面数据 + 引入 fe-data.js，
  由 JS 把 header / 目录 / 正文 / 页尾小目录 / 返回按钮 全部动态建出来。

为什么数据**内联在 html 里**而不是 fetch 一个 .json：
  浏览器不允许 file:// 下 fetch 本地文件。内联之后，
  直接双击 .html 也能正常看 —— 开发时最方便。

每篇的「正文」作为一段不透明字符串存进 __FE_PAGE__.body，
由渲染器识别其中的 <h2 id="…"> 自动生成左侧目录 ——
所以以后加小节只要写正文，目录不用手维护。
"""
import io
import json
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
import make_pages as MP

SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>前端 · {title}</title>
<link rel="stylesheet" href="assets/{css}">
</head>
<body>
<noscript>
  <div style="max-width:680px;margin:60px auto;padding:0 20px;font:16px/1.8 sans-serif">
    <h1>需要开启 JavaScript</h1>
    <p>这一页的界面（目录、正文、页脚导航）由脚本动态生成，请开启 JavaScript 后刷新。</p>
    <p><a href="../../index.html">← 返回教程总目录</a></p>
  </div>
</noscript>
<script>
/* 本页数据。正文里的 <h2 id="…"> 会被渲染器自动收进左侧目录。 */
window.__FE_PAGE__ = {data};
</script>
<script src="assets/fe-data.js"></script>
</body>
</html>
"""


def extract(fn):
    """从生成好的页面里取出**正文**与标题。

    这里必须把「渲染器会自己生成的东西」全部剥掉，否则会重复渲染：
      * <h1> 与 .sub-title —— 渲染器用 P.title / P.num 新建，数据里不能再有
        （曾经漏掉这两步，结果页面上 h1 与 .sub-title 各出现两次）
      * 旧的 .page-nav / .series-nav / footer / 注入块 —— 渲染器会重新生成
    """
    t = io.open(os.path.join(TUT, fn), encoding="utf-8").read()
    m = re.search(r'(?s)<main[^>]*>(.*?)</main>', t)
    body = m.group(1) if m else ""

    # 一级标题与副标题：渲染器会生成，这里去掉
    body = re.sub(r'(?s)<h1\b[^>]*>.*?</h1>', "", body, count=1)
    body = re.sub(r'(?s)<p class="sub-title">.*?</p>', "", body, count=1)

    # 页内导航 / 页脚 / 注入块：渲染器会生成
    body = re.sub(r'(?s)<div class="page-nav">.*?</div>\s*', "", body)
    body = re.sub(r'(?s)<div class="series-nav">.*?</div>\s*', "", body)
    body = re.sub(r'(?s)<footer>.*?</footer>', "", body)
    body = re.sub(r'(?s)<!-- NAV-AUTO -->.*?<!-- /NAV-AUTO -->', "", body)
    body = body.strip()

    # 标题：优先用 <title> 里「前端 · xxx」的 xxx，其次正文 h1
    tm = re.search(r'<title>\s*前端\s*·\s*(.*?)\s*</title>', t)
    if tm:
        title = tm.group(1).strip()
    else:
        hm = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
        title = re.sub(r'<[^>]+>', '', hm.group(1)).replace("★", "").strip() if hm else fn

    # 校验：这些标签不该出现在正文数据里，否则一定会重复渲染
    for bad in ('<h1', 'class="sub-title"', 'class="series-nav"',
                'class="page-nav"', 'home-fab'):
        if bad in body:
            raise SystemExit("  !! %s 的正文里仍有 %s —— 会重复渲染" % (fn, bad))
    return title, body


def main():
    entries = MP.FE
    meta = {fn: (num, title, star) for fn, num, title, desc, kind, star in entries}
    n = 0
    for fn, num, title, desc, kind, star in entries:
        if not os.path.exists(os.path.join(TUT, fn)):
            print("  !! 找不到 %s" % fn)
            continue
        h1, body = extract(fn)

        data = {
            "file": fn,
            "num": num,
            "title": title,
            "star": bool(star),
            "body": body,
            "series": [
                {"file": f2, "num": n2, "title": t2, "star": bool(s2)}
                for f2, n2, t2, d2, k2, s2 in entries
            ],
        }
        js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        # 防止正文里出现 </script> 把脚本提前截断
        js = js.replace("</", "<\\/")

        stem = re.sub(r'[^A-Za-z0-9]+', '_', os.path.splitext(fn)[0]).strip('_')
        out = SHELL.format(title=title, css=stem + ".css", data=js)
        io.open(os.path.join(TUT, fn), "w", encoding="utf-8", newline="").write(out)
        n += 1
        print("  ✔ %-18s %-10s 正文 %6d 字符 → 整页 %6d 字符"
              % (fn, num, len(body), len(out)))
    print("\n  重写 %d 篇" % n)


if __name__ == "__main__":
    main()
