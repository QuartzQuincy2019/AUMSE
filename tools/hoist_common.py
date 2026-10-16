# -*- coding: utf-8 -*-
"""2e：把正文页**剩余的全部公共块**一次性抽进 genelayout.css。

为什么这次不再按声明性质分类
----------------------------
2b 抽了 90 条纯布局、2c 抽了 69 条纯颜色，剩下的 154 条里：
    纯布局 68、纯颜色 34、混合 52
那 68+34 条本该被 2b/2c 收走，却留了下来 —— 原因是**覆盖面口径不同**：
2b 用的是「19 份共有」，而现在是「20 份共有」（t01/t03 等页面在抽取后
规则集变了，口径跟着变）。与其再猜一轮，不如换个更稳的做法：

    凡是「所有正文页都逐字相同」的块，整块抽进 genelayout.css。

理由
  · 这些块在每页都只有一份，页面上没有同名规则与之竞争，
    搬走不改变任何计算结果（加载顺序也无关）。
  · 52 条「混合」是**整块组件定义**（#toc / .card / .box / .flow .s …），
    硬拆成「布局一条、颜色一条」会让层叠更难推理，却几乎没有收益 ——
    既然 20 篇逐字相同，整块搬走是零风险的。

与 tg 层的关系
  genelayout.css 与 tg_L/tg_D 都在页面样式表之前加载，本就不区分
  「布局/颜色」的优先级 —— 2b/2c 之所以分开，只是因为当时按性质筛过。
  这里把剩余的公共块（含颜色与混合）一并归入 genelayout，
  语义上就是「所有页面共用的组件定义层」。

用法：
    python hoist_common.py --dry
    python hoist_common.py
"""
import io
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import parse, all_rules, norm  # noqa: E402
from pagecss import page_css_of              # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
A = os.path.join(T, "assets")
SKIP = {"series-theme.css", "t-theme.css", "fe-dark.css",
        "tg_L.css", "tg_D.css", "genelayout.css", "fe_base.css"}
TARGET = os.path.join(A, "genelayout.css")


def units_of(path):
    c = io.open(path, encoding="utf-8").read()
    return {(tuple(cd), norm(nd.prelude), norm(nd.body)): nd
            for cd, nd in all_rules(c)}


def remove_by_tree(css, kill_keys):
    """树式删除（顺序不能反：先处理容器内部，再决定容器存留）。"""
    root = parse(css)

    def walk(nodes):
        keep = []
        for nd in nodes:
            if nd.kind == 'comment':
                keep.append(nd)
                continue
            if nd.kind == 'rule':
                if ((), norm(nd.prelude), norm(nd.body)) in kill_keys:
                    continue
                keep.append(nd)
                continue
            if nd.children:
                walk(nd.children)
                inner = remove_by_tree(nd.body, kill_keys)
                if not re.search(r'[^\s;{}]',
                                 re.sub(r'/\*.*?\*/', '', inner, flags=re.S)):
                    continue
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


def main():
    dry = "--dry" in sys.argv
    pages = {}
    for f in sorted(os.listdir(T)):
        if not f.endswith(".html"):
            continue
        h = io.open(os.path.join(T, f), encoding="utf-8").read()
        fn = page_css_of(h)
        if fn and fn not in SKIP and not fn.startswith("fe_"):
            pages[f] = fn
    print("  正文页 %d 篇" % len(pages))

    U = {f: units_of(os.path.join(A, fn)) for f, fn in pages.items()}
    cnt = collections.Counter()
    for f, u in U.items():
        for k in u:
            cnt[k] += 1
    top = max(cnt.values())
    cand = {k for k, v in cnt.items() if v == top}
    print("  %d 份共有的块：%d 条" % (top, len(cand)))

    existing = set(units_of(TARGET)) if os.path.exists(TARGET) else set()
    new_rules = cand - existing
    print("  genelayout 已有 %d 条；新增 %d 条" % (len(existing), len(new_rules)))
    if not new_rules:
        print("  ⚠ 没有新增，产物保持不动")
        return
    if dry:
        pick = sorted(new_rules, key=lambda k: (len(k[0]), k[1]))
        for conds, sel, body in pick[:26]:
            tag = ("@%s " % conds[-1][:20]) if conds else ""
            print("     %-46s %s" % ((tag + sel)[:46], body[:38]))
        print("     … 共 %d 条" % len(pick))
        return

    # ---------- 合并写入 genelayout.css ----------
    allr = sorted(set(cand) | existing, key=lambda k: (len(k[0]), k[1]))
    by_cond = collections.OrderedDict()
    for conds, sel, body in allr:
        by_cond.setdefault(tuple(conds), []).append((sel, body))
    head = io.open(TARGET, encoding="utf-8").read()
    head = head[:head.index("*/") + 2]        # 保留原文件头注释
    out = [head, "",
           "/* ---------- 2e：其余公共组件块（含混合声明） ---------- */"]
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
    io.open(TARGET, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    print("  ✓ genelayout.css 重写，共 %d 条" % len(allr))

    # ---------- 逐份删除 ----------
    kill = set(cand)
    for pf in sorted(pages):
        cp = os.path.join(A, pages[pf])
        c = io.open(cp, encoding="utf-8").read()
        before = len(c)
        c2 = remove_by_tree(c, kill)
        c2 = re.sub(r'\n{3,}', '\n\n', c2)
        io.open(cp, "w", encoding="utf-8", newline="").write(c2)
        print("  %-32s %6d → %6d B" % (pf, before, len(c2)))

    # ---------- 自检 ----------
    print()
    bad = 0
    for fn in sorted(os.listdir(A)):
        if not fn.endswith(".css"):
            continue
        c = io.open(os.path.join(A, fn), encoding="utf-8").read()
        d, i, unc = 0, 0, 0
        while i < len(c):
            if c[i:i + 2] == '/*':
                j = c.find('*/', i + 2)
                if j < 0:
                    unc += 1
                    break
                i = j + 2
                continue
            if c[i] == '{':
                d += 1
            elif c[i] == '}':
                d -= 1
            i += 1
        if d or unc:
            bad += 1
            print("     !! %-30s 注释感知 %+d 未闭合注释 %d" % (fn, d, unc))
    print("  注释感知结构自检：%d 份有问题 %s" % (bad, "✅" if bad == 0 else "❌"))


if __name__ == "__main__":
    main()
