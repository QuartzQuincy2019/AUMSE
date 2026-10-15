# -*- coding: utf-8 -*-
"""给 F 系列文档增强「代码区」的颜色区分度。

问题：F 系列的页面底色是浅蓝网格，而代码块用的是原来的深蓝灰
(#1e2430)，在浅底上边界不清晰、整体偏「糊」。

做法：把 F 系列里的代码区换成更深的蓝黑底，并把高亮色整体提亮一档，
再给一层明显的边框和左侧强调条，让「这段是代码」一眼可辨。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

MARK = "/* ===== F 系列：代码区加强对比 ===== */"

EXTRA = MARK + """
/* 代码块：更深的底 + 明显的边框 + 左侧强调条 */
body.fseries .code-wrap{
  background-color:#0b1220;
  border:1px solid #2a3a55;
  border-left:4px solid #4d8dfb;
  box-shadow:0 1px 0 rgba(255,255,255,.7) inset, 0 2px 8px rgba(15,25,45,.10);
}
body.fseries .code-wrap:hover{
  border-color:#3d5580;
  border-left-color:#6ba4ff;
  box-shadow:0 8px 26px rgba(15,25,45,.24);
}
body.fseries .code-wrap .bar{
  background:#151f33;
  border-bottom:1px solid #2a3a55;
  color:#9fb4d0;
}
body.fseries .code-wrap .bar .cp{
  background:#1c2942;border-color:#33456a;color:#b6c8e2;
}
body.fseries .code-wrap .bar .cp:hover{
  background:#26364f;color:#eaf2ff;border-color:#4a6191;
}
/* 正文用更亮的字色，和深底拉开距离 */
body.fseries .code-wrap pre{color:#eaf1fb}
body.fseries .code-wrap pre .hl-k{color:#d7b0ff}
body.fseries .code-wrap pre .hl-n{color:#ffa76b}
body.fseries .code-wrap pre .hl-s{color:#a8e6a3}
body.fseries .code-wrap pre .hl-c{color:#8d9fb8}
body.fseries .code-wrap pre .hl-f{color:#9dc4ff}
body.fseries .code-wrap pre .hl-p{color:#8ce1ff}
body.fseries .code-wrap pre .arw{color:#ffd479}
body.fseries .code-wrap pre .arw2{color:#9dc4ff}
body.fseries .code-wrap pre .hl-bad{color:#ff8b8b}
body.fseries .code-wrap pre .hl-ok{color:#8ff0a4}
body.fseries .code-wrap pre .hl-bad,
body.fseries .code-wrap pre .hl-ok{font-weight:700}

/* 运行结果：底色再深一点、绿色边条更亮，与代码块区分开 */
body.fseries .out-wrap{
  background-color:#060b14;
  border:1px solid #23324a;
  border-left:4px solid #3ddc84;
  box-shadow:0 2px 8px rgba(15,25,45,.10);
}
body.fseries .out-wrap:hover{
  border-left-color:#5ef29c;
  box-shadow:0 8px 22px rgba(15,25,45,.20);
}
body.fseries .out-wrap .cap{background:#0d1626;border-bottom-color:#23324a;color:#8ba0bb}
body.fseries .out-wrap pre{color:#c6f0d8}

/* 内嵌的小代码片（pre 直接写在文档里那些）也要拉开对比 */
body.fseries .card pre,
body.fseries .mnemonic pre,
body.fseries p pre,
body.fseries .qa pre{
  background-color:#0b1220 !important;
  border:1px solid #2a3a55 !important;
  color:#eaf1fb !important;
}
body.fseries .card pre .hl-c,
body.fseries .mnemonic pre .hl-c,
body.fseries .qa pre .hl-c{color:#8d9fb8}
body.fseries .card pre .hl-k,
body.fseries .mnemonic pre .hl-k,
body.fseries .qa pre .hl-k{color:#d7b0ff}
body.fseries .card pre .hl-f,
body.fseries .mnemonic pre .hl-f,
body.fseries .qa pre .hl-f{color:#9dc4ff}
body.fseries .card pre .hl-s,
body.fseries .mnemonic pre .hl-s,
body.fseries .qa pre .hl-s{color:#a8e6a3}
body.fseries .card pre .hl-n,
body.fseries .mnemonic pre .hl-n,
body.fseries .qa pre .hl-n{color:#ffa76b}

/* 终端窗口：加深底色、亮化文字，与代码块风格统一 */
body.fseries .term{
  background-color:#060b14;
  border:1px solid #2a3a55;
  border-left:4px solid #4d8dfb;
}
body.fseries .term:hover{border-left-color:#6ba4ff}
body.fseries .term .tbar{background:#151f33;border-bottom-color:#2a3a55;color:#9fb4d0}
body.fseries .term pre{color:#e6eef8}
body.fseries .term .pr{color:#8ff0a4}
body.fseries .term .cmd{color:#ffffff;font-weight:600}
body.fseries .term .out{color:#b9cbe0}
body.fseries .term .warn{color:#ffd479}
body.fseries .term .err{color:#ff8b8b}

/* 行内 code 在浅底上也要看得清 */
body.fseries code{background:#e3ecf8;border-color:#c3d6ee;color:#0a3f86}
"""


def apply(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    if MARK in t:
        return "已有加强样式，跳过"
    if "fseries" not in t:
        return "不是 F 系列，跳过"
    t = t.replace("</head>", "<style>" + EXTRA + "</style>\n</head>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    return "已加强代码区对比"


if __name__ == "__main__":
    n = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        p = os.path.join(ROOT, name)
        with io.open(p, encoding="utf-8") as fh:
            head = fh.read(400000)
        if "fseries" not in head:
            continue
        print("%-46s %s" % (name, apply(p)))
        n += 1
    print("共处理 %d 个 F 系列文档" % n)
