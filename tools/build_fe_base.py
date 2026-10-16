# -*- coding: utf-8 -*-
"""2d：把 FE 八篇共有的 182 条规则抽成 fe_base.css。

为什么 FE 可以整体抽、而正文页只能抽「纯布局」
--------------------------------------------
实测：
  · 正文页（20 份）：共用选择器名，但**值各不相同** —— 同一套设计系统的
    不同主题。所以只能先抽「与配色无关」的那部分（2b 做的 90 条纯布局）。
  · FE 八篇：182 条规则**逐字完全相同**（8/8）。它们就是同一套东西被
    复制了 8 遍，可以整体抽出，不必逐声明去挑。

那 82 条「混合」声明为什么不拆
----------------------------
按声明性质分，182 条里纯布局 44、纯颜色 56、混合 82。
混合的那些长这样：
    #toc{position:sticky;top:0;width:274px;…;background:…;color:…}
    .card{margin:16px 0;border:1px solid …;border-radius:12px;…}
它们是**整块组件定义**，不是「布局里混了个颜色」。硬拆成两条
（一条管摆位、一条管颜色）只会让层叠更难推理，收益却很小。
既然八篇逐字相同，整条搬走是**零风险**的 —— 这也是 FE 比正文页简单的地方。

产物与加载顺序
    fe_base.css   八篇共有的 182 条（含 154 顶层 + 28 条媒体查询内规则）
    加载顺序：genelayout.css → fe_base.css → tg_L.css → tg_D.css
              → series-theme.css → fe-dark.css → fe_NN.css
    （FE 目前不挂 genelayout，见脚本末尾说明）

用法：
    python build_fe_base.py --dry
    python build_fe_base.py --only fe-01.html
    python build_fe_base.py
"""
import io
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import parse, all_rules, norm  # noqa: E402
from pagecss import page_css_of               # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
A = os.path.join(T, "assets")

HEAD = """/* =====================================================================
   fe_base.css —— FE（前端）系列的公共基础层
   ---------------------------------------------------------------------
   由 tools/build_fe_base.py 生成，**不要手改**。
   来源：FE 八篇样式表里**逐字完全相同**的 %d 条规则
   （顶层 %d 条 + 媒体查询内 %d 条）。

   为什么单独一层，而不并进 genelayout.css
     FE 的观感自成一系（紫色渐变紫金风），它与正文页只是**选择器重名**，
     值并不相同 —— 实测两者同名的 98 个选择器里有 72 个值不一样。
     并进去会互相污染，所以 FE 走自己这一层。

   加载顺序：fe_base.css → tg_L.css → tg_D.css → fe-dark.css → fe_NN.css
     · fe-dark.css 仍是 FE 暗色的最后一层，优先级最高。
   ===================================================================== */

"""


def main():
    dry = "--dry" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    # 页面 → 该页样式表
    pages = {}
    for f in sorted(os.listdir(T)):
        if not f.endswith(".html"):
            continue
        h = io.open(os.path.join(T, f), encoding="utf-8").read()
        fn = page_css_of(h)
        if fn and fn.startswith("fe_"):
            pages[f] = fn
    print("  FE 页面 %d 篇" % len(pages))

    U = {}
    for f, fn in pages.items():
        c = io.open(os.path.join(A, fn), encoding="utf-8").read()
        U[f] = {(tuple(cd), norm(nd.prelude), norm(nd.body)): nd
                for cd, nd in all_rules(c)}

    cnt = collections.Counter()
    for f, u in U.items():
        for k in u:
            cnt[k] += 1
    n = len(pages)
    share = sorted({k for k, v in cnt.items() if v == n},
                   key=lambda k: (len(k[0]), k[1]))
    top_cnt = sum(1 for k in share if not k[0])
    print("  %d 篇逐字相同的规则：%d 条（顶层 %d + 媒体查询内 %d）"
          % (n, len(share), top_cnt, len(share) - top_cnt))

    # ---------- 防呆：与产物比对，无新增就不动 ----------
    p0 = os.path.join(A, "fe_base.css")
    existing = set()
    if os.path.exists(p0):
        c0 = io.open(p0, encoding="utf-8").read()
        existing = {(tuple(cd), norm(nd.prelude), norm(nd.body))
                    for cd, nd in all_rules(c0)}
    new_rules = set(share) - existing
    print("  产物已有 %d 条；新增 %d 条" % (len(existing), len(new_rules)))
    if not new_rules:
        print("  ⚠ 没有新增，产物保持不动（%d B）" % os.path.getsize(p0))
        return
    if dry:
        for conds, sel, body in share[:24]:
            tag = ("@%s " % conds[-1][:20]) if conds else ""
            print("     %-48s %s" % ((tag + sel)[:48], body[:38]))
        return

    # ---------- 合并生成 ----------
    allr = sorted(set(share) | existing, key=lambda k: (len(k[0]), k[1]))
    by_cond = collections.OrderedDict()
    for conds, sel, body in allr:
        by_cond.setdefault(tuple(conds), []).append((sel, body))
    out = []
    for key, items in by_cond.items():
        if not key:
            for sel, body in items:
                out.append("%s{%s}" % (sel, body))
        else:
            for cond in key:
                out.append("@media %s{" % cond)
            for sel, body in items:
                out.append("  %s{%s}" % (sel, body))
            for _ in key:
                out.append("}")
    mq = sum(1 for k in allr if k[0])
    gl = HEAD % (len(allr), len(allr) - mq, mq) + "\n".join(out) + "\n"
    io.open(p0, "w", encoding="utf-8", newline="\n").write(gl)
    print("  ✓ fe_base.css  %d B（%d 条）" % (len(gl), len(allr)))

    # ---------- 逐份删除 + 加链接 ----------
    kill = set(share)
    LINK = '<link rel="stylesheet" href="assets/fe_base.css">'
    for pf in sorted(pages):
        if only and pf != only:
            continue
        cp = os.path.join(A, pages[pf])
        c = io.open(cp, encoding="utf-8").read()
        before = len(c)
        c2 = remove_by_tree(c, kill)
        c2 = re.sub(r'\n{3,}', '\n\n', c2)
        io.open(cp, "w", encoding="utf-8", newline="").write(c2)
        hp = os.path.join(T, pf)
        h = io.open(hp, encoding="utf-8").read()
        if "fe_base.css" not in h:
            first = re.search(r'[ \t]*<link[^>]*rel="stylesheet"[^>]*>\n?', h)
            if first:
                h = h[:first.start()] + LINK + "\n" + h[first.start():]
                io.open(hp, "w", encoding="utf-8", newline="").write(h)
        print("  %-20s %6d → %6d B" % (pf, before, len(c2)))

    # ---------- 碎片自检 ----------
    print()
    bad = 0
    for pf, fn in pages.items():
        c = io.open(os.path.join(A, fn), encoding="utf-8").read()
        if c.count('{') != c.count('}'):
            bad += 1
            print("     !! %s 花括号不配平" % fn)
    print("  花括号自检：%d 份有问题 %s" % (bad, "✅" if bad == 0 else "❌"))


def remove_by_tree(css, kill_keys):
    """在解析树上删掉命中 kill_keys 的规则（与 build_genelayout 同一套）。

    为什么必须树式删除：按区间删除会在「@media 里的规则被全部抽走」时
    留下 `@media(...){` 与 `}` 的碎片，和相邻文本粘成垃圾，
    导致紧随其后的规则被整段吞掉（2b 踩过这个坑）。

    注意顺序：先把容器内部处理好、再把容器本身放进 keep ——
    反过来写（先 keep 再处理 children）会丢掉 newbody，
    等于没删干净。
    """
    root = parse(css)

    def walk(nodes):
        keep = []
        for nd in nodes:
            if nd.kind == 'comment':
                keep.append(nd)
                continue
            if nd.kind == 'rule':
                k = ((), norm(nd.prelude), norm(nd.body))
                if k in kill_keys:
                    continue                      # 摘掉
                keep.append(nd)
                continue
            if nd.children:
                walk(nd.children)
                inner = remove_by_tree(nd.body, kill_keys)
                if not re.search(r'[^\s;{}]',
                                 re.sub(r'/\*.*?\*/', '', inner, flags=re.S)):
                    continue                      # 容器空了 → 整个摘掉
                nd.newbody = inner
                keep.append(nd)
                continue
            keep.append(nd)
        nodes[:] = keep

    walk(root)
    out = []
    for nd in root:
        if nd.kind in ('rule', 'comment'):
            out.append(nd.text)
        elif nd.children:
            nb = nd.newbody if nd.newbody is not None else nd.body
            brace = nd.text.find('{')
            out.append(nd.text[:brace + 1] + nb + "}")
        else:
            out.append(nd.text)
    return "".join(out)


if __name__ == "__main__":
    main()
