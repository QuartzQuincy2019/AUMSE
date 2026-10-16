# -*- coding: utf-8 -*-
"""Q07 本轮第 1~3 件事。

1. 删除第 2 节「与项目组的关系」，后面各节顺次前移（13 节 → 12 节）
       s3→s2 … s13→s12
   连带检查：正文里有没有引用「第 N 节」。实测没有，但要再确认一次。

2. 补 distanceTo 的全局写法（友元函数形式）—— 3 行说明带过
   放在第 7 节「第一层抽象：将坐标封装为 Point」里，
   紧跟在成员函数版本之后。

3. 删除小结里的「本题的数学」
   那是 <h3>本题的数学</h3> + 一个 .mnemonic 块，整块删。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\_q07_body.html"

# 友元函数形式：3 行说明
FRIEND = """
<div class="card note">
  <div class="card-t">另一种等价写法：全局（友元）函数</div>
  <p><code>distanceTo</code> 也可以不写成成员，而写成**全局函数**
  —— 若它需要访问私有成员，就在类里写一行 <code>friend</code> 声明授权。
  这样调用处变成 <code>distanceTo(a, b)</code>，而不是
  <code>a.distanceTo(b)</code>。两种都合法；差别在于前者把距离当成
  <b>两个点之间的事</b>，后者当成<b>点自己的能力</b> ——
  本题选后者，因为调用处读起来更直接。</p>
</div>
"""


def main():
    dry = "--dry" in sys.argv
    t = io.open(P, encoding="utf-8").read()

    # ---------- 1. 删第 2 节 ----------
    i2 = t.index('<h2 id="s3">')
    # s2 的起点：它前面就是 s1 的结尾
    i2s = t.index('<h2 id="s2">')
    seg = t[i2s:i2]
    t = t[:i2s] + t[i2:]
    print("  删除第 2 节「与项目组的关系」：%d 字符" % len(seg))

    # ---------- 重排编号：原 s3..s13 → s2..s12 ----------
    for old in range(3, 14):
        t = t.replace('<h2 id="s%d">' % old, '<h2 id="@%d@">' % old)
    for old in range(3, 14):
        new = old - 1
        t = t.replace('<h2 id="@%d@">' % old, '<h2 id="s%d">' % new)
        t = re.sub(r'(<h2 id="s%d"><span class="n">)\d+(</span>)' % new,
                   r'\g<1>%d\g<2>' % new, t)

    # ---------- 2. 补友元写法 ----------
    # 插在 s7（原 s8「第一层抽象」）里那张 alisa/tip 之后。
    # 找准位置：该节里「这就是 Q06 说的…」那段卡片的结尾。
    # 插在**第 7 节（第一层抽象）的末尾**，也就是下一个 <h2> 之前。
    # 第一版用「从锚点往后找两个 </div>」定位，结果插进了 Tower.h 的
    # code-wrap 中间，把代码块劈成两半（<span class="name">Tower.h…</span>
    # 后面紧跟卡片，然后才是 <pre>）。
    # 改用节边界定位 —— 稳定，且不依赖卡片内部结构。
    i7 = t.find('<h2 id="s7">')
    i8 = t.find('<h2 id="s8">')
    if i7 < 0 or i8 < 0:
        print("  !! 找不到 s7 / s8 的边界")
    else:
        t = t[:i8].rstrip() + "\n\n" + FRIEND.strip() + "\n\n" + t[i8:]
        print("  已补友元函数写法（插在第 7 节末尾）")

    # ---------- 3. 删「本题的数学」 ----------
    i = t.find("<h3>本题的数学</h3>")
    if i < 0:
        print("  「本题的数学」已不在")
    else:
        # 到下一个 <h3> 之前
        j = t.find("<h3>", i + 5)
        if j < 0:
            j = len(t)
        seg2 = t[i:j]
        t = t[:i] + t[j:]
        print("  删除「本题的数学」整块：%d 字符" % len(seg2))

    # ---------- markdown 记号自检 ----------
    # 教程页是纯 HTML，不解析 markdown —— 正文里留下 **…** 会**原样显示**。
    # 我在补友元说明时又犯了一次，所以把检查写进脚本。
    prose = re.sub(r"<pre[\\s\\S]*?</pre>", "", t)
    prose = re.sub(r"<code[\\s\\S]*?</code>", "", prose)
    n_md = prose.count("**")
    if n_md:
        print("  !! 正文里有 markdown 粗体记号 ** ：%d 处 —— 会原样显示" % n_md)

    # ---------- 自检 ----------
    hs = re.findall(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                    t, re.S)
    ids = [h[0] for h in hs]
    nos = [h[1] for h in hs]
    ok = (ids == ["s%d" % i for i in range(1, len(ids) + 1)]
          and nos == [str(i) for i in range(1, len(nos) + 1)])
    print()
    print("  小节 %d 个，id/编号连续 = %s" % (len(hs), "是 OK" if ok else "否 !!"))
    for h in hs:
        print("      %-4s %-3s %s" % (h[0], h[1], re.sub(r"<[^>]+>", "", h[2]).strip()))
    print()
    refs = re.findall(r"第\s*\d+\s*节", t)
    print("  正文里「第 N 节」引用：%s" % (refs if refs else "无"))
    print("  「本题的数学」残留：%s" % ("本题的数学" in t))
    print("  含 friend：%s" % ("friend" in t))
    print("  正文 %d 字符" % len(t))

    if not ok or not dry and False:
        return
    if not dry:
        io.open(P, "w", encoding="utf-8", newline="").write(t)
        print("  已写入")


if __name__ == "__main__":
    main()
