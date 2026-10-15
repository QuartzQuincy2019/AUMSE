# -*- coding: utf-8 -*-
"""重建导航页（index.html / home.html）

本次改动：
  1. 每张卡显示完整讲次编号，如「08-E02」「01」「10」
  2. 带 * 的篇目显著加强：
     - 左侧金色粗条 + 淡金底色
     - 实心 ★ 徽章（不再是小小的上标星号）
     - 底部标注「与本项目施行密切相关」
  3. 加入第十讲，共 16 篇
  4. 09-F04《Unicode 和编码》改号 09-E03（E 系列更贴切，F 留给 File）
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
TUT = os.path.join(REPO, "SharingGroup", "tutorials")
ASSETS = os.path.join(TUT, "assets")

# 这一轮的重命名：旧名 → 新名
RENAME = {
    "09-f04-unicode-and-encoding.html": "09-e03-unicode-and-encoding.html",
}
CSS_RENAME = {
    "09-f04.css": "09-e03.css",
}

# (文件名, 编号, 标题, 一句话说明, 类别, 是否星标)
META = [
    ("01-c-arrays.html",                 "01",      "数组初步",                 "一排数据怎么存、怎么遍历",                     "C",     False),
    ("02-c-functions.html",              "02",      "函数初步",                 "重复的代码怎么打包复用",                       "C",     False),
    ("03-c-types.html",                  "03",      "类型概论",                 "数据在内存里占多宽、怎么解释",                 "C",     False),
    ("04-c-pointers.html",               "04",      "指针初步",                 "地址是什么、怎么顺着地址改数据",               "C",     False),
    ("05-memory.html",                   "05",      "静态、动态内存与内存安全初步", "内存从哪来、怎么还、怎么不崩",                 "C",     False),
    ("06-class-struct.html",             "06",      "类、结构体",               "数据和行为怎么打包、怎么保护",                 "C++",   False),
    ("07-scope.html",                    "07",      "作用域、全局与局部变量",    "一个名字能被谁看见、活多久",                   "C",     False),
    ("08-c-strings.html",                "08",      "C 风格字符串",             "一串文字怎么存、\\0 为什么重要",                "C",     False),
    ("09-vector-and-array.html",         "09",      "vector 和 array",          "更安全的数组、自动管内存",                     "C++",   True),
    ("10-std-and-namespace.html",        "10",      "std 与命名空间初步",        "从这里进入 C++：std:: 是什么、using 该不该用",  "C++",   False),
    ("08-e01-recursion.html",            "08-E01",  "递归",                     "函数自己调用自己",                             "Extra", False),
    ("08-e02-batch-and-cmd.html",        "08-E02",  "批处理与命令提示符进阶",    "把命令写成 .bat 一键重跑，接上 node / npm / python", "Extra", False),
    ("09-e03-unicode-and-encoding.html", "09-E03",  "Unicode 和编码",           "文字怎么变成字节、变长编码的设计思路",         "Extra", True),
    ("08-f01-command-prompt.html",       "08-F01",  "命令提示符（cmd）初步",     "怎么打开、最该先会的几条命令",                 "File",  True),
    ("08-f02-paths-and-env.html",        "08-F02",  "相对文件路径与宏",          "文件在哪、环境变量是什么、VS 属性宏",          "File",  True),
    ("08-f03-compile-and-link.html",     "08-F03",  "编译与链接、头文件与库",    "三步原理 + VS 2026 静态库手把手",              "File",  True),
]

STYLE = """<style>
:root{
  --bg:#ffffff; --bg-soft:#f7f9fc; --line:#e3e8f0; --line-2:#ccd5e3;
  --fg:#1a1f28; --fg-2:#4b5563; --fg-3:#8b95a5;
  --blue:#1f6feb; --blue-soft:#e8f1fe;
  --green:#17864a; --green-soft:#e7f6ee;
  --violet:#6b46c1; --violet-soft:#f2ecfd;
  --amber:#a4690d; --amber-soft:#fdf4e3;
  --teal:#0d7d7d; --teal-soft:#e4f5f5;
  --gold:#c8901a; --gold-line:#e8c877;
  --mono:"Consolas","Cascadia Mono","Courier New",monospace;
  --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB",system-ui,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.8 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1120px;margin:0 auto;padding:48px 24px 80px}

header{border-bottom:1px solid var(--line);padding-bottom:26px;margin-bottom:8px}
h1{margin:0 0 8px;font-size:30px;letter-spacing:-.01em}
.sub{color:var(--fg-3);font-size:14px;margin:0}
.lead{background:var(--blue-soft);border:1px solid #cfe1fb;border-left:4px solid var(--blue);
  border-radius:0 10px 10px 0;padding:14px 18px;margin:26px 0 34px;font-size:14.5px}
.lead b{color:var(--blue)}
.lead p{margin:0 0 6px}
.lead p:last-child{margin-bottom:0}

h2{font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-3);
  font-weight:600;margin:38px 0 14px;display:flex;align-items:center;gap:10px}
h2::after{content:"";flex:1;height:1px;background:var(--line)}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(324px,1fr));gap:14px}
.card{display:block;text-decoration:none;color:inherit;background:#fff;
  border:1px solid var(--line-2);border-radius:12px;padding:15px 18px;
  position:relative;transition:box-shadow .16s,transform .16s,border-color .16s}
.card:hover{box-shadow:0 8px 24px rgba(30,45,70,.13);transform:translateY(-2px);
  border-color:var(--blue)}
.card .top{display:flex;align-items:center;gap:9px;margin-bottom:8px;flex-wrap:wrap}
.card .no{font-family:var(--mono);font-size:12.5px;font-weight:700;
  letter-spacing:.02em;padding:2px 9px;border-radius:6px;
  background:#eef2f8;border:1px solid var(--line-2);color:var(--fg-2)}
.card .tt{font-weight:700;font-size:16.5px;margin-bottom:4px}
.card .ds{font-size:13px;color:var(--fg-3);line-height:1.6}

.k{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.04em;
  padding:1px 7px;border-radius:999px}
.k-c{background:var(--green-soft);color:var(--green);border:1px solid #bfe2cd}
.k-cpp{background:var(--violet-soft);color:var(--violet);border:1px solid #ded0f7}
.k-file{background:var(--blue-soft);color:var(--blue);border:1px solid #cfe1fb}
.k-extra{background:var(--amber-soft);color:var(--amber);border:1px solid #efd9a8}

/* ---------- 星标篇目：显著加强 ---------- */
.card.star{
  background:linear-gradient(135deg,#fffdf5 0%,#fdf3dc 100%);
  border:1px solid var(--gold-line);
  border-left:6px solid var(--gold);
  box-shadow:0 2px 8px rgba(200,144,26,.10);
}
.card.star:hover{border-color:var(--gold);border-left-color:var(--gold);
  box-shadow:0 10px 28px rgba(200,144,26,.22)}
.card.star .tt{color:#7a5307}
.card.star .no{background:#fbeecb;border-color:var(--gold-line);color:#8a5e0c}
.star-badge{display:inline-flex;align-items:center;gap:4px;
  font-size:11px;font-weight:700;letter-spacing:.02em;
  padding:2px 9px;border-radius:999px;
  background:var(--gold);color:#fff;box-shadow:0 1px 3px rgba(200,144,26,.35)}
.star-flag{margin-top:9px;font-size:11.5px;font-weight:600;color:#8a5e0c}

.note{margin-top:38px;border:1px solid var(--line-2);border-radius:12px;
  padding:16px 20px;background:var(--bg-soft);font-size:13.5px;color:var(--fg-2)}
.note h3{margin:0 0 8px;font-size:14px;color:var(--fg)}
.note table{border-collapse:collapse;margin-top:8px;font-size:13px}
.note td{padding:3px 14px 3px 0;vertical-align:top}
.note code,.lead code{font-family:var(--mono);font-size:12.5px;background:#eef2f8;
  border:1px solid var(--line);border-radius:4px;padding:1px 5px}

footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
  color:var(--fg-3);font-size:12.5px}

@media (max-width:560px){
  .wrap{padding:28px 16px 56px}
  h1{font-size:23px}
  .grid{grid-template-columns:1fr}
  .card.star{border-left-width:5px}
}
</style>"""


def card(fn, num, title, desc, kind, star):
    k = {"C": "k-c", "C++": "k-cpp", "File": "k-file", "Extra": "k-extra"}[kind]
    parts = ['<span class="no">%s</span>' % num,
             '<span class="k %s">%s</span>' % (k, kind)]
    if star:
        parts.insert(0, '<span class="star-badge">\u2605 重点</span>')
    flag = ('\n        <div class="star-flag">\u2605 与本项目施行密切相关</div>'
            if star else "")
    return ('      <a class="card%s" href="SharingGroup/tutorials/%s">\n'
            '        <div class="top">%s</div>\n'
            '        <div class="tt">%s</div>\n'
            '        <div class="ds">%s</div>%s\n'
            '      </a>' % (" star" if star else "", fn, "".join(parts),
                            title, desc, flag))


def build_html():
    main_cards = [card(*m) for m in META if m[4] in ("C", "C++")]
    more_cards = [card(*m) for m in META if m[4] in ("Extra", "File")]
    n_star = sum(1 for m in META if m[5])

    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UME 项目组内部教程 · 总目录</title>
''' + STYLE + '''
</head>
<body>
<div class="wrap">

<header>
  <h1>UME 项目组内部教程</h1>
  <p class="sub">回鹘蒙文编辑器（Uyghur-Mongolian Script Editor）· 面向零编程基础的成员 ·
     共 %(total)d 篇</p>
</header>

<div class="lead">
  <p><b>怎么用这套教程</b>：从 01 开始按顺序看，每篇里的代码建议<b>亲手敲一遍</b>。</p>
  <p><b>01~08 讲 C 语言，09 起进入 C++</b>（因为项目实际用的 Qt 是 C++ 框架）。</p>
  <p>每张卡片左上角是<b>讲次编号</b>（如 <code>08-E02</code>），旁边是语言标记。
     其中 <b>%(nstar)d 篇</b>标着 <span class="star-badge">\u2605 重点</span> ——
     它们<b>与本项目施行密切相关</b>，卡片底色也不同。</p>
</div>

<h2>正文 · 01 ~ 10</h2>
<div class="grid">
%(main)s
</div>

<h2>Extra · File · 补充与实用</h2>
<div class="grid">
%(more)s
</div>

<div class="note">
  <h3>编号怎么看</h3>
  <table>
    <tr><td><code>01</code> ~ <code>10</code></td><td>正文讲次，按顺序看</td></tr>
    <tr><td><code>08-E01</code></td><td>第 08 讲之后的 <b>E</b>xtra（通用补充技巧）</td></tr>
    <tr><td><code>08-F02</code></td><td>第 08 讲之后的 <b>F</b>ile（动手实用内容）</td></tr>
    <tr><td><span class="k k-c">C</span></td><td>用 <code>gcc</code>（或 VS 里的 <code>.c</code>）编译</td></tr>
    <tr><td><span class="k k-cpp">C++</span></td><td>用 <code>g++</code>（或 VS 里的 <code>.cpp</code>）编译</td></tr>
  </table>
  <p style="margin-top:10px">09 之前的篇目以 C 为主。凡是不可避免地用到 C++ 的地方，
  代码块标题栏上都会挂一个紫色的 <span class="k k-cpp">C++</span> 徽标。</p>
  <p>文中所有「运行结果」与实际报错，都是在真实环境里跑出来的，不是凭记忆写的。</p>
</div>

<footer>
  UME 项目组内部教程 · 共 %(total)d 篇 · 样式表位于
  <code>SharingGroup/tutorials/assets/</code>
</footer>

</div>
</body>
</html>
''' % {"total": len(META), "nstar": n_star,
       "main": "\n".join(main_cards), "more": "\n".join(more_cards)}


def main():
    # ---- 1. 重命名（幂等）----
    for old, new in RENAME.items():
        s, d = os.path.join(TUT, old), os.path.join(TUT, new)
        if os.path.exists(d):
            continue
        if os.path.exists(s):
            os.rename(s, d)
            print("  改名：%s → %s" % (old, new))
        else:
            print("  !! 找不到 %s" % old)
    for old, new in CSS_RENAME.items():
        s, d = os.path.join(ASSETS, old), os.path.join(ASSETS, new)
        if os.path.exists(d):
            continue
        if os.path.exists(s):
            os.rename(s, d)
            print("  改名：assets/%s → assets/%s" % (old, new))

    for _, new in RENAME.items():
        p = os.path.join(TUT, new)
        if not os.path.exists(p):
            continue
        t = io.open(p, encoding="utf-8").read()
        for o, n in CSS_RENAME.items():
            t = t.replace('href="assets/%s"' % o, 'href="assets/%s"' % n)
        io.open(p, "w", encoding="utf-8", newline="").write(t)

    # ---- 2. 生成导航页 ----
    html = build_html()
    for out in ("index.html", "home.html"):
        io.open(os.path.join(REPO, out), "w", encoding="utf-8", newline="").write(html)
    print("  已生成 index.html / home.html（%d 字符）" % len(html))

    # ---- 3. 自检 ----
    bad = 0
    for m in re.finditer(r'href="(SharingGroup/tutorials/[^"]+)"', html):
        p = os.path.join(REPO, m.group(1).replace("/", os.sep))
        if not os.path.exists(p):
            print("  !! 链接失效: %s" % m.group(1))
            bad += 1
    for name in os.listdir(TUT):
        if not name.endswith(".html"):
            continue
        t = io.open(os.path.join(TUT, name), encoding="utf-8").read()
        for m in re.finditer(r'href="(assets/[^"]+)"', t):
            p = os.path.join(TUT, m.group(1).replace("/", os.sep))
            if not os.path.exists(p):
                print("  !! %s 的 css 缺失: %s" % (name, m.group(1)))
                bad += 1
    print("  链接检查：%s" % ("全部有效" if bad == 0 else "%d 处失效" % bad))
    print("  共 %d 篇，其中星标 %d 篇"
          % (len(META), sum(1 for m in META if m[5])))


if __name__ == "__main__":
    main()
