# -*- coding: utf-8 -*-
"""前端系列的示例展示辅助。

用法（在内容脚本里）：
    from fe_kit import pv, code, fmt_css
    pv(1, "标题", ".sel { color: red; }", demo="<div class='sel'>…</div>")

pv() 会自动把压缩写的 CSS 排成三行式（选择器 / 缩进声明 / }），
见 fmt_css()。
"""
import re

_CP = '<span class="cp">复制</span>'


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def hl(src):
    """极简高亮：HTML 标签着成紫色，CSS 注释着成灰色。只用于代码展示。"""
    out = []
    for line in src.split("\n"):
        line = re.sub(r'(/\*.*?\*/)',
                      lambda m: '\x01' + m.group(1) + '\x01', line)
        line = re.sub(r'(&lt;/?[a-zA-Z][^&]*?&gt;)',
                      r'<span class="hl-p">\1</span>', line)
        out.append(line)
    s = "\n".join(out)
    return re.sub(r'\x01(.*?)\x01', r'<span class="hl-c">\1</span>', s)


# ---------------------------------------------------------------------
# CSS 排版：压缩写法 → 三行式
# ---------------------------------------------------------------------
def _fmt_decls(decl, pad):
    """'a:b;c:d' → 多行声明，冒号后加空格。"""
    lines = []
    for part in decl.split(";"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            k, v = part.split(":", 1)
            lines.append("%s%s: %s;" % (pad, k.strip(), v.strip()))
        else:
            lines.append("%s%s;" % (pad, part))
    return "\n".join(lines)


def _fmt_rule(sel, body, pad=""):
    body = body.strip()
    inner_ind = pad + "    "
    if "{" not in body:
        return "%s%s {\n%s\n%s}" % (pad, sel, _fmt_decls(body, inner_ind), pad)

    # 含嵌套（@media 之类）
    lines = []
    first = body.find("{")
    head = body[:first]
    cut = head.rfind(";")
    if cut >= 0:
        decl = head[:cut + 1]
        if decl.strip():
            lines.append(_fmt_decls(decl, inner_ind))
        rest = head[cut + 1:] + body[first:]
    else:
        rest = body
    j = 0
    while j < len(rest):
        b = rest.find("{", j)
        if b < 0:
            break
        s = rest.rfind("}", j, b)
        s = s + 1 if s >= 0 else j
        sel2 = rest[s:b].strip()
        depth, k = 1, b + 1
        while k < len(rest) and depth:
            if rest[k] == "{":
                depth += 1
            elif rest[k] == "}":
                depth -= 1
            k += 1
        lines.append(_fmt_rule(sel2, rest[b + 1:k - 1], inner_ind))
        j = k
    return "%s%s {\n%s\n%s}" % (pad, sel, "\n".join(x for x in lines if x), pad)


def fmt_css(src):
    """把 CSS 排成三行式，注释单独占一行。

        p{background:#ffe9a8}
        →
        p {
            background: #ffe9a8;
        }
    """
    src = src.strip()
    if not src:
        return src
    out, i, n = [], 0, len(src)
    while i < n:
        if src.startswith("/*", i):
            e = src.find("*/", i + 2)
            e = n if e < 0 else e + 2
            out.append(src[i:e].strip())
            i = e
            continue
        b = src.find("{", i)
        if b < 0:
            tail = src[i:].strip()
            if tail:
                out.append(tail)
            break
        sel = src[i:b].strip()
        depth, k = 1, b + 1
        while k < n and depth:
            if src[k] == "{":
                depth += 1
            elif src[k] == "}":
                depth -= 1
            k += 1
        out.append(_fmt_rule(sel, src[b + 1:k - 1]))
        i = k
    return "\n\n".join(x for x in out if x.strip())


# ---------------------------------------------------------------------
def code(title, src, extra_cls="", fmt=True):
    """普通代码块（无示例展示）"""
    if fmt:
        src = fmt_css(src)
    return ('<div class="code-wrap%s"><div class="bar">'
            '<span class="dot r"></span><span class="dot y"></span>'
            '<span class="dot g"></span><span class="name">%s</span>%s</div>'
            '<pre>%s</pre></div>' % (extra_cls, _esc(title), _CP, hl(_esc(src))))


def pv(n, title, src, kind="css", demo="", cap="", ids=(), fmt=True):
    """带「示例展示」的代码块。

    n     示例编号（同一页内唯一，用于作用域隔离）
    kind  "css"  → src 是 CSS，规则会被加上 [data-pv="n"] 前缀
          "html" → src 是 HTML，直接渲染进示例框
    demo  **HTML 源码**，放进示例框里被选择器作用。必须用关键字传！
    ids   需要唯一化的 id 名，如 ("uniq",)
    fmt   CSS 是否排成三行式（默认排）
    """
    for name, v in (("title", title), ("kind", kind)):
        if isinstance(v, str) and re.search(r'<(div|p|span|a|ul|li|table|tr|input|button)\b', v):
            raise ValueError(
                "pv(%d): 参数 %s 看起来是 HTML，位置可能传错了 —— demo 必须用 demo= 传"
                % (n, name))

    inner = demo
    shown = src
    for old in ids:
        new = "%s%d" % (old, n)
        inner = inner.replace('id="%s"' % old, 'id="%s"' % new)
        shown = shown.replace("#" + old, "#" + new)

    if fmt and kind == "css":
        shown = fmt_css(shown)

    return (
        '<div class="pv-wrap" data-pv="%d" data-pv-kind="%s">'
        '<div class="code-wrap"><div class="bar">'
        '<span class="dot r"></span><span class="dot y"></span>'
        '<span class="dot g"></span><span class="name">%s</span>%s</div>'
        '<pre>%s</pre></div>'
        '<div class="pv-frame"><div class="pv-cap">%s</div>'
        '<div class="pv-body">%s</div></div>'
        '</div>' % (n, kind, _esc(title), _CP, hl(_esc(shown)), _esc(cap or title), inner)
    )
