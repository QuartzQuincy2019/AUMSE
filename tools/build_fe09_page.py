# -*- coding: utf-8 -*-
"""FE-09《DOM 操作基础》—— 从正文片段生成页面。

正文放在 tools/_fe09_body_v2.html（改版：9 节 → 6 节，
§1 改名为「DOM 树」并扩写示例，§5 改为「与 Qt 的联系」），
这个脚本只负责外壳与流水线。
结构与 build_fe08_page.py 一致（两级流水线：完整页面 → 数据壳）。

本篇的写作要求（用户指定）
  · 三个函数：getElementById、createElement、append
  · 简单讲「DOM 树」的概念
  · 重点：把要添加的元素视作**组件（Widget）**，
    那么「向父元素添加子元素」与 Qt 的 addWidget **完全相同**

诚实声明
  · 三个 DOM 函数的行为**在浏览器里逐条实测过**（21 项断言全过），
    正文里写的返回值、isConnected、childNodes.length 都是实际结果。
  · Qt 那侧的代码**本机没有 Qt 工具链，没有编译过** ——
    它是按 Qt 文档语义写的对照，footer 里如实说明。
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build  # noqa: E402

R = r"E:\QKMansion\CSX10\w\UME"
TUT = os.path.join(R, "SharingGroup", "tutorials")
TOOLS = os.path.join(R, "tools")

FN, NUM, TITLE = "fe-09.html", "FE-09", "DOM 操作基础"
FOOTER_NOTE = ("本篇的 DOM 示例与返回值均在浏览器中实际运行核对；"
               "Qt 那段对照代码本机无 Qt 工具链，未编译，"
               "按 Qt 文档语义整理。")

DESC = "getElementById / createElement / append；DOM 树与 Qt addWidget 的对照"

SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>前端 · @@TITLE@@</title>
<link rel="stylesheet" href="assets/css/fe_base.css">
<link rel="stylesheet" href="assets/css/tg_L.css">
<link rel="stylesheet" href="assets/css/tg_D.css">
<link rel="stylesheet" href="assets/css/series-theme.css">
<link rel="stylesheet" href="assets/css/fe_09.css">
<link rel="stylesheet" href="assets/css/fe-dark.css">
</head>
<body data-series="FE">
<script>
/* 极早执行：在样式生效前就按系统偏好声明配色方案，避免亮→暗闪一下 */
(function(){var d=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;
var m=document.createElement('meta');m.name='color-scheme';
m.content=d?'dark light':'light dark';document.head.appendChild(m);})();
</script>
<noscript>
  <div style="max-width:680px;margin:60px auto;padding:0 20px;font:16px/1.8 sans-serif">
    <h1>需要开启 JavaScript</h1>
    <p>这一页的界面（目录、正文、页脚导航）由脚本动态生成，请开启 JavaScript 后刷新。</p>
    <p><a href="../../index.html">← 返回教程总目录</a></p>
  </div>
</noscript>
<script>
/* 本页数据。正文里的 <h2 id="…"> 会被渲染器自动收进左侧目录。 */
window.__FE_PAGE__ = @@DATA@@;
</script>
<script src="assets/js/fe-data.js"></script>
</body>
</html>
"""


def shell_for(entries):
    """把生成的完整页面抽成数据壳（与 make_fe_shells.extract 同一套规则）。"""
    t = io.open(os.path.join(TUT, FN), encoding="utf-8").read()
    m = re.search(r'(?s)<main[^>]*>(.*?)</main>', t)
    body = m.group(1) if m else ""
    body = re.sub(r'(?s)<h1\b[^>]*>.*?</h1>', "", body, count=1)
    body = re.sub(r'(?s)<p class="sub-title">.*?</p>', "", body, count=1)
    body = re.sub(r'(?s)<div class="page-nav">.*?</div>\s*', "", body)
    body = re.sub(r'(?s)<div class="series-nav">.*?</div>\s*', "", body)
    body = re.sub(r'(?s)<footer>.*?</footer>', "", body)
    body = re.sub(r'(?s)<!-- NAV-AUTO -->.*?<!-- /NAV-AUTO -->', "", body)
    body = body.strip()
    for bad in ('<h1', 'class="sub-title"', 'class="series-nav"',
                'class="page-nav"', 'home-fab'):
        if bad in body:
            raise SystemExit("  !! 正文里仍有 %s —— 会重复渲染" % bad)

    data = {
        "file": FN, "num": NUM, "title": TITLE, "star": True,   # 用户要求设为重点项目
        # 按篇的页脚补充（fe-data.js 会拼在公共那句之后）
        "footerNote": FOOTER_NOTE,
        "body": body,
        "series": [{"file": f2, "num": n2, "title": t2, "star": bool(s2)}
                   for f2, n2, t2, _d2, s2 in entries],
    }
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")
    out = SHELL.replace("@@TITLE@@", TITLE).replace("@@DATA@@", js)
    return out, len(body)


def main():
    body = io.open(os.path.join(TOOLS, "_fe09_body_v2.html"),
                   encoding="utf-8").read()

    if re.search(r'<h1[\s>]', body):
        print("  !! 正文片段里有 <h1>，渲染器会再加一个 —— 请删掉")
        return

    heads = re.findall(r'<h2[^>]*id="(s\d+)"[^>]*>(?:<span class="key-mark"[^>]*>[^<]*</span>)?<span class="n">(\d+)</span>(?:<span class="key-mark"[^>]*>[^<]*</span>)?(.*?)</h2>',
                       body, re.S)
    ids = [h[0] for h in heads]
    nos = [int(h[1]) for h in heads]
    if ids != ["s%d" % i for i in range(1, len(ids) + 1)] or \
       nos != list(range(1, len(ids) + 1)):
        print("  !! 小节 id / 编号不连续：%s / %s" % (ids, nos))
        return

    toc = "\n".join('  <a href="#%s">%s · %s</a>'
                    % (hid, num, re.sub(r'<[^>]+>', '', title).strip())
                    for hid, num, title in heads)

    import build_fe
    if not any(m[0] == FN for m in build_fe.FE):
        build_fe.FE.append((FN, NUM, TITLE, DESC, True))
    # FE-09 要排在 FE-08 之后
    build_fe.FE.sort(key=lambda m: m[0])

    n = build(FN, NUM, TITLE, body, toc)
    print("  ① 完整页面  %d 字符" % n)

    out, blen = shell_for(build_fe.FE)
    io.open(os.path.join(TUT, FN), "w",
            encoding="utf-8", newline="").write(out)
    print("  ② 数据壳    %s  %d B（正文 %d 字符）" % (FN, len(out), blen))
    print("  ③ 小节 %d 个：%s" % (len(heads),
                                 " ".join(h[1] for h in heads)))

    # 写作要求自检
    three = all(x in body for x in ('getElementById', 'createElement',
                                    '.append('))
    print("  ④ 三个函数都在: %s" % ("是" if three else "否 !!"))
    qt = all(x in body for x in ('addWidget', 'Widget', 'layout'))
    print("     提到 Qt 对照（addWidget / Widget / layout）: %s"
          % ("是" if qt else "否 !!"))
    print("     DOM 树: %s" % ("有" if 'DOM 树' in body else "否 !!"))
    # 不该出现的（这一篇不做事件，别顺手带出来）
    for w in ('addEventListener', 'querySelector'):
        if w in body:
            print("     ⚠ 正文里出现了 %s（本篇范围外）" % w)


if __name__ == "__main__":
    main()
