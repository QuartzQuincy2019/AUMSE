# -*- coding: utf-8 -*-
"""FE-08《JavaScript 语法初步》—— 从正文片段生成页面。

正文放在 tools/_fe08_body.html，这个脚本只负责外壳与流水线。

走的是前端系列既有的两级流水线：
    ① build_fe.build()   把正文 + 目录套进完整页面模板
    ② 再抽成数据壳       把 <main> 里的正文存进 window.__FE_PAGE__.body
                        由 assets/fe-data.js 在运行时生成目录与整页 DOM

为什么只动 FE-08
    已有的 7 篇壳是「先转壳、后补示例」的产物 —— 直接重跑
    make_fe_shells.py 会把那些后补的示例丢掉。所以这里只处理 FE-08 一篇。

本篇的写作要求（用户指定）
  · 开篇强调 JS 的**弱类型**与**解释性**，并强调语法比 C / C++ **更简单**
  · console.log() 放在第 3 节**之前**，并强调它和 printf() 调试页面时等价
  · **不提** DOM 的「树」模型
  · 结尾用**外联**形式给出 demo.html + demo.css + demo.js 三文件项目
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build  # noqa: E402

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
TOOLS = r"E:\QKMansion\CSX10\w\UME\tools"

FN, NUM, TITLE = "fe-08.html", "FE-08", "JavaScript 语法初步"

SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>前端 · @@TITLE@@</title>
<link rel="stylesheet" href="assets/fe_base.css">
<link rel="stylesheet" href="assets/tg_L.css">
<link rel="stylesheet" href="assets/tg_D.css">
<link rel="stylesheet" href="assets/series-theme.css">
<link rel="stylesheet" href="assets/fe_08.css">
<link rel="stylesheet" href="assets/fe-dark.css">
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
<script src="assets/fe-data.js"></script>
</body>
</html>
"""


def shell_for(entries):
    """把生成的完整页面抽成数据壳（与 make_fe_shells.extract 同一套规则）。

    SHELL 用普通替换而不是 str.format —— 里面的 JS 全是花括号，
    format 会把它们当占位符报错。
    """
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

    # build_fe.FE 是 5 元组 (文件, 编号, 标题, 说明, 是否重要)。
    # 注意 make_fe_shells.py 用的是**另一个** 6 元组列表（多一个 kind 字段），
    # 两者不能混用 —— 照搬会 unpack 失败。
    data = {
        "file": FN, "num": NUM, "title": TITLE, "star": False,
        "body": body,
        "series": [{"file": f2, "num": n2, "title": t2, "star": bool(s2)}
                   for f2, n2, t2, _d2, s2 in entries],
    }
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")      # 防止正文里的 </script> 截断脚本
    out = SHELL.replace("@@TITLE@@", TITLE).replace("@@DATA@@", js)
    return out, len(body)


def main():
    body = io.open(os.path.join(TOOLS, "_fe08_body.html"),
                   encoding="utf-8").read()

    if re.search(r'<h1[\s>]', body):
        print("  !! 正文片段里有 <h1>，渲染器会再加一个 —— 请删掉")
        return

    heads = re.findall(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
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
        build_fe.FE.append((FN, NUM, TITLE,
                            "弱类型与解释性、与 C/C++ 的异同、console.log / alert / prompt",
                            False))

    # build() 会**自己写文件**（写到 TUT/fe-08.html），返回字符数而不是 HTML
    n = build(FN, NUM, TITLE, body, toc)
    print("  ① 完整页面  %d 字符" % n)

    out, blen = shell_for(build_fe.FE)
    io.open(os.path.join(TUT, FN), "w",
            encoding="utf-8", newline="").write(out)
    print("  ② 数据壳    %s  %d B（正文 %d 字符）" % (FN, len(out), blen))
    print("  ③ 小节 %d 个" % len(heads))

    # 写作要求的自检
    bad = [w for w in ('树', '节点树') if w in body]
    print("  ④ 未出现「树」的说法: %s" % ("否 !! %s" % bad if bad else "是"))
    print("     三文件项目齐备: %s"
          % all(x in body for x in ('demo.html', 'demo.css', 'demo.js')))
    print("     console.log 在第 %s 节（要求在第 3 节之前）"
          % next((num for hid, num, t in heads if 'console.log' in t), '?'))


if __name__ == "__main__":
    main()
