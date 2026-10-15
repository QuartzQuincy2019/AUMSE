# -*- coding: utf-8 -*-
"""修复 CSS 分离引入的顺序 bug（直接重排 assets/tutorial.css）。

问题现象（手机端）：
    #toc 仍是 position:sticky + height:100vh，留在文档流里占满一屏，
    把 main 推到 667px 之下 —— 页面顶部出现一个视口高的空白。

根因：
    上一版分离脚本按「规则出现在多少篇」分区，并且是逐篇处理，
    于是基础规则（@media 之外）被追加到了 @media 块**之后**：

        … @media(max-width:980px){ … } …        ← 媒体查询
        … #toc{position:sticky;height:100vh}    ← 桌面基础规则，却在后面

    两者选择器优先级相同（#toc），**后写的赢**，
    所以手机端拿到的是桌面布局。

修法：
    只调顺序，不动内容 ——
      1. 所有非 @media 规则（保持原有相对顺序）
      2. 所有 @media 块（保持原有相对顺序）
    这样媒体查询一定在基础规则之后，窄屏覆盖才能生效。
"""
import io
import os
import re
import sys
from collections import OrderedDict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ASSETS = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
CSS = os.path.join(ASSETS, "tutorial.css")


def split_rules(css):
    """切成 [(comment, rule), ...]；@media / @supports 整块算一条。

    注意：原文档里存在**嵌套写法的注释**（一个 /* 里还含 /* ... */），
    例如
        /* ===== 移动端增强 ===== */
        /* 说明…… */
        @media ... { }
    如果只取「第一个 /* 到第一个 */」，会把第一个注释**截断**，
    剩下的碎片会带上后面的 @media，被误判成普通规则 ——
    顺序就再也排不对了。

    所以这里把「连续的多个注释」一起收下，直到遇到真正的规则为止。
    """
    out, i, n = [], 0, len(css)
    while i < n:
        while i < n and css[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
        # ---- 收下连续的注释（可能不止一个）----
        comments = []
        while css.startswith("/*", i):
            j = css.find("*/", i + 2)
            if j < 0:
                break
            comments.append(css[i:j + 2])
            i = j + 2
            while i < n and css[i] in " \t\r\n":
                i += 1
        if i >= n:
            break
        # ---- 取规则 ----
        if css[i] == "@":
            k = css.find("{", i)
            if k < 0:
                break
            depth, j = 1, k + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            rule, i = css[i:j], j
        else:
            j = css.find("}", i)
            if j < 0:
                break
            rule, i = css[i:j + 1], j + 1
        out.append(("\n".join(comments) if comments else None, rule))
    return out


def main():
    t = io.open(CSS, encoding="utf-8").read()
    orig_len = len(t)

    # 顶部的大段注释单拎出来（它是设计系统说明）
    m = re.match(r'\s*/\* =+\s*\n.*?\n\s*=+ \*/', t, re.S)
    if m:
        header = m.group(0).strip()
        body = t[m.end():]
    else:
        header, body = "", t

    items = split_rules(body)
    normal, media = [], []
    seen = set()
    for comment, rule in items:
        key = re.sub(r'\s+', ' ', rule).strip()
        if key in seen:
            continue
        seen.add(key)
        text = ((comment or "") + rule).strip()
        # 注意：条目可能是「注释 + @media 块」，所以要看 rule 本身，
        # 而且允许 @media 前面有空白。
        is_media = rule.lstrip().startswith("@")
        (media if is_media else normal).append(text)

    new = ((header + "\n\n") if header else "") + \
          "\n\n".join(normal + media) + "\n"

    # ---- 顺序校验：不通过就不写盘 ----
    i_first_media = new.find("@media")
    i_base = new.find('#toc{position:sticky')
    i_draw = new.find('display:block !important')
    print("tutorial.css: %d → %d 字符" % (orig_len, len(new)))
    print("  非 @media 规则 %d 条，@media 块 %d 个" % (len(normal), len(media)))
    print("")
    print("  基础 #toc{position:sticky} 位置 : %d" % i_base)
    print("  第一条 @media 位置             : %d" % i_first_media)
    print("  移动端 #toc 抽屉规则位置        : %d" % i_draw)
    ok = 0 <= i_base < i_first_media < i_draw
    print("  → %s" % ("顺序正确：基础 → @media → 抽屉覆盖" if ok
                      else "顺序仍不对"))
    if not ok:
        print("\n  未写盘。诊断：@media 是否被误判为普通规则")
        for k, v in list(media.items() if isinstance(media, dict) else []):
            pass
        for text in media[:8]:
            print("    media[%d] 开头: %r" % (media.index(text), text[:60]))
        print("    normal 里以 @ 开头的条数: %d"
              % sum(1 for x in normal if '@media' in x))
        for x in normal:
            if '@media' in x:
                print("      %r" % x[:80])
        return

    io.open(CSS, "w", encoding="utf-8", newline="\n").write(new)
    print("")
    print("  已写盘。@media 块顺序：")
    for mm in re.finditer(r'@media[^{]*', new):
        print("    " + mm.group(0).strip())
    return


if __name__ == "__main__":
    main()
