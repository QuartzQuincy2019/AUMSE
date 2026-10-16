# -*- coding: utf-8 -*-
"""放宽各构建脚本里「解析 h2 标题」的正则，让它同时接受两种写法。

问题
    这些脚本用同一条正则推导目录（`#toc`）并校验编号连续：
        <h2 id="sN"><span class="n">N</span>标题</h2>
    它要求 `<span class="n">` **紧跟** 在 `id="sN">` 之后。

    而重点小节（key-h）有两种写法：
      A. ★ 在数字前（t02 / f01 等手工页用的）
         <h2 id="s4" class="key-h"><span class="key-mark" …>★</span><span class="n">4</span>…
      B. ★ 在数字后（各 build_* 脚本生成的）
         <h2 id="s4" class="key-h"><span class="n">4</span><span class="key-mark" …>★</span>…

    严格式两种都匹配不上 → 目录少一条、编号连续性校验直接失败。
    实测：Q05 的 7 个小节只抓到 6 条，正是漏了 §3。

放宽后的正则
    <h2[^>]*id="(s\\d+)"[^>]*>
    (?:
        <span class="key-mark"[^>]*>[^<]*</span>)?      ← 允许 ★ 在前
    <span class="n">(\\d+)</span>
    (?:
        <span class="key-mark"[^>]*>[^<]*</span>)?      ← 允许 ★ 在后
    (标题)

    两处可选，A、B 就都覆盖了。

影响面
    5 个脚本：build_page.py / build_q02.py / build_r_pages.py /
              build_fe08_page.py / build_fe09_page.py
    改完各自重跑一遍，确认小节数与编号校验都过。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME\tools"

STRICT = ('<h2 id="(s\\d+)"><span class="n">(\\d+)</span>(.*?)</h2>')
LOOSE = ('<h2[^>]*id="(s\\d+)"[^>]*>'
         '(?:<span class="key-mark"[^>]*>[^<]*</span>)?'
         '<span class="n">(\\d+)</span>'
         '(?:<span class="key-mark"[^>]*>[^<]*</span>)?'
         '(.*?)</h2>')


def main():
    dry = "--dry" in sys.argv
    total = 0
    for f in sorted(os.listdir(R)):
        if not f.endswith(".py"):
            continue
        p = os.path.join(R, f)
        t = io.open(p, encoding="utf-8").read()
        if STRICT not in t:
            continue
        n = t.count(STRICT)
        t2 = t.replace(STRICT, LOOSE)
        # 自检：新正则在文件里必须是**字面**的 Python 字符串内容
        ok = (LOOSE in t2) and (STRICT not in t2)
        print("  %-24s 替换 %d 处 %s" % (f, n, "OK" if ok else "!! 有问题"))
        if ok and not dry:
            io.open(p, "w", encoding="utf-8", newline="").write(t2)
        total += n
    print()
    print("  合计 %d 处%s" % (total, "  [dry-run]" if dry else ""))
    print()
    # 用放宽后的正则验证 Q05
    q = os.path.join(R, "_q05_body.html")
    if os.path.exists(q):
        body = io.open(q, encoding="utf-8").read()
        hs = re.findall(LOOSE, body, re.S)
        ids = [h[0] for h in hs]
        nos = [int(h[1]) for h in hs]
        good = (ids == ["s%d" % i for i in range(1, len(ids) + 1)]
                and nos == list(range(1, len(nos) + 1)))
        print("  验证 Q05：抓到 %d 条，id/编号连续 = %s"
              % (len(hs), "是 OK" if good else "否 !!"))
        for h in hs:
            print("      %-4s %-2s %s" % (h[0], h[1],
                                          re.sub(r"<[^>]+>", "", h[2]).strip()))


if __name__ == "__main__":
    main()
