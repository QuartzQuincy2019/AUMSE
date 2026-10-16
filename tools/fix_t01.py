# -*- coding: utf-8 -*-
"""2f：T01 特例 —— 它自己的样式表里大半是「已经在 tg 层里的」重复内容。

发现
----
t01.css 只有 27 条规则，其中：
    :root{--sfc…} + @media dark{:root:root{--sfc…}} + 暗色组件补丁
    （code/.hd/.k/.mnemonic/.cpp-note/.lv/.ch.end/.ptr-demo/.box）
    + @media dark{:root:root{--bg-soft…}}
这些**与 tg_L.css / tg_D.css 里的逐字相同**，而 T01 已经加载了那两个文件
（它的 <link> 顺序是 genelayout → f03_… → t01 → t-theme → series-theme
  → tg_L → tg_D），所以这些是纯重复。

真正属于 T01 的只剩少数几条：
    .umc-demo / .umc-inline（蒙文渲染演示区，UMCompos.js 专用）
    .fig / .fig img / .fig figcaption
    table 的窄屏横向滚动
    @media (max-width:720px) 相关的几条

做法
    把与 tg 层逐字相同的规则从 t01.css 删掉；属于 T01 的原样保留。
    删之前逐条核对「tg 里确实有同一条」，核不上就不动。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import parse, all_rules, norm  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
P = os.path.join(A, "t01.css")


def units_of(path):
    c = io.open(path, encoding="utf-8").read()
    return {(tuple(cd), norm(nd.prelude), norm(nd.body)): nd
            for cd, nd in all_rules(c)}


def remove_by_tree(css, kill_keys):
    """树式删除（顺序不能反）。"""
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
    tg = {}
    for fn in ("tg_L.css", "tg_D.css"):
        p = os.path.join(A, fn)
        if os.path.exists(p):
            tg.update(units_of(p))
    print("  tg 两文件合计 %d 条规则" % len(tg))

    c = io.open(P, encoding="utf-8").read()
    before = len(c)
    kill = set()
    shown = []
    for k in units_of(P):
        if k in tg:
            kill.add(k)
            shown.append(k)
    print("  t01.css 共 %d 条；其中与 tg 逐字相同的 %d 条（可删）"
          % (len(units_of(P)), len(kill)))
    for conds, sel, body in sorted(shown, key=lambda k: (len(k[0]), k[1]))[:30]:
        tag = ("@%s " % conds[-1][:22]) if conds else ""
        print("     删 %-46s %s" % ((tag + sel)[:46], body[:36]))
    print()
    keep = [k for k in units_of(P) if k not in tg]
    print("  保留 %d 条（T01 真正专属）：" % len(keep))
    for conds, sel, body in sorted(keep, key=lambda k: (len(k[0]), k[1])):
        tag = ("@%s " % conds[-1][:22]) if conds else ""
        print("     留 %-46s %s" % ((tag + sel)[:46], body[:36]))

    if dry:
        return
    if not kill:
        print("\n  ⚠ 没有可删的，文件保持不动")
        return

    c2 = remove_by_tree(c, kill)
    c2 = re.sub(r'\n{3,}', '\n\n', c2)
    io.open(P, "w", encoding="utf-8", newline="\n").write(c2)
    print()
    print("  ✓ t01.css %d → %d B（删 %d 条）" % (before, len(c2), len(kill)))

    # 自检
    d = 0
    i = 0
    unc = 0
    while i < len(c2):
        if c2[i:i + 2] == '/*':
            j = c2.find('*/', i + 2)
            if j < 0:
                unc += 1
                break
            i = j + 2
            continue
        if c2[i] == '{':
            d += 1
        elif c2[i] == '}':
            d -= 1
        i += 1
    print("  结构自检：注释感知 %+d，未闭合注释 %d %s"
          % (d, unc, "✅" if d == 0 and unc == 0 else "❌"))


if __name__ == "__main__":
    main()
