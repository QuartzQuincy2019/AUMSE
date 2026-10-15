# -*- coding: utf-8 -*-
"""给 08-F01 ~ 09-F04 这几篇「与本项目关系密切」的文档加上不同的背景色。

做法：在每个 F 文档的 <body> 上加 class="fseries"，
再追加一段覆盖样式的 <style>。为了不影响全局，覆盖只针对 body 背景、
目录底色、卡片底色与代码块头部，正文对比度保持原样。

主题定为「蓝图感」：冷调浅蓝灰 + 细网格 + 左侧色条，
一眼能看出「这是实用工具类文档」，与前面的语言教程区分开。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

THEME = """
/* ===== F 系列主题：与本项目施行密切相关的实用文档 ===== */
body.fseries{
  --f-bg:#eef3f9;
  --f-grid:rgba(31,111,235,.055);
  background-color:var(--f-bg);
  background-image:
    linear-gradient(var(--f-grid) 1px,transparent 1px),
    linear-gradient(90deg,var(--f-grid) 1px,transparent 1px);
  background-size:26px 26px;
}
body.fseries #toc{background:#e4ecf6;border-right-color:#c8d8ea}
body.fseries main{padding-top:52px}
/* 顶部一条明显的标记，说明这是 F 系列 */
body.fseries::before{
  content:"F 系列 · 与本项目施行密切相关";
  position:fixed;top:0;left:0;right:0;z-index:80;
  padding:5px 14px;font:600 12px/1.5 var(--sans);
  color:#fff;background:#1f6feb;letter-spacing:.02em;
  box-shadow:0 1px 6px rgba(31,111,235,.28);
}
body.fseries h1{margin-top:6px}
body.fseries h2 .n{background:#1f6feb}
/* 正文与卡片：在网格背景上给一层白，保证可读性 */
body.fseries main>.card,
body.fseries main>.code-wrap,
body.fseries main>.out-wrap,
body.fseries main>table,
body.fseries main>.mnemonic,
body.fseries main>.flow,
body.fseries main>.qa{
  background-color:#fff;
}
body.fseries .card.note{background-color:var(--blue-soft)}
body.fseries .card.tip{background-color:var(--green-soft)}
body.fseries .card.warn{background-color:var(--red-soft)}
body.fseries .card.key{background-color:var(--violet-soft)}
body.fseries .card.teal{background-color:var(--teal-soft)}
body.fseries .mnemonic{background-color:var(--amber-soft)}
body.fseries .code-wrap{background-color:var(--bg-code)}
body.fseries .out-wrap{background-color:var(--bg-out)}
/* 移动端：顶部条会挡住目录按钮，把按钮下移 */
@media (max-width:980px){
  body.fseries::before{font-size:11px;padding:4px 10px}
  body.fseries #tocToggle{top:34px}
  body.fseries main{padding-top:72px}
  body.fseries #toc{padding-top:80px}
  body.fseries html{scroll-padding-top:96px}
}
@media print{
  body.fseries{background:#fff}
  body.fseries::before{position:static;display:block;background:#fff;color:#000;
    border-bottom:1px solid #999}
}
"""

MARK = "/* ===== F 系列主题"


def apply(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    if MARK in t:
        return "已打过主题，跳过"
    if "<body>" not in t:
        return "找不到 <body>，跳过"
    t = t.replace("<body>", '<body class="fseries">', 1)
    t = t.replace("</head>", "<style>" + THEME + "</style>\n</head>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    return "已加 F 系列主题"


if __name__ == "__main__":
    targets = [a for a in sys.argv[1:] if a]
    if not targets:
        targets = [f for f in os.listdir(ROOT) if "-F" in f and f.endswith(".html")]
    for name in targets:
        p = name if os.path.isabs(name) else os.path.join(ROOT, name)
        if not os.path.exists(p):
            print("%-46s 不存在" % os.path.basename(p))
            continue
        print("%-46s %s" % (os.path.basename(p), apply(p)))
