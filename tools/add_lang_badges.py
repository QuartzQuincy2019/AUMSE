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
LANG = {
    # ---- T：回鹘蒙文理论 ----
    "t01-mongolian-script-intro.html": ("HTML", "html"),
    "t02-unicode-and-encoding.html": ("HTML", "html"),
    "t03-font-file-anatomy.html": ("HTML", "html"),
    # ---- F：文件操作（命令行 + 编译链接）----
    "f01-command-prompt.html": ("Shell", "sh"),
    "f02-paths-and-env.html": ("Shell", "sh"),
    # F03 讲的是编译/链接这套**工具链**（cl 命令行、静态库、LNK 报错），
    # 代码只是被编译的素材 —— 所以归 Shell，与首页保持一致。
    "f03-compile-and-link.html": ("Shell", "sh"),
    # ---- M：课本内容 ----
    "m01-c-arrays.html": ("C++", "cpp"),
    "m02-c-functions.html": ("C++", "cpp"),
    "m03-c-types.html": ("C++", "cpp"),
    "m04-c-pointers.html": ("C++", "cpp"),
    "m05-memory.html": ("C++", "cpp"),
    "m06-class-struct.html": ("C++", "cpp"),
    "m07-scope.html": ("C++", "cpp"),
    "m08-c-strings.html": ("C++", "cpp"),
    "m09-vector-and-array.html": ("C++", "cpp"),
    # ---- Q：Qt / C++ 开发事项 ----
    "q01-std-and-namespace.html": ("C++", "cpp"),
    "q02-references.html": ("C++", "cpp"),
    # ---- R：相关信息 ----
    "r01-font-design-metrics.html": ("CSS", "css"),
    "r02-bubble-sort.html": ("C++", "cpp"),
    "r03-collation.html": ("C++", "cpp"),
    # ---- E：补充练习 ----
    "e01-recursion.html": ("C++", "cpp"),
    "e02-batch-and-cmd.html": ("Shell", "sh"),
    "e03-syntactic-sugar.html": ("C++", "cpp"),
    # ---- FE：前端 ----
    "fe-01.html": ("HTML", "html"),
    "fe-02.html": ("HTML", "html"),
    "fe-03-F01.html": ("CSS", "css"),
    "fe-03.html": ("CSS", "css"),
    "fe-04.html": ("CSS", "css"),
    "fe-05.html": ("CSS", "css"),
    "fe-06.html": ("CSS", "css"),
    "fe-07.html": ("CSS", "css"),
    "fe-08.html": ("JS", "js"),
}

TAGROW = re.compile(r'(<p)(>)(\s*<span class="tag)', re.S)


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
            print("  %-34s （未指定语言，跳过）" % f)
            continue
        lang, cls = LANG[f]
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        # 幂等判断：注意 FE 页的正文是 JSON，引号被转义成 \" ——
        # 只匹配 class="lang 会漏掉它们，于是同一篇被插两次、徽章翻倍。
        # 两种写法都要认。（第一版就漏了这个，靠「再跑一次」才发现。）
        if 'class="lang ' in t or 'class=\\"lang ' in t:
            print("  %-34s 已有语言徽章，跳过" % f)
            continue

        if f.startswith("fe-"):
            t2, how = patch_fe(t, lang, cls)
        else:
            t2, how = patch_doc(t, lang, cls)

        if t2 == t:
            miss += 1
            print("  %-34s %s" % (f, how))
            continue
        done += 1
        print("  %-34s %-6s %s" % (f, lang, how))
        if not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)
    print()
    print("  处理 %d 篇，未插入 %d 篇%s" % (done, miss, "  [dry-run]" if dry else ""))


if __name__ == "__main__":
    main()
