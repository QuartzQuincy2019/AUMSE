# -*- coding: utf-8 -*-
"""修复移动端横向溢出：长且不可断的路径字号串撑宽了表格与终端块。

原因：表格单元格和终端输出里有
  D:\\Path\\To\\project\\build\\path1.exe
这类「没有空格的长串」，浏览器默认不在其中断行，
于是最小内容宽度就变成了 700 多像素，扛破了 375px 的视口。

做法：在移动端断点里允许在长串内部断行。
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"

MARK = "/* ===== 移动端：长路径字符串断行 ====="

CSS = MARK + """
/* 长且无空格的串（路径、命令、变量名）在窄屏上必须允许内部断行，
   否则会把表格和终端块撑得比视口还宽。 */
@media (max-width:980px){
  main table th,
  main table td,
  main table td code,
  main table th code,
  main table td .c,
  main td,
  main th{
    overflow-wrap:anywhere;
    word-break:break-word;
  }
  /* 表头文字允许换行 */
  main table th{white-space:normal}

  /* 终端块里的提示符与输出 */
  .term pre,
  .term .pr,
  .term .cmd,
  .term .out,
  .term .warn,
  .term .err{
    overflow-wrap:anywhere;
    word-break:break-word;
    white-space:pre-wrap;
  }
  /* 行内 code 也别撑宽 */
  main p code,
  main li code,
  main td code,
  .card code{
    overflow-wrap:anywhere;
    word-break:break-word;
  }
}
"""


def apply(path):
    with io.open(path, encoding="utf-8") as fh:
        t = fh.read()
    if MARK in t:
        return "已有，跳过"
    t = t.replace("</head>", "<style>" + CSS + "</style>\n</head>", 1)
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    return "已加长串断行规则"


if __name__ == "__main__":
    n = 0
    for name in sorted(os.listdir(ROOT)):
        if not name.endswith(".html"):
            continue
        p = os.path.join(ROOT, name)
        print("%-46s %s" % (name, apply(p)))
        n += 1
    print("共处理 %d 篇" % n)
