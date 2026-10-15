# -*- coding: utf-8 -*-
"""让「示例展示」里的 id 在同一页内唯一。

问题：FE-04 有十几个示例，每个的 demo HTML 都含 <p id="uniq">，
      整页就有十几个重复 id —— HTML 不允许。
修法：只对「demo 自带的 id」做唯一化。
      * 怎么区分？pv() 生成的示例框是 data-pv-kind="css" 的，
        里面的 id 来自 demo；而目录锚点（id="s1" 等）在 <nav> 里、不在 pv-body 里。
      * 改 id 的同时，把该示例框里 CSS 代码中的 #id 选择器一起改掉，
        否则示例就不生效了。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"


def find_div_span(html, start):
    """从 <div ...> 的 start 位置起，返回配对 </div> 的结束位置。"""
    i = html.find(">", start)
    if i < 0:
        return -1
    depth = 1
    pat = re.compile(r'<(/?)div(\s[^>]*)?>', re.I)
    for m in pat.finditer(html, i + 1):
        if m.group(1):
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    return -1


def main():
    changed_total = 0
    for fn in sorted(f for f in os.listdir(TUT)
                     if f.startswith("fe-") and f.endswith(".html")):
        p = os.path.join(TUT, fn)
        t = io.open(p, encoding="utf-8").read()
        if 'data-pv-kind="css"' not in t:
            continue

        # 已处理过的跳过（id 里带编号）
        if re.search(r'id="uniq\d+"', t):
            print("  · %-16s 已经唯一化" % fn)
            continue

        out, pos, n_fixed = [], 0, 0
        for m in re.finditer(r'<div class="pv-wrap" data-pv="(\d+)" data-pv-kind="css">', t):
            num = m.group(1)
            end = find_div_span(t, m.start())
            if end < 0:
                continue
            block = t[m.start():end]
            ids = set(re.findall(r'id="([^"]+)"', block))
            if not ids:
                continue
            nb = block
            for old in ids:
                new = "%s%s" % (old, num)
                nb = nb.replace('id="%s"' % old, 'id="%s"' % new)
                nb = nb.replace("#" + old, "#" + new)
            if nb != block:
                out.append(t[pos:m.start()])
                out.append(nb)
                pos = end
                n_fixed += 1
        if out:
            out.append(t[pos:])
            t = "".join(out)
            io.open(p, "w", encoding="utf-8", newline="").write(t)
            print("  ✔ %-16s 唯一化 %d 个示例框的 id" % (fn, n_fixed))
            changed_total += n_fixed
        else:
            print("  · %-16s 无需改动" % fn)
    print("\n  合计处理 %d 个示例框" % changed_total)


if __name__ == "__main__":
    main()
