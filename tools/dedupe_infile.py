# -*- coding: utf-8 -*-
"""文件内去重：把「同一个文件里、同选择器、声明逐字相同」的重复规则删掉。

为什么这是安全的
----------------
同一份文件里两条选择器与声明都完全相同的规则，**后者完全覆盖前者**，
删掉前一条不改变任何计算结果（包括层叠顺序 —— 保留最后一条即可）。

不碰什么
--------
  · 同选择器但**声明不同**的（那是有意的覆盖，比如 #toc 的 274px/270px）
  · 媒体查询里的规则（另有条件，单独处理）
  · 选择器不同但文本相同的（不做跨选择器合并）

用法：
    python dedupe_infile.py            # 全部处理
    python dedupe_infile.py --only x.css
    python dedupe_infile.py --dry      # 只报告不修改
"""
import io
import os
import re
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cssparse import parse, norm  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

A = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\assets"
SKIP = {"series-theme.css", "t-theme.css", "fe-dark.css",
        "tg_L.css", "tg_D.css"}


def balanced(css):
    d = 0
    i, n = 0, len(css)
    while i < n:
        if css[i:i + 2] == '/*':
            j = css.find('*/', i + 2)
            if j < 0:
                return False
            i = j + 2
            continue
        if css[i] == '{':
            d += 1
        elif css[i] == '}':
            d -= 1
            if d < 0:
                return False
        i += 1
    return d == 0


def body_key(body):
    """声明的归一化键。

    关键细节：两份「看起来一样」的规则常常只差一个**结尾分号**
    （`.card{…}` 与 `.card{…;}`）。不把它规整掉，去重会一条都找不到
    —— 第一次跑就是 0 条，查了半天才发现是差一个 ';'。
    CSS 里结尾分号可有可无，语义完全相同。
    """
    s = norm(body)
    s = re.sub(r'\s*;\s*$', '', s)          # 去掉结尾分号
    s = re.sub(r'\s*;\s*', ';', s)          # 规整中间分号
    return s.strip()


def dup_spans(css):
    """返回可以安全删除的规则区间列表。

    只处理**顶层**规则：按 (归一化选择器, 归一化声明) 分组，
    同组内保留最后一个，其余标记删除。
    """
    groups = collections.defaultdict(list)
    for nd in parse(css):
        if nd.kind != 'rule':
            continue
        key = (norm(nd.prelude), body_key(nd.body))
        groups[key].append((nd.start, nd.end))
    kill = []
    for key, lst in groups.items():
        if len(lst) > 1:
            kill.extend(lst[:-1])          # 保留最后一个
    return sorted(kill)


def main():
    dry = "--dry" in sys.argv
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    files = sorted(f for f in os.listdir(A)
                   if f.endswith(".css") and f not in SKIP)
    tot_kill = tot_before = tot_after = 0
    bad = 0
    for f in files:
        if only and f != only:
            continue
        p = os.path.join(A, f)
        c = io.open(p, encoding="utf-8").read()
        before = len(c)
        kill = dup_spans(c)
        if not kill:
            print("  %-30s 无重复" % f)
            continue
        if not dry:
            for (st, en) in reversed(kill):
                c = c[:st] + c[en:]
            c = re.sub(r'\n{3,}', '\n\n', c)
            if not balanced(c):
                print("  !! %-28s 删后不配平，跳过" % f)
                bad += 1
                continue
            io.open(p, "w", encoding="utf-8", newline="").write(c)
        tot_kill += len(kill)
        tot_before += before
        tot_after += len(c)
        print("  %-30s 删 %2d 条  %6d → %6d B" % (f, len(kill), before, len(c)))
    print()
    print("  共删 %d 条重复规则，%d → %d B（−%d）%s"
          % (tot_kill, tot_before, tot_after, tot_before - tot_after,
             "  [dry-run]" if dry else ""))
    if bad:
        print("  跳过 %d 份（结构自检不过）" % bad)


if __name__ == "__main__":
    main()
