# -*- coding: utf-8 -*-
"""F03 收尾：恢复被误删的 footer（更新内容），并加一条
   「命令行 gcc ↔ VS 2026」的对应说明，让第 1~4 节的模型接到第 8 节。"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F03_编译与链接、头文件与库.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)

# ---------- 1) 补 footer ----------
FOOTER = '''<footer>
UME 项目组内部教程 · 08-F03（File）《编译与链接、头文件与库》<br>
第 1~4 节的报错信息使用 gcc 13.1.0 实际编译产生；
第 7~10 节的静态库流程、产物路径、<code>LNK2005</code> /
<code>LNK1104</code> / <code>LNK2019</code> / <code>C1083</code>
与编码报错，均在 <b>Visual Studio Community 2026</b>（18.10.3 ·
MSVC 14.51.36231 · MSBuild v145）实际生成核对。
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>

'''
if '<footer' not in t:
    i = t.index('</main>')
    t = t[:i] + FOOTER + t[i:]
    print("已补回 footer")

# ---------- 2) 在第 1 节末尾加「命令行 ↔ VS」对照 ----------
ANCHOR = '''<p>平时一句 <code>gcc main.c -o main.exe</code> 就把三步都做完了。
但<b>报错发生在哪一步，含义完全不同</b> —— 这就是本篇的核心。</p>'''

BRIDGE = ANCHOR + '''

<div class="card tip">
  <div class="card-t">本节用 gcc 讲原理，第 8 节用 Visual Studio 实操</div>
  <p>原理是<b>通用的</b>，不分编译器。为了讲得干净，前面几节用
  <code>gcc</code> 这一行命令把三步「摊开」给你看。</p>
  <p>但<b>实际动手请用 Visual Studio 2026</b> ——
  第 8 节会一步步做一遍。两者的对应关系是：</p>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:22%">阶段</th><th style="width:30%">命令行（gcc）</th>
    <th>Visual Studio 2026</th></tr></thead>
  <tbody>
  <tr><td><b>预处理 + 编译</b></td>
      <td class="c">gcc -c main.c -o main.obj</td>
      <td>点「生成」时自动做，不用手敲</td></tr>
  <tr><td><b>链接</b></td>
      <td class="c">gcc main.obj helpers.obj -o app.exe</td>
      <td><b>右键项目 → 生成</b>，链接器由 MSBuild 调起</td></tr>
  <tr><td><b>指定头文件目录</b></td>
      <td class="c">-I 目录</td>
      <td>C/C++ → 常规 → <b>附加包含目录</b></td></tr>
  <tr><td><b>指定库</b></td>
      <td class="c">-L 目录 -l 名字</td>
      <td>链接器 → 输入 → <b>附加依赖项</b><br>链接器 → 常规 → <b>附加库目录</b></td></tr>
  <tr><td><b>看报错</b></td>
      <td>打印在窗口里</td>
      <td><b>输出</b>窗口 + <b>错误列表</b>窗口</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>学会看「哪一步出错」比记住命令更重要</b> ——
  这一点两种方式完全一样。</p>
</div>'''

if ANCHOR in t and '第 8 节用 Visual Studio 实操' not in t:
    t = t.replace(ANCHOR, BRIDGE, 1)
    print("已加「命令行 ↔ VS」对照卡")

# ---------- 3) 引导语里补一句 ----------
if '本文里所有报错信息都是真实编译出来的（gcc 13.1.0）。' in t:
    t = t.replace(
        '本文里所有报错信息都是真实编译出来的（gcc 13.1.0）。',
        '第 1~6 节用 gcc 讲清原理，第 7 节起改用 '
        '<b>Visual Studio 2026</b> 实操（含一份完整的静态库教程）；'
        '文中的报错、产物路径与命令输出，都是实际跑出来的。', 1)
    print("已更新引导语")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("")
print("F03：%d → %d 字符" % (orig, len(t)))
print("含 footer: %s" % ('<footer' in t))
print("footer 在 </main> 之前: %s" % (t.index('<footer') < t.index('</main>')))
