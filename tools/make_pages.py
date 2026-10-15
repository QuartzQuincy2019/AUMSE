# -*- coding: utf-8 -*-
"""为 GitHub Pages 做收尾：
   1. 把 15 篇教程改成 ASCII 文件名
      —— 现在的名字里有「、」「（）」等全角字符，在 URL 里要百分号编码，
         虽然浏览器能处理，但复制出来是一长串 %E3%80%81，对公开站点不友好。
         改完之后地址就是纯 ASCII，可以直接手打。
   2. 生成仓库根的 index.html —— 导航页（GitHub Pages 的默认入口）
"""
import io
import os
import re
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = r"E:\QKMansion\CSX10\w\UME"
TUT = os.path.join(REPO, "SharingGroup", "tutorials")
ASSETS = os.path.join(TUT, "assets")

# 旧名 → 新名。保持讲次顺序可读，纯 ASCII。
RENAME = {
    "_ds_01_C风格数组初步.html":                    "01-c-arrays.html",
    "_ds_02_C函数初步.html":                        "02-c-functions.html",
    "_ds_03_C类型概论.html":                        "03-c-types.html",
    "_ds_04_C指针初步.html":                        "04-c-pointers.html",
    "_ds_05_静态、动态内存与内存安全初步.html":           "05-memory.html",
    "_ds_06_类、结构体.html":                       "06-class-struct.html",
    "_ds_07_作用域、全局与局部变量.html":               "07-scope.html",
    "_ds_08_C风格字符串.html":                      "08-c-strings.html",
    "_ds_08_E01_递归.html":                        "08-e01-recursion.html",
    "_ds_08_E02_批处理与命令提示符进阶.html":           "08-e02-batch-and-cmd.html",
    "_ds_08_F01_命令提示符初步.html":                 "08-f01-command-prompt.html",
    "_ds_08_F02_相对文件路径与宏.html":                "08-f02-paths-and-env.html",
    "_ds_08_F03_编译与链接、头文件与库.html":            "08-f03-compile-and-link.html",
    "_ds_09_F04_Unicode和编码.html":               "09-f04-unicode-and-encoding.html",
    "_ds_09_vector和array.html":                  "09-vector-and-array.html",
}

# 学生看的中文标题 + 一句话说明
META = [
    ("01-c-arrays.html",              "数组初步",               "一排数据怎么存、怎么遍历",                  "C",   ""),
    ("02-c-functions.html",           "函数初步",               "重复的代码怎么打包复用",                    "C",   ""),
    ("03-c-types.html",               "类型概论",               "数据在内存里占多宽、怎么解释",              "C",   ""),
    ("04-c-pointers.html",            "指针初步",               "地址是什么、怎么顺着地址改数据",            "C",   ""),
    ("05-memory.html",                "静态、动态内存与内存安全初步", "内存从哪来、怎么还、怎么不崩",           "C",   ""),
    ("06-class-struct.html",          "类、结构体",             "数据和行为怎么打包、怎么保护",              "C++", ""),
    ("07-scope.html",                 "作用域、全局与局部变量",   "一个名字能被谁看见、活多久",                "C",   ""),
    ("08-c-strings.html",             "C 风格字符串",           "一串文字怎么存、<code>\\0</code> 为什么重要",  "C",   ""),
    ("08-e01-recursion.html",         "递归",                   "函数自己调用自己",                          "Extra", ""),
    ("08-e02-batch-and-cmd.html",     "批处理与命令提示符进阶",   "把命令写成 .bat 一键重跑，接上 node / npm / python", "Extra", ""),
    ("08-f01-command-prompt.html",    "命令提示符（cmd）初步",    "怎么打开、最该先会的几条命令",              "File",  "related"),
    ("08-f02-paths-and-env.html",     "相对文件路径与宏",        "文件在哪、环境变量是什么、VS 属性宏",        "File",  "related"),
    ("08-f03-compile-and-link.html",  "编译与链接、头文件与库",   "三步原理 + VS 2026 静态库手把手",           "File",  "related"),
    ("09-vector-and-array.html",      "vector 和 array",        "更安全的数组、自动管内存",                  "C++",  "related"),
    ("09-f04-unicode-and-encoding.html", "Unicode 和编码",       "文字怎么变成字节、变长编码的设计思路",       "File",  "related"),
]


def main():
    # ---------- 1. 改名（幂等：已改过的跳过）----------
    os.makedirs(ASSETS, exist_ok=True)
    moved, skipped = [], 0
    for old, new in RENAME.items():
        src = os.path.join(TUT, old)
        dst = os.path.join(TUT, new)
        if os.path.exists(dst):
            skipped += 1                      # 已经是新名
            continue
        if os.path.exists(src):
            os.rename(src, dst)
            moved.append((old, new))
        else:
            print("  !! 新旧名都找不到: %s" % old)

    # assets 里的 css 也跟着改成对应讲次号，便于对照
    css_rename = {
        "ds_01_C.css": "01.css", "ds_02_C.css": "02.css", "ds_03_C.css": "03.css",
        "ds_05.css": "05.css", "ds_06.css": "06.css", "ds_07.css": "07.css",
        "ds_08_C.css": "08.css", "ds_08_E01.css": "08-e01.css",
        "ds_08_E02.css": "08-e02.css", "ds_08_F01.css": "08-f01.css",
        "ds_08_F02.css": "08-f02.css", "ds_08_F03.css": "08-f03.css",
        "ds_09_F04_Unicode.css": "09-f04.css",
        "ds_09_vector_array.css": "09.css",
    }
    for old, new in css_rename.items():
        s, d = os.path.join(ASSETS, old), os.path.join(ASSETS, new)
        if os.path.exists(s):
            if os.path.exists(d):
                os.remove(d)
            os.rename(s, d)

    # 更新 html 里的 css 引用
    for _, new_html in RENAME.items():
        p = os.path.join(TUT, new_html)
        if not os.path.exists(p):
            continue
        t = io.open(p, encoding="utf-8").read()
        for old, new in css_rename.items():
            t = t.replace('href="assets/%s"' % old, 'href="assets/%s"' % new)
        io.open(p, "w", encoding="utf-8", newline="").write(t)

    print("改名 %d 篇，%d 篇已是新名；assets 里 css 也已改名" % (len(moved), skipped))

    # ---------- 2. 导航页 ----------
    def make_card(fn, title, desc, kind, star):
        badge = ""
        if kind == "Extra":
            badge = '<span class="k k-extra">Extra</span>'
        elif kind == "File":
            badge = '<span class="k k-file">File</span>'
        elif kind == "C++":
            badge = '<span class="k k-cpp">C++</span>'
        else:
            badge = '<span class="k k-c">C</span>'
        s = '<span class="st" title="与本项目施行密切相关">*</span>' if star else ""
        return ('      <a class="card%s" href="SharingGroup/tutorials/%s">\n'
                '        <div class="top">%s%s</div>\n'
                '        <div class="tt">%s</div>\n'
                '        <div class="ds">%s</div>\n'
                '      </a>' % (" star" if star else "", fn, badge, s, title, desc))

    main_cards = [make_card(*m) for m in META if m[3] in ("C", "C++")]
    more_cards = [make_card(*m) for m in META if m[3] in ("Extra", "File")]

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>UME 项目组内部教程 · 总目录</title>
<style>
:root{
  --bg:#ffffff; --bg-soft:#f7f9fc; --line:#e3e8f0; --line-2:#ccd5e3;
  --fg:#1a1f28; --fg-2:#4b5563; --fg-3:#8b95a5;
  --blue:#1f6feb; --blue-soft:#e8f1fe;
  --green:#17864a; --green-soft:#e7f6ee;
  --violet:#6b46c1; --violet-soft:#f2ecfd;
  --amber:#a4690d; --amber-soft:#fdf4e3;
  --teal:#0d7d7d; --teal-soft:#e4f5f5;
  --mono:"Consolas","Cascadia Mono","Courier New",monospace;
  --sans:"Microsoft YaHei","PingFang SC","Hiragino Sans GB",system-ui,sans-serif;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:16px/1.8 var(--sans);-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:48px 24px 80px}

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

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
.card{display:block;text-decoration:none;color:inherit;background:#fff;
  border:1px solid var(--line-2);border-radius:12px;padding:16px 18px;
  transition:box-shadow .16s,transform .16s,border-color .16s}
.card:hover{box-shadow:0 8px 24px rgba(30,45,70,.13);transform:translateY(-2px);
  border-color:var(--blue)}
.card .top{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.card .tt{font-weight:700;font-size:16.5px;margin-bottom:4px}
.card .ds{font-size:13px;color:var(--fg-3);line-height:1.6}
.k{font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.04em;
  padding:1px 7px;border-radius:999px}
.k-c{background:var(--green-soft);color:var(--green);border:1px solid #bfe2cd}
.k-cpp{background:var(--violet-soft);color:var(--violet);border:1px solid #ded0f7}
.k-file{background:var(--blue-soft);color:var(--blue);border:1px solid #cfe1fb}
.k-extra{background:var(--amber-soft);color:var(--amber);border:1px solid #efd9a8}
.st{color:#e0a800;font-size:.8em;font-weight:700;vertical-align:super;cursor:help}
.card.star{background:linear-gradient(#fbfdff,#f4f9ff);border-color:#c9dcf3}

.note{margin-top:38px;border:1px solid var(--line-2);border-radius:12px;
  padding:16px 20px;background:var(--bg-soft);font-size:13.5px;color:var(--fg-2)}
.note h3{margin:0 0 8px;font-size:14px;color:var(--fg)}
.note table{border-collapse:collapse;margin-top:8px;font-size:13px}
.note td{padding:3px 14px 3px 0;vertical-align:top}
.note code{font-family:var(--mono);font-size:12.5px;background:#eef2f8;
  border:1px solid var(--line);border-radius:4px;padding:1px 5px}

footer{margin-top:44px;padding-top:18px;border-top:1px solid var(--line);
  color:var(--fg-3);font-size:12.5px}

@media (max-width:560px){
  .wrap{padding:28px 16px 56px}
  h1{font-size:23px}
  .grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>UME 项目组内部教程</h1>
  <p class="sub">回鹘蒙文编辑器（Uyghur-Mongolian Script Editor）· 面向零编程基础的成员</p>
</header>

<div class="lead">
  <p><b>怎么用这套教程</b>：从 01 开始按顺序看，每篇里的代码建议<b>亲手敲一遍</b>。</p>
  <p>带 <span class="st">*</span> 的篇目<b>与本项目施行密切相关</b>，页面底色也不同；
  带 <span class="k k-extra">Extra</span> 的是通用补充技巧，
  带 <span class="k k-file">File</span> 的是动手时立刻会用到的实用内容。</p>
</div>

<h2>正文 · 01 ~ 09</h2>
<div class="grid">
%s
</div>

<h2>Extra · File · 补充与实用</h2>
<div class="grid">
%s
</div>

<div class="note">
  <h3>关于这套教程</h3>
  <p>09 之前的篇目以 <b>C 语言</b>为主。凡是不可避免地用到 C++ 的地方，
  代码块标题栏上都会挂一个紫色的 <span class="k k-cpp">C++</span> 徽标。</p>
  <table>
    <tr><td><b>C</b></td><td>用 <code>gcc</code>（或 VS 里的 <code>.c</code> 文件）编译</td></tr>
    <tr><td><b>C++</b></td><td>用 <code>g++</code>（或 VS 里的 <code>.cpp</code> 文件）编译</td></tr>
    <tr><td><b>Extra</b></td><td>不属于某一讲，但到处会用到的通用技巧</td></tr>
    <tr><td><b>File</b></td><td>命令行、路径、编译链接、编码等动手内容</td></tr>
  </table>
  <p style="margin-top:10px">文中所有「运行结果」与实际报错，都是在真实环境里跑出来的，
  不是凭记忆写的。</p>
</div>

<footer>
  UME 项目组内部教程 · 共 15 篇 · 样式表位于
  <code>SharingGroup/tutorials/assets/</code>
</footer>

</div>
</body>
</html>
''' % ("\n".join(main_cards), "\n".join(more_cards))

    for out in ("index.html", "home.html"):
        io.open(os.path.join(REPO, out), "w", encoding="utf-8", newline="").write(html)
        print("  已生成 %s" % out)

    print("")
    print("教程目录现在的内容：")
    for f in sorted(os.listdir(TUT)):
        p = os.path.join(TUT, f)
        if os.path.isdir(p):
            print("  <目录> %s  (%d 个文件)" % (f, len(os.listdir(p))))
        else:
            print("  %7d B  %s" % (os.path.getsize(p), f))


if __name__ == "__main__":
    main()
