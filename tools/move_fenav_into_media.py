# -*- coding: utf-8 -*-
"""把上一轮追加到 fe-dark.css 末尾的 series-nav 暗色覆盖，移进已有的
@media (prefers-color-scheme: dark) 块里。

为什么必须移
    fe-dark.css 的约定是：**亮色规则写在外面，暗色规则写在
    @media (prefers-color-scheme: dark) 里**。
    我上一轮直接 append 到文件末尾，等于让这几条规则在**两种模式下都生效** ——
    结果亮色模式下 FE 的系列导航也被压成了深底（实测亮暗两模式取到的
    计算样式一模一样：底 rgb(30,36,46) 字 rgb(195,207,221)）。
    用户报的是「暗色下背景是白的」，我却把亮色也改坏了。

做法
    1. 把那一段从文件末尾剪掉。
    2. 找最后一个 @media (prefers-color-scheme: dark) 块，插到它内部末尾。
    3. 自检：那几条规则必须落在 @media 里（用括号配平判断）。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets\fe-dark.css"

MARK = "/* ---------- 系列导航：暗色下的链接底色 ---------- */"


def media_span(c, start):
    """从 @media 的 '{' 起，返回 (开括号位置, 闭括号位置)，按括号配平。"""
    i = c.index("{", start)
    depth = 0
    for k in range(i, len(c)):
        if c[k] == "{":
            depth += 1
        elif c[k] == "}":
            depth -= 1
            if depth == 0:
                return i, k
    return i, len(c) - 1


def main():
    c = io.open(P, encoding="utf-8").read()
    i = c.find(MARK)
    if i < 0:
        print("  没找到要移动的那段（可能已处理过）")
        return

    block = c[i:].rstrip() + "\n"
    c2 = c[:i].rstrip() + "\n"
    print("  剪出 %d 字符" % len(block))

    # 缩进成 @media 内部的样子（+2 空格）
    indented = "\n".join(("  " + l) if l.strip() else l
                         for l in block.rstrip().split("\n")) + "\n"

    # 找最后一个 prefers-color-scheme: dark 块
    hits = [m for m in re.finditer(r'@media\s*\(prefers-color-scheme:\s*dark\)\s*\{', c2)]
    if not hits:
        print("  !! 找不到 prefers-color-scheme: dark 块")
        return
    last = hits[-1]
    _, close = media_span(c2, last.start())
    print("  最后一个暗色块：起始 %d，闭合 } 在 %d" % (last.start(), close))

    c3 = c2[:close].rstrip() + "\n\n" + indented + c2[close:]
    io.open(P, "w", encoding="utf-8", newline="\n").write(c3)

    # ---- 自检：规则确实在 @media 内部 ----
    c4 = io.open(P, encoding="utf-8").read()
    j = c4.find(MARK)
    inside = False
    for m in re.finditer(r'@media\s*\(prefers-color-scheme:\s*dark\)\s*\{', c4):
        _, cl = media_span(c4, m.start())
        if m.start() < j < cl:
            inside = True
            break
    print()
    print("  自检：该段落在暗色 @media 内 = %s" % ("是 OK" if inside else "否 !!"))


if __name__ == "__main__":
    main()
