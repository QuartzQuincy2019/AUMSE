# -*- coding: utf-8 -*-
"""2d 收尾：把 FE 八篇的 <link> 顺序理顺。

目标顺序
    fe_base.css        FE 公共基础（本步新增）
    tg_L.css           全局亮色变量（--sfc 等，fe_base 里用到）
    tg_D.css           全局暗色变量
    series-theme.css   系列主题（FE 由 fe-data.js 接管，基本不匹配）
    fe_NN.css          该页自己的样式
    fe-dark.css        FE 暗色，**必须在最后** —— 这是它一直以来的定位

为什么现在顺序是乱的
    之前 FE 的 <head> 是 fe_NN → series-theme → fe-dark，
    第一步加 tg_L/tg_D 时按「插在最后一个 link 之后」追加，
    结果变成 fe_NN → series-theme → fe-dark → tg_L → tg_D，
    tg_L/tg_D 跑到了 fe-dark 后面，破坏了「fe-dark 最后」这个约定。

    实测（fe-01，亮/暗 × 宽/窄 四组）当前顺序的渲染是对的，
    但约定被破坏后很脆弱：以后任何给 tg 层加规则的人
    都会意外覆盖掉 fe-dark。所以这里把顺序摆正。

做法：把整段 stylesheet link 重排，不增不删（fe_base 若缺则补上）。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# 期望的先后次序（前面的先加载）
ORDER = ["fe_base.css", "tg_L.css", "tg_D.css", "series-theme.css",
         "fe-dark.css"]


def rank(fn):
    """该页自己的样式表排倒数第二，fe-dark 最后。"""
    if fn in ORDER:
        return ORDER.index(fn)
    return len(ORDER) - 1 + 0.5      # 页面自己的样式表


def main():
    n = 0
    for f in sorted(os.listdir(T)):
        if not (f.startswith("fe-") and f.endswith(".html")):
            continue
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        links = list(re.finditer(r'[ \t]*<link[^>]*href="assets/([^"]+\.css)"[^>]*>\n?', t))
        if not links:
            print("  ! %s 没有 stylesheet link" % f)
            continue
        names = [m.group(1) for m in links]
        # 该页自己的样式表 = 不在 ORDER 里的那个
        own = [x for x in names if x not in ORDER]
        if len(own) != 1:
            print("  ! %s 的页面样式表识别异常：%s" % (f, own))
            continue
        want = [x for x in ORDER if x in names]
        if "fe_base.css" not in want:
            want.insert(0, "fe_base.css")
        # 页面自己的样式表放 fe-dark 之前
        want = [x for x in want if x != "fe-dark.css"] + [own[0], "fe-dark.css"]
        if names == want:
            print("  %-20s 顺序已正确" % f)
            continue
        block = "".join('<link rel="stylesheet" href="assets/%s">\n' % x for x in want)
        st, en = links[0].start(), links[-1].end()
        t2 = t[:st] + block + t[en:]
        io.open(p, "w", encoding="utf-8", newline="").write(t2)
        print("  %-20s %s → %s" % (f, ", ".join(names), ", ".join(want)))
        n += 1
    print()
    print("  调整 %d 篇" % n)


if __name__ == "__main__":
    main()
