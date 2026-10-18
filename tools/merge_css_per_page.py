# -*- coding: utf-8 -*-
"""把每篇的两个样式表合并成一个，并保证「媒体查询排在最后」。

背景（手机端顶部一大片空白的真正原因）：
    文档里有两张表：
        <link href="assets/css/tutorial.css">   ← 通用 + 移动端媒体查询
        <link href="assets/01.css">         ← 本篇专属

    但 01/02/03 三篇的**基础桌面规则**略有差异（#toc 宽度 270px vs 274px、
    padding 不同），按「出现频率」判定时它们没被收进通用表，
    于是留在了 01.css 里。而 01.css **在后面加载**，
    它的 #toc{position:sticky;height:100vh} 就压过了
    tutorial.css 媒体查询里的抽屉样式 ——
    手机端侧边栏因此留在文档流里占满一屏，正文被推到一屏之外。

修法（合并成一个文件，不删任何规则）：
    每篇只留一张样式表 = 通用 + 本篇专属，并按
        ① 所有非 @media 规则
        ② 所有 @media 块
    的顺序重排。

    为什么这样就对了：本篇专属的基础规则排在通用基础规则**之后**
    （保持它原本的覆盖关系），而所有媒体查询排在**最末**，
    于是窄屏覆盖一定生效 —— 与原文档内嵌时的顺序完全一致。
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

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
ASSETS = os.path.join(TUT, "assets")


def split_rules(css):
    """切成 [(comments, rule), ...]；连续的多个注释会一起收下（原文里有嵌套写法）。"""
    out, i, n = [], 0, len(css)
    while i < n:
        while i < n and css[i] in " \t\r\n":
            i += 1
        if i >= n:
            break
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


def reorder(css):
    """普通规则在前，@media 块在后；各段内部保持原顺序。"""
    items = split_rules(css)
    normal, media, seen = [], [], set()
    for comment, rule in items:
        key = re.sub(r'\s+', ' ', rule).strip()
        if key in seen:
            continue
        seen.add(key)
        text = (((comment + "\n") if comment else "") + rule).strip()
        (media if rule.lstrip().startswith("@") else normal).append(text)
    return "\n\n".join(normal + media) + "\n"


def main():
    docs = sorted(f for f in os.listdir(TUT)
                  if f.endswith(".html") and re.match(r'^\d\d-', f))
    merged = 0
    for name in docs:
        p = os.path.join(TUT, name)
        t = io.open(p, encoding="utf-8").read()

        links = re.findall(r'<link rel="stylesheet" href="(assets/[^"]+)">', t)
        if not links:
            print("  !! %s 没有样式表链接" % name)
            continue
        if len(links) == 1:
            print("  ·  %-42s 已经是一个样式表，跳过" % name)
            continue

        # 把 @media 拆出来单独放，其余留在原地
        parts = []
        for lk in links:
            fp = os.path.join(TUT, lk.replace("/", os.sep))
            parts.append(io.open(fp, encoding="utf-8").read())
        combined = "\n\n".join(parts)

        head = ("/* ==== %s\n"
                "       本篇样式表 = 通用（tutorial.css）+ 本篇专属，"
                "已合并并按「媒体查询在后」重排 ==== */\n\n" % name)
        out = head + reorder(combined)

        stem = re.sub(r'[^A-Za-z0-9]+', '_', os.path.splitext(name)[0]).strip('_')
        target = stem + ".css"
        io.open(os.path.join(ASSETS, target), "w",
                encoding="utf-8", newline="\n").write(out)

        # 文档里只留一个 link
        t = re.sub(r'(?:\s*<link rel="stylesheet" href="assets/[^"]+">)+',
                   '\n<link rel="stylesheet" href="assets/%s">' % target, t, count=1)
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        merged += 1
        print("  ✔  %-42s → assets/%s（%d 字符）" % (name, target, len(out)))

    print("")
    print("合并 %d 篇" % merged)

    # 删掉不再被引用的 css
    used = set()
    for name in os.listdir(TUT):
        if name.endswith(".html"):
            t = io.open(os.path.join(TUT, name), encoding="utf-8").read()
            used.update(re.findall(r'href="(assets/[^"]+)"', t))
    used = {u.split("/")[-1] for u in used}
    removed = []
    for f in os.listdir(ASSETS):
        if f.endswith(".css") and f not in used:
            os.remove(os.path.join(ASSETS, f))
            removed.append(f)
    print("已删除不再引用的：%s" % (", ".join(removed) if removed else "无"))
    print("assets 剩余 %d 个文件" % len(os.listdir(ASSETS)))


if __name__ == "__main__":
    main()
