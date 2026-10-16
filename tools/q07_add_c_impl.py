# -*- coding: utf-8 -*-
"""Q07 第 2 步：补 C 实现、补「与项目组的关系」、补 C/C++ 对照，并重排编号。

新增三节
    在 s1（数学模型）之后插入：
        · 与项目组的关系  —— 用户指出这份作业是 10 月 12 日的，
          所以本篇是精准贴合项目组进度的教程
    在 s3（直接实现）之后插入：
        · C 语言的实现 —— 同一个算法的 C 写法
        · C 与 C++ 的对照 —— 强调：同样的工作，C++ 更易懂、更简单

重排
    原 s2..s10 依次后移，最终 13 节：
        1  数学模型
        2  与项目组的关系          ← 新
        3  数据类型的选择          （原 s2）
        4  直接实现（C++）         （原 s3）
        5  C 语言的实现            ← 新
        6  C 与 C++ 的对照         ← 新
        7  需求变更的影响范围       （原 s4）
        8  第一层抽象              （原 s5）
        9  第二层抽象              （原 s6）
        10 数据与逻辑分离          （原 s7）
        11 提高可扩展性的原则       （原 s8）
        12 两种实现的对照          （原 s9）
        13 小结                   （原 s10）
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\_q07_body.html"

# ----------------------------------------------------------------------
# 新节 1：与项目组的关系（插在 s1 之后）
# ----------------------------------------------------------------------
NEW_A = """
<h2 id="s2"><span class="n">2</span>与项目组的关系</h2>

<p>这道题不是随手找来的练习 —— 它是<b>本项目组 10 月 12 日布置的第 4 次作业</b>。</p>

<div class="card key">
  <div class="card-t">为什么把它写进教程</div>
  <p>这道题在课程里只是一次普通的作业，但它的形态和真实工程问题很接近：
  <b>题目给一组数据（塔心、半径、高度），要求写一个查询</b>。</p>
  <p>而 UME 项目里到处是同一形态的东西 ——
  字形表、码位映射、推进量表，都是「<b>一份数据 + 一组查询</b>」。
  所以这一篇的落点不在解出这道题，而在
  <b>用这道题练「数据与逻辑怎么分」</b>。</p>
</div>

<p>它同时是一道<b>很好的反面教材</b>：题面给的都是具体数字
（<code>±2</code>、<code>1</code>、<code>10</code>），
非常容易顺手写死。而项目里最怕的正是这个 ——
字体换了版本、码位范围变了、行高算法调整了，
如果当初写死了数字，改动就会散落到各处。</p>
"""

# ----------------------------------------------------------------------
# 新节 2 / 3：C 实现 + C/C++ 对照（插在「直接实现」之后）
# ----------------------------------------------------------------------
NEW_B = """
<h2 id="s5"><span class="n">5</span>C 语言的实现</h2>

<p>同一道题，用 <b>C</b> 写出来是这样的。注意它的组织方式：
<b>用 <code>struct</code> 放数据，用普通函数做操作</b>，
数据和行为是分开的两样东西。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">homework.c —— C 的写法</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;math.h&gt;</span>

<span class="hl-c">/* 一个点：x 和 y 总是一起出现 */</span>
<span class="hl-k">typedef struct</span> {
    <span class="hl-k">double</span> x;
    <span class="hl-k">double</span> y;
} Point;

<span class="hl-c">/* 一个塔 */</span>
<span class="hl-k">typedef struct</span> {
    Point  center;
    <span class="hl-k">double</span> radius;
    <span class="hl-k">double</span> height;
} Tower;

<span class="hl-c">/* 距离 —— 只能写成自由函数，第一个参数得自己传 */</span>
<span class="hl-k">double</span> <span class="hl-f">distanceTo</span>(<span class="hl-k">const</span> Point *a, <span class="hl-k">const</span> Point *b)
{
    <span class="hl-k">double</span> dx = a-&gt;x - b-&gt;x;
    <span class="hl-k">double</span> dy = a-&gt;y - b-&gt;y;
    <span class="hl-k">return</span> <span class="hl-f">sqrt</span>(dx * dx + dy * dy);
}

<span class="hl-c">/* 这个点在不在塔顶范围内 */</span>
<span class="hl-k">int</span> <span class="hl-f">towerCovers</span>(<span class="hl-k">const</span> Tower *t, <span class="hl-k">const</span> Point *p)
{
    <span class="hl-k">return</span> <span class="hl-f">distanceTo</span>(&amp;t-&gt;center, p) &lt;= t-&gt;radius;
}

<span class="hl-c">/* 查询：遍历数组 */</span>
<span class="hl-k">double</span> <span class="hl-f">heightAt</span>(<span class="hl-k">const</span> Tower *towers, <span class="hl-k">int</span> n,
                <span class="hl-k">const</span> Point *p)
{
    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; n; i++) {
        <span class="hl-k">if</span> (<span class="hl-f">towerCovers</span>(&amp;towers[i], p))
            <span class="hl-k">return</span> towers[i].height;
    }
    <span class="hl-k">return</span> <span class="hl-n">0.0</span>;
}

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>)
{
    <span class="hl-c">/* 题面数据 */</span>
    Tower towers[<span class="hl-n">4</span>] = {
        { { <span class="hl-n">2.0</span>,  <span class="hl-n">2.0</span>}, <span class="hl-n">1.0</span>, <span class="hl-n">10.0</span> },
        { {-<span class="hl-n">2.0</span>,  <span class="hl-n">2.0</span>}, <span class="hl-n">1.0</span>, <span class="hl-n">10.0</span> },
        { {-<span class="hl-n">2.0</span>, -<span class="hl-n">2.0</span>}, <span class="hl-n">1.0</span>, <span class="hl-n">10.0</span> },
        { { <span class="hl-n">2.0</span>, -<span class="hl-n">2.0</span>}, <span class="hl-n">1.0</span>, <span class="hl-n">10.0</span> },
    };
    Point p;

    <span class="hl-f">scanf</span>(<span class="hl-s">"%lf %lf"</span>, &amp;p.x, &amp;p.y);
    <span class="hl-f">printf</span>(<span class="hl-s">"%.2f\n"</span>, <span class="hl-f">heightAt</span>(towers, <span class="hl-n">4</span>, &amp;p));
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行</div><pre>输入： 2 3
输出： 10.00

输入： 0 0
输出： 0.00</pre></div>

<p>这段 C 代码<b>并不差</b>，它已经做到了数据与逻辑分离：
<code>heightAt</code> 里同样没有题面数字。问题出在<b>表达方式</b>上。</p>

<h2 id="s6"><span class="n">6</span>C 与 C++ 的对照</h2>

<p>把两次「算距离」并排看 —— 它们做的是<b>同一件事</b>：</p>

<div class="two">
  <div class="side">
    <div class="hd bad">C</div>
<pre>/* 距离要单独写一个函数，
   「谁到谁」得靠两个参数传进去 */
double distanceTo(const Point *a,
                  const Point *b)
{
    double dx = a-&gt;x - b-&gt;x;
    double dy = a-&gt;y - b-&gt;y;
    return sqrt(dx*dx + dy*dy);
}

/* 调用处 */
distanceTo(&amp;t-&gt;center, p) &lt;= t-&gt;radius</pre>
  </div>
  <div class="side">
    <div class="hd good">C++</div>
<pre>// 距离是这个类型自己的行为
struct Point {
    double x = 0.0, y = 0.0;

    double distanceTo(const Point&amp; other) const {
        double dx = x - other.x;
        double dy = y - other.y;
        return std::sqrt(dx*dx + dy*dy);
    }
};

// 调用处
p.distanceTo(center) &lt;= radius</pre>
  </div>
</div>

<div class="card key">
  <div class="card-t">结论：同样的工作，C++ 的代码更易懂、更简单</div>
  <p>这一点不是风格偏好，<b>是可以在代码上指出来的</b>：</p>
  <table>
  <thead><tr><th style="width:26%">看什么</th><th style="width:34%">C</th>
  <th>C++</th></tr></thead>
  <tbody>
  <tr><td>调用处读起来像什么</td>
      <td class="c"><code>distanceTo(&amp;a, &amp;b)</code><br>
      ——「算 a 和 b 的距离」，主客体不明</td>
      <td class="c"><code>a.distanceTo(b)</code><br>
      ——「a 到 b 的距离」，<b>就是一句人话</b></td></tr>
  <tr><td>要传几个参数</td>
      <td class="c">2 个指针，还得记顺序</td>
      <td class="c"><b>1 个</b>，主语写在点号前面</td></tr>
  <tr><td>公式写在哪</td>
      <td class="c">散在各处的自由函数里</td>
      <td class="c">贴在类型上，<b>一看就知道去哪找</b></td></tr>
  <tr><td>符号 Noise</td>
      <td class="c">满屏 <code>*</code>、<code>&amp;</code>、<code>-&gt;</code></td>
      <td class="c">用引用 <code>&amp;</code>，<code>.</code> 点点到底</td></tr>
  <tr><td>以后要加三维</td>
      <td class="c">所有函数的参数表都要改</td>
      <td class="c">只改 <code>Point</code> 里那几行</td></tr>
  <tr><td>传参数会不会误改</td>
      <td class="c">指针可能被改成 <code>NULL</code>，
      也可能改了指向的内容</td>
      <td class="c"><code>const Point&amp;</code> 一句话锁死，
      <b>不可能为空、不可能改</b></td></tr>
  </tbody>
  </table>
</div>

<p>用一句更具体的话说清楚这个差别：</p>

<div class="mnemonic">
  C 的写法是「<b>有个函数，你拿两个点去调它</b>」；<br>
  C++ 的写法是「<b>这个点知道怎么算到另一个点的距离</b>」。
</div>

<p>第二种说法更接近我们思考这件事的方式 ——
所以它读起来更简单，也更容易记住。
下面几节讲的「把坐标封装成类型」，做的正是这个转换。</p>

<div class="card note">
  <div class="card-t">为什么后面的示例都用 C++</div>
  <p>原因有两层：</p>
  <ul>
    <li><b>表达力更强</b> —— 数据和行为可以放在一起，
    也就是上面这张表说的那些</li>
    <li><b>项目用的是 C++ 和 Qt</b> —— UME 的排版核心基于 Qt，
    所以教程从 Q01 起就转到了 C++</li>
  </ul>
  <p>但要说明一点：<b>C 的那一版在工程上并没有错。</b>
  它同样做到了数据与逻辑分离。这一节比较的是<b>哪种写法更好读</b>，
  不是「C 不能用」。</p>
</div>
"""


def main():
    dry = "--dry" in sys.argv
    t = io.open(P, encoding="utf-8").read()

    # ---------- 先把原 s2..s10 的 id 与编号后移 ----------
    # 目标：原 s2→s3, s3→s4, s4→s7, s5→s8, s6→s9, s7→s10, s8→s11,
    #        s9→s12, s10→s13
    # 为了不互相踩，先整体改成占位 id，再统一落位。
    MOVE = {  # 原 id → 新号
        "s2": 3, "s3": 4, "s4": 7, "s5": 8, "s6": 9,
        "s7": 10, "s8": 11, "s9": 12, "s10": 13,
    }
    # 1) 先把 h2 与所有 #sN 引用换成 @sN@ 占位
    for old in sorted(MOVE, key=lambda x: -int(x[1:])):
        t = t.replace('<h2 id="%s">' % old, '<h2 id="@%s@">' % old)
    # 2) 落位
    for old, newno in MOVE.items():
        t = t.replace('<h2 id="@%s@">' % old, '<h2 id="s%d">' % newno)
        t = re.sub(r'(<h2 id="s%d"><span class="n">)\d+(</span>)' % newno,
                   r'\g<1>%d\g<2>' % newno, t)

    # ---------- 插入新节 ----------
    # 新 s2（与项目组的关系）：插在 s1 之后、s3 之前
    i3 = t.index('<h2 id="s3">')
    t = t[:i3] + NEW_A.strip() + "\n\n" + t[i3:]

    # 新 s5 / s6：插在 s4 之后、s7 之前
    i7 = t.index('<h2 id="s7">')
    t = t[:i7] + NEW_B.strip() + "\n\n" + t[i7:]

    # ---------- 自检 ----------
    hs = re.findall(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                    t, re.S)
    ids = [h[0] for h in hs]
    nos = [h[1] for h in hs]
    ok = (ids == ["s%d" % i for i in range(1, len(ids) + 1)]
          and nos == [str(i) for i in range(1, len(nos) + 1)])
    print("  小节 %d 个，id/编号连续 = %s" % (len(hs), "是 OK" if ok else "否 !!"))
    for h in hs:
        print("      %-4s %-3s %s" % (h[0], h[1], re.sub(r"<[^>]+>", "", h[2]).strip()))
    print()
    print("  key-h 残留 %d 处（应为 0）；★ 残留 %d 个（应为 0）"
          % (t.count("key-h"), t.count("★")))
    print("  正文 %d 字符" % len(t))

    if not ok:
        print("  !! 编号不连续，未写入")
        return
    if not dry:
        io.open(P, "w", encoding="utf-8", newline="").write(t)
        print("  已写入")


if __name__ == "__main__":
    main()
