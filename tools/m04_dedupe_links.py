# -*- coding: utf-8 -*-
"""M04：去掉「退化」小节的重复演示，补回 E03 / M09 的链接。

背景
    上一轮把整块内容从 §1 挪到 §5 ⑥ 时，为了不重复，删掉了两张卡，
    连带把 E03 与 M09 的链接也删了。但这两处交叉引用是有价值的：
      · ⑥ 讲 arr[i] ≡ *(arr + i) —— 正是 E03《语法糖》的主题
      · ⑦ 讲「必须另传长度」—— M09 把它归成「C 数组的三大短板」

    另外，挪过来的「退化」小节自带一份 sizeof 演示（16 / 8），
    与 ⑥ 第 3 层（40 / 8）、⑦（40 → 8）重复了三次。
    这里把那份演示换成一句话，指向已有的两处。
"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\m04.html"
t = io.open(P, encoding="utf-8").read()

# ---------------------------------------------------------------- 1. 去掉重复演示
OLD = """<p>用 <code>sizeof</code> 能直接看到这件事：同一个数组，在 <code>main</code> 里量是
<b>16</b>，进了函数只剩 <b>8</b>。</p>"""

i = t.find(OLD)
if i < 0:
    print("  !! 找不到 sizeof 演示段落")
    sys.exit(1)
# 到「这就是退化留下的痕迹」那段结束
j = t.find("这就是退化留下的痕迹。</p>", i)
if j < 0:
    print("  !! 找不到痕迹段落结尾")
    sys.exit(1)
j += len("这就是退化留下的痕迹。</p>")

NEW = """<p>它的痕迹很好认：上面第 3 层那个 <code>sizeof(arr) = 40</code> 与
<code>sizeof(p) = 8</code>，就是同一块内存被两种类型看出来的差别。
下一问会更直白 —— <b>同一个 <code>sizeof(arr)</code>，在 <code>main</code> 里是 40，
一进函数就变成 8</b>。</p>"""

t = t[:i] + NEW + t[j:]
print("  已把重复的 sizeof 演示换成一句话（省 %d 字符）" % (j - i - len(NEW)))

# ---------------------------------------------------------------- 2. 补 E03 链接
E_OLD = """    <p>这解释了一个你可能早就疑惑的写法：
    <b><code>arr[i]</code> 和 <code>*(arr + i)</code> 是一回事</b>，
    方括号只是「从首地址出发加偏移、再解引用」的简写。</p>"""
E_NEW = E_OLD + """

    <p><a href="e03.html">E03 · 语法糖</a> 把这一层拆得更细：
    <code>arr[i]</code> 与 <code>arr[i][j]</code> 本质上都是「先算地址、再取值」，
    方括号只是编译器替你写好的糖。</p>"""

if 'href="e03.html"' in t:
    print("  E03 链接已在，跳过")
elif E_OLD not in t:
    print("  !! 找不到 arr[i] 那段")
else:
    t = t.replace(E_OLD, E_NEW, 1)
    print("  已补 E03 链接")

# ---------------------------------------------------------------- 3. 补 M09 链接
M_OLD = """      <p>另外，函数内部只用 <code>a[i]</code>（<code>0 &lt;= i &lt; n</code>），
      不要试图用 <code>sizeof(a)</code> 去算长度 —— 那一定是你以为的那个数。</p>"""
M_NEW = M_OLD + """
      <p>「C 数组天生缺什么」这件事，<a href="m09.html">M09 · vector 和 array</a>
      归成了三条短板（长度写死、不知道自己多长、不检查越界），可以对照着看。</p>"""

if 'href="m09.html"' in t:
    print("  M09 链接已在，跳过")
elif M_OLD not in t:
    print("  !! 找不到 ⑦ 的 tip 段")
else:
    t = t.replace(M_OLD, M_NEW, 1)
    print("  已补 M09 链接")

io.open(P, "w", encoding="utf-8", newline="").write(t)
print()
print("  最终 %d 字符" % len(t))
for f in ("e03.html", "m09.html", "f03.html"):
    print("     链到 %-9s %d 处" % (f, t.count('href="%s"' % f)))
