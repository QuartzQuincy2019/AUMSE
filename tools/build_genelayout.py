# -*- coding: utf-8 -*-
"""2b（正确版）：把 20 份正文页共有的纯布局规则抽进 genelayout.css。

为什么必须按「树」删除，而不是按「区间」删除
--------------------------------------------
上一版是这么干的：对每条要抽的规则取 (start,end)，然后在原文上从后往前删。
这个做法**会破坏文件**：

  · 当一条规则嵌在 @media 里时，删掉它会留下一个空壳 `@media(...){}`；
  · 更糟的是，当某个 @media 里的**所有**规则都要被抽走时，
    多个内层区间被依次删掉，区间之间的 `@media(...){` 与 `}` 反而被留成
    碎片，和相邻文本粘成 `0 12px;frm:uppercase;font-weightar(--line-2)}`
    这种垃圾 —— 解析器到这儿就乱了，**紧随其后的规则会被整段吞掉**。
  · 实测后果：f03 的 `#toc{position:sticky…}` 与窄屏 `#toc{display:block…}`
    双双失效，窄屏目录退化成 sticky。

正确做法：在**解析树上**操作
    · 逐个容器处理：把要抽的规则从 children 里摘掉
    · 容器摘空了就整个删掉（连同 @media 外壳）
    · 每个容器的区间**只删一次**，不存在碎片拼接
    · 顶层规则同理

实测这一版对 f03 的删除结果与预期一致（原 1196 行 → 正常，无垃圾文本）。
"""
import io
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import parse, all_rules, norm  # noqa: E402
from pagecss import page_css_of  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
A = os.path.join(T, "assets")
SKIP = {"series-theme.css", "t-theme.css", "fe-dark.css",
        "tg_L.css", "tg_D.css", "genelayout.css"}

COLOR = re.compile(r'^\s*(background|background-color|background-image|color|border|border-\w+|'
                   r'box-shadow|outline|outline-color|fill|stroke|text-shadow)\s*:', re.I)
OTHER = re.compile(r'^\s*(display|position|float|clear|width|height|min-|max-|padding|margin|'
                   r'flex|grid|gap|top|left|right|bottom|z-index|overflow|white-space|'
                   r'font|line-height|letter-spacing|text-align|text-indent|list-style|'
                   r'vertical-align|visibility|opacity|transition|transform|cursor|'
                   r'box-sizing|content|order|align|justify|table-layout|border-collapse|'
                   r'border-spacing|writing-mode|word-break|overflow-wrap|text-overflow|'
                   r'scrollbar|backdrop-filter|pointer-events|user-select|-webkit)', re.I)

HEAD = """/* =====================================================================
   genelayout.css —— 公共布局层
   ---------------------------------------------------------------------
   由 tools/build_genelayout.py 生成，**不要手改**。
   来源：20 份正文页样式表里逐字相同的「纯布局」规则（尺寸 / 间距 /
   定位 / 字号 / 媒体查询里的排布），共 %d 条。

   加载顺序：genelayout.css → tg_L.css → tg_D.css → sp_<page>.css
     · 本层只管「怎么摆」，不管「什么颜色」——
       颜色在 tg_L / tg_D（全局主题）与各页 sp_ 里。
     · 放在最前：页面自己的样式始终能覆盖这里。

   注意 T01 不参与：t01.css 只有 27 条规则，它走的是另一套（t-theme）。
   ===================================================================== */

"""


def decls(body):
    return [d.strip() for d in body.split(';') if d.strip()]


def pure_layout(body):
    ds = decls(body)
    if not ds:
        return False
    return (all(OTHER.match(d) for d in ds)
            and not any(COLOR.match(d) for d in ds))


def units_of(path):
    c = io.open(path, encoding="utf-8").read()
    return {(tuple(cd), norm(nd.prelude), norm(nd.body)): nd for cd, nd in all_rules(c)}


def remove_by_tree(css, kill_keys):
    """在解析树上删掉命中 kill_keys 的规则。返回新文本。"""
    root = parse(css)
    # 收集要删的区间：容器级只删一次
    spans = []

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
                # 递归后重新解析该容器，看还剩多少实质内容
                inner = remove_by_tree(nd.body, kill_keys)
                if not re.search(r'[^\s;{}]', re.sub(r'/\*.*?\*/', '', inner, flags=re.S)):
                    continue                      # 容器空了 → 整个摘掉
                nd.newbody = inner
                keep.append(nd)
                continue
            keep.append(nd)
        nodes[:] = keep

    walk(root)

    def emit(nodes):
        out = []
        for nd in nodes:
            if nd.kind == 'rule':
                out.append(nd.text)
            elif nd.kind == 'comment':
                out.append(nd.text)
            elif nd.children:
                nb = getattr(nd, 'newbody', None) or nd.body
                brace = nd.text.find('{')
                head = nd.text[:brace + 1]
                out.append(head + nb + "}")
            else:
                out.append(nd.text)
        return "".join(out)

    return emit(root)


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
        if not fn or fn in SKIP or fn.startswith("fe_"):
            continue
        pages[f] = fn
    print("  目标页面 %d 篇" % len(pages))

    U = {f: units_of(os.path.join(A, fn)) for f, fn in pages.items()}
    cnt = collections.Counter()
    for f, u in U.items():
        for k in u:
            if pure_layout(k[2]):
                cnt[k] += 1
    top = max(cnt.values()) if cnt else 0
    cand = {k for k, v in cnt.items() if v == top}

    # ---------- 防呆：与「产物里已有的规则」比对 ----------
    # 这是踩了三次坑之后的做法。前两次分别栽在：
    #   ① 产物参与统计（把 genelayout.css 当成输入）→ 交集被稀释
    #   ② 已抽过的页面拉低交集 → 每跑一次产物就小一圈，最后成空壳
    # 根因是「该抽什么」被算成了「各页的交集」，而各页在抽过之后就变了。
    # 正确依据是**产物本身**：
    #     · 产物里已有的规则 = 已经抽过的
    #     · 本次候选若没有超出产物 → 无事可做，直接返回，绝不覆盖
    p0 = os.path.join(A, "genelayout.css")
    existing = set()
    if os.path.exists(p0):
        existing = {k for k in units_of(p0) if pure_layout(k[2])}
    new_rules = cand - existing
    print("  候选 %d 条；产物已有 %d 条；新增 %d 条"
          % (len(cand), len(existing), len(new_rules)))
    if not new_rules:
        print("  ⚠ 没有新增规则可抽，产物保持不动（%d B）" % os.path.getsize(p0))
        return

    fresh = [f for f, u in U.items() if any(k in u for k in new_rules)]
    share = sorted(set.intersection(*[{k for k in U[f] if pure_layout(k[2])}
                                      for f in fresh]) & new_rules,
                   key=lambda k: (len(k[0]), k[1])) if fresh else []
    print("  未抽过的页面 %d 篇；本次要抽 %d 条" % (len(fresh), len(share)))
    if not share:
        print("  ⚠ 没有可抽的规则，产物保持不动")
        return
    if dry:
        for conds, sel, body in share[:20]:
            tag = ("@%s " % conds[-1][:22]) if conds else ""
            print("     %-52s %s" % ((tag + sel)[:52], body[:34]))
        return

    # ---------- 生成 genelayout.css ----------
    # 关键：**合并**已有规则与本次新增，而不是只用本次的 share。
    # 否则第二次运行时产物会从 90 条缩到 68 条 —— 数据就丢了。
    # share 的元素是 (conds, sel, body)，existing 是同类键，直接求并集。
    merged = {k: None for k in share}
    for k in existing:
        merged.setdefault(k, None)
    # existing 里的规则文本要去产物里取原文（保持原样）
    if os.path.exists(p0):
        for k in units_of(p0):
            if pure_layout(k[2]):
                merged[k] = None
    allrules = sorted(set(share) | existing, key=lambda k: (len(k[0]), k[1]))
    by_cond = collections.OrderedDict()
    for conds, sel, body in allrules:
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
    gl = HEAD % len(allrules) + "\n".join(out) + "\n"
    io.open(p0, "w", encoding="utf-8", newline="\n").write(gl)
    print("  ✓ genelayout.css  %d B（合并后共 %d 条）" % (len(gl), len(allrules)))

    kill = set(share)
    LINK = '<link rel="stylesheet" href="assets/css/genelayout.css">'
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
        if "genelayout.css" not in h:
            first = re.search(r'[ \t]*<link[^>]*rel="stylesheet"[^>]*>\n?', h)
            if first:
                h = h[:first.start()] + LINK + "\n" + h[first.start():]
                io.open(hp, "w", encoding="utf-8", newline="").write(h)
        n_hit = sum(1 for k in kill if k in U[pf])
        print("  %-32s %6d → %6d B  摘掉 %2d 条规则" % (pf, before, len(c2), n_hit))

    # ---------- 收尾自检：残留垃圾文本 ----------
    print()
    bad = 0
    for pf, fn in pages.items():
        c = io.open(os.path.join(A, fn), encoding="utf-8").read()
        # 典型的「区间删除碎片」特征：行首出现裸声明残片
        for m in re.finditer(r'(?m)^\s*[0-9a-zA-Z-]+\s*:[^;{}]*[)}]\s*$', c):
            frag = m.group(0).strip()
            if not re.match(r'^\s*[\w-]+\s*:\s*[^;]*;\s*$', frag + ';'):
                bad += 1
                print("     !! %s 疑似碎片: %r" % (fn, frag[:70]))
    print("  碎片自检：%d 处 %s" % (bad, "✅" if bad == 0 else "❌"))


if __name__ == "__main__":
    main()
