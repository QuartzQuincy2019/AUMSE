# -*- coding: utf-8 -*-
"""精确标注「重点」★ —— 最终版。

前几版踩过的坑，都记在这里：
  1. 用 <h[234]>(.*?)</h\\1> 非贪婪匹配 —— 标题里含别的元素时会跨太远，
     把中间内容当标题，星插错位置。
  2. 数嵌套配平 —— 遇到孤立的闭合标签会迷路，只找到一部分标题。
  3. 正序遍历 + 插入 —— 插入会改变后面元素的偏移，
     后续用的 start/end 已过期，越插越乱。
  4. 只认 <span class="n"> —— 会漏掉「3.5 为什么…」这种纯文本编号的标题。

这版的原则：
  * 只用**开标签位置 + 最近一个 </h2>** 定位，不做嵌套计数。
  * 标记只插在**开标签之后、<span class="n"> 之前**，位置好算。
  * 所有插入**从后往前**做，偏移不失效。
  * 可重复运行：先清掉旧标记再重标。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

PLAN = {
    "f02-paths-and-env.html": {
        "keys": ["1绝对路径与相对路径", "8另一种宏"],
    },
    "t02-unicode-and-encoding.html": {
        "keys": ["2码位：字符的编号", "3UTF-8 的字节规律",
                 "3.5 为什么设计成变长", "5三种 UTF 编码"],
    },
    "f01-command-prompt.html": {
        "keys": ["4最该先会的几条命令"],
    },
    "f03-compile-and-link.html": {
        "keys": ["1从源码到程序的三步", "3编译：各自翻译", "4链接：拼起来",
                 "5头文件为什么存在", "7库：静态库与动态库"],
        "optional": ["8手把手"],
    },
    "m09-vector-and-array.html": {
        "keys": ["2vector：会自己长大的数组", "3常用操作", "4size 与 capacity"],
    },
    "fe-06.html": {
        "keys": ["2writing-mode 是什么", "3vertical-lr：竖向排版",
                 "5word-break 与换行控制"],
    },
    "fe-03-F01.html": {
        "keys": ["2十六进制 RGB", "5Alpha 通道"],
    },
    "fe-04.html": {
        "all_h2": True,
    },
}

STAR = '<span class="key-mark" title="重点内容">★</span>'
HINT = '<span class="key-hint">纯选修，可跳过</span>'
STYLE = """
.key-mark{display:inline-block;margin-right:8px;color:#c8901a;font-size:15px;
  vertical-align:1px;cursor:help}
.key-hint{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;
  font-size:11px;font-weight:600;background:#eef2f8;border:1px solid var(--line-2);
  color:var(--fg-3);vertical-align:2px;font-family:var(--sans)}
"""


def h_blocks(html, lo, hi):
    """<main> 里每个 h2/h3/h4 的开标签区间 + 标题纯文本。

    用「开标签位置 + 最近一个同名闭合标签」定位，不数嵌套 ——
    数嵌套遇到孤立的闭合标签会迷路。
    """
    out = []
    for m in re.compile(r'<(h[234])(\s[^>]*)?>', re.I).finditer(html, lo, hi):
        tag = m.group(1).lower()
        c = html.find("</%s>" % tag, m.end(), hi)
        if c < 0:
            continue
        inner = html[m.end():c]
        text = re.sub(r'<[^>]+>', '', inner).replace("&nbsp;", " ").strip()
        out.append({"tag": tag, "inner_start": m.end(), "inner_end": c,
                    "text": text.replace("★", "").strip()})
    return out


def h2_blocks(html, lo, hi):
    return [b for b in h_blocks(html, lo, hi) if b["tag"] == "h2"]


def n_blocks(html, lo, hi):
    """带编号徽章的 h2/h3/h4（用于「纯选修」标注）。"""
    out = []
    for m in re.compile(r'<(h[234])(\s[^>]*)?>', re.I).finditer(html, lo, hi):
        tag = m.group(1).lower()
        c = html.find("</%s>" % tag, m.end(), hi)
        if c < 0:
            continue
        inner = html[m.end():c]
        if 'class="n"' not in inner:
            continue
        text = re.sub(r'<[^>]+>', '', inner).replace("&nbsp;", " ").strip()
        out.append({"inner_start": m.end(), "inner_end": c,
                    "text": text.replace("★", "").strip()})
    return out


def strip_marks(html):
    """清掉旧标记。注意先数再替换，且 ★ 只数**游离**的那些 ——
       STAR span 里已经含一个 ★，重复计数会得到虚高的数字。"""
    n = html.count(STAR) + html.count(HINT)
    html = html.replace(STAR, "").replace(HINT, "")
    stray = html.count("★")
    if stray:
        html = html.replace("★", "")
    return html, n + stray


def add_style(html):
    if "key-mark{" in html:
        return html, False
    i = html.rfind("</style>")
    if i < 0:
        return html, False
    return html[:i] + STYLE + html[i:], True



def fix_heading(html, inner_start, kind):
    """在标题的**开标签**与**内容**里各做一次修改，整体替换 —— 只改一轮。

    kind='star' → 开标签加 class="key-h"，内容最前面加 ★
    kind='hint' → 内容末尾加「纯选修」标签
    """
    lt = html.rfind("<", 0, inner_start - 1)
    gt = html.find(">", lt)
    if lt < 0 or gt < 0 or gt >= inner_start:
        return html, False
    open_tag = html[lt:gt + 1]
    inner = html[gt + 1:inner_start]

    if kind == "hint":
        if "key-hint" in inner:
            return html, False
        return html[:gt + 1] + inner + HINT + html[inner_start:], True

    if 'class="' in open_tag:
        new_open = open_tag.replace('class="', 'class="key-h ', 1)
    else:
        new_open = open_tag[:-1] + ' class="key-h">'
    new_inner = inner
    if STAR not in new_inner:
        m = re.search(r'<span class="n">', new_inner)
        pos = m.start() if m else 0
        new_inner = new_inner[:pos] + STAR + new_inner[pos:]

    if new_open == open_tag and new_inner == inner:
        return html, False
    return html[:lt] + new_open + new_inner + html[inner_start:], True


def main():
    for fn, spec in PLAN.items():
        p = os.path.join(TUT, fn)
        if not os.path.exists(p):
            print("  !! 找不到 %s" % fn)
            continue
        html = io.open(p, encoding="utf-8").read()
        html, removed = strip_marks(html)
        html, _ = add_style(html)

        ms, me = html.find("<main"), html.rfind("</main>")
        if ms < 0 or me < 0:
            print("  !! %s 找不到 main" % fn)
            continue

        targets, miss = [], []
        if spec.get("all_h2"):
            for b in h2_blocks(html, ms, me):
                targets.append((b["inner_start"], b["inner_end"], "star"))
        else:
            # 关键词按完整层级（h2/h3/h4）查找 —— 用户指的重点有些落在小节上，
            # 比如 Unicode 的「编码和变长编码规则」对应的就是 3.5 那个 h3。
            blocks = h_blocks(html, ms, me)
            def norm(s):
                return s.replace(" ", "").replace("\u3000", "")
            for key in spec.get("keys", []):
                k = norm(key)
                hit = next((b for b in blocks if norm(b["text"]).startswith(k)), None)
                if hit is None:
                    miss.append(key)
                    continue
                targets.append((hit["inner_start"], hit["inner_end"], "star"))
            for key in spec.get("optional", []):
                hit = next((b for b in n_blocks(html, ms, me)
                            if norm(b["text"]).startswith(norm(key))), None)
                if hit:
                    targets.append((hit["inner_start"], hit["inner_end"], "hint"))

        # 算出插入点，再从后往前插 —— 偏移不会失效
        ops = []
        for s, e, kind in targets:
            inner = html[s:e]
            marker = STAR if kind == "star" else HINT
            if marker in inner:
                continue
            if kind == "star":
                m = re.search(r'<span class="n">', inner)
                pos = s + (m.start() if m else 0)
            else:
                pos = e
            ops.append((pos, marker))
        # 每个标题一次性改完（开标签 + 内容），从后往前 ——
        # 分两步做会因为偏移互踩写出坏标签（见 fix_heading 注释）
        nstar = 0
        for s, e, kind in sorted(targets, key=lambda x: x[0], reverse=True):
            html, done = fix_heading(html, s, kind)
            if done and kind == "star":
                nstar += 1

        io.open(p, "w", encoding="utf-8", newline="").write(html)
        print("  %-34s ★ %-2d %s%s" % (
            fn, nstar, ("清理 %d " % removed) if removed else "",
            ("未命中: " + ", ".join(miss)) if miss else ""))


if __name__ == "__main__":
    main()
