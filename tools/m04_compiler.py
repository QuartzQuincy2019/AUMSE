# -*- coding: utf-8 -*-
"""M04：解释「编译器」是什么，并链到 F03。

用户指出
    「编译器会自动把它换成一个『指向第一个元素的指针』」—— 什么是编译器？
    给出 F03 的链接。

做法
    在「先把退化说清楚」的「一句话」卡之后，插一张 .card note：
      · 一句话说明编译器是干什么的（gcc / g++ / cl.exe 都是它）
      · 为什么本篇非要提它：类型大小、地址怎么走、「退化」都是它执行的规则
      · 链到 F03《编译与链接、头文件与库》—— 那篇第 3 节就叫「编译：各自翻译」
    并注明本篇只用到其中一件事，避免把读者推得太远。
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\m04.html"
t = io.open(P, encoding="utf-8").read()

NOTE = """
<div class="card note">
  <div class="card-t">先岔一句：编译器是什么</div>
  <p>上面反复说「编译器」。它就是<b>把你写的源代码翻译成机器能执行的程序的那个工具</b>
  —— <code>gcc</code>、<code>g++</code>、<code>cl.exe</code> 都是它。</p>
  <p>为什么这里要提它：<b>「类型占多大」「地址怎么走」「数组名要不要退化」，
  这些决定全是编译器做的</b>，不是运行时的事。你在编辑器里写下的
  <code>int arr[4]</code>，它得先算出「这占 16 字节、下一格在 4 字节后」，
  才能把后面每一句翻译成正确的指令。</p>
  <p>它具体做了哪几步、报错分别出在哪一步 ——
  <a href="f03.html">F03 · 编译与链接、头文件与库</a> 讲得最清楚
  （第 3 节就叫「编译：各自翻译」）。本篇只用到其中一件事：
  <b>编译器会按类型规则改写你的表达式</b>。</p>
</div>

"""

ANCHOR = """  <p>这个过程就叫<b>退化</b>（英文 decay）。从类型上看，是
  <code>int[4]</code> 变成了 <code>int*</code>。</p>
</div>
"""

if "先岔一句：编译器是什么" in t:
    print("  M04 已有该说明，跳过")
elif ANCHOR not in t:
    print("  !! 锚点未匹配")
    sys.exit(1)
else:
    t = t.replace(ANCHOR, ANCHOR + NOTE, 1)
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  M04 已插入「编译器是什么」，%d 字符" % len(t))

print()
print("  f03.html 链接数: %d" % t.count('href="f03.html"'))
print("  「编译器」出现: %d 次" % t.count("编译器"))
