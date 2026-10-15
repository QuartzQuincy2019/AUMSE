# -*- coding: utf-8 -*-
"""修正 F 系列的两个问题：

1. .term 嵌在 .card 里时，`body.fseries .card pre`(0,3,1) 的优先级高于
   `body.fseries .term pre`(0,2,1)，把字号和字体一起覆盖了 ——
   结果卡片里的终端窗口变成 16px 的默认 monospace。
   办法：把 .term 的选择器也提到同样层级，并显式声明字体。

2. 顺手把所有终端 / 代码区的 font-family 都用显式字体栈写死，
   不再只靠 var(--mono) 继承，避免以后同类问题。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

OLD = """/* 终端窗口：加深底色、亮化文字，与代码块风格统一 */
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
body.fseries .term .err{color:#ff8b8b}"""

NEW = """/* 终端窗口：加深底色、亮化文字，与代码块风格统一。
   注意：.term 有时嵌在 .card 里，而上面那条 `body.fseries .card pre`
   优先级更高，会连带把字号/字体覆盖掉。这里把选择器提到同一层级
   （都带上 .card 变体），并显式写死字体栈。 */
body.fseries .term,
body.fseries .card .term{
  background-color:#060b14;
  border:1px solid #2a3a55;
  border-left:4px solid #4d8dfb;
}
body.fseries .term:hover,
body.fseries .card .term:hover{border-left-color:#6ba4ff}

body.fseries .term .tbar,
body.fseries .card .term .tbar{
  background:#151f33;border-bottom-color:#2a3a55;color:#9fb4d0;
  font-family:var(--mono);font-size:11.5px;
}

body.fseries .term pre,
body.fseries .card .term pre{
  color:#e6eef8 !important;
  font-family:var(--mono) !important;
  font-size:13.5px !important;
  line-height:1.7 !important;
  background-color:transparent !important;
  border:0 !important;
  padding:12px 14px !important;
  margin:0 !important;
}

body.fseries .term .pr{color:#8ff0a4}
body.fseries .term .cmd{color:#ffffff;font-weight:600}
body.fseries .term .out{color:#b9cbe0}
body.fseries .term .warn{color:#ffd479}
body.fseries .term .err{color:#ff8b8b}"""


def apply(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    if "body.fseries .card .term" in t:
        return "已修正，跳过"
    if OLD not in t:
        return "未找到待替换片段（可能结构不同）"
    t = t.replace(OLD, NEW, 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    return "已修正 .term 优先级与字体"


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
    print("共处理 %d 个" % n)
