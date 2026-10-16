# -*- coding: utf-8 -*-
"""2c：把 20 份正文页共有的 69 条纯颜色规则抽进 tg_L / tg_D。

分配规则
    顶层（亮色）40 条   → tg_L.css
    @media (prefers-color-scheme: dark) 27 条 → tg_D.css
    其它媒体查询        2 条   → 一并进 tg_L（它们不是暗色）
（上一版统计里写的「74 条」是含了 5 条已被 2b 抽走的；实际纯颜色 69 条。）

冲突检查：0
    先比对过 tg 两文件里已有的 (条件,选择器) 组合（16 个），
    要抽的 69 条里**没有一条**与之同名同条件 → 不会改变层叠。

为什么抽走不会改变渲染
    · 这些规则在每页里都只有一份（文件内重复已在 2a 清掉）
    · 页面上没有同名同条件的规则与之竞争
    · 加载顺序：genelayout → tg_L → tg_D → … 页面样式表在后面，
      但由于没有竞争，先后无关
    
踩过的坑（都靠「先试跑单页 / 产物比对防呆」拦下）
    ① 产物参与统计 → 自我覆盖成空壳
    ② 按区间删除 → @media 里规则被抽空时留下碎片，吞掉后续规则
    本脚本沿用 build_genelayout / build_fe_base 的树式删除 + 三重防呆。

用法：
    python build_tg_color.py --dry
    python build_tg_color.py --only m02-c-functions.html
    python build_tg_color.py
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

COLOR = re.compile(r'^\s*(background|background-color|background-image|color|border|border-\w+|'
                   r'box-shadow|outline|outline-color|fill|stroke|text-shadow)\s*:', re.I)
OTHER = re.compile(r'^\s*(display|position|float|clear|width|height|min-|max-|padding|margin|'
                   r'flex|grid|gap|top|left|right|bottom|z-index|overflow|white-space|'
                   r'font|line-height|letter-spacing|text-align|text-indent|list-style|'
                   r'vertical-align|visibility|opacity|transition|transform|cursor|'
                   r'box-sizing|content|order|align|justify|table-layout|border-collapse|'
                   r'border-spacing|writing-mode|word-break|overflow-wrap|text-overflow|'
                   r'scrollbar|backdrop-filter|pointer-events|user-select|-webkit)', re.I)


def decls(b):
    return [d.strip() for d in b.split(';') if d.strip()]


def pure_color(b):
    ds = decls(b)
    if not ds:
        return False
    return (all(COLOR.match(d) for d in ds)
            and not any(OTHER.match(d) for d in ds))


def units_of(path):
    c = io.open(path, encoding="utf-8").read()
    return {(tuple(cd), norm(nd.prelude), norm(nd.body)): nd
            for cd, nd in all_rules(c)}


def remove_by_tree(css, kill_keys):
    """树式删除（与 build_genelayout 同一套，顺序不能反）。"""
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


def append_to(path, rules, header):
    """把规则追加到某个 tg 文件末尾（按条件分组）。"""
    old = io.open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    have = {k for k in units_of(path)} if old else set()
    new = [k for k in rules if k not in have]
    if not new:
        return 0
    by_cond = collections.OrderedDict()
    for conds, sel, body in sorted(new, key=lambda k: (len(k[0]), k[1])):
        by_cond.setdefault(tuple(conds), []).append((sel, body))
    out = ["", header]
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
    io.open(path, "a", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    return len(new)


def main():
    dry = "--dry" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

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
            if pure_color(k[2]):
                cnt[k] += 1
    top = max(cnt.values()) if cnt else 0
    cand = {k for k, v in cnt.items() if v == top}

    # ---------- 防呆 1：排除已被抽走的（与产物已有比对）----------
    tg_existing = set()
    for fn in ("tg_L.css", "tg_D.css"):
        p = os.path.join(A, fn)
        if os.path.exists(p):
            tg_existing |= set(units_of(p))
    new_rules = cand - tg_existing
    print("  候选 %d 条；tg 已有 %d 条；新增 %d 条"
          % (len(cand), len(tg_existing), len(new_rules)))
    if not new_rules:
        print("  ⚠ 没有新增，产物保持不动")
        return

    # ---------- 防呆 2：只在「仍含这些规则」的页面里求交 ----------
    fresh = [f for f, u in U.items() if any(k in u for k in new_rules)]
    share = sorted(set.intersection(*[{k for k in U[f] if pure_color(k[2])}
                                      for f in fresh]) & new_rules,
                   key=lambda k: (len(k[0]), k[1])) if fresh else []
    print("  未抽过的页面 %d 篇；本次要抽 %d 条" % (len(fresh), len(share)))
    if not share:
        print("  ⚠ 没有可抽的规则，产物保持不动")
        return

    light = [k for k in share if not k[0]
             or 'dark' not in (k[0][-1] if k[0] else '')]
    dark = [k for k in share if k[0] and 'dark' in k[0][-1]]
    print("     亮色 %d 条 → tg_L.css" % len(light))
    print("     暗色 %d 条 → tg_D.css" % len(dark))
    if dry:
        for conds, sel, body in share[:20]:
            tag = ("@%s " % conds[-1][:20]) if conds else ""
            print("     %-46s %s" % ((tag + sel)[:46], body[:40]))
        return

    n1 = append_to(os.path.join(A, "tg_L.css"), light,
                   "/* ---------- 2c：正文页共有的亮色规则 ---------- */")
    n2 = append_to(os.path.join(A, "tg_D.css"), dark,
                   "/* ---------- 2c：正文页共有的暗色规则 ---------- */")
    print("  ✓ tg_L.css 追加 %d 条，tg_D.css 追加 %d 条" % (n1, n2))

    # ---------- 逐份删除 ----------
    kill = {k for k in share}
    for pf in sorted(pages):
        if only and pf != only:
            continue
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
        if c.count('{') != c.count('}'):
            bad += 1
            print("     !! %s 花括号不配平" % fn)
    print("  花括号自检：%d 份有问题 %s" % (bad, "✅" if bad == 0 else "❌"))


if __name__ == "__main__":
    main()
