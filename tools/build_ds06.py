# -*- coding: utf-8 -*-
"""生成 _ds_06_类、结构体.html 与 _ds_07_引用和指针函数.html"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
PARTS = os.path.join(ROOT, "_shell_parts")

with io.open(os.path.join(PARTS, "css.html"), encoding="utf-8") as fh:
    CSS = fh.read()
with io.open(os.path.join(PARTS, "scripts.html"), encoding="utf-8") as fh:
    SCRIPTS = fh.read()

# ============================================================
# 公共附加样式
# ============================================================
EXTRA_COMMON = """
/* 权限标记 */
.tag.pub{background:var(--green-soft);border-color:#bfe2cd;color:var(--green)}
.tag.pri{background:var(--red-soft);border-color:#f0c8c2;color:var(--red)}
.tag.pro{background:var(--amber-soft);border-color:#efd9a8;color:var(--amber)}

/* 接口示意图：一个接口，多个实现 */
.iface{
  display:grid;grid-template-columns:1fr;gap:0;margin:18px 0;
  border:1px solid var(--line-2);border-radius:12px;overflow:hidden;background:#fff;
}
.iface .top{
  padding:12px 16px;background:var(--violet-soft);border-bottom:1px solid #ded0f7;
  transition:background .15s;
}
.iface .top:hover{background:#e9ddfc}
.iface .top .nm{font-family:var(--mono);font-weight:700;color:var(--violet);font-size:15px}
.iface .top .ds{font-size:13px;color:var(--fg-2);margin-top:4px}
.iface .impls{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0}
.iface .impls .im{
  padding:11px 14px;border-right:1px solid var(--line);border-top:1px solid var(--line);
  transition:background .15s,transform .15s;
}
.iface .impls .im:last-child{border-right:0}
.iface .impls .im:hover{background:var(--blue-soft);transform:translateY(-2px)}
.iface .impls .im .n{font-family:var(--mono);font-weight:650;font-size:14px;margin-bottom:3px}
.iface .impls .im .d{font-size:12.5px;color:var(--fg-3);line-height:1.6}

/* 「值/引用/指针」三列对照 */
.trio{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:18px 0}
.trio .c{
  border:1px solid var(--line-2);border-radius:11px;padding:13px 15px;background:#fff;
  transition:box-shadow .16s,transform .16s,border-color .16s;
}
.trio .c:hover{box-shadow:0 6px 18px rgba(30,45,70,.12);transform:translateY(-2px)}
.trio .c .h{font-weight:700;font-size:14px;margin-bottom:6px;display:flex;align-items:center;gap:7px}
.trio .c.v .h{color:var(--fg)}
.trio .c.r .h{color:var(--green)}
.trio .c.p .h{color:var(--blue)}
.trio .c .code{font-family:var(--mono);font-size:12.5px;background:#f2f4f8;
  border:1px solid var(--line);border-radius:6px;padding:6px 9px;margin:8px 0;
  color:var(--fg);overflow:auto;white-space:pre}
.trio .c .note{font-size:12.5px;color:var(--fg-3);line-height:1.6}

/* 生命周期条 */
.lifecycle{display:flex;flex-wrap:wrap;margin:16px 0;align-items:stretch}
.lifecycle .st{
  flex:1 1 120px;border:1px solid var(--line);border-radius:9px;padding:10px 12px;
  background:#fff;position:relative;transition:box-shadow .15s,transform .15s;
}
.lifecycle .st:hover{box-shadow:0 5px 16px rgba(30,45,70,.1);transform:translateY(-2px)}
.lifecycle .st+.st{margin-left:24px}
.lifecycle .st+.st::before{
  content:"→";position:absolute;left:-19px;top:50%;transform:translateY(-50%);
  color:var(--fg-3);font-size:15px;font-family:var(--mono);
}
.lifecycle .st .t{font-weight:650;font-size:13.5px;margin-bottom:2px;font-family:var(--mono)}
.lifecycle .st .d{font-size:12px;color:var(--fg-3);line-height:1.55}
@media(max-width:560px){
  .lifecycle{display:block}
  .lifecycle .st+.st{margin:20px 0 0}
  .lifecycle .st+.st::before{content:"↓";left:50%;top:-19px;transform:translateX(-50%)}
}
"""

# ============================================================
# 文档 06
# ============================================================
HTML06 = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C/C++ · 类、结构体</title>
@@CSS@@
<style>@@EXTRA@@</style>
</head>
<body>
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
  <a href="#s1">1 · 从「一堆平行数组」说起</a>
  <a href="#s2">2 · 用 struct 打包</a>
  <a href="#s3">3 · 一队玩家</a>
  <a href="#s4">4 · 给 struct 加上函数</a>
  <div class="sep"></div>
  <a href="#s5">5 · 私有与共有成员</a>
  <a href="#s5a" class="sub">5.1 为什么要藏起来</a>
  <a href="#s5b" class="sub">5.2 private / public 怎么写</a>
  <a href="#s5c" class="sub">5.3 亲眼看看编译错误</a>
  <a href="#s6">6 · struct 与 class 的唯一区别</a>
  <div class="sep"></div>
  <a href="#s7">7 · 接口：约定「必须会做什么」</a>
  <a href="#s7a" class="sub">7.1 三个角色，一套动作</a>
  <a href="#s7b" class="sub">7.2 接口为什么省事</a>
  <a href="#s7c" class="sub">7.3 接口与实现分离</a>
  <a href="#s8">8 · 对象的生与死</a>
  <a href="#s9">9 · 常见错误</a>
  <a href="#s10">10 · 一页速查</a>
</nav>

<main>
<h1>类、结构体</h1>
<p class="sub-title">UME 项目组内部教程 · 第六讲 · C / C++ 混合项目 · 游戏开发场景</p>
<p>
  <span class="tag">已学：数组 / 函数 / 指针</span>
  <span class="tag">已学：内存与内存安全</span>
  <span class="tag b">本讲：把数据和行为打包</span>
  <span class="tag">C++ 项目</span>
</p>

<div class="card note">
  <div class="card-t">这一讲从游戏开发讲起</div>
  <p>前面几讲我们存的都是「一堆数」：成绩、数组、内存块。
  但游戏里要存的是<b>一个个角色</b> —— 每个角色有名字、血量、魔法、攻击力，
  还有「挨打」「加血」「攻击」这些行为。</p>
  <p>这一讲就是把这类东西<b>打包成一个整体</b>。
  语法在 C 和 C++ 里都叫 <code>struct</code>，C++ 还多了一个 <code>class</code>。</p>
  <p>文中所有「运行结果」与「编译错误」均经过实际编译运行核对（GCC 13.1）。</p>
</div>

<!-- ============================================================ -->
<h2 id="s1"><span class="n">1</span>从「一堆平行数组」说起</h2>

<p>假设要存 3 个玩家：名字、血量、魔法值。</p>

<p>用你已经会的知识，最直接的办法是开三个数组：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">平行数组：能跑，但很别扭</span><span class="cp">复制</span></div><pre><span class="hl-k">char</span> names[<span class="hl-n">3</span>][<span class="hl-n">20</span>] = {<span class="hl-s">"Archer"</span>, <span class="hl-s">"Mage"</span>, <span class="hl-s">"Knight"</span>};
<span class="hl-k">int</span>  hps[<span class="hl-n">3</span>]        = {<span class="hl-n">100</span>, <span class="hl-n">80</span>, <span class="hl-n">150</span>};
<span class="hl-k">int</span>  mps[<span class="hl-n">3</span>]        = {<span class="hl-n">30</span>, <span class="hl-n">120</span>, <span class="hl-n">10</span>};

<span class="hl-c">/* 下标 1 就是同一个人的三个属性 */</span>
<span class="hl-f">printf</span>(<span class="hl-s">"%s hp=%d mp=%d\n"</span>, names[<span class="hl-n">1</span>], hps[<span class="hl-n">1</span>], mps[<span class="hl-n">1</span>]);</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>Mage hp=80 mp=120</pre></div>

<p>能跑。但问题会随着属性变多而迅速恶化：</p>

<div class="flow">
  <div class="s"><div class="t">加属性很烦</div>
    <div class="d">想加「攻击力」，就得再加一个数组，并且所有相关代码都要改</div></div>
  <div class="s"><div class="t">容易错位</div>
    <div class="d"><code>names[2]</code> 配 <code>hps[1]</code> 编译器不会拦你，但逻辑已经错了</div></div>
  <div class="s"><div class="t">传参更烦</div>
    <div class="d">想把「一个玩家」传给函数，得传三个参数，再加属性就再加参数</div></div>
</div>

<div class="card key">
  <div class="card-t">问题的根源</div>
  <p><b>「名字、血量、魔法」本来是同一个东西的三个部分，
  却被拆成了三个互不相干的数组。</b></p>
  <p>它们之间只有「下标相同」这一条<b>口头约定</b>，
  编译器完全不知道它们有关系，自然也没法替你检查。</p>
</div>

<!-- ============================================================ -->
<h2 id="s2"><span class="n">2</span>用 struct 打包</h2>

<p><code>struct</code> 解决的就是这件事：<b>把属于同一个东西的若干数据，
声明成一个新的类型。</b></p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">定义一个玩家类型</span><span class="cp">复制</span></div><pre><span class="hl-k">struct</span> Player {
    <span class="hl-k">char</span> name[<span class="hl-n">20</span>];
    <span class="hl-k">int</span>  hp;
    <span class="hl-k">int</span>  mp;
};                       <span class="hl-c">/* ← 注意这个分号，忘了会报一堆奇怪的错 */</span></pre></div>

<p>这四行的意思是：<b>从今以后，<code>Player</code> 就是一个类型了</b>，
和 <code>int</code>、<code>double</code> 一样可以用来声明变量。</p>

<table>
<thead><tr><th style="width:30%">对比</th><th>写法</th><th>含义</th></tr></thead>
<tbody>
<tr><td>内置类型</td><td class="c">int score;</td><td>一个整数</td></tr>
<tr><td>内置类型</td><td class="c">double h;</td><td>一个小数</td></tr>
<tr><td><b>自定义类型</b></td><td class="c">Player p;</td><td><b>一个玩家</b>（里面含 name、hp、mp）</td></tr>
</tbody>
</table>

<h4>怎么用</h4>
<p>用「点号」访问里面的成员，每个成员就<b>像一个普通变量</b>：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">读写成员</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string.h&gt;</span>

<span class="hl-k">struct</span> Player {
    <span class="hl-k">char</span> name[<span class="hl-n">20</span>];
    <span class="hl-k">int</span>  hp;
    <span class="hl-k">int</span>  mp;
};

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    <span class="hl-k">struct</span> Player p;              <span class="hl-c">/* 声明一个玩家 */</span>

    <span class="hl-f">strcpy</span>(p.name, <span class="hl-s">"Archer"</span>);   <span class="hl-c">/* 字符串要用 strcpy */</span>
    p.hp = <span class="hl-n">100</span>;
    p.mp = <span class="hl-n">30</span>;

    <span class="hl-f">printf</span>(<span class="hl-s">"%s hp=%d mp=%d\n"</span>, p.name, p.hp, p.mp);

    <span class="hl-c">/* 成员可以像普通变量一样参与运算 */</span>
    p.hp = p.hp - <span class="hl-n">30</span>;
    <span class="hl-f">printf</span>(<span class="hl-s">"受伤后 hp=%d\n"</span>, p.hp);

    <span class="hl-c">/* 看这个类型占多少字节 */</span>
    <span class="hl-f">printf</span>(<span class="hl-s">"sizeof(Player) = %d\n"</span>, (<span class="hl-k">int</span>)<span class="hl-k">sizeof</span>(<span class="hl-k">struct</span> Player));
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>Archer hp=100 mp=30
受伤后 hp=70
sizeof(Player) = 28</pre></div>

<p><code>28</code> 字节 = 20（<code>char name[20]</code>）+ 4（<code>int hp</code>）+ 4（<code>int mp</code>）。
<b>结构体的大小大致就是所有成员之和</b>（有时因为「对齐」会稍大一点，入门阶段不必深究）。</p>

<div class="card tip">
  <div class="card-t">C 语言里要写 <code>struct Player p;</code></div>
  <p>上面那样写是 C 的规范写法。每次都写 <code>struct</code> 有点啰嗦，
  所以常用 <code>typedef</code> 起个别名：</p>
  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">typedef</span> <span class="hl-k">struct</span> {
    <span class="hl-k">char</span> name[<span class="hl-n">20</span>];
    <span class="hl-k">int</span>  hp;
    <span class="hl-k">int</span>  mp;
} Player;                 <span class="hl-c">/* 以后直接写 Player p; */</span></pre>
  <p><b>在 C++ 里不用这么麻烦</b> —— 直接写 <code>Player p;</code> 就行，
  <code>struct</code> 这个名字本身就当类型名用。本讲后面都用 C++ 的写法。</p>
</div>

<!-- ============================================================ -->
<h2 id="s3"><span class="n">3</span>一队玩家</h2>

<p>结构体可以放进数组，于是「一队玩家」就是<b>一个数组</b>，
而不是三个平行的数组。这一步让代码立刻清爽起来。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">结构体数组</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
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
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>Archer hp=100 mp=30
Mage hp=80 mp=120
Knight hp=150 mp=10</pre></div>

<div class="card key">
  <div class="card-t">对比一下差别</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:30%">想做的事</th><th>平行数组</th><th>结构体数组</th></tr></thead>
  <tbody>
  <tr><td>取第 1 个玩家的血量</td><td class="c">hps[1]</td><td class="c">team[1].hp</td></tr>
  <tr><td>看出「这是一整个玩家」</td><td>看不出来</td><td class="c">很明显</td></tr>
  <tr><td>加一个属性「攻击力」</td><td>再加一个数组 + 到处改</td><td>加一行成员即可</td></tr>
  <tr><td>把「一个玩家」传给函数</td><td>传 3 个参数</td><td class="c">传 1 个</td></tr>
  </tbody></table>
</div>

<!-- ============================================================ -->
<h2 id="s4"><span class="n">4</span>给 struct 加上函数</h2>

<p>数据打包好了，但「挨打」「加血」这些操作还散在外面。
如果能把它们<b>也放进结构体里</b>，用起来就顺多了 —— 这是 C++ 的加强。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">成员函数</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">struct</span> Player {
    string name;
    <span class="hl-k">int</span> hp;
    <span class="hl-k">int</span> mp;

    <span class="hl-c">/* 写在结构体里面的函数，叫「成员函数」 */</span>
    <span class="hl-k">void</span> <span class="hl-f">show</span>() {
        <span class="hl-f">cout</span> &lt;&lt; name &lt;&lt; <span class="hl-s">" hp="</span> &lt;&lt; hp &lt;&lt; <span class="hl-s">" mp="</span> &lt;&lt; mp &lt;&lt; <span class="hl-f">endl</span>;
    }
    <span class="hl-k">bool</span> <span class="hl-f">isAlive</span>() { <span class="hl-k">return</span> hp &gt; <span class="hl-n">0</span>; }

    <span class="hl-k">void</span> <span class="hl-f">takeDamage</span>(<span class="hl-k">int</span> dmg) {
        hp -= dmg;
        <span class="hl-k">if</span> (hp &lt; <span class="hl-n">0</span>) hp = <span class="hl-n">0</span>;   <span class="hl-c">/* 血量不会变成负数 */</span>
    }
};

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    Player p;
    p.name = <span class="hl-s">"Archer"</span>;
    p.hp = <span class="hl-n">100</span>;
    p.mp = <span class="hl-n">30</span>;

    p.<span class="hl-f">show</span>();          <span class="hl-c">/* 用「对象.函数名()」调用 */</span>
    p.<span class="hl-f">takeDamage</span>(<span class="hl-n">30</span>);
    p.<span class="hl-f">show</span>();

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"还活着吗？ "</span> &lt;&lt; (p.<span class="hl-f">isAlive</span>() ? <span class="hl-s">"是"</span> : <span class="hl-s">"否"</span>) &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>Archer hp=100 mp=30
Archer hp=70 mp=30
还活着吗？ 是</pre></div>

<p>两个要点：</p>

<ul>
  <li><b>成员函数里可以直接写 <code>hp</code></b>，不用写 <code>p.hp</code>。
    因为它「知道」自己是哪个对象在调用 —— 编译器替你传递了这个信息。</li>
  <li><b>好处是「数据和操作放在一起」。</b>
    「挨打」这件事该改哪些数据，就在定义 <code>Player</code> 的地方一眼看全，
    不用在几千行代码里到处找。</li>
</ul>

<div class="card tip">
  <div class="card-t">术语对照（先有个印象）</div>
  <table style="margin:8px 0 0">
  <tbody>
  <tr><td style="width:30%"><b>结构体 / 类</b></td><td><code>Player</code> ——
    类型的定义，描述「一个玩家有什么」</td></tr>
  <tr><td><b>对象 / 实例</b></td><td><code>p</code>、<code>team[0]</code> ——
    按这个类型造出来的具体东西</td></tr>
  <tr><td><b>成员变量</b></td><td><code>name</code>、<code>hp</code>、<code>mp</code> ——
    对象里的数据</td></tr>
  <tr><td><b>成员函数</b></td><td><code>show()</code>、<code>takeDamage()</code> ——
    对象能做的操作</td></tr>
  </tbody></table>
</div>

<!-- ============================================================ -->
<h2 id="s5"><span class="n">5</span>私有与共有成员</h2>

<p>上面那个 <code>Player</code> 有个隐患：<b>外面可以随便改 <code>hp</code></b>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">危险：外面为所欲为</span><span class="cp">复制</span></div><pre>Player p;
p.hp = <span class="hl-n">100</span>;
p.hp = <span class="hl-n">999999</span>;      <span class="hl-c">/* 血量改到天文数字，没人管 */</span>
p.hp = <span class="hl-n">-500</span>;        <span class="hl-c">/* 血量变负数，后面判断全乱 */</span></pre></div>

<p>我们在 <code>takeDamage</code> 里写了「不让血量变成负数」的保护，
可这个保护<b>可以被绕过去</b> —— 只要有人直接写 <code>p.hp = -500</code>。</p>

<h3 id="s5a">5.1 为什么要藏起来</h3>

<div class="card key">
  <div class="card-t">核心思想：把「能改的东西」控制起来</div>
  <p>如果一个数据<b>必须满足某种规则</b>（血量不能为负、魔法不能超上限），
  那么就应该<b>只允许通过函数去改它</b>，在函数里保证规则成立。</p>
  <p>这样「规则」只需要在一处维护，外部代码不可能绕过。</p>
</div>

<p>用生活里的例子理解：</p>

<div class="flow">
  <div class="s"><div class="t">自动售货机</div>
    <div class="d">你按按钮（接口），它给你饮料。
      你打不开它的内部去直接拿（数据被保护）</div></div>
  <div class="s"><div class="t">汽车</div>
    <div class="d">你踩油门（接口），发动机按规则响应。
      你不会去直接拧发动机的喷油嘴</div></div>
</div>

<h3 id="s5b">5.2 <code>private</code> / <code>public</code> 怎么写</h3>

<p>用 <code>class</code> 定义，并把数据放在 <code>private:</code> 下面，
把想对外提供的函数放在 <code>public:</code> 下面：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">class + private / public</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">class</span> Player {
<span class="hl-k">private</span>:                       <span class="hl-c">/* 私有：只有自己人能用 */</span>
    <span class="hl-k">int</span> hp;
    <span class="hl-k">int</span> maxHp;

<span class="hl-k">public</span>:                        <span class="hl-c">/* 公开：外面可以调用 */</span>
    string name;

    Player(string n, <span class="hl-k">int</span> m) {   <span class="hl-c">/* 构造函数：造对象时自动执行 */</span>
        name = n;
        maxHp = m;
        hp = m;
    }

    <span class="hl-k">void</span> <span class="hl-f">takeDamage</span>(<span class="hl-k">int</span> dmg) {
        hp -= dmg;
        <span class="hl-k">if</span> (hp &lt; <span class="hl-n">0</span>) hp = <span class="hl-n">0</span>;
    }
    <span class="hl-k">void</span> <span class="hl-f">heal</span>(<span class="hl-k">int</span> v) {
        hp += v;
        <span class="hl-k">if</span> (hp &gt; maxHp) hp = maxHp;
    }

    <span class="hl-k">int</span>  <span class="hl-f">getHp</span>() { <span class="hl-k">return</span> hp; }     <span class="hl-c">/* 只读接口 */</span>
    <span class="hl-k">bool</span> <span class="hl-f">isAlive</span>() { <span class="hl-k">return</span> hp &gt; <span class="hl-n">0</span>; }
    <span class="hl-k">void</span> <span class="hl-f">show</span>() {
        <span class="hl-f">cout</span> &lt;&lt; name &lt;&lt; <span class="hl-s">" HP "</span> &lt;&lt; hp &lt;&lt; <span class="hl-s">"/"</span> &lt;&lt; maxHp &lt;&lt; <span class="hl-f">endl</span>;
    }
};

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    Player p(<span class="hl-s">"Archer"</span>, <span class="hl-n">100</span>);     <span class="hl-c">/* 构造函数自动被调用 */</span>
    p.<span class="hl-f">show</span>();

    p.<span class="hl-f">takeDamage</span>(<span class="hl-n">40</span>);
    p.<span class="hl-f">show</span>();

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"从接口读 HP: "</span> &lt;&lt; p.<span class="hl-f">getHp</span>() &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-c">/* 一路打到死 */</span>
    p.<span class="hl-f">takeDamage</span>(<span class="hl-n">1000</span>);
    p.<span class="hl-f">show</span>();
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"还活着吗？ "</span> &lt;&lt; (p.<span class="hl-f">isAlive</span>() ? <span class="hl-s">"是"</span> : <span class="hl-s">"否"</span>) &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-c">/* 治疗也不会超过上限 */</span>
    p.<span class="hl-f">heal</span>(<span class="hl-n">9999</span>);
    p.<span class="hl-f">show</span>();
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>Archer HP 100/100
Archer HP 60/100
从接口读 HP: 60
Archer HP 0/100
还活着吗？ 否
Archer HP 100/100</pre></div>

<p>注意最后两行：<b>无论外面怎么折腾，血量都守规矩</b> ——
打不死成负数，也治不过上限。因为所有修改都必须经过
<code>takeDamage</code> / <code>heal</code>，而规则就写在里面。</p>

<h4>构造函数：造对象时自动跑一次</h4>
<p><code>Player(string n, int m)</code> 这个函数<b>名字和类名一样、没有返回值类型</b>，
它就是构造函数。写 <code>Player p("Archer", 100);</code> 时自动被调用，
用来把对象初始化好。</p>

<div class="card tip">
  <div class="card-t">为什么要构造函数</div>
  <p>没有它的话，新造出来的对象里 <code>hp</code> 是<b>不确定的值</b>，
  你可能会忘了初始化就用。构造函数保证<b>对象一造出来就是合法状态</b>。</p>
</div>

<h3 id="s5c">5.3 亲眼看看编译错误</h3>

<p>如果你从外面直接改私有成员，<b>编译器根本不会让它编过</b>。
实际编译一下（GCC 13.1）：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">故意写错：从外面改私有成员</span><span class="cp">复制</span></div><pre><span class="hl-k">class</span> Player {
<span class="hl-k">private</span>:
    <span class="hl-k">int</span> hp;
<span class="hl-k">public</span>:
    Player() { hp = <span class="hl-n">100</span>; }
    <span class="hl-k">int</span> <span class="hl-f">getHp</span>() { <span class="hl-k">return</span> hp; }
};

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    Player p;
    p.hp = <span class="hl-n">999</span>;          <span class="hl-c">/* ← 这一行会编译失败 */</span>
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'int Player::hp' is private within this context
   12 |     p.hp = 999;
      |       ^~
note: declared private here
    4 |     int hp;
      |         ^~
note: field 'int Player::hp' can be accessed via 'int Player::getHp()'
   12 |     p.hp = 999;
      |       ^~
      |       getHp()</pre></div>

<p>编译器说得很清楚：<b><code>hp</code> 在这个上下文里是私有的</b>，
而且还贴心地提示你「可以通过 <code>getHp()</code> 访问」。</p>

<div class="card key">
  <div class="card-t">这就是「私有」最大的价值</div>
  <p>它把一类错误<b>从「运行时的诡异 bug」变成了「编译时的明确报错」</b>。</p>
  <p>对比一下：如果 <code>hp</code> 是公开的，你写了 <code>p.hp = -500</code>，
  程序<b>照样编过、照样跑</b>，直到某天血量算出乱七八糟的伤害才被发现问题所在 ——
  那时你可能已经排查很久了。</p>
  <p><b>能不写 bug，就别写 bug。</b>让编译器帮你拦，是最省事的做法。</p>
</div>

<h4>三种权限</h4>
<table>
<thead><tr><th style="width:22%">关键字</th><th style="width:30%">谁能访问</th><th>典型用途</th></tr></thead>
<tbody>
<tr><td class="c">private</td><td><span class="tag pri">只有自己</span> 类内部的函数能用</td>
    <td>数据（血量、上限），需要保护的成员</td></tr>
<tr><td class="c">public</td><td><span class="tag pub">谁都能用</span></td>
    <td>对外提供的函数、构造函数</td></tr>
<tr><td class="c">protected</td><td><span class="tag pro">自己和子类</span></td>
    <td>给继承用的，本讲暂不展开</td></tr>
</tbody>
</table>

<!-- ============================================================ -->
<h2 id="s6"><span class="n">6</span>struct 与 class 的唯一区别</h2>

<p>你可能会问：前面用 <code>struct</code>，这里用 <code>class</code>，到底差在哪？</p>

<div class="card key">
  <div class="card-t">答案是：只有一个区别 —— 默认权限</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:24%"></th><th>不写权限时，成员默认是</th></tr></thead>
  <tbody>
  <tr><td class="c">struct</td><td><span class="tag pub">public</span>（公开）</td></tr>
  <tr><td class="c">class</td><td><span class="tag pri">private</span>（私有）</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>除此之外两者完全一样</b> ——
  都可以有成员函数、构造函数、继承。<code>sizeof</code> 也一样大。</p>
</div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">验证默认权限不同</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">struct</span> SA { <span class="hl-k">int</span> x; };      <span class="hl-c">/* 默认 public */</span>
<span class="hl-k">class</span>  SB { <span class="hl-k">int</span> x; };      <span class="hl-c">/* 默认 private */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    SA a;
    a.x = <span class="hl-n">10</span>;                <span class="hl-c">/* ✅ 可以，struct 默认公开 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"struct SA 可以直接 a.x = "</span> &lt;&lt; a.x &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-c">/* SB b; b.x = 10; */</span>
    <span class="hl-c">/* ↑ 取消注释就编译失败：class 默认私有 */</span>

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"sizeof(SA)="</span> &lt;&lt; <span class="hl-k">sizeof</span>(SA)
         &lt;&lt; <span class="hl-s">"  sizeof(SB)="</span> &lt;&lt; <span class="hl-k">sizeof</span>(SB) &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>struct SA 可以直接 a.x = 10
sizeof(SA)=4  sizeof(SB)=4</pre></div>

<div class="card tip">
  <div class="card-t">实际项目里的选择习惯</div>
  <ul>
    <li><b>纯数据、没有规则要保护</b>（比如一个坐标 <code>Point{x, y}</code>）
      → 用 <code>struct</code>，简单直接。</li>
    <li><b>有内部状态和不变量要维护</b>（比如玩家血量、银行账户）
      → 用 <code>class</code>，把数据放 private。</li>
  </ul>
  <p>这个习惯不是强制的，但它能让人<b>一眼看出你的意图</b>：
  看到 <code>struct</code> 就知道「这只是个数据包」。</p>
</div>

<!-- ============================================================ -->
<h2 id="s7"><span class="n">7</span>接口：约定「必须会做什么」</h2>

<p>现在来解决游戏开发里最实际的问题：<b>角色有很多种，但战斗时要用同一套动作。</b></p>

<h3 id="s7a">7.1 三个角色，一套动作</h3>

<p>我们希望这样写代码：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">愿望：不管什么角色，都能这样调</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 遍历所有角色，一律调用 describe() 和 attack() */</span>
<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; <span class="hl-n">3</span>; i++) {
    list[i]-&gt;<span class="hl-f">describe</span>();
    list[i]-&gt;<span class="hl-f">attack</span>();
}</pre></div>

<p>问题在于：弓箭手、法师、骑士是<b>三个不同的类</b>，
凭什么能放进同一个数组、用同样的方式调用？</p>

<p>答案是<b>让它们都「实现同一个接口」</b>。</p>

<div class="iface">
  <div class="top">
    <div class="nm">class GameCharacter &nbsp;（接口）</div>
    <div class="ds">只规定「必须会做什么」，不写「怎么做」</div>
  </div>
  <div class="impls">
    <div class="im"><div class="n">Archer</div><div class="d">射箭，伤害 15<br>远程、血少</div></div>
    <div class="im"><div class="n">Mage</div><div class="d">火球，伤害 25<br>远程、魔法高</div></div>
    <div class="im"><div class="n">Knight</div><div class="d">挥剑，伤害 20<br>近战、血厚</div></div>
  </div>
</div>

<h4>写法和运行结果</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">接口 + 三个实现</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-c">/* ===== 接口：只声明「必须会做什么」 ===== */</span>
<span class="hl-k">class</span> GameCharacter {
<span class="hl-k">public</span>:
    <span class="hl-k">virtual</span> <span class="hl-k">void</span> <span class="hl-f">attack</span>() = <span class="hl-n">0</span>;      <span class="hl-c">/* 纯虚函数：自己不实现 */</span>
    <span class="hl-k">virtual</span> <span class="hl-k">void</span> <span class="hl-f">describe</span>() = <span class="hl-n">0</span>;
    <span class="hl-k">virtual</span> ~<span class="hl-f">GameCharacter</span>() {}       <span class="hl-c">/* 虚析构（先照抄） */</span>
};

<span class="hl-c">/* ===== 三个实现 ===== */</span>
<span class="hl-k">class</span> Archer : <span class="hl-k">public</span> GameCharacter {
<span class="hl-k">public</span>:
    <span class="hl-k">void</span> <span class="hl-f">attack</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"Archer 射出一箭，伤害 15"</span> &lt;&lt; <span class="hl-f">endl</span>; }
    <span class="hl-k">void</span> <span class="hl-f">describe</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"弓箭手：远程，血少"</span> &lt;&lt; <span class="hl-f">endl</span>; }
};

<span class="hl-k">class</span> Mage : <span class="hl-k">public</span> GameCharacter {
<span class="hl-k">public</span>:
    <span class="hl-k">void</span> <span class="hl-f">attack</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"Mage 放火球，伤害 25"</span> &lt;&lt; <span class="hl-f">endl</span>; }
    <span class="hl-k">void</span> <span class="hl-f">describe</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"法师：远程，魔法高"</span> &lt;&lt; <span class="hl-f">endl</span>; }
};

<span class="hl-k">class</span> Knight : <span class="hl-k">public</span> GameCharacter {
<span class="hl-k">public</span>:
    <span class="hl-k">void</span> <span class="hl-f">attack</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"Knight 挥剑，伤害 20"</span> &lt;&lt; <span class="hl-f">endl</span>; }
    <span class="hl-k">void</span> <span class="hl-f">describe</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"骑士：近战，血厚"</span> &lt;&lt; <span class="hl-f">endl</span>; }
};

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    Archer a;
    Mage m;
    Knight k;

    <span class="hl-c">/* 关键：用「接口指针」把它们放进同一个数组 */</span>
    GameCharacter *list[<span class="hl-n">3</span>] = { &amp;a, &amp;m, &amp;k };

    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; <span class="hl-n">3</span>; i++) {
        list[i]-&gt;<span class="hl-f">describe</span>();      <span class="hl-c">/* 各自执行自己的版本 */</span>
        list[i]-&gt;<span class="hl-f">attack</span>();
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>弓箭手：远程，血少
Archer 射出一箭，伤害 15
法师：远程，魔法高
Mage 放火球，伤害 25
骑士：近战，血厚
Knight 挥剑，伤害 20</pre></div>

<p>循环只写了一份，但三个角色各自动了自己的那一版。
这叫<b>「多态」</b> —— 同一个调用，根据实际对象走不同的代码。</p>

<h3 id="s7b">7.2 接口为什么省事</h3>

<p>最实在的好处：<b>加新角色时，旧代码一行都不用改。</b></p>

<p>假设现在要加一个「治疗者」：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">新角色 + 一个只依赖接口的函数</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 新写的角色，同样实现这个接口 */</span>
<span class="hl-k">class</span> Healer : <span class="hl-k">public</span> GameCharacter {
<span class="hl-k">public</span>:
    <span class="hl-k">void</span> <span class="hl-f">attack</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"Healer 投掷圣光，伤害 5"</span> &lt;&lt; <span class="hl-f">endl</span>; }
    <span class="hl-k">void</span> <span class="hl-f">describe</span>() <span class="hl-k">override</span> { <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"治疗者：辅助"</span> &lt;&lt; <span class="hl-f">endl</span>; }
};

<span class="hl-c">/* 这个函数只认接口，不关心具体是谁。
   它是之前就写好的，一行都没动。 */</span>
<span class="hl-k">void</span> <span class="hl-f">letThemFight</span>(GameCharacter *c) {
    c-&gt;<span class="hl-f">describe</span>();
    c-&gt;<span class="hl-f">attack</span>();
}

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    Archer a; Mage m; Knight k; Healer h;
    <span class="hl-f">letThemFight</span>(&amp;a);
    <span class="hl-f">letThemFight</span>(&amp;m);
    <span class="hl-f">letThemFight</span>(&amp;h);      <span class="hl-c">/* 新角色，函数没改过 */</span>
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>弓箭手：远程，血少
Archer 射出一箭，伤害 15
法师：远程，魔法高
Mage 放火球，伤害 25
治疗者：辅助
Healer 投掷圣光，伤害 5</pre></div>

<div class="card key">
  <div class="card-t">接口的真正价值</div>
  <p><code>letThemFight</code> 这个函数<b>只依赖「接口」，不依赖任何具体角色</b>。</p>
  <p>所以：</p>
  <ul>
    <li>加新角色 → <b>不用改它</b></li>
    <li>改某个角色的技能 → <b>不用改它</b></li>
    <li>把角色删掉 → <b>也不用改它</b></li>
  </ul>
  <p>这就是「<b>对扩展开放，对修改封闭</b>」的含义：
  新功能靠<b>加新类</b>实现，而不是靠改老代码。
  改老代码就有改坏的风险，加新类则不会影响已有功能。</p>
</div>

<h3 id="s7c">7.3 接口与实现分离</h3>

<p>你会注意到，接口里那个 <code>= 0</code> 是关键：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">普通虚函数 vs 纯虚函数</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 普通虚函数：有函数体，子类可以选择性重写 */</span>
<span class="hl-k">virtual</span> <span class="hl-k">void</span> <span class="hl-f">attack</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"默认攻击"</span> &lt;&lt; <span class="hl-f">endl</span>;
}

<span class="hl-c">/* 纯虚函数：= 0，没有函数体，子类【必须】实现 */</span>
<span class="hl-k">virtual</span> <span class="hl-k">void</span> <span class="hl-f">attack</span>() = <span class="hl-n">0</span>;</pre></div>

<table>
<thead><tr><th style="width:30%"></th><th>普通虚函数</th><th>纯虚函数（<code>= 0</code>）</th></tr></thead>
<tbody>
<tr><td><b>有没有函数体</b></td><td>有</td><td><b>没有</b></td></tr>
<tr><td><b>子类必须实现吗</b></td><td>不必（可继承默认行为）</td><td><b>必须</b></td></tr>
<tr><td><b>能直接造对象吗</b></td><td class="c">能</td><td class="c"><b>不能</b>（只能通过子类）</td></tr>
<tr><td><b>用途</b></td><td>提供可覆盖的默认行为</td><td><b>定义接口</b></td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">为什么含纯虚函数的类不能直接造对象</div>
  <p>因为「该怎么做」还没定下来。
  写 <code>GameCharacter c;</code> 编译器会拒绝 ——
  如果允许，那 <code>c.attack()</code> 到底该干什么？没人知道。</p>
  <p>这个限制正是接口的意义：<b>接口只描述能力，实际干活的是具体角色。</b></p>
</div>

<h4>接口该长什么样</h4>
<p>好的接口有两个特点：</p>

<div class="flow">
  <div class="s"><div class="t">名字说清「做什么」</div>
    <div class="d"><code>attack()</code>、<code>takeDamage()</code>、
      <code>isAlive()</code> —— 不看实现也知道大概</div></div>
  <div class="s"><div class="t">不暴露「怎么做」</div>
    <div class="d">接口里没有 <code>hp</code>，没有内部算法。
      换一套实现，用接口的代码不用动</div></div>
</div>

<!-- ============================================================ -->
<h2 id="s8"><span class="n">8</span>对象的生与死</h2>

<p>最后一节快速过一下对象的「生命周期」，这是把类用对的关键。</p>

<div class="lifecycle">
  <div class="st"><div class="t">构造</div><div class="d">对象被创建时<br>自动跑构造函数</div></div>
  <div class="st"><div class="t">使用</div><div class="d">通过公开接口<br>读写、调用成员函数</div></div>
  <div class="st"><div class="t">析构</div><div class="d">对象消失时<br>自动跑析构函数</div></div>
</div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">构造函数与析构函数</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
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
};

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"--- 进入 main ---"</span> &lt;&lt; <span class="hl-f">endl</span>;
    Player p(<span class="hl-s">"Archer"</span>, <span class="hl-n">100</span>);      <span class="hl-c">/* 构造 */</span>
    p.<span class="hl-f">show</span>();
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"--- 即将离开 main ---"</span> &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;                    <span class="hl-c">/* 离开作用域，自动析构 */</span>
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>--- 进入 main ---
[构造] Archer 诞生
Archer HP 100
--- 即将离开 main ---
[析构] Archer 退场</pre></div>

<p>注意 <code>[析构]</code> 是在 <code>--- 即将离开 main ---</code>
<b>之后</b>打印的：对象在离开作用域（<code>main</code> 结束）时自动销毁。</p>

<div class="card key">
  <div class="card-t">析构函数最重要的用途</div>
  <p>如果类里用 <code>malloc</code> / <code>new</code> 申请了资源，
  <b>就该在析构函数里释放</b>。这样对象一消失，资源自动归还 ——
  不用你记着写 <code>free</code>。</p>
  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">class</span> Buffer {
    <span class="hl-k">int</span> *data;
<span class="hl-k">public</span>:
    <span class="hl-f">Buffer</span>(<span class="hl-k">int</span> n)  { data = <span class="hl-k">new</span> <span class="hl-k">int</span>[n]; }   <span class="hl-c">/* 申请 */</span>
    ~<span class="hl-f">Buffer</span>()       { <span class="hl-k">delete</span>[] data; }        <span class="hl-c">/* 归还，自动！ */</span>
};</pre>
  <p>这就是第五讲「谁申请谁释放」在类里的落地方式：
  <b>申请写在构造函数，释放写在析构函数</b>，
  只要对象正常销毁，就不会泄漏。</p>
</div>

<div class="card warn">
  <div class="card-t">本讲不展开的内容</div>
  <p>再往下还有「继承的细节」「拷贝构造函数 / 赋值运算符」「虚析构为什么必须写」
  「智能指针」等，属于进阶话题。<b>先把本讲的接口与封装用熟，比急着往下学更重要。</b></p>
</div>

<!-- ============================================================ -->
<h2 id="s9"><span class="n">9</span>常见错误</h2>

<h4>错误 1 · 定义结构体后忘了分号</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-k">struct</span> Player {
    <span class="hl-k">int</span> hp;
}                        <span class="hl-c">/* ❌ 少分号：后面会报一串莫名其妙的错 */</span>

<span class="hl-k">struct</span> Player {
    <span class="hl-k">int</span> hp;
};                       <span class="hl-c">/* ✅ */</span></pre></div>

<h4>错误 2 · 忘了「数据放 private」</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 数据全公开，保护形同虚设 */</span>
<span class="hl-k">class</span> Player {
<span class="hl-k">public</span>:
    <span class="hl-k">int</span> hp;              <span class="hl-c">/* 外面能写 p.hp = -500 */</span>
};

<span class="hl-c">/* ✅ 数据私有，只通过接口改 */</span>
<span class="hl-k">class</span> Player {
<span class="hl-k">private</span>:
    <span class="hl-k">int</span> hp;
<span class="hl-k">public</span>:
    <span class="hl-k">void</span> <span class="hl-f">takeDamage</span>(<span class="hl-k">int</span> d);   <span class="hl-c">/* 规则写在里面 */</span>
    <span class="hl-k">int</span>  <span class="hl-f">getHp</span>();</pre></div>

<h4>错误 3 · 接口里漏写 <code>= 0</code></h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 这不是接口，而是「有默认实现的虚函数」，
      子类不实现也能编过，就失去约束了 */</span>
<span class="hl-k">virtual</span> <span class="hl-k">void</span> <span class="hl-f">attack</span>() { }

<span class="hl-c">/* ✅ 纯虚函数，子类必须实现 */</span>
<span class="hl-k">virtual</span> <span class="hl-k">void</span> <span class="hl-f">attack</span>() = <span class="hl-n">0</span>;</pre></div>

<h4>错误 4 · 用 <code>.</code> 去访问指针指向的对象</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre>Player p;
Player *ptr = &amp;p;

ptr.<span class="hl-f">show</span>();      <span class="hl-c">/* ❌ 指针要用 -&gt; */</span>
ptr-&gt;<span class="hl-f">show</span>();     <span class="hl-c">/* ✅ */</span>
(*ptr).<span class="hl-f">show</span>();  <span class="hl-c">/* ✅ 也合法，但没人这么写 */</span></pre></div>
<p><b>记法：对象用 <code>.</code>，指针用 <code>-&gt;</code>。</b>
（第四讲讲过，<code>ptr-&gt;show()</code> 就等价于 <code>(*ptr).show()</code>）</p>

<h4>错误 5 · 忘了构造函数导致成员没初始化</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-k">class</span> Player {
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
};</pre></div>

<h4>错误 6 · 数组或容器里放对象，却用了接口指针</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 接口不能直接当元素（它是抽象类型，造不出对象） */</span>
GameCharacter list[<span class="hl-n">3</span>];

<span class="hl-c">/* ✅ 存指针（或引用） */</span>
GameCharacter *list[<span class="hl-n">3</span>] = { &amp;a, &amp;m, &amp;k };</pre></div>

<!-- ============================================================ -->
<h2 id="s10"><span class="n">10</span>一页速查</h2>

<table>
<thead><tr><th style="width:38%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>定义一个纯数据类型</td><td class="c">struct Point { int x; int y; };</td></tr>
<tr><td>定义带保护的对象</td><td class="c">class Player { private: ... public: ... };</td></tr>
<tr><td>声明一个对象</td><td class="c">Player p;</td></tr>
<tr><td>用构造函数初始化</td><td class="c">Player p("Archer", 100);</td></tr>
<tr><td>访问成员</td><td class="c">p.hp&nbsp;&nbsp;/&nbsp;&nbsp;p.show()</td></tr>
<tr><td>通过指针访问</td><td class="c">ptr-&gt;hp&nbsp;&nbsp;/&nbsp;&nbsp;ptr-&gt;show()</td></tr>
<tr><td>对象数组</td><td class="c">Player team[3];</td></tr>
<tr><td>私有成员</td><td class="c">private:  （只有类内函数能用）</td></tr>
<tr><td>公开成员</td><td class="c">public:   （外面能调用）</td></tr>
<tr><td>只读访问私有数据</td><td class="c">int getHp() { return hp; }</td></tr>
<tr><td>构造函数</td><td class="c">Player(string n, int h) { ... }</td></tr>
<tr><td>析构函数</td><td class="c">~Player() { ... }</td></tr>
<tr><td>定义接口</td><td class="c">virtual void attack() = 0;</td></tr>
<tr><td>实现接口</td><td class="c">class Archer : public GameCharacter { ... }</td></tr>
<tr><td>标记重写</td><td class="c">void attack() override { ... }</td></tr>
<tr><td>用接口统一调用</td><td class="c">GameCharacter *c = &amp;a; c-&gt;attack();</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">本讲要记住的六句话</div>
  <ol>
    <li><b><code>struct</code> / <code>class</code> 把「同一个东西的数据」打包成一个新类型</b>，
      不再用平行数组。</li>
    <li><b>成员函数写在类里面</b>，数据和操作放在一起。</li>
    <li><b><code>private</code> 保护数据</b>，只留 <code>public</code> 的函数当出口 ——
      规矩写在一处，外面绕不过去。</li>
    <li><b><code>struct</code> 与 <code>class</code> 只差默认权限</b>：
      struct 默认 public，class 默认 private。</li>
    <li><b>接口用纯虚函数 <code>= 0</code> 定义</b>，只规定「必须会做什么」。</li>
    <li><b>依赖接口而非具体类</b>，加新角色不用改旧代码。</li>
  </ol>
</div>

<div class="card note">
  <div class="card-t">下一讲预告</div>
  <p>这一讲里反复出现了两种调用方式：</p>
  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">void</span> <span class="hl-f">takeDamage</span>(Player &amp;p, <span class="hl-k">int</span> dmg);   <span class="hl-c">/* 引用 */</span>
<span class="hl-k">void</span> <span class="hl-f">takeDamage</span>(Player *p, <span class="hl-k">int</span> dmg);   <span class="hl-c">/* 指针 */</span></pre>
  <p>两者都能改到外面的对象，但写法不一样：一个用 <code>.</code>，
  一个用 <code>-&gt;</code>；一个调用时不用加 <code>&amp;</code>，一个要加。</p>
  <p>下一讲《引用和指针函数》就把这件事彻底讲透：
  <b>引用到底是什么、和指针什么关系、什么时候该用哪个</b>，
  并且会讲到「函数指针」这种把函数当参数传的用法。</p>
</div>

<footer>
UME 项目组内部教程 · 第六讲《类、结构体》<br>
代码示例均以 <b>Consolas</b> 等宽字体呈现；文中所有「运行结果」与「编译错误」
均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。
</footer>

</main>
</div>

@@SCRIPTS@@
</body>
</html>
"""

out6 = (HTML06.replace("@@CSS@@", CSS)
              .replace("@@EXTRA@@", EXTRA_COMMON)
              .replace("@@SCRIPTS@@", SCRIPTS))
dest6 = os.path.join(ROOT, "_ds_06_类、结构体.html")
with io.open(dest6, "w", encoding="utf-8", newline="") as fh:
    fh.write(out6)

print("已生成: %s" % os.path.basename(dest6))
print("  字符数 %d | 代码块 %d | 输出块 %d | 按钮 %d"
      % (len(out6), out6.count('class="code-wrap"'),
         out6.count('class="out-wrap"'), out6.count('class="cp"')))
