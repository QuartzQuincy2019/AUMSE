# -*- coding: utf-8 -*-
"""把每篇页尾的「本系列」小目录**整体重写**成 series_data.py 里的正确内容。

上一版是「找出旧的 <a> 再改文字」，漏了带星标的那 4 篇 ——
因为星标是 `<a>标题 <span class="star">*</span></a>`，
我的正则 `<a href="([^"]+)">([^<]*)</a>` 遇到内层 `<span>` 就匹配不上，
于是 m09 / f01 / f02 / f03 四项原样留了下来。

教训：**不要从产物里反推数据**。篇目表已经在 series_data.py 里了，
直接用数据重新生成整块，比修修补补可靠得多，也不会再漏。

顺带把「本系列」的语义也修正：原来 M / Q / E / F / T 全混在一条里，
现在按**各自系列**列出（本系列就是本系列），另加一行「全部系列」做跳转。
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from series_data import SERIES, PAGES, ORDER, pages_of  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
META = {p[1]: p for p in PAGES}


def build_nav(cur_file, sk):
    """生成页尾小目录：本系列全部篇目 + 一行系列跳转。"""
    s = SERIES[sk]
    mine = pages_of(sk)
    out = ['<div class="series-nav">']
    out.append('<b>本系列</b>　<span class="series-tag">%s</span>　' % s["banner"])
    for p in mine:
        _old, new, _sk, num, title, _d, star = p
        cls = ' class="cur"' if new == cur_file else ''
        star_html = ' <span class="star" title="与本项目施行密切相关">*</span>' if star else ''
        out.append('<a href="%s"%s>%s %s%s</a>'
                   % (new, cls, num, title, star_html))
    out.append('</div>')
    return "\n".join(out)


def build_switcher(cur_file, sk):
    """全部系列的跳转条（并列系列之间互跳）。"""
    out = ['<div class="series-switch">']
    out.append('<b>全部系列</b>　')
    for k in ORDER:
        s = SERIES[k]
        n = len(pages_of(k))
        label = "%s（%d 篇%s）" % (s["label"], n, "，暂空" if n == 0 else "")
        if k == sk:
            out.append('<span class="ss-cur">%s</span>' % label)
        else:
            # 跳到该系列第一篇；R 还没有篇目，就先不生成链接
            if n == 0:
                out.append('<span class="ss-empty">%s</span>' % label)
            else:
                first = pages_of(k)[0][1]
                out.append('<a href="%s">%s</a>' % (first, label))
    out.append('</div>')
    return "\n".join(out)


def main():
    n = 0
    for p in PAGES:
        new, sk = p[1], p[2]
        path = os.path.join(T, new)
        if not os.path.exists(path):
            print("  ! 找不到 %s" % new)
            continue
        t = io.open(path, encoding="utf-8").read()

        block = build_nav(new, sk) + "\n" + build_switcher(new, sk)
        m = re.search(r'(?s)<div class="series-nav">.*?</div>', t)
        if m:
            t = t[:m.start()] + block + t[m.end():]
        else:
            # T 篇原来没有页尾小目录（用的是 t-common.js 的动态跳转），
            # 现在统一补上静态兜底 —— 即使 JS 没跑也有得跳
            m2 = re.search(r'</main>', t)
            if not m2:
                print("  ! %s 没有 </main>" % new)
                continue
            t = t[:m2.start()] + block + "\n" + t[m2.start():]
        io.open(path, "w", encoding="utf-8", newline="").write(t)
        n += 1
    print("  页尾小目录已按数据重写：%d 篇" % n)


if __name__ == "__main__":
    main()
