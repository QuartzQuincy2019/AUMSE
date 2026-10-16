# -*- coding: utf-8 -*-
"""共用：从 HTML 里找出「该页自己的样式表」。

为什么要这个函数
----------------
之前的脚本都用 `re.search(r'<link[^>]*href="assets/([^"]+\\.css)"', h)`
取**第一个** stylesheet —— 在只有「页面样式表 + series-theme」的时候没问题。

但分层之后，`<head>` 里先是 genelayout / tg_L / tg_D 这些**全局层**，
再才是该页自己的样式表。于是「第一个」变成了 genelayout.css，
被 SKIP 一过滤，目标页面数直接变 0 ——
`build_genelayout.py` 因此把好端端的产物覆盖成了空壳（第二次踩同一个坑）。

正确做法：把已知的全局层排除掉，剩下的第一个才是该页自己的样式表。
"""
import re

# 全局层（所有页面共用，不是「某页的样式表」）
GLOBAL_CSS = {
    "genelayout.css",     # 公共布局层
    "tg_L.css", "tg_D.css",   # 全局主题层
    "series-theme.css",   # 系列主题
    "t-theme.css",        # T 系列主题
    "fe-dark.css",        # FE 暗色
    "tutorial.css",        # 早期共用基础（现已并入 genelayout）
}


def page_css_of(html):
    """返回该页自己的样式表文件名；找不到返回 None。"""
    for m in re.finditer(r'<link[^>]*href="assets/([^"]+\.css)"', html):
        fn = m.group(1)
        if fn not in GLOBAL_CSS:
            return fn
    return None
