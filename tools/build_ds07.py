# -*- coding: utf-8 -*-
"""生成 _ds_07_作用域、全局与局部变量.html"""
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

EXTRA = """
/* 作用域嵌套示意（像俄罗斯套娃） */
.scopes{margin:18px 0}
.scopes .lv{
  border:1px solid var(--line-2);border-radius:10px;padding:12px 14px;background:#fff;
  transition:box-shadow .16s,border-color .16s;
}
.scopes .lv:hover{box-shadow:0 5px 18px rgba(30,45,70,.11)}
.scopes .lv .hd{font-weight:650;font-size:13.5px;margin-bottom:8px;display:flex;
  align-items:center;gap:8px;flex-wrap:wrap}
.scopes .lv .hd .mono{font-family:var(--mono);font-size:12.5px;background:#f2f4f8;
  border:1px solid var(--line);border-radius:5px;padding:1px 7px;color:var(--fg-2)}
.scopes .lv.l0{border-color:#cfe0fb;background:var(--blue-soft)}
.scopes .lv.l1{border-color:#ded0f7;background:var(--violet-soft);margin:10px 0 0 18px}
.scopes .lv.l2{border-color:#c6e6d3;background:var(--green-soft);margin:10px 0 0 18px}
.scopes .lv .vars{display:flex;gap:8px;flex-wrap:wrap}
.scopes .lv .v{
  font-family:var(--mono);font-size:12.5px;background:#fff;border:1px solid var(--line-2);
  border-radius:6px;padding:3px 9px;transition:transform .14s,box-shadow .14s;
}
.scopes .lv .v:hover{transform:translateY(-2px);box-shadow:0 4px 10px rgba(30,45,70,.14)}
.scopes .note{font-size:12.5px;color:var(--fg-3);margin-top:8px;line-height:1.6}
@media(max-width:560px){
  .scopes .lv.l1,.scopes .lv.l2{margin-left:8px}
}

/* 三类变量对照 */
.three{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin:18px 0}
.three .c{
  border:1px solid var(--line-2);border-radius:11px;padding:13px 15px;background:#fff;
  transition:box-shadow .16s,transform .16s,border-color .16s;
}
.three .c:hover{box-shadow:0 6px 18px rgba(30,45,70,.12);transform:translateY(-2px)}
.three .c .h{font-weight:700;font-size:14px;margin-bottom:7px}
.three .c.loc .h{color:var(--green)}
.three .c.glo .h{color:var(--amber)}
.three .c.sta .h{color:var(--violet)}
.three .c .code{font-family:var(--mono);font-size:12.5px;background:#f2f4f8;
  border:1px solid var(--line);border-radius:6px;padding:6px 9px;margin:8px 0;
  color:var(--fg);overflow:auto;white-space:pre}
.three .c .note{font-size:12.5px;color:var(--fg-3);line-height:1.65}
"""

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>C/C++ · 作用域、全局与局部变量</title>
@@CSS@@
<style>@@EXTRA@@</style>
</head>
<body>
<div id="shell">

<nav id="toc">
  <h5>目录</h5>
  <a href="#s1">1 · 一个名字能活在哪</a>
  <a href="#s2">2 · 块作用域</a>
  <a href="#s3">3 · for / if 里的变量</a>
  <a href="#s4">4 · 函数参数也是局部的</a>
  <div class="sep"></div>
  <a href="#s5">5 · 全局变量</a>
  <a href="#s5a" class="sub">5.1 写法与可见性</a>
  <a href="#s5b" class="sub">5.2 它为什么危险</a>
  <a href="#s5c" class="sub">5.3 什么时候才该用</a>
  <a href="#s6">6 · static 局部变量</a>
  <a href="#s7">7 · 同名遮蔽</a>
  <a href="#s8">8 · 作用域 ≠ 生存期</a>
  <a href="#s9">9 · 常见错误</a>
  <a href="#s10">10 · 一页速查</a>
</nav>

<main>
<h1>作用域、全局与局部变量</h1>
<p class="sub-title">UME 项目组内部教程 · 第七讲 · 面向零编程基础成员</p>
<p>
  <span class="tag">已学：数组 / 函数 / 指针</span>
  <span class="tag">已学：类与结构体</span>
  <span class="tag b">本讲：一个名字能被谁看见</span>
</p>

<div class="card note">
  <div class="card-t">这一讲回答三个「为什么」</div>
  <ul>
    <li>为什么 <code>for (int i = 0; ...)</code> 里的 <code>i</code>
      出了循环就用不了？</li>
    <li>为什么两个函数里可以有同名变量，而它们互不影响？</li>
    <li>全局变量到处能用，为什么老程序员都劝你少用？</li>
  </ul>
  <p>答案都在同一个概念里：<b>作用域</b> ——
  一个名字在哪些地方能被看见。文中所有「运行结果」与「编译错误」
  均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。</p>
</div>

<!-- ============================================================ -->
<h2 id="s1"><span class="n">1</span>一个名字能活在哪</h2>

<p>先看一个现象。<b>同一个名字在三个地方各写一遍，它们互不相干：</b></p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三个毫不相干的 n</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">void</span> <span class="hl-f">f</span>() {
    <span class="hl-k">int</span> n = <span class="hl-n">100</span>;          <span class="hl-c">/* 这个 n 属于 f */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"f 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;
}

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-k">int</span> n = <span class="hl-n">1</span>;            <span class="hl-c">/* 这个 n 属于 main */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"main 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-f">f</span>();

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"调用 f 之后 main 里的 n 还是 "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>main 里的 n = 1
f 里的 n = 100
调用 f 之后 main 里的 n 还是 1</pre></div>

<p><code>f</code> 里的 <code>n</code> 改成 100，<code>main</code> 里的 <code>n</code> 一点没动。
<b>说明它们根本是两个不同的变量</b>，只是碰巧重名。</p>

<div class="card key">
  <div class="card-t">作用域的定义</div>
  <p><b>作用域 = 一个名字能被使用的范围。</b></p>
  <p>出了这个范围，那个名字就「不存在了」——
  不是值变成 0，而是<b>编译器根本不认识这个名字</b>，写了就编译报错。</p>
  <p>所以问题不是「变量在哪」，而是<b>「这个名字在哪些行有效」</b>。</p>
</div>

<!-- ============================================================ -->
<h2 id="s2"><span class="n">2</span>块作用域</h2>

<p>C / C++ 里最基本的规则很简单：</p>

<div class="mnemonic">
  <b>一对花括号 <code>{ }</code> 就是一层作用域。</b><br>
  在里面声明的变量，只活到这对花括号结束。
</div>

<div class="scopes">
  <div class="lv l0">
    <div class="hd">main 函数体 <span class="mono">{ ... }</span></div>
    <div class="vars"><span class="v">int a = 1;</span></div>
    <div class="lv l1">
      <div class="hd">内层块 <span class="mono">{ ... }</span>
        <span style="font-weight:400;color:var(--fg-3);font-size:12.5px">
          能看见 a，也能改 a</span></div>
      <div class="vars"><span class="v">int b = 2;</span></div>
      <div class="lv l2">
        <div class="hd">更内层 <span class="mono">{ ... }</span>
          <span style="font-weight:400;color:var(--fg-3);font-size:12.5px">
            能看见 a、b</span></div>
        <div class="vars"><span class="v">int c = 3;</span></div>
      </div>
      <div class="note">出了最内层，c 就没了；出了这一层，b 也没了。</div>
    </div>
    <div class="note"><b>规律：里面能看见外面，外面看不见里面。</b></div>
  </div>
</div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">块作用域实测</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-k">int</span> a = <span class="hl-n">1</span>;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"外层 a = "</span> &lt;&lt; a &lt;&lt; <span class="hl-f">endl</span>;

    {
        <span class="hl-k">int</span> b = <span class="hl-n">2</span>;              <span class="hl-c">/* 只在这个 {} 里活着 */</span>
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"内层 看得到 a = "</span> &lt;&lt; a
             &lt;&lt; <span class="hl-s">"，b = "</span> &lt;&lt; b &lt;&lt; <span class="hl-f">endl</span>;

        a = <span class="hl-n">99</span>;                   <span class="hl-c">/* 可以改外层 */</span>
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"内层改了 a，a = "</span> &lt;&lt; a &lt;&lt; <span class="hl-f">endl</span>;
    }

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"出了内层，a = "</span> &lt;&lt; a &lt;&lt; <span class="hl-s">"（改动保留）"</span> &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-c">/* cout &lt;&lt; b;   ← 取消注释就报错：b 已经不在了 */</span>
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>外层 a = 1
内层 看得到 a = 1，b = 2
内层改了 a，a = 99
出了内层，a = 99（改动保留）</pre></div>

<p>注意两件事：</p>
<ul>
  <li><b>里面能改外面的变量</b>（<code>a</code> 变成 99，出了内层还是 99）。</li>
  <li><b>外面的那个 <code>b</code> 用不了</b>。如果硬写，编译器会说：</li>
</ul>

<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'b' was not declared in this scope
    7 |     std::cout &lt;&lt; b &lt;&lt; std::endl;
      |                  ^</pre></div>

<p><code>was not declared in this scope</code> 直译就是
<b>「这个名字在本作用域里没有声明」</b>。以后看到这句报错，
第一反应应该是：<b>我是不是在块外面用了块里面的变量？</b></p>

<!-- ============================================================ -->
<h2 id="s3"><span class="n">3</span>for / if 里的变量</h2>

<p><code>for</code> 和 <code>if</code> 的圆括号 / 花括号同样构成一层作用域。
这解释了那个最常见的问题。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">循环变量只活在循环里</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; <span class="hl-n">3</span>; i++) {
        <span class="hl-k">int</span> t = i * <span class="hl-n">10</span>;
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"i="</span> &lt;&lt; i &lt;&lt; <span class="hl-s">" t="</span> &lt;&lt; t &lt;&lt; <span class="hl-f">endl</span>;
    }
    <span class="hl-c">/* cout &lt;&lt; i;   ← 报错：i 已经不在了 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"循环结束后 i 和 t 都不存在了"</span> &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-k">if</span> (<span class="hl-k">true</span>) {
        <span class="hl-k">int</span> only = <span class="hl-n">5</span>;
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"if 块里的 only = "</span> &lt;&lt; only &lt;&lt; <span class="hl-f">endl</span>;
    }
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"if 块结束后 only 也不存在了"</span> &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-c">/* 同名不冲突：第二个循环可以再用 i */</span>
    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">100</span>; i &lt; <span class="hl-n">102</span>; i++) {
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"第二个循环 i = "</span> &lt;&lt; i &lt;&lt; <span class="hl-f">endl</span>;
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>i=0 t=0
i=1 t=10
i=2 t=20
循环结束后 i 和 t 都不存在了
if 块里的 only = 5
if 块结束后 only 也不存在了
第二个循环 i = 100
第二个循环 i = 101</pre></div>

<p>硬要在循环外用 <code>i</code>，编译器会说：</p>
<div class="out-wrap"><div class="cap">编译器的真实报错（已核对）</div><pre>error: 'i' was not declared in this scope
    5 |     std::cout &lt;&lt; i &lt;&lt; std::endl;
      |                  ^</pre></div>

<div class="card tip">
  <div class="card-t">为什么这个设计是好事</div>
  <p>你可以在每个 <code>for</code> 里都写 <code>int i</code>，
  <b>不用担心名字撞车</b> —— 它们各在各的循环里，互不干扰。</p>
  <p>如果循环变量能跑到循环外面，写十个循环就得想十个不同的名字，
  而且很容易误用上一次残留的值。作用域把这类麻烦直接消除了。</p>
</div>

<!-- ============================================================ -->
<h2 id="s4"><span class="n">4</span>函数参数也是局部的</h2>

<p>函数的<b>形参</b>也是这个函数的局部变量，出了函数就没了。
所以「改形参改不到外面」这件事，从作用域角度看是很自然的。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">形参只属于这个函数</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">void</span> <span class="hl-f">f</span>(<span class="hl-k">int</span> n) {              <span class="hl-c">/* n 只属于 f */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  f 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;
    n = <span class="hl-n">999</span>;                 <span class="hl-c">/* 改的是 f 自己的 n */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  f 里改过之后 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;
}

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-k">int</span> n = <span class="hl-n">5</span>;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"main 里的 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-f">f</span>(n);                    <span class="hl-c">/* 传进去的是 n 的值（副本） */</span>

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"调用 f 之后 main 里的 n = "</span> &lt;&lt; n
         &lt;&lt; <span class="hl-s">"（没变）"</span> &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>main 里的 n = 5
  f 里的 n = 5
  f 里改过之后 n = 999
调用 f 之后 main 里的 n = 5（没变）</pre></div>

<p>两个 <code>n</code> 同名，但是<b>两个不同作用域里的两个变量</b>。
这也把第四讲「值传递传的是副本」从另一个角度解释通了。</p>

<!-- ============================================================ -->
<h2 id="s5"><span class="n">5</span>全局变量</h2>

<h3 id="s5a">5.1 写法与可见性</h3>

<p>写在<b>所有函数外面</b>的变量就是全局变量。它的作用域是
<b>从声明处到文件结束</b>，期间所有函数都能用。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">全局变量</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">int</span> gCount = <span class="hl-n">0</span>;             <span class="hl-c">/* 全局：写在函数外面 */</span>

<span class="hl-k">void</span> <span class="hl-f">bump</span>()  { gCount++; }
<span class="hl-k">void</span> <span class="hl-f">reset</span>() { gCount = <span class="hl-n">0</span>; }

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"开始 gCount = "</span> &lt;&lt; gCount &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-f">bump</span>(); <span class="hl-f">bump</span>(); <span class="hl-f">bump</span>();
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"调用 bump 三次后 gCount = "</span> &lt;&lt; gCount &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-f">reset</span>();
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"reset 之后 gCount = "</span> &lt;&lt; gCount &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>开始 gCount = 0
调用 bump 三次后 gCount = 3
reset 之后 gCount = 0</pre></div>

<p>全局变量的特点：<b>不用传参，哪个函数都能直接读写。</b>
看起来很省事 —— 这正是它的陷阱。</p>

<h3 id="s5b">5.2 它为什么危险</h3>

<div class="card warn">
  <div class="card-t">三个真实问题</div>
  <ol>
    <li><b>谁改的查不出来。</b>如果 <code>gCount</code> 突然变成奇怪的值，
      你得翻遍整个文件找哪一行写了它。<b>局部变量就不会有这个问题</b> ——
      只有那一个函数碰得到。</li>
    <li><b>函数变得「不老实」。</b>一个只依赖参数的函数，
      给同样的输入必然给同样的输出。但一旦它偷偷读全局变量，
      同样的输入可能给出不同结果 —— 你没法单独测它。</li>
    <li><b>名字容易被撞。</b>全局变量在整个文件都可见，
      任何函数里的局部变量都得小心别重名（重名会「遮蔽」，见第 7 节）。</li>
  </ol>
</div>

<h4>一个具体例子</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">全局状态让函数难以理解</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> gHp = <span class="hl-n">100</span>;                 <span class="hl-c">/* 全局血量 */</span>

<span class="hl-k">void</span> <span class="hl-f">hit</span>() { gHp -= <span class="hl-n">10</span>; }      <span class="hl-c">/* 谁调用它，谁就在改全局 */</span>

<span class="hl-c">/* 一个月后你看到这一行： */</span>
<span class="hl-f">hit</span>();

<span class="hl-c">/* 问题：gHp 现在是多少？要看之前 hit() 被调用过几次。
   而「被调用过几次」这件事，散落在整个程序里。 */</span></pre></div>

<div class="card tip">
  <div class="card-t">更好的写法</div>
  <p>把状态<b>收进对象</b>（第六讲的类），让「谁的状态」一目了然：</p>
  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">class</span> Player {
<span class="hl-k">private</span>:
    <span class="hl-k">int</span> hp = <span class="hl-n">100</span>;
<span class="hl-k">public</span>:
    <span class="hl-k">void</span> <span class="hl-f">hit</span>() { hp -= <span class="hl-n">10</span>; }
};

Player p;        <span class="hl-c">/* 看这一行：p.hp 是多少，只与 p 有关 */</span>
p.<span class="hl-f">hit</span>();</pre>
  <p>这样「状态属于谁」写得清清楚楚，也不需要满程序找谁改过它。</p>
</div>

<h3 id="s5c">5.3 什么时候才该用</h3>

<p>不是不能用，而是<b>要有理由</b>。</p>

<table>
<thead><tr><th style="width:44%">场景</th><th>建议</th></tr></thead>
<tbody>
<tr><td>需要在多个函数间共享数据</td>
    <td><span class="tag r">先别用全局</span> 优先用「传参 + 返回值」，
      或收进类里</td></tr>
<tr><td>函数需要返回多个结果</td>
    <td><span class="tag r">先别用全局</span> 用第四讲的指针参数</td></tr>
<tr><td>数据很大、拷贝代价高，又不想改</td>
    <td><span class="tag r">先别用全局</span> 用 <code>const</code> 引用传参</td></tr>
<tr><td>整个程序唯一的配置 / 常量</td>
    <td><span class="tag g">可以用</span> 例如版本号、开关，
      <b>建议加 <code>const</code></b></td></tr>
<tr><td>程序运行期间的唯一状态（如程序是否该退出）</td>
    <td><span class="tag g">谨慎用</span> 但要在注释里写清谁负责改</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">一句话原则</div>
  <p><b>能用局部变量解决，就不要用全局变量。</b></p>
  <p>变量的作用域越窄，你需要在心里同时记住的东西就越少，
  出错的机会也就越少。</p>
</div>

<!-- ============================================================ -->
<h2 id="s6"><span class="n">6</span>static 局部变量</h2>

<p>局部变量前面加 <code>static</code>，会得到一个很特别的东西：
<b>作用域还是局部的（只有这个函数能看见），但活得和全局变量一样久
（程序结束才消失）。</b></p>

<div class="three">
  <div class="c loc">
    <div class="h">普通局部变量</div>
    <div class="code">void f() {
    int n = 0;
    n++;
}</div>
    <div class="note">每次调用都<b>重新初始化</b>为 0。
      上次的值不保留。</div>
  </div>
  <div class="c sta">
    <div class="h">static 局部变量</div>
    <div class="code">void f() {
    static int n = 0;
    n++;
}</div>
    <div class="note"><b>只初始化一次</b>，之后一直保留上次的值。</div>
  </div>
  <div class="c glo">
    <div class="h">全局变量</div>
    <div class="code">int n = 0;

void f() { n++; }</div>
    <div class="note">值也保留，但<b>任何函数都能碰它</b>。</div>
  </div>
</div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比实测</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">void</span> <span class="hl-f">normalCounter</span>() {
    <span class="hl-k">int</span> n = <span class="hl-n">0</span>;              <span class="hl-c">/* 每次进来都重新变成 0 */</span>
    n++;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  普通局部   n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;
}

<span class="hl-k">void</span> <span class="hl-f">staticCounter</span>() {
    <span class="hl-k">static</span> <span class="hl-k">int</span> n = <span class="hl-n">0</span>;       <span class="hl-c">/* 只初始化一次，之后一直留着 */</span>
    n++;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  static局部 n = "</span> &lt;&lt; n &lt;&lt; <span class="hl-f">endl</span>;
}

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; <span class="hl-n">3</span>; i++) {
        <span class="hl-f">normalCounter</span>();
        <span class="hl-f">staticCounter</span>();
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>  普通局部   n = 1
  static局部 n = 1
  普通局部   n = 1
  static局部 n = 2
  普通局部   n = 1
  static局部 n = 3</pre></div>

<p>普通局部每次都打印 1，<code>static</code> 那个一路涨到 3。</p>

<div class="card tip">
  <div class="card-t">static 局部变量适合什么</div>
  <ul>
    <li><b>计数器</b>：「这个函数被调用过几次」。</li>
    <li><b>缓存</b>：算过一次的昂贵结果留着下次用。</li>
  </ul>
  <p>它比全局变量安全，因为<b>只有这个函数能碰它</b>。
  但也要注意：它会让函数<b>记住状态</b>，
  同样的输入可能得到不同结果 —— 用之前想清楚这是不是你要的。</p>
</div>

<!-- ============================================================ -->
<h2 id="s7"><span class="n">7</span>同名遮蔽</h2>

<p>如果内层声明了一个和外层同名的变量，会发生什么？
答案是<b>内层的把外层的「遮住」了</b>（术语叫遮蔽 / shadowing）。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">一层层遮住</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">int</span> value = <span class="hl-n">100</span>;              <span class="hl-c">/* 全局 */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"全局 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-k">int</span> value = <span class="hl-n">20</span>;            <span class="hl-c">/* 局部把全局遮住了 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"局部 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;

    {
        <span class="hl-k">int</span> value = <span class="hl-n">3</span>;         <span class="hl-c">/* 又遮一层 */</span>
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"最内层 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;
    }

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"出了内层 value = "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl;

    <span class="hl-c">/* 用 :: 访问被遮住的全局变量 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"::value = "</span> &lt;&lt; ::value &lt;&lt; <span class="hl-f">endl</span>;

    ::value = <span class="hl-n">555</span>;              <span class="hl-c">/* 改的是全局那个 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"::value = 555 之后，全局 value = "</span> &lt;&lt; ::value &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"局部 value 还是 "</span> &lt;&lt; value &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>全局 value = 100
局部 value = 20
最内层 value = 3
出了内层 value = 20
::value = 100
::value = 555 之后，全局 value = 555
局部 value 还是 20</pre></div>

<p>规律很清楚：<b>就近优先</b> ——
用名字时找「最近的那一层」，一层层往外找，找到就停。</p>

<h4><code>::</code> 是干什么的</h4>
<p><code>::value</code> 表示「<b>全局作用域里的 value</b>」，
用它可以绕过所有局部变量，直接指名全局那个。</p>

<table>
<thead><tr><th style="width:34%">写法</th><th>指的是</th></tr></thead>
<tbody>
<tr><td class="c">value</td><td>就近的那个（可能是局部）</td></tr>
<tr><td class="c">::value</td><td><b>全局</b>那个，不管中间遮了多少层</td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">遮蔽是把双刃剑</div>
  <p><b>好处：</b>内层想用个临时变量叫 <code>i</code>，不用管外面有没有叫 <code>i</code> 的。</p>
  <p><b>坏处：</b>如果你本来想改外层变量，却手滑写了一句
  <code>int value = 20;</code>（多了 <code>int</code>），
  那就变成了<b>新建一个局部变量</b>，外层的完全没动 ——
  而且编译器不会警告你。</p>
  <pre style="background:#fdeceb;border:1px solid #f0c8c2;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">int</span> total = <span class="hl-n">0</span>;
<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; n; i++) {
    <span class="hl-k">int</span> total = total + a[i];   <span class="hl-c">/* ❌ 多了 int：新建了一个局部 total，</span>
<span class="hl-c">                                    外面的 total 一直是 0 */</span>
}</pre>
  <p><b>习惯：不要故意给内层变量起和外层一样的名字。</b>
  报错还好，最怕的是它悄悄编过、结果错了。</p>
</div>

<!-- ============================================================ -->
<h2 id="s8"><span class="n">8</span>作用域 ≠ 生存期</h2>

<p>最后澄清一个容易混的点。这两个词是<b>两件事</b>：</p>

<table>
<thead><tr><th style="width:20%">概念</th><th>说的是</th><th style="width:34%">回答的问题</th></tr></thead>
<tbody>
<tr><td><b>作用域</b></td><td>名字在<b>代码里</b>哪个范围可见</td>
    <td>「我在这一行能不能写出这个名字？」</td></tr>
<tr><td><b>生存期</b></td><td>变量在<b>运行时</b>什么时候存在</td>
    <td>「这块内存什么时候被回收？」</td></tr>
</tbody>
</table>

<p><code>static</code> 局部变量就是「作用域窄、生存期长」的典型：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">名字出不去，但变量一直在</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-c">/* 返回引用：让调用者能碰到那个 static 变量 */</span>
<span class="hl-k">int</span> &amp;<span class="hl-f">makeStatic</span>() {
    <span class="hl-k">static</span> <span class="hl-k">int</span> keep = <span class="hl-n">42</span>;     <span class="hl-c">/* 名字只在函数内可见 */</span>
    <span class="hl-k">return</span> keep;               <span class="hl-c">/* 但它活到程序结束 */</span>
}

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"第一次读: "</span> &lt;&lt; <span class="hl-f">makeStatic</span>() &lt;&lt; <span class="hl-f">endl</span>;

    <span class="hl-f">makeStatic</span>() = <span class="hl-n">77</span>;         <span class="hl-c">/* 还能改它 */</span>
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"改成 77 后再读: "</span> &lt;&lt; <span class="hl-f">makeStatic</span>() &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>第一次读: 42
改成 77 后再读: 77</pre></div>

<p>在 <code>main</code> 里你<b>写不出 <code>keep</code> 这个名字</b>（作用域不在这里），
可是通过函数返回的引用，你确实碰到了<b>同一个变量</b>，而且改了它
（生存期还在）。</p>

<div class="card key">
  <div class="card-t">对比着记</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:30%">变量种类</th><th>作用域</th><th>生存期</th></tr></thead>
  <tbody>
  <tr><td>块内局部变量</td><td>那一对 <code>{ }</code> 内</td><td>出了块就结束</td></tr>
  <tr><td>函数形参</td><td>那个函数内</td><td>函数返回就结束</td></tr>
  <tr><td>全局变量</td><td>整个文件（声明之后）</td><td>整个程序</td></tr>
  <tr><td><code>static</code> 局部</td><td><b>那个函数内</b></td><td><b>整个程序</b></td></tr>
  <tr><td>堆内存（<code>malloc</code>）</td><td>看指针在谁手里</td><td>直到 <code>free</code></td></tr>
  </tbody></table>
  <p style="margin-top:10px">最后一行值得留意：<b>堆内存的生存期和任何作用域都无关</b> ——
  第五讲说过，它活到你 <code>free</code> 为止。</p>
</div>

<!-- ============================================================ -->
<h2 id="s9"><span class="n">9</span>常见错误</h2>

<h4>错误 1 · 在块外面用块内的变量</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre>{
    <span class="hl-k">int</span> b = <span class="hl-n">2</span>;
}
<span class="hl-f">cout</span> &lt;&lt; b;         <span class="hl-c">/* ❌ error: 'b' was not declared in this scope */</span>

<span class="hl-c">/* ✅ 要么把声明提到外面 */</span>
<span class="hl-k">int</span> b = <span class="hl-n">0</span>;
{
    b = <span class="hl-n">2</span>;
}
<span class="hl-f">cout</span> &lt;&lt; b;         <span class="hl-c">/* ✅ */</span></pre></div>

<h4>错误 2 · 在循环外面用循环变量</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; n; i++) { <span class="hl-c">/* ... */</span> }
<span class="hl-f">cout</span> &lt;&lt; i;         <span class="hl-c">/* ❌ i 已经不在了 */</span>

<span class="hl-c">/* ✅ 需要在循环后用，就把 i 声明到循环外面 */</span>
<span class="hl-k">int</span> i;
<span class="hl-k">for</span> (i = <span class="hl-n">0</span>; i &lt; n; i++) { <span class="hl-c">/* ... */</span> }
<span class="hl-f">cout</span> &lt;&lt; i;         <span class="hl-c">/* ✅ */</span></pre></div>

<h4>错误 3 · 手滑多写 <code>int</code>，变成新的局部变量</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> total = <span class="hl-n">0</span>;
<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; n; i++) {
    <span class="hl-k">int</span> total = total + a[i];   <span class="hl-c">/* ❌ 新建了局部 total */</span>
}

<span class="hl-k">int</span> total = <span class="hl-n">0</span>;
<span class="hl-k">for</span> (<span class="hl-k">int</span> i = <span class="hl-n">0</span>; i &lt; n; i++) {
    total = total + a[i];       <span class="hl-c">/* ✅ 没有 int，改的是外面那个 */</span>
}</pre></div>
<p><b>这个错误最阴险</b>：编译器不报错，程序也照跑，只是结果不对。</p>

<h4>错误 4 · 用全局变量在函数间「偷偷」传数据</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 靠全局传结果：看不出 f 和 g 有依赖 */</span>
<span class="hl-k">int</span> gResult;
<span class="hl-k">void</span> <span class="hl-f">f</span>() { gResult = <span class="hl-n">42</span>; }
<span class="hl-k">void</span> <span class="hl-f">g</span>() { <span class="hl-f">cout</span> &lt;&lt; gResult; }   <span class="hl-c">/* 必须 f 先调用过才对 */</span>

<span class="hl-c">/* ✅ 靠返回值 / 参数：依赖关系写在明面上 */</span>
<span class="hl-k">int</span>  <span class="hl-f">f</span>() { <span class="hl-k">return</span> <span class="hl-n">42</span>; }
<span class="hl-k">void</span> <span class="hl-f">g</span>(<span class="hl-k">int</span> v) { <span class="hl-f">cout</span> &lt;&lt; v; }</pre></div>

<h4>错误 5 · 在头文件里定义全局变量</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* tool.h */</span>
<span class="hl-k">int</span> gCount = <span class="hl-n">0</span>;      <span class="hl-c">/* ❌ 被多个 .cpp 包含时会重复定义 */</span>

<span class="hl-c">/* ✅ 头文件里只写声明 */</span>
<span class="hl-k">extern</span> <span class="hl-k">int</span> gCount;   <span class="hl-c">/* 声明：有这么个东西 */</span>
<span class="hl-c">/* 然后在某一个 .cpp 里定义：int gCount = 0; */</span></pre></div>
<p>关于头文件与链接，第 08-F03 讲会专门讲。</p>

<!-- ============================================================ -->
<h2 id="s10"><span class="n">10</span>一页速查</h2>

<table>
<thead><tr><th style="width:40%">想做的事</th><th>写法 / 说明</th></tr></thead>
<tbody>
<tr><td>只在块里用的小变量</td><td class="c">在 { } 里声明</td></tr>
<tr><td>循环变量</td><td class="c">for (int i = 0; ...) 只活在循环里</td></tr>
<tr><td>循环后还要用</td><td class="c">把 i 声明到循环外面</td></tr>
<tr><td>函数自己用的变量</td><td class="c">在函数里声明（局部）</td></tr>
<tr><td>形参</td><td class="c">void f(int n) —— n 只属于 f</td></tr>
<tr><td>多个函数共享</td><td class="c">优先传参 + 返回值，别急着用全局</td></tr>
<tr><td>全局变量</td><td class="c">写在所有函数外面</td></tr>
<tr><td>全局常量</td><td class="c">const int kMax = 100;</td></tr>
<tr><td>跨文件共享</td><td class="c">头文件写 extern，某一个 .cpp 里定义</td></tr>
<tr><td>函数间保留值的局部变量</td><td class="c">static int n = 0;</td></tr>
<tr><td>函数被调用了几次</td><td class="c">static 局部计数器</td></tr>
<tr><td>指名被遮住的全局</td><td class="c">::value</td></tr>
<tr><td>判断「名字能不能用」</td><td>看它是否在当前 <code>{ }</code> 或外层 <code>{ }</code> 里</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">本讲要记住的五句话</div>
  <ol>
    <li><b>一对 <code>{ }</code> 就是一层作用域</b>，里面能看见外面，外面看不见里面。</li>
    <li><b>作用域是「名字在哪几行有效」，生存期是「变量在运行时活多久」</b> ——
      两件事，<code>static</code> 局部就是「窄作用域 + 长生存期」。</li>
    <li><b>能用局部变量解决，就不要用全局变量。</b>作用域越窄，越不容易出错。</li>
    <li><b>就近优先</b>：同名时用最近的那一层；<code>::</code> 可以指名全局。</li>
    <li><b>不要故意给内层起和外层一样的名字</b>，
      尤其别手滑多写一个 <code>int</code> —— 那种错编译器不拦。</li>
  </ol>
</div>

<div class="card note">
  <div class="card-t">下一讲预告</div>
  <p>这一讲解决的是「名字」。下一讲回到数据本身，讲一件在 C 里绕不开的事：
  <b>字符串</b>。</p>
  <p>你可能已经注意到，C 里表示一串文字用的是 <code>char</code> 数组
  （第五讲里就出现过 <code>malloc(sizeof(char) * (len + 1))</code>）。
  那个 <b><code>+ 1</code></b> 是干什么的？
  为什么字符串比较不能用 <code>==</code>？
  为什么 <code>strcpy</code> 老被说「不安全」？</p>
  <p>下一讲《C 风格字符串》把这些讲清楚 ——
  它是后面读文件、处理路径、写编辑器都躲不开的基础。</p>
</div>

<footer>
UME 项目组内部教程 · 第七讲《作用域、全局与局部变量》<br>
代码示例均以 <b>Consolas</b> 等宽字体呈现；文中所有「运行结果」与「编译错误」
均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。
</footer>

</main>
</div>

@@SCRIPTS@@
</body>
</html>
"""

out = (HTML.replace("@@CSS@@", CSS)
           .replace("@@EXTRA@@", EXTRA)
           .replace("@@SCRIPTS@@", SCRIPTS))
dest = os.path.join(ROOT, "_ds_07_作用域、全局与局部变量.html")
with io.open(dest, "w", encoding="utf-8", newline="") as fh:
    fh.write(out)

print("已生成: %s" % os.path.basename(dest))
print("  字符数 %d | 代码块 %d | 输出块 %d | 按钮 %d | 表格 %d"
      % (len(out), out.count('class="code-wrap"'), out.count('class="out-wrap"'),
         out.count('class="cp"'), out.count("<table")))
