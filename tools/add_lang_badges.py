# -*- coding: utf-8 -*-
"""给每篇教程加「语言标注」徽章（.lang.X）。

需求（用户指定，浅色模式）
    CSS  天蓝色底白字      HTML 橙红色底白字      JS 黄色底白字
    C++  深蓝色底白字      C    蓝紫色底白字       （暗色由本脚本自行决定）

色值定义在 tools/build_tg.py 的 LANG_CSS / LANG_DARK_CSS 里，
由它写进 tg_L.css 与 tg_D.css —— 本脚本只负责把徽章**插进页面**。

插入位置的三条规则（按页面现有结构分情况）
  ① 已有标签行、且里面就有「要求 C++」这类语言标签
     → 把它换成 .lang 徽章（不新增一行）
  ② 已有标签行、但没有语言标签
     → 在行首插一个 .lang 徽章
  ③ 完全没有标签行（如 R01 / R03）
     → 在 .sub-title 之后新建一行放徽章

为什么用 .lang 而不是 .tag.X
    .tag.b/.g/.r/.v 已经被「本讲：…」「可以/不要这样写」占用了，
    M06 还用它做权限标记（.tag.pub/.pri/.pro）。语言标注单开命名空间，
    否则改颜色会误伤那些语义标签。
"""
import io
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# 页面 → 语言（徽章文字, .lang 的类名）
# 语言映射不再手写 —— 权威定义在 tools/series_data.py 里
# （SERIES_LANG 按系列给 + PAGE_LANG 单篇覆盖，FE 各篇取自
#   FE_PAGES 的语言字段），这里只做导入。
# 手写那张 38 行的表已经因为漏同步出过问题（加 Q07 / FE-09 时）。
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import LANG_OF as LANG  # noqa: E402

TAGROW = re.compile(r'(<p)(>)(\s*<span class="tag)', re.S)

# ---- 徽章的「读 / 删 / 换」（支持多个）-------------------------------
# 两个坑（都踩过）：
#   ① FE 页的正文在 JSON 里，引号写成 \" —— 两种写法都要认。
#      raw string 里 \\? 表示「一个反斜杠，出现 0 或 1 次」。
#   ② FE 页的闭标签是 <\/span>（斜杠被转义），所以不能对整份 HTML 直接做
#      正则替换 —— 必须解析 JSON、在 body 字段里操作。下面这些函数收的是
#      **body**（已反转义的普通 HTML），两种页面都能用。
#
# 一篇可以有**多个**语言徽章（FE-09 = Qt + JS），所以这里返回/处理的是
# 「徽章序列」而不是单个。
_BADGE_RE = re.compile(r'<span class=\\?lang ([a-z]+)\\?>([^<]*)</span>[ \t]*')


def find_badges(body):
    """返回 [(显示名, class), …]，按出现顺序。"""
    return [(m.group(2), m.group(1)) for m in _BADGE_RE.finditer(body)]


def _render(specs):
    return " ".join(badge(name, cls) for name, cls in specs)


def set_badges(body, specs):
    """把正文里的徽章序列整串换成 specs。

    没有徽章时按 patch_doc / patch_fe 的位置规则插入一个；
    已有徽章时把它们整串替换掉（通常都挤在同一处，不担心版面）。
    """
    hits = list(_BADGE_RE.finditer(body))
    if hits:
        a, b = hits[0].start(), hits[-1].end()
        return body[:a] + _render(specs) + body[b:]
    return None      # 交给调用方按位置规则插入


def drop_badges(body):
    """删掉所有语言徽章，并清理因此空掉的段落。"""
    out = _BADGE_RE.sub("", body)
    return re.sub(r'<p(?: [^>]*)?>\s*</p>\s*', "", out)


TAGROW = re.compile(r'(<p)(>)(\s*<span class="tag)', re.S)

# ---- 徽章的「读 / 删 / 换」 ----------------------------------------------
# 两个坑（都踩过）：
#   ① FE 页的正文在 JSON 里，引号写成 \" —— 两种写法都要认。
#      raw string 里 \\? 表示「一个反斜杠，出现 0 或 1 次」。
#   ② FE 页的闭标签是 <\/span>（斜杠被转义），所以不能对整份 HTML 直接做
#      正则替换 —— 必须解析 JSON、在 body 字段里操作。下面三个函数收的是
#      **body**（已反转义的普通 HTML），两种页面都能用。
_BADGE_RE = re.compile(r'<span class=\\?"lang ([a-z]+)\\?">([^<]*)</span>')


def find_badge(body):
    """返回 (显示名, class)，没有则 None。"""
    m = _BADGE_RE.search(body)
    return (m.group(2), m.group(1)) if m else None


def drop_badge(body):
    """删掉语言徽章，并清理因此空掉的段落。

    标签行里通常只有这一个徽章，删完会剩下一个空 <p>（页面上是一片空白），
    所以整行一起删；行里还有别的标签时只删徽章、保留其余。
    """
    out = _BADGE_RE.sub("", body)
    return re.sub(r'<p(?: [^>]*)?>\s*</p>\s*', "", out)


def swap_badge(body, lang, cls):
    """把已有徽章换成指定语言。"""
    return _BADGE_RE.sub(badge(lang, cls), body, count=1)


def badge(lang, cls):
    return '<span class="lang %s">%s</span>' % (cls, lang)


def patch_doc(html, lang, cls):
    """文档页：标签行是 <p><span class="tag"...>…</span> …</p>"""
    # 情况 ①：把「要求 C++」这类语言标签换成 .lang
    m = re.search(r'<span class="tag">(要求|需要)\s*(C\+\+|C|JS|JavaScript|HTML|CSS|Shell)</span>',
                  html)
    if m:
        return html[:m.start()] + badge(lang, cls) + html[m.end():], "把「%s」换成了 .lang" % m.group(0)

    # 情况 ②：已有标签行 → 行首插入
    m = re.search(r'(<p[^>]*>)(\s*<span class="tag)', html)
    if m:
        return (html[:m.end(1)] + badge(lang, cls) + " " + html[m.end(1):].lstrip(),
                "标签行行首插入")

    # 情况 ③：没有标签行 → 在 .sub-title 之后新建一行
    m = re.search(r'(<p class="sub-title">.*?</p>)', html, re.S)
    if m:
        return (html[:m.end(1)] + "\n<p>" + badge(lang, cls) + "</p>"
                + html[m.end(1):]), "在 .sub-title 后新建标签行"

    return html, "!! 找不到插入位置"


def patch_fe(html, lang, cls):
    """FE 页：正文是 JSON 字符串里的 body 片段。

    不能对文本做正则替换 —— body 在 HTML 里是**转义过的 JSON**
    （</div> 写成 <\\/div>、引号写成 \\"），正则很难写对。
    改成「解析 → 改 body 字段 → 重新序列化」，可靠得多。
    """
    m = re.search(r'(window\.__FE_PAGE__\s*=\s*)(\{.*?\})(;\s*\n</script>)',
                  html, re.S)
    if not m:
        return html, "!! 找不到 __FE_PAGE__（FE）"
    try:
        data = json.loads(m.group(2))
    except Exception as e:
        return html, "!! __FE_PAGE__ 解析失败：%s" % e

    body = data.get("body", "")

    # ① 已经有「语言：XX」这种标签 → 换成 .lang
    mm = re.search(r'<span class="tag">语言：([A-Za-z+#]+)</span>', body)
    if mm:
        body2 = body[:mm.start()] + badge(lang, cls) + body[mm.end():]
        how = "把「语言：%s」换成了 .lang" % mm.group(1)
    else:
        # ② 已有标签行 → 行首插入
        mm = re.search(r'<p>(\s*)<span class="tag', body)
        if mm:
            body2 = body[:mm.start() + 3] + badge(lang, cls) + " " + body[mm.start() + 3:].lstrip()
            how = "标签行行首插入"
        else:
            # ③ 没有标签行 —— 正文开头就是卡片，直接在正文最前面加一行
            body2 = "<p>" + badge(lang, cls) + "</p>\n\n" + body
            how = "正文开头新建标签行"

    data["body"] = body2
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    js = js.replace("</", "<\\/")      # 与 make_fe_shells 同一处理
    return html[:m.start(2)] + js + html[m.end(2):], how


def main():
    dry = "--dry" in sys.argv
    done = miss = 0
    for f in sorted(os.listdir(T)):
        if not f.endswith(".html"):
            continue
        if f not in LANG:
            print("  %-34s （LANG_OF 里没有，跳过）" % f)
            continue

        want = LANG[f]           # [(名, class), …]；空列表 = 不要徽章
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        tag = "+".join(n for n, _ in want) or "-"

        # ---------------- FE 页：先解析 JSON ----------------
        if f.startswith("fe-"):
            m = re.search(
                r'(window\.__FE_PAGE__\s*=\s*)(\{.*?\})(;\s*\n</script>)',
                t, re.S)
            if not m:
                print("  %-34s !! 找不到 __FE_PAGE__" % f)
                miss += 1
                continue
            data = json.loads(m.group(2))
            body = data.get("body", "")
            cur = find_badges(body)

            if cur == want:
                print("  %-34s 徽章正确（%s），跳过" % (f, tag))
                continue

            if not want:
                data["body"] = drop_badges(body)
                how = "移除徽章（%s）" % " ".join(n for n, _ in cur)
            else:
                nb = set_badges(body, want)
                if nb is None:
                    nb = "<p>" + _render(want) + "</p>\n\n" + body
                    how = "正文开头新建标签行"
                else:
                    how = "徽章 %s → %s" % (
                        " ".join(n for n, _ in cur) or "无", tag)
                data["body"] = nb

            js = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            js = js.replace("</", "<\\/")
            t2 = t[:m.start(2)] + js + t[m.end(2):]
            done += 1
            print("  %-34s %-9s %s" % (f, tag, how))
            if not dry:
                io.open(p, "w", encoding="utf-8", newline="").write(t2)
            continue

        # ---------------- 文档页：直接在 HTML 上操作 ----------------
        cur = find_badges(t)
        if cur == want:
            print("  %-34s 徽章正确（%s），跳过" % (f, tag))
            continue

        if not want:
            t2 = drop_badges(t)
            how = "移除徽章（%s）" % " ".join(n for n, _ in cur)
        else:
            t2 = set_badges(t, want)
            if t2 is None:
                t2, how = patch_doc(t, want[0][0], want[0][1])
                # 多个语言时把其余徽章补在后面
                if len(want) > 1:
                    t2 = set_badges(t2, want) or t2
            else:
                how = "徽章 %s → %s" % (
                    " ".join(n for n, _ in cur) or "无", tag)

        done += 1
        print("  %-34s %-9s %s" % (f, tag, how))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)

    print()
    print("  处理 %d 篇，未处理 %d 篇%s"
          % (done, miss, "  [dry-run]" if dry else ""))


if __name__ == "__main__":
    main()
