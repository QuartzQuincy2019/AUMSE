# -*- coding: utf-8 -*-
"""M08 / M09 的「下一讲预告」按实际情况改写。

用户要求
    · M08 的「下一讲预告」不符合实际项目，作出更改
    · M09 的「下一讲预告」不符合实际项目，应该指明「移步 Q 系列第 1 篇」，
      并强调「建议学习 C++ 的输入和输出流之后进行」

原来的问题
    M08：
        「下一讲先讲一个纯编程技巧：递归（函数自己调用自己）。
          然后进入几篇与项目直接相关的实用文档：命令行、文件路径、
          编译链接，以及 Unicode 与编码……」
      —— 三处不对：
        ① M08 的下一讲是 **M09《vector 和 array》**，不是「递归」
           （递归在 E01，是补充练习，不在 M 主线后面）
        ② 「命令行 / 文件路径 / 编译链接」是 F01-F03，也不在 M08 之后
        ③ 整段像是在描述一份旧目录

    M09：
        「接下来是 09-F04《Unicode 和编码》」
      —— 「09-F04」是个**早就废弃的旧编号**（现在 Unicode 那篇是 T02），
         而且 M 系列到此结束，下一步应该是 Q 系列，不是回跳到别的 M 编号。

改法
    M08 → 下一讲写实：M09《vector 和 array》，
          并把「为什么 char 装不下蒙文」指向 T02（那篇确实有完整答案）
    M09 → M 系列收尾，移步 Q 系列第 1 篇 Q01《std 与命名空间初步》，
          并明确建议先学 C++ 的输入输出流（cin / cout / endl）再开始 ——
          Q01 全篇用 std::cout 举例（22 处），不再讲 printf
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# ---------------------------------------------------------------- M08
M08_OLD = """<div class="card note">
  <div class="card-t">下一讲预告</div>
  <p>这一讲处理的是「一串英文字符」。但我们的项目要处理
  <b>回鹘蒙文</b> —— 那可不是 1 个字节能装下的。</p>
  <p>下一讲先讲一个纯编程技巧：<b>递归</b>（函数自己调用自己）。
  然后进入几篇与项目直接相关的实用文档：命令行、文件路径、
  编译链接，以及 <b>Unicode 与编码</b> ——
  那一篇会解释为什么 <code>char</code> 处理不了蒙文，
  以及为什么 QPainter 里到处都是 <code>QString</code> 而不是 <code>char*</code>。</p>
</div>"""

M08_NEW = """<div class="card note">
  <div class="card-t">下一讲预告</div>
  <p>这一讲处理的是「一串英文字符」。但我们的项目要处理
  <b>回鹘蒙文</b> —— 那可不是 1 个字节能装下的。</p>
  <p>下一讲是 <b>M09《vector 和 array》</b>，把「数组」这条线收尾：
  这一讲开头那几条 C 数组的短板（长度写死、不知道自己多长、
  不检查越界），标准库的 <code>vector</code> / <code>array</code> 是怎么补上的，
  以及给函数传数组参数时该怎么写。</p>
  <p>「蒙文为什么装不进 <code>char</code>」这个问题，会在
  <a href="t02.html">T02《Unicode 和编码》</a> 里正面回答 ——
  一个字符为什么要占多个字节，以及 Qt 里为什么到处都是
  <code>QString</code> 而不是 <code>char*</code>。</p>
</div>"""

# ---------------------------------------------------------------- M09
M09_OLD = """<div class="card note">
  <div class="card-t">最后一篇</div>
  <p>接下来是 <b>09-F04《Unicode 和编码》</b> ——
  这一篇直接关系到本项目的核心。</p>
  <p>它会回答：为什么 <code>char</code> 装不下蒙文？
  为什么同一个字符在不同编码下字节数不一样？
  为什么编辑器里读文件时要指定编码？</p>
</div>"""

M09_NEW = """<div class="card note">
  <div class="card-t">M 系列到此结束 · 下一步</div>
  <p>接下来请<b>移步 Q 系列第 1 篇</b> ——
  <a href="q01.html">Q01《std 与命名空间初步》</a>。
  从那里开始正式进入 C++：<code>std</code> 是什么、
  <code>std::</code> 该怎么读、<code>using</code> 该不该用。</p>
  <p><b>建议在学完 C++ 的输入和输出流之后再进行</b>
  （也就是 <code>cin</code> / <code>cout</code> / <code>endl</code> 这一套，
  以及 <code>#include &lt;iostream&gt;</code>）。Q01 全篇用
  <code>std::cout</code> 举例，不再像 M 系列那样用 <code>printf</code> 讲输出 ——
  不熟这套写法的话，例子会看不懂。</p>
</div>"""

for fn, old, new in (("m08.html", M08_OLD, M08_NEW), ("m09.html", M09_OLD, M09_NEW)):
    p = T + "\\" + fn
    t = io.open(p, encoding="utf-8").read()
    if old not in t:
        print("  !! %s 锚点未匹配" % fn)
        continue
    t = t.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("  %-10s 已改写（%d 字符）" % (fn, len(t)))

# ---------------------------------------------------------------- 自检
print()
for fn, must in (("m08.html", ["M09", "t02.html"]),
                 ("m09.html", ["Q 系列第 1 篇", "q01.html", "输入和输出流"])):
    t = io.open(T + "\\" + fn, encoding="utf-8").read()
    miss = [m for m in must if m not in t]
    print("  %-10s 关键内容: %s" % (fn, "齐" if not miss else "缺 " + " ".join(miss)))
    for bad in ("09-F04", "递归"):
        if bad in t and fn == "m09.html":
            print("        !! 仍有旧内容 %s" % bad)
