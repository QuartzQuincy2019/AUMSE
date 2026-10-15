# -*- coding: utf-8 -*-
"""把三篇 T 接到统一主题上，并完成用户要求的其余改动。

改动清单（对应用户 1~5 条）：
  1. 整篇金色渐变背景 —— 三篇都 <link> assets/t-theme.css（最后加载）
     并加 body class="tseries"；T02 去掉 class="fseries"（覆盖旧的蓝色皮肤）
  2. 暗色模式适配 —— 由 t-theme.css 的 prefers-color-scheme 段完成；
     这里额外插一段**极早执行**的脚本，先按系统偏好定好配色方案，
     避免亮→暗闪一下（FOUC）
  3. 删掉 T02 里「一句话记住三篇的分工」那张 card
  4. 修「返回 home」样式 —— 原来只在 T02 的内嵌 <style> 里，
     T01 / T03 因此是裸链接。现在统一定义在 t-theme.css，
     并把三篇的内嵌 <style> 一并去掉（回归「样式都在 assets/」的约定）
  5. 文末动态生成 T 系列内部跳转 —— 由 assets/t-common.js 完成，这里只挂脚本
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

FILES = ["t01-mongolian-script-intro.html",
         "t02-unicode-and-encoding.html",
         "t03-font-file-anatomy.html"]

THEME_LINK = '<link rel="stylesheet" href="assets/t-theme.css">'
COMMON_JS = '<script src="assets/t-common.js"></script>'

# 极早执行：先定配色方案，避免暗色模式下的白闪
ANTI_FLASH = '''<script>
/* 极早执行：在样式生效前就按系统偏好声明配色方案，避免亮→暗闪一下 */
(function(){var d=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;
var m=document.createElement('meta');m.name='color-scheme';
m.content=d?'dark light':'light dark';document.head.appendChild(m);})();
</script>'''


def main():
    for f in FILES:
        p = os.path.join(T, f)
        t = io.open(p, encoding="utf-8").read()
        acts = []

        # ---- ① body class ----
        m = re.search(r'<body([^>]*)>', t)
        if not m:
            print("  ! %s 没有 body 标签" % f)
            continue
        attrs = m.group(1)
        cls = re.search(r'class="([^"]*)"', attrs)
        if cls:
            classes = [c for c in cls.group(1).split()
                       if c not in ("fseries", "tseries")]
        else:
            classes = []
        classes.insert(0, "tseries")
        newbody = '<body class="%s">' % " ".join(classes)
        t = t[:m.start()] + newbody + t[m.end():]
        acts.append("body.tseries")

        # ---- ② 主题样式表：放在最后一个 <link> 之后（保证能压过旧主题）----
        if THEME_LINK not in t:
            links = list(re.finditer(r'<link[^>]*rel="stylesheet"[^>]*>', t))
            if links:
                last = links[-1]
                t = t[:last.end()] + "\n" + THEME_LINK + t[last.end():]
            else:
                t = t.replace("</head>", THEME_LINK + "\n</head>", 1)
            acts.append("t-theme.css")

        # ---- ④ 去掉内嵌 <style>（规则已进 t-theme.css）----
        sm = re.search(r'(?s)\n?<style>.*?</style>\n?', t)
        if sm:
            t = t[:sm.start()] + "\n" + t[sm.end():]
            acts.append("去内嵌 style")

        # ---- ② 防闪脚本：紧跟 <body ...> ----
        if "避免亮→暗闪一下" not in t:
            m2 = re.search(r'<body[^>]*>', t)
            t = t[:m2.end()] + "\n" + ANTI_FLASH + t[m2.end():]
            acts.append("防闪脚本")

        # ---- ⑤ 系列跳转脚本：放在 </body> 之前 ----
        if COMMON_JS not in t:
            t = t.replace("</body>", COMMON_JS + "\n</body>", 1)
            acts.append("t-common.js")

        # ---- ③ 删掉 T02 那张 card ----
        if f.startswith("t02"):
            mk = '<div class="card-t">一句话记住三篇的分工</div>'
            i = t.find(mk)
            if i >= 0:
                start = t.rfind('<div class="card', 0, i)
                # 靠层数配平找结尾
                depth, j = 0, start
                while j < len(t):
                    if t.startswith("<div", j):
                        depth += 1; j += 4
                    elif t.startswith("</div>", j):
                        depth -= 1
                        if depth == 0:
                            j += len("</div>"); break
                        j += 6
                    else:
                        j += 1
                a = start
                while a > 0 and t[a - 1] in "\r\n":
                    a -= 1
                t = t[:a] + "\n" + t[j:].lstrip("\r\n")
                acts.append("删「一句话记住三篇的分工」")
            else:
                acts.append("（那张 card 已不在）")

        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("  ✔ %-36s %s" % (f, " · ".join(acts)))


if __name__ == "__main__":
    main()
