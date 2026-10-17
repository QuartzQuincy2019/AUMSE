# -*- coding: utf-8 -*-
"""R04：把「凡是音标就包 .ipa」变成一条统一规则，重做一遍。

上一版的毛病
    按**容器类型**判断（只包 <code> 与「无汉字的 td.c」），
    于是 `<td class="c">爸 [pa] / 怕 [pʰa]</td>` 这种「汉字＋音标」的单元格
    被整格跳过，22 处音标留在 Consolas 里 —— 用户看到的正是这一批。

这一版改成按**内容**判断，规则只有一条：
    标签之外、且不在 <pre> 里、且不在已有 .ipa 里的文字，
    凡是「方括号音标」或「音标字符连成的片段」，一律包 .ipa。
    无论它长在 <td>、<p>、<b>、<i> 还是裸文本里。

为什么 <pre> 例外
    DejaVu Serif 是比例字体。整段换过去，<pre> 里靠空格对齐的 ASCII 图
    会散架（那两块是「英语靠清浊 / 普通话靠送气」的左右对照）。
    <pre> 里改用 unicode-range 兜底：只有音标码位换 DejaVu Serif，
    ASCII 仍是等宽 —— 视觉效果与 .ipa 相同，只是不套 span。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\tools\_r04_body.html"
t = io.open(P, encoding="utf-8").read()
before = len(t)

# 音标字符集：IPA 扩展 + 修饰字母 + 组合符号 + 音标扩展
IPA_CH = r"\u0250-\u02ff\u0300-\u036f\u1d00-\u1dbf\ua700-\ua71f"
IPA_RUN = re.compile(r"[%s]+(?:\s*[%s]+)*" % (IPA_CH, IPA_CH))

tokens = re.split(r"(<[^>]+>)", t)
out = []
in_pre = 0
in_ipa = 0
stack = []
n_br = 0
n_bare = 0

SELF = {"br", "img", "hr", "meta", "link", "input", "circle", "line",
        "polygon", "text", "path", "rect"}


def wrap_brackets(seg):
    """把 [ … ] 里的内容整体包成 .ipa。"""
    global n_br
    def rep(m):
        global n_br
        n_br += 1
        return '<span class="ipa">%s</span>' % m.group(0)
    return re.sub(r"\[[^\]<]*\]", rep, seg)


def wrap_bare(seg):
    """把裸露的音标字符片段包成 .ipa。"""
    global n_bare
    def rep(m):
        global n_bare
        n_bare += 1
        return '<span class="ipa">%s</span>' % m.group(0)
    return IPA_RUN.sub(rep, seg)


for tok in tokens:
    if tok.startswith("<"):
        tag = tok
        m = re.match(r"</?\s*([a-zA-Z0-9]+)", tag)
        name = m.group(1).lower() if m else "?"
        if tag.startswith("</"):
            if stack:
                stack.pop()
            if name == "pre":
                in_pre = max(0, in_pre - 1)
            if name == "span" and in_ipa > 0:
                in_ipa -= 1
        else:
            if name not in SELF:
                stack.append(name)
            if name == "pre":
                in_pre += 1
            if name == "span" and 'class="ipa"' in tag:
                in_ipa += 1
        out.append(tag)
        continue

    if not tok.strip():
        out.append(tok)
        continue

    if in_pre or in_ipa:
        out.append(tok)
        continue

    seg = wrap_bracket_first = wrap_brackets(tok)
    seg = wrap_bare(seg)
    out.append(seg)

t = "".join(out)
io.open(P, "w", encoding="utf-8", newline="").write(t)

print("  方括号音标新包：%d 处" % n_br)
print("  裸露音标新包：  %d 处" % n_bare)
print("  .ipa 总数：     %d" % t.count('class="ipa"'))
print("  字数：%d → %d" % (before, len(t)))

# ---------- 复核 ----------
IPA = re.compile(r"[%s]" % IPA_CH)
tokens = re.split(r"(<[^>]+>)", t)
in_pre = in_ipa = 0
stack = []
left = []
for tok in tokens:
    if tok.startswith("<"):
        m = re.match(r"</?\s*([a-zA-Z0-9]+)", tok)
        name = m.group(1).lower() if m else "?"
        if tok.startswith("</"):
            if stack:
                stack.pop()
            if name == "pre":
                in_pre = max(0, in_pre - 1)
            if name == "span" and in_ipa > 0:
                in_ipa -= 1
        else:
            if name not in SELF:
                stack.append(name)
            if name == "pre":
                in_pre += 1
            if name == "span" and 'class="ipa"' in tok:
                in_ipa += 1
        continue
    if IPA.search(tok) and not in_ipa:
        left.append(("pre" if in_pre else "/".join(stack[-2:]), tok.strip()[:50]))

print()
print("  复核 —— 未包住的音标：%d 处" % len(left))
for cont, ctx in left[:10]:
    print("      容器 %-14s %s" % (cont, ctx))
