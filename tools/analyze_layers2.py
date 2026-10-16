# -*- coding: utf-8 -*-
"""用**正确的解析器**重新做分层分析，并交叉验证旧结论错在哪。

先自证解析器是对的（否则又是一次基于错误数据的决策）：
  · 对每份 CSS 用解析器统计花括号配平、规则条数
  · 与「朴素正则」的结果对照，把两者的差异摆出来
然后再输出分层结论。
"""
import io
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import parse, all_rules, norm, at_condition  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
SKIP = {"series-theme.css", "t-theme.css", "fe-dark.css"}
FILES = sorted(f for f in os.listdir(A)
               if f.endswith(".css") and f not in SKIP)


def naive_rules(css):
    """旧分析用的朴素正则（故意保留，用来暴露它的错）。"""
    c = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    return [(m.group(1).strip(), m.group(2).strip())
            for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', c)]


print("=" * 74)
print("① 解析器自检：与朴素正则对照")
print("=" * 74)
print("%-30s %8s %8s %8s" % ("文件", "正确规则", "朴素正则", "差"))
print("-" * 74)
tot_ok = tot_naive = 0
for f in FILES:
    c = io.open(os.path.join(A, f), encoding="utf-8").read()
    ok = len(all_rules(c))
    nv = len(naive_rules(c))
    tot_ok += ok
    tot_naive += nv
    flag = "" if abs(ok - nv) <= 2 else "   ← 差得多"
    print("%-30s %8d %8d %8d%s" % (f, ok, nv, ok - nv, flag))
print("-" * 74)
print("%-30s %8d %8d %8d" % ("合计", tot_ok, tot_naive, tot_ok - tot_naive))
print()

# ---------------------------------------------------------------- ② 真正的公共层
print("=" * 74)
print("② 真正逐字相同的顶层块（用解析器）")
print("=" * 74)


def top_blocks(css):
    """顶层块：comment 跳过；at 整块；rule 整块。返回 (条件链, 选择器, 归一化文本)。"""
    out = []
    for nd in parse(css):
        if nd.kind == 'comment':
            continue
        out.append((nd.norm(), nd.prelude[:60], nd.kind))
    return out


cnt = collections.Counter()
for f in FILES:
    c = io.open(os.path.join(A, f), encoding="utf-8").read()
    for t, pre, kind in top_blocks(c):
        cnt[t] += 1

buckets = collections.Counter()
for t, n in cnt.items():
    buckets[n] += 1
print("  顶层块去重后 %d 种；覆盖面分布：" % len(cnt))
for n in sorted(buckets, reverse=True):
    if n >= 2:
        print("     %2d 份 → %3d 种" % (n, buckets[n]))
print()

for lo in (len(FILES), len(FILES) - 1, 20, 19):
    sel = [t for t, n in cnt.items() if n >= lo]
    if sel:
        print("  ≥%-2d 份共有的块：%3d 个" % (lo, len(sel)))
print()

print("  出现在**全部 %d 份**里的块：" % len(FILES))
allsame = [t for t, n in cnt.items() if n == len(FILES)]
if not allsame:
    print("     （一个都没有）")
for t in allsame:
    print("     %s…" % t[:90])
print()

# ---------------------------------------------------------------- ③ :root 变量分布
print("=" * 74)
print("③ 每份文件的 :root 里到底定义了哪些变量（这决定了 tg 层怎么设计）")
print("=" * 74)
for f in FILES:
    c = io.open(os.path.join(A, f), encoding="utf-8").read()
    vs = set()
    for conds, nd in all_rules(c):
        if conds:
            continue
        if re.match(r'^\s*:root\s*$', nd.prelude):
            for m in re.finditer(r'(--[\w-]+)\s*:', nd.body):
                vs.add(m.group(1))
    print("  %-30s %3d 个  %s" % (f, len(vs), " ".join(sorted(vs))[:96]))
