# -*- coding: utf-8 -*-
"""把 06《类、结构体》改写为 C 风格；不可避免的 C++ 部分加显眼标识。

C 部分（改写成 printf / char[] / struct）：
  · 结构体数组
  · 构造函数与析构函数（→ 用 C 的初始化函数 + 显式清理）
  · 常见错误里的 . 与 -> 对比、构造函数那两处
C++ 部分（加 C++ 徽标 + 说明框）：
  · 成员函数
  · class + private / public
  · 故意写错：从外面改私有成员
  · 验证默认权限不同
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
PATH = os.path.join(ROOT, "_ds_06_类、结构体.html")

BADGE_CSS = """
/* ===== C++ 内容标识：09 之前尽量用 C，不得已用 C++ 时必须显眼 ===== */
.cpp-badge{
  display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;
  font-family:var(--mono);font-size:10.5px;font-weight:700;letter-spacing:.04em;
  background:#7c3aed;color:#fff;vertical-align:1px;
}
.cpp-note{
  border:1px solid #ded0f7;border-left:4px solid #7c3aed;background:var(--violet-soft);
  border-radius:0 9px 9px 0;padding:11px 16px;margin:14px 0;font-size:14px;
}
.cpp-note b{color:#7c3aed}
.cpp-note .t2{font-weight:700;color:#7c3aed;margin-bottom:4px}
.cpp-note p:last-child{margin-bottom:0}
"""

with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()

orig = len(t)
done = []

if "cpp-badge" not in t:
    t = t.replace("</head>", "<style>" + BADGE_CSS + "</style>\n</head>", 1)
    done.append("注入 C++ 徽标样式")


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        print("  !! %s：命中 %d 次" % (label, n))
        return False
    t = t.replace(old, new, 1)
    done.append(label)
    return True


# ---------- 1. 结构体数组：改成 C ----------
sub(
    r'''<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">struct</span> Player {
    string name;         <span class="hl-c">/* C++ 的 string 比 char[] 好用得多 */</span>
    <span class="hl-k">int</span> hp;
    <span class="hl-k">int</span> mp;
};

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    Player team[<span class="hl-n">3</span>];        <span class="hl-c">/* 一个数组，装 3 个玩家 */</span>

    team[<span class="hl-n">0</span>].name = <span class="hl-s">"Archer"</span>;  team[<span class="hl-n">0</span>].hp = <span class="hl-n">100</span>;  team[<span class="hl-n">0</span>].mp = <span class="hl-n">30</span>;
    team[<span class="hl-n">1</span>].name = <span class="hl-s">"Mage"</span>;    team[<span class="hl-n">1</span>].hp = <span class="hl-n">80</span>;   team[<span class="hl-n">1</span>].mp = <span class="hl-n">120</span>;
    team[<span class="hl-n">2</span>].name = <span class="hl-s">"Knight"</span>;  team[<span class="hl-n">2</span>].hp = <span class="hl-n">150</span>;  team[<span class="hl-n">2</span>].mp = <span class="hl-n">10</span>;

    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; <span class="hl-n">3</span>; i++) {
        <span class="hl-f">cout</span> &lt;&lt; team[i].name &lt;&lt; <span class="hl-s">" hp="</span> &lt;&lt; team[i].hp
             &lt;&lt; <span class="hl-s">" mp="</span> &lt;&lt; team[i].mp &lt;&lt; <span class="hl-f">endl</span>;
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''',
    r'''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>

<span class="hl-k">struct</span> Player {
    <span class="hl-k">char</span> name[<span class="hl-n">20</span>];       <span class="hl-c">/* C 里用字符数组存名字，第八讲细讲 */</span>
    <span class="hl-k">int</span>  hp;
    <span class="hl-k">int</span>  mp;
};

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-k">struct</span> Player team[<span class="hl-n">3</span>];   <span class="hl-c">/* 一个数组，装 3 个玩家 */</span>

    <span class="hl-f">strcpy</span>(team[<span class="hl-n">0</span>].name, <span class="hl-s">"Archer"</span>);  team[<span class="hl-n">0</span>].hp = <span class="hl-n">100</span>;  team[<span class="hl-n">0</span>].mp = <span class="hl-n">30</span>;
    <span class="hl-f">strcpy</span>(team[<span class="hl-n">1</span>].name, <span class="hl-s">"Mage"</span>);    team[<span class="hl-n">1</span>].hp = <span class="hl-n">80</span>;   team[<span class="hl-n">1</span>].mp = <span class="hl-n">120</span>;
    <span class="hl-f">strcpy</span>(team[<span class="hl-n">2</span>].name, <span class="hl-s">"Knight"</span>);  team[<span class="hl-n">2</span>].hp = <span class="hl-n">150</span>;  team[<span class="hl-n">2</span>].mp = <span class="hl-n">10</span>;

    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; <span class="hl-n">3</span>; i++) {
        <span class="hl-f">printf</span>(<span class="hl-s">"%s hp=%d mp=%d\n"</span>,
               team[i].name, team[i].hp, team[i].mp);
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''',
    "结构体数组 → C")

# ---------- 2. 成员函数：加 C++ 徽标，并在前面插说明 ----------
sub('<span class="name">成员函数</span>',
    '<span class="name">成员函数</span><span class="cpp-badge">C++</span>',
    "成员函数 → C++ 徽标")

sub('''<h2 id="s4"><span class="n">4</span>给 struct 加上函数</h2>

<p>数据打包好了，但「挨打」「加血」这些操作还散在外面。
如果能把它们<b>也放进结构体里</b>，用起来就顺多了 —— 这是 C++ 的加强。</p>''',
    '''<h2 id="s4"><span class="n">4</span>给 struct 加上函数</h2>

<div class="cpp-note">
  <div class="t2">本节开始出现 C++ —— 已用紫色「C++」徽标标出</div>
  <p>本文档其余部分是 <b>C</b>。但「把函数放进结构体里」这件事
  <b>C 语言做不到</b>，它是 C++ 的特性，所以接下来几段代码是 C++。</p>
  <p>看到<b>紫色 C++ 徽标</b>就说明：这段代码需要 <code>g++</code>
  而不是 <code>gcc</code> 来编译。</p>
</div>

<p>数据打包好了，但「挨打」「加血」这些操作还散在外面。
如果能把它们<b>也放进结构体里</b>，用起来就顺多了 —— 这是 C++ 的加强。</p>''',
    "第 4 节插入 C++ 说明框")

# ---------- 3. class + private：加徽标 ----------
sub('<span class="name">class + private / public</span>',
    '<span class="name">class + private / public</span><span class="cpp-badge">C++</span>',
    "class+private → C++ 徽标")
sub('<span class="name">危险：外面为所欲为</span>',
    '<span class="name">危险：外面为所欲为</span>',
    "占位")
sub('<span class="name">故意写错：从外面改私有成员</span>',
    '<span class="name">故意写错：从外面改私有成员</span><span class="cpp-badge">C++</span>',
    "私有访问报错 → C++ 徽标")
sub('<span class="name">验证默认权限不同</span>',
    '<span class="name">验证默认权限不同</span><span class="cpp-badge">C++</span>',
    "默认权限 → C++ 徽标")

# ---------- 4. 构造函数与析构函数：改成 C ----------
sub(
    r'''<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">class</span> Player {
<span class="hl-k">private</span>:
    string name;
    <span class="hl-k">int</span> hp;
<span class="hl-k">public</span>:
    <span class="hl-c">/* 构造函数：名字同 类名，无返回值 */</span>
    Player(string n, <span class="hl-k">int</span> h) {
        name = n;
        hp = h;
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"[构造] "</span> &lt;&lt; name &lt;&lt; <span class="hl-s">" 诞生"</span> &lt;&lt; <span class="hl-f">endl</span>;
    }

    <span class="hl-c">/* 析构函数：名字是 ~类名，无参数无返回值 */</span>
    ~<span class="hl-f">Player</span>() {
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"[析构] "</span> &lt;&lt; name &lt;&lt; <span class="hl-s">" 退场"</span> &lt;&lt; <span class="hl-f">endl</span>;
    }

    <span class="hl-k">void</span> <span class="hl-f">show</span>() { <span class="hl-f">cout</span> &lt;&lt; name &lt;&lt; <span class="hl-s">" HP "</span> &lt;&lt; hp &lt;&lt; <span class="hl-f">endl</span>; }
};''',
    r'''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>

<span class="hl-k">struct</span> Player {
    <span class="hl-k">char</span> name[<span class="hl-n">20</span>];
    <span class="hl-k">int</span>  hp;
};

<span class="hl-c">/* C 里没有构造函数，用「初始化函数」代替 —— 约定：名字叫 xxx_init */</span>
<span class="hl-k">void</span> <span class="hl-f">player_init</span>(<span class="hl-k">struct</span> Player *p, <span class="hl-k">const</span> <span class="hl-k">char</span> *n, <span class="hl-k">int</span> h) {
    <span class="hl-f">strcpy</span>(p-&gt;name, n);
    p-&gt;hp = h;
    <span class="hl-f">printf</span>(<span class="hl-s">"[构造] %s 诞生\n"</span>, p-&gt;name);
}

<span class="hl-c">/* 需要收尾时，同样自己写一个函数显式调用 */</span>
<span class="hl-k">void</span> <span class="hl-f">player_destroy</span>(<span class="hl-k">struct</span> Player *p) {
    <span class="hl-f">printf</span>(<span class="hl-s">"[析构] %s 退场\n"</span>, p-&gt;name);
}

<span class="hl-k">void</span> <span class="hl-f">player_show</span>(<span class="hl-k">struct</span> Player *p) {
    <span class="hl-f">printf</span>(<span class="hl-s">"%s HP %d\n"</span>, p-&gt;name, p-&gt;hp);
}''',
    "构造函数与析构函数 → C 的 init/destroy")

# 把该段后面调用构造函数的 main 也改成 C
sub(
    r'''<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"--- 进入 main ---"</span> &lt;&lt; <span class="hl-f">endl</span>;
    Player p(<span class="hl-s">"Archer"</span>, <span class="hl-n">100</span>);      <span class="hl-c">/* 构造 */</span>
    p.<span class="hl-f">show</span>();
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"--- 即将离开 main ---"</span> &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;                    <span class="hl-c">/* 离开作用域，自动析构 */</span>
}''',
    r'''<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-f">printf</span>(<span class="hl-s">"--- 进入 main ---\n"</span>);

    <span class="hl-k">struct</span> Player p;
    <span class="hl-f">player_init</span>(&amp;p, <span class="hl-s">"Archer"</span>, <span class="hl-n">100</span>);   <span class="hl-c">/* 手动「构造」 */</span>
    <span class="hl-f">player_show</span>(&amp;p);

    <span class="hl-f">printf</span>(<span class="hl-s">"--- 即将离开 main ---\n"</span>);
    <span class="hl-f">player_destroy</span>(&amp;p);            <span class="hl-c">/* 手动「析构」—— 别忘了 */</span>
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}''',
    "构造/析构示例的 main → C")

# 该段前面的正文里提到「构造函数：造对象时自动跑一次」
sub('<strong>析构函数</strong>最重要的用途', '析构函数最重要的用途',
    "占位2")

# ---------- 5. 常见错误 3（. 与 ->）改成 C ----------
sub(
    r'''Player p;
Player *ptr = &amp;p;

ptr.<span class="hl-f">show</span>();      <span class="hl-c">/* ❌ 指针要用 -&gt; */</span>
ptr-&gt;<span class="hl-f">show</span>();     <span class="hl-c">/* ✅ */</span>
(*ptr).<span class="hl-f">show</span>();  <span class="hl-c">/* ✅ 也合法，但没人这么写 */</span>''',
    r'''<span class="hl-k">struct</span> Player p;
<span class="hl-k">struct</span> Player *ptr = &amp;p;

ptr.<span class="hl-f">hp</span> = <span class="hl-n">10</span>;       <span class="hl-c">/* ❌ 指针要用 -&gt; */</span>
ptr-&gt;<span class="hl-f">hp</span> = <span class="hl-n">10</span>;      <span class="hl-c">/* ✅ */</span>
(*ptr).<span class="hl-f">hp</span> = <span class="hl-n">10</span>;   <span class="hl-c">/* ✅ 也合法，但没人这么写 */</span>''',
    "错误 3 的 . 与 -> 示例 → C")

# ---------- 6. 常见错误 4（构造函数）改成 C ----------
sub(
    r'''<span class="hl-k">class</span> Player {
<span class="hl-k">public</span>:
    <span class="hl-k">int</span> hp;                 <span class="hl-c">/* ❌ 没有构造函数，hp 是不确定的值 */</span>
};
Player p;
<span class="hl-f">cout</span> &lt;&lt; p.hp;             <span class="hl-c">/* 输出什么都有可能 */</span>

<span class="hl-c">/* ✅ 用构造函数保证一造出来就合法 */</span>
<span class="hl-k">class</span> Player {
    <span class="hl-k">int</span> hp;
<span class="hl-k">public</span>:
    <span class="hl-f">Player</span>() { hp = <span class="hl-n">100</span>; }
};''',
    r'''<span class="hl-k">struct</span> Player {
    <span class="hl-k">int</span> hp;
};
<span class="hl-k">struct</span> Player p;              <span class="hl-c">/* ❌ 没初始化，hp 是不确定的值 */</span>
<span class="hl-f">printf</span>(<span class="hl-s">"%d\n"</span>, p.hp);       <span class="hl-c">/* 输出什么都有可能 */</span>

<span class="hl-c">/* ✅ 用初始化函数保证一造出来就合法 */</span>
<span class="hl-k">void</span> <span class="hl-f">player_init</span>(<span class="hl-k">struct</span> Player *q) {
    q-&gt;hp = <span class="hl-n">100</span>;
}
<span class="hl-f">player_init</span>(&amp;p);''',
    "错误 4 的构造函数示例 → C")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("06：%d → %d 字符" % (orig, len(t)))
for d in done:
    print("  ✓ " + d)
print("")
print("剩余含 cout/iostream 的块：%d" % len(re.findall(r'cout|iostream', t)))
