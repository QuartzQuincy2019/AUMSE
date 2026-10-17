# -*- coding: utf-8 -*-
"""M04：把「回扣 M03 / 退化 / 硬规矩 / 多维数组」从 §1 挪到 §5 ⑥。

用户指出
    「回扣M03」在 M04 中的位置及其不合理。学习者连指针的运算符都没完全了解。

说得对：那块内容里用了 `int *p = arr;` 和 `*p`，而 `&` 与 `*`
要到 §2、§4 才讲。放在 §1 末尾属于「先用后学」。

改法
    1. 从 §1 整块摘出（6793 字符）：
         回扣 M03 卡 / 「先把退化说清楚」/ 「指针的硬规矩」/ 「多维数组为什么省第一维」
    2. 挪到 §5 ⑥「数组的本质是什么」的末尾 —— 那里正好讲完
       「数组名 = 首元素地址」「数组名不是指针变量」「sizeof 的差别」，
       是「退化」最自然的位置；紧接着的 ⑦ 就是「为什么要多传一个长度」，
       正好接得上。
    3. 挪过去时**去掉重复内容**：
         · 「回扣 M03」这张卡不需要了 —— ⑥ 本来就在讲数组的本质
         · 「等一下：那 arr[i] 为什么还能用？」也删 ——
           ⑥ 已经用两张代码块讲透 arr[i] ≡ *(arr+i)
         · 「什么场合不退化」里的 sizeof 例子与 ⑥ 已有的 sizeof 演示重复，
           合并成一句
       保留的是 ⑥ 原本没有的：**「退化」这个词的确切含义**（英文 decay、
       三点界定），以及**多维数组能省第一维**。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\m04.html"
t = io.open(P, encoding="utf-8").read()

# ---------------- 1. 摘出 §1 里的整块 ----------------
a = t.find('<div class="card tip">\n  <div class="card-t">回扣 M03')
b = t.find('<h2 id="s2">')
if a < 0 or b < 0:
    print("  !! 找不到要摘的块")
    sys.exit(1)
block = t[a:b]
print("  摘出 %d 字符" % len(block))
t = t[:a] + t[b:]

# ---------------- 2. 只保留不重复的两部分 ----------------
# 2a. 「退化」小节（去掉开头的「上面的回扣用了…」那句 —— 回扣卡已删）
m1 = block.find('<h4>先把「退化」说清楚</h4>')
m2 = block.find('<div class="card warn">\n  <div class="card-t">所以「传数组」必须另给长度</div>')
if m1 < 0 or m2 < 0:
    print("  !! 定位失败（退化小节）")
    sys.exit(1)
DECAY_HEAD = block[m1:m2]

# 2b. 多维数组小节
m3 = block.find('<h4>附：为什么多维数组只有第一维可以省</h4>')
if m3 < 0:
    print("  !! 定位失败（多维小节）")
    sys.exit(1)
MULTI = block[m3:]

# 2c. 「传数组必须另给长度」那张卡的下半段 —— 只留与 M09 的链接，其余 ⑦ 已讲
#     这里直接不要（⑦ 专门讲「为什么要多传一个长度」）

# 调整 2a 的开头：不再引用「上面的回扣」
DECAY_HEAD = DECAY_HEAD.replace(
    "<p>上面的回扣用了「退化」这个词。它不是比喻，而是一个有确切含义的说法，\n"
    "后面还会反复碰到，所以单独讲清。</p>",
    "<p>上面第 2 层说「数组名会自动变成首元素的地址」。这件事有个正式说法，"
    "叫<b>退化</b> —— 后面到处会遇到，所以这里讲准它。</p>")

# 「什么场合不退化」里别再重复 sizeof 演示（⑥ 已演示过）
DECAY_HEAD = DECAY_HEAD.replace(
    "<p>最常见的例外是 <code>sizeof(arr)</code> —— 它量的是「整个数组」，\n"
    "  所以能得出 16。如果这里也退化了，那就只会得到 8。</p>\n"
    "  <p>反过来说，这是一个很好用的判据：<b>还能量出整个数组的大小，\n"
    "  就说明它还没退化。</b>其余绝大多数场合，数组名一出现就已经是指针了。</p>",
    "<p>就是上面第 3 层见过的 <code>sizeof(arr)</code> —— 它量的是「整个数组」，"
    "所以得到 40（10 个 int）。如果这里也退化了，那就只会得到 8。</p>\n"
    "  <p>反过来说，这是一个很好用的判据：<b>还能量出整个数组的大小，"
    "就说明它还没退化。</b>其余绝大多数场合，数组名一出现就已经是指针了。</p>")

# 多维小节里那句「和这一节的回扣连起来看」改成自洽的说法
MULTI = MULTI.replace(
    "<div class=\"card-t\">和这一节的回扣连起来看</div>\n"
    "  <p>回扣说的是「<code>arr</code> 的类型是 <code>int[4]</code> 而不是 <code>int</code>」；\n"
    "  这里说的是「<code>a</code> 的类型是 <code>int[2][3]</code>，\n"
    "  它的一层元素是 <code>int[3]</code>」。</p>",
    "<div class=\"card-t\">和「退化」连起来看</div>\n"
    "  <p>多维数组的类型里，每一维的大小都写着；而只要缺一维，"
    "编译器就没法算「下一行在哪」。</p>")

# ---------------- 3. 插到 ⑥ 的末尾 ----------------
# ⑥ 以 .qa 结束；⑦ 的标题是 s5g。定位 ⑦ 标题前的 </div>\n</div>
anchor = t.find('<h3 id="s5g">')
if anchor < 0:
    print("  !! 找不到 ⑦")
    sys.exit(1)
seg = t[:anchor]
# 往回找 ⑥ 的收尾：最后一个 </div>\n</div>\n\n 之前是 ⑥ 的 a 块结束
tail = seg.rstrip()
# ⑥ 结束形如 ...</p>\n    </div>\n  </div>\n\n
# ⑥ 的收尾是：  ...</p>
#                   </div>     ← card warn
#                 </div>       ← .a
#               </div>         ← .qa
# 要插在 .a 的收尾之前。
SUF = "  </div>" + chr(10) + "</div>"
if not tail.endswith(SUF):
    print("  !! ⑥ 的收尾形状不符：%r" % tail[-60:])
    sys.exit(1)
insert_at = len(tail) - len(SUF)
INS = DECAY_HEAD.rstrip() + "\n\n" + MULTI.rstrip() + "\n\n"
t = t[:insert_at] + INS + t[insert_at:]

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  已挪到 §5 ⑥ 末尾，%d 字符" % len(t))

# ---------------- 4. 自检 ----------------
print()
i1 = t.find('<h2 id="s1">')
i2 = t.find('<h2 id="s2">')
s1 = t[i1:i2]
print("  §1 里还剩：退化=%d 回扣=%d 多维=%d 硬规矩=%d"
      % (s1.count("退化"), s1.count("回扣"), s1.count("多维"),
         s1.count("硬规矩")))
i6 = t.find('<h3 id="s5f">')
i7 = t.find('<h3 id="s5g">')
s6 = t[i6:i7]
print("  ⑥ 里：退化=%d 多维=%d decay=%d"
      % (s6.count("退化"), s6.count("多维"), s6.count("decay")))
print()
print("  §1 结尾 5 行：")
for l in s1.strip().split("\n")[-5:]:
    print("      " + l[:90])
