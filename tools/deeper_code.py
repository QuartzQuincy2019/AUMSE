# -*- coding: utf-8 -*-
"""F 系列代码区：配色「加深 + 提亮」。

上一版的问题是整体偏灰、不够实：
  · 代码底 #0b1220 还是「深蓝灰」，压在浅蓝网格上不够沉
  · 正文 #eaf1fb 偏灰白，高亮色（关键字紫、字符串绿）饱和度也不够
  · 结果整块看起来「灰蒙蒙的浅」

这一版：
  · 代码底压到近黑 #010409（不再偏灰）
  · 正文提到 #f8fbff（近纯白）
  · 全部高亮色改用高饱和、高亮的色板
  · 终端块同步加深
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

OLD_HEAD = "/* ===== F 系列：代码区加强对比 ===== */"
NEW_HEAD = "/* ===== F 系列：代码区配色（深底亮字 + 高饱和高亮）===== */"

# 用正则整体替换旧的加强块（从旧标记到该 <style> 结束）
OLD_BLOCK_RE = re.compile(
    r"/\* ===== F 系列：代码区加强对比 ===== \*/.*?(?=</style>)", re.S)

NEW_BLOCK = NEW_HEAD + """
/* ---- 代码块：近黑底，把「这是代码」和浅蓝网格彻底分开 ----
   注意：F 系列主题里有一条
     body.fseries main>.code-wrap{background-color:#fff}   (0,2,2)
   它的优先级高于 body.fseries .code-wrap            (0,2,1)，
   所以这里必须把选择器写成同样带 main> 的形式，否则白底会赢。 */
body.fseries main>.code-wrap,
body.fseries .card .code-wrap,
body.fseries .code-wrap{
  background-color:#010409;
  border:1px solid #33486b;
  border-left:5px solid #4d8dfb;
  box-shadow:0 2px 10px rgba(8,15,30,.22);
}
body.fseries main>.code-wrap:hover,
body.fseries .card .code-wrap:hover,
body.fseries .code-wrap:hover{
  border-color:#45608f;
  border-left-color:#7db0ff;
  box-shadow:0 10px 30px rgba(8,15,30,.34);
}
body.fseries .code-wrap .bar{
  background-color:#0d1526;
  border-bottom:1px solid #26364f;
  color:#c6d4e8;
}
body.fseries .code-wrap .bar .cp{
  background-color:#1a2740;border-color:#3a5378;color:#dce8f8;
}
body.fseries .code-wrap .bar .cp:hover{
  background-color:#243454;color:#ffffff;border-color:#5b7cae;
}

/* ---- 正文：近纯白，和小字号的灰拉开 ---- */
body.fseries .code-wrap pre{color:#f8fbff;font-weight:500}

/* ---- 高亮色板：全部提到高饱和、高亮 ---- */
body.fseries .code-wrap pre .hl-k{color:#e2b8ff}   /* 关键字  紫 */
body.fseries .code-wrap pre .hl-f{color:#8fc4ff}   /* 函数    蓝 */
body.fseries .code-wrap pre .hl-n{color:#ffb066}   /* 数字    橙 */
body.fseries .code-wrap pre .hl-s{color:#95f2a8}   /* 字符串  绿 */
body.fseries .code-wrap pre .hl-p{color:#7ee7ff}   /* 预处理  青 */
body.fseries .code-wrap pre .hl-c{color:#9fb0c9}   /* 注释    灰蓝 */
body.fseries .code-wrap pre .hl-b{color:#ff9ec4}   /* 加粗    粉 */
body.fseries .code-wrap pre .arw{color:#ffd75e}
body.fseries .code-wrap pre .arw2{color:#8fc4ff}
body.fseries .code-wrap pre .hl-bad{color:#ff8f8f;font-weight:700}
body.fseries .code-wrap pre .hl-ok{color:#8dfab0;font-weight:700}

/* ---- 运行结果：比代码再深一档，绿色边条更实 ----
   同样要带 main> ，压过主题里那条白色的 main>.out-wrap */
body.fseries main>.out-wrap,
body.fseries .card .out-wrap,
body.fseries .out-wrap{
  background-color:#000206;
  border:1px solid #26364f;
  border-left:5px solid #34e07a;
  box-shadow:0 2px 10px rgba(8,15,30,.20);
}
body.fseries main>.out-wrap:hover,
body.fseries .card .out-wrap:hover,
body.fseries .out-wrap:hover{
  border-left-color:#5cf59a;
  box-shadow:0 10px 26px rgba(8,15,30,.30);
}
body.fseries main>.out-wrap .cap,
body.fseries .out-wrap .cap{
  background-color:#071019;border-bottom-color:#26364f;color:#9db0c8;
}
body.fseries main>.out-wrap pre,
body.fseries .card .out-wrap pre,
body.fseries .out-wrap pre{color:#c9f7dc}

/* ---- 终端窗口：同样保证深底（它也可能嵌在 .card 里）---- */
body.fseries .term,
body.fseries .card .term,
body.fseries main>.term{
  background-color:#010409;
  border:1px solid #33486b;
  border-left:5px solid #4d8dfb;
}
body.fseries .term:hover,
body.fseries .card .term:hover{border-left-color:#7db0ff}
body.fseries .term .tbar,
body.fseries .card .term .tbar{
  background-color:#0d1526;border-bottom-color:#26364f;color:#c6d4e8;
  font-family:var(--mono);font-size:11.5px;
}
body.fseries .term pre,
body.fseries .card .term pre{
  color:#f8fbff !important;
  font-family:var(--mono) !important;
  font-size:13.5px !important;
  line-height:1.7 !important;
  background-color:transparent !important;
  border:0 !important;
  padding:12px 14px !important;
  margin:0 !important;
}
body.fseries .term .pr{color:#7cf59a}
body.fseries .term .cmd{color:#ffffff;font-weight:600}
body.fseries .term .out{color:#cfe0f2}
body.fseries .term .warn{color:#ffd75e}
body.fseries .term .err{color:#ff9090}

/* ---- 内嵌小代码片（卡片里的 pre）同步用深底亮字 ---- */
body.fseries .card pre,
body.fseries .mnemonic pre,
body.fseries p pre,
body.fseries .qa pre,
body.fseries .cpp-note pre{
  background-color:#010409 !important;
  border:1px solid #33486b !important;
  color:#f8fbff !important;
}
body.fseries .card pre .hl-k,
body.fseries .mnemonic pre .hl-k,
body.fseries .qa pre .hl-k,
body.fseries .cpp-note pre .hl-k{color:#e2b8ff}
body.fseries .card pre .hl-f,
body.fseries .mnemonic pre .hl-f,
body.fseries .qa pre .hl-f,
body.fseries .cpp-note pre .hl-f{color:#8fc4ff}
body.fseries .card pre .hl-s,
body.fseries .mnemonic pre .hl-s,
body.fseries .qa pre .hl-s,
body.fseries .cpp-note pre .hl-s{color:#95f2a8}
body.fseries .card pre .hl-c,
body.fseries .mnemonic pre .hl-c,
body.fseries .qa pre .hl-c,
body.fseries .cpp-note pre .hl-c{color:#9fb0c9}
body.fseries .card pre .hl-n,
body.fseries .mnemonic pre .hl-n,
body.fseries .qa pre .hl-n,
body.fseries .cpp-note pre .hl-n{color:#ffb066}
body.fseries .card pre .hl-p,
body.fseries .mnemonic pre .hl-p,
body.fseries .qa pre .hl-p,
body.fseries .cpp-note pre .hl-p{color:#7ee7ff}

/* ---- 行内 code：浅底上加深，别发灰 ---- */
body.fseries code{
  background:#dbe8f8;border-color:#b6cdea;color:#06357a;font-weight:600;
}

/* ---- 命令卡片里的小代码片（F01 用的 div.e，不是 pre）---- */
body.fseries .cmds .c .e{
  background-color:#010409;border:1px solid #33486b;color:#f8fbff;
  font-weight:500;
}
"""


def apply(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    if "fseries" not in t:
        return "非 F 系列，跳过"

    # 两种旧块都要能替换掉
    for mark in ("/* ===== F 系列：代码区加强对比 ===== */",
                 "/* ===== F 系列：代码区配色（深底亮字 + 高饱和高亮）===== */"):
        if mark in t:
            t = re.sub(re.escape(mark) + r".*?(?=</style>)", NEW_BLOCK, t, count=1, flags=re.S)
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(t)
            return "代码区配色已更新（替换旧块）"

    # 都没有：直接插入（放在 </head> 前，优先级足够）
    t = t.replace("</head>", "<style>" + NEW_BLOCK + "</style>\n</head>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    return "代码区配色已插入"


if __name__ == "__main__":
    n = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        p = os.path.join(ROOT, name)
        with io.open(p, encoding="utf-8") as fh:
            if "fseries" not in fh.read():
                continue
        print("%-46s %s" % (name, apply(p)))
        n += 1
    print("共处理 %d 篇" % n)
