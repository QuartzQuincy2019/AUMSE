# -*- coding: utf-8 -*-
"""生成 _ds_08_F03_编译与链接、头文件与库.html"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from tut import build

EXTRA = """
/* 编译流程 */
.pipe{display:flex;flex-wrap:wrap;margin:18px 0;align-items:stretch}
.pipe .st{
  flex:1 1 130px;border:1px solid var(--line-2);border-radius:10px;padding:11px 13px;
  background:#fff;position:relative;transition:box-shadow .15s,transform .15s,border-color .15s;
}
.pipe .st:hover{box-shadow:0 6px 18px rgba(30,45,70,.12);transform:translateY(-2px);
  border-color:var(--blue)}
.pipe .st+.st{margin-left:26px}
.pipe .st+.st::before{
  content:"→";position:absolute;left:-20px;top:50%;transform:translateY(-50%);
  color:var(--fg-3);font-size:16px;font-family:var(--mono);
}
.pipe .st .n{font-weight:700;font-size:13.5px;margin-bottom:3px;color:var(--blue)}
.pipe .st .d{font-size:12px;color:var(--fg-3);line-height:1.55}
.pipe .st .io{font-family:var(--mono);font-size:11.5px;color:var(--fg-2);margin-top:6px}
@media(max-width:700px){
  .pipe{display:block}
  .pipe .st+.st{margin:22px 0 0}
  .pipe .st+.st::before{content:"↓";left:50%;top:-20px;transform:translateX(-50%)}
}
/* 三段对照 */
.stages{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:13px;margin:16px 0}
.stages .c{border:1px solid var(--line-2);border-radius:11px;padding:12px 14px;background:#fff;
  transition:box-shadow .16s,transform .16s}
.stages .c:hover{box-shadow:0 6px 18px rgba(30,45,70,.12);transform:translateY(-2px)}
.stages .c .h{font-weight:700;font-size:14px;margin-bottom:6px}
.stages .c.p1 .h{color:var(--violet)}
.stages .c.p2 .h{color:var(--blue)}
.stages .c.p3 .h{color:var(--green)}
.stages .c .note{font-size:12.5px;color:var(--fg-3);line-height:1.65}
"""

TOC = """  <a href="#s1">1 · 从源码到程序的三步</a>
  <a href="#s2">2 · 预处理：<code>#include</code> 做了什么</a>
  <a href="#s3">3 · 编译：各自翻译</a>
  <a href="#s4">4 · 链接：拼起来</a>
  <a href="#s5">5 · 头文件为什么存在</a>
  <a href="#s6">6 · 三种错误怎么分</a>
  <a href="#s7">7 · 库</a>
  <a href="#s8">8 · 实际编译命令</a>"""

BODY = r"""<h1>编译与链接、头文件与库</h1>
<p class="sub-title">UME 项目组内部教程 · 08-F03（File）· 与本项目施行密切相关</p>
<p>
  <span class="tag">已学：cmd / 路径与宏</span>
  <span class="tag b">本讲：那一行 g++ 到底做了什么</span>
</p>

<div class="card note">
  <div class="card-t">为什么这一篇对本项目重要</div>
  <p>你敲的每一行编译命令背后都有三步。
  <b>分成哪三步、每步会报什么错</b> —— 搞清楚这个，
  编译报错就不再是天书，而是「一眼能定位」的信息。</p>
  <p>本文里所有报错信息都是<b>真实编译出来的</b>（g++ 13.1.0）。</p>
</div>

<!-- ============================================================ -->
<h2 id="s1"><span class="n">1</span>从源码到程序的三步</h2>

<p>你写的是 <code>main.cpp</code>，最后得到的是 <code>main.exe</code>。
中间发生了三件事：</p>

<div class="pipe">
  <div class="st">
    <div class="n">① 预处理</div>
    <div class="d">处理所有 <code>#</code> 开头的行：
      展开宏、把 <code>#include</code> 的文件内容粘进来</div>
    <div class="io">main.cpp → main.i</div>
  </div>
  <div class="st">
    <div class="n">② 编译</div>
    <div class="d">把 C++ 翻译成机器指令，
      但地址还没填</div>
    <div class="io">main.i → main.o</div>
  </div>
  <div class="st">
    <div class="n">③ 链接</div>
    <div class="d">把多个 <code>.o</code> 和库
      <b>拼成一个 exe</b>，填好地址</div>
    <div class="io">main.o → main.exe</div>
  </div>
</div>

<p>平时一句 <code>g++ main.cpp -o main.exe</code> 就把三步都做完了。
但<b>报错发生在哪一步，含义完全不同</b> —— 这就是本篇的核心。</p>

<!-- ============================================================ -->
<h2 id="s2"><span class="n">2</span>预处理：<code>#include</code> 做了什么</h2>

<p><code>#include</code> <b>不是「引用」，而是「把那个文件的内容原样粘到这里」</b>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">include 是文字替换</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 你写的 */</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>() { <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"hi"</span>; }

<span class="hl-c">/* 预处理之后，等价于（几万行） */</span>
<span class="hl-c">/* ...iostream 的全部内容粘在这里... */</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>() { <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"hi"</span>; }</pre></div>

<div class="card tip">
  <div class="card-t">想亲眼看？</div>
  <p>用 <code>-E</code> 让 g++ <b>只做预处理就停</b>：</p>
  <div class="term">
    <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
      <span>查看预处理结果</span></div>
<pre><span class="pr">E:\demo&gt;</span><span class="cmd">g++ -E main.cpp -o main.i</span>
<span class="pr">E:\demo&gt;</span><span class="cmd">dir main.i</span>
<span class="out">main.i    1,234,567 字节     ← 一个 10 行的源文件变成 100 多万字节</span></pre>
  </div>
  <p>这就是为什么 <code>#include</code> 太多会拖慢编译。</p>
</div>

<h4><code>&lt;&gt;</code> 和 <code>""</code> 的区别</h4>
<table>
<thead><tr><th style="width:30%">写法</th><th>去哪里找</th><th>用途</th></tr></thead>
<tbody>
<tr><td class="c">#include &lt;iostream&gt;</td>
    <td>系统头文件目录</td><td>标准库、第三方库</td></tr>
<tr><td class="c">#include "my.h"</td>
    <td><b>先找当前目录</b>，再找系统目录</td><td><b>自己写的头文件</b></td></tr>
</tbody>
</table>

<p>找不到头文件时报的是<b>预处理期错误</b>：</p>

<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>nohdr.cpp:1:10: fatal error: no_such_header_xyz.h: No such file or directory</pre></div>

<p>看到 <code>fatal error: ... No such file or directory</code>，
就知道是<b>找文件找不到</b>，而不是代码写错了 ——
先检查路径、拼写、有没有把目录加进搜索路径（<code>-I</code>）。</p>

<!-- ============================================================ -->
<h2 id="s3"><span class="n">3</span>编译：各自翻译</h2>

<p>这一步把 C++ 变成机器指令，但<b>只处理一个文件</b>。
输出是 <code>.o</code>（目标文件）：里面机器指令写好了，
但「调用了别人的函数」这些地址<b>还空着</b>。</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>只编译，不链接</span></div>
<pre><span class="pr">E:\demo&gt;</span><span class="cmd">g++ -c main.cpp -o main.o</span>
<span class="warn">（-c 表示 compile only，到这里就停）</span>
<span class="pr">E:\demo&gt;</span><span class="cmd">dir /b</span>
<span class="out">main.cpp</span>
<span class="out">main.o        ← 中间产物</span></pre>
</div>

<p>这一步报的错是<b>代码本身的错</b>：语法、类型不匹配、
变量没声明、函数参数不对……</p>

<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>syn.cpp:1:22: error: expected primary-expression before ';' token
    1 | int main() { int x = ; return 0; }
      |                      ^</pre></div>

<p><code>error: expected ... before ';' token</code> 的意思是
「在 <code>;</code> 之前缺少了点什么」——
<b>编译器能精确指到列号</b>，照着改就行。</p>

<!-- ============================================================ -->
<h2 id="s4"><span class="n">4</span>链接：拼起来</h2>

<p>把多个 <code>.o</code> 和用到的库拼成一个 exe，同时<b>把地址填好</b>。</p>

<p>问题来了：如果你<b>声明</b>了一个函数却忘了<b>定义</b>它，
编译期看不出来（有声明就够编过了），到了链接期才发现
「这个函数根本没实现」：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">只有声明，没有定义</span><span class="cp">复制</span></div><pre><span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b);      <span class="hl-c">/* 声明了，但没人实现它 */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">add</span>(<span class="hl-n">1</span>, <span class="hl-n">2</span>) &lt;&lt; <span class="hl-f">endl</span>;   <span class="hl-c">/* 编译能过，链接会失败 */</span>
}</pre></div>

<div class="out-wrap"><div class="cap">真实报错（已核对）</div><pre>ld.exe: lk1.cpp:(.text+0x18): undefined reference to `add(int, int)'
collect2.exe: error: ld returned 1 exit status</pre></div>

<div class="card key">
  <div class="card-t">认出链接错误的关键字</div>
  <p>看到下面这些词，就是<b>链接期</b>问题，不是代码语法问题：</p>
  <ul>
    <li><code>undefined reference to ...</code> —— <b>找不到实现</b></li>
    <li><code>multiple definition of ...</code> —— 同一个东西定义了多次</li>
    <li><code>ld.exe</code> / <code>collect2.exe</code> —— 链接器在报错</li>
  </ul>
  <p>而编译期错误长这样：<code>error: expected ...</code>、
  <code>error: 'x' was not declared</code>。</p>
</div>

<h4>常见的 <code>undefined reference</code> 原因</h4>
<table>
<thead><tr><th style="width:44%">原因</th><th>解决</th></tr></thead>
<tbody>
<tr><td>忘把实现所在的 <code>.cpp</code> 加进编译命令</td>
    <td>把它一起写上，或用构建系统管理</td></tr>
<tr><td>函数名拼写不一致（声明和定义不同）</td>
    <td>对一下两边签名</td></tr>
<tr><td>声明在 <code>namespace</code> 里，定义不在（或反过来）</td>
    <td>名字必须完全一致，包括命名空间</td></tr>
<tr><td>忘了链接某个库</td>
    <td>加 <code>-l</code> 参数，见第 7 节</td></tr>
<tr><td>C/C++ 混编没写 <code>extern "C"</code></td>
    <td>C++ 会对函数名做修饰，C 不会</td></tr>
</tbody>
</table>

<!-- ============================================================ -->
<h2 id="s5"><span class="n">5</span>头文件为什么存在</h2>

<p>既然 <code>#include</code> 就是粘贴，那为什么不直接把代码都写一个文件里？</p>

<p>假设有两个 <code>.cpp</code>，<code>main.cpp</code> 想用
<code>tools.cpp</code> 里的 <code>add</code>：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">没有头文件时的困境</span><span class="cp">复制</span></div><pre><span class="hl-c">/* main.cpp —— 编译 main.cpp 时，编译器不知道 add 长什么样 */</span>
<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-f">add</span>(<span class="hl-n">1</span>, <span class="hl-n">2</span>);        <span class="hl-c">/* ❌ 编译器：add 是什么？ */</span>
}

<span class="hl-c">/* tools.cpp —— 定义在这里，但编译 main.cpp 时看不到它 */</span>
<span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) { <span class="hl-k">return</span> a + b; }</pre></div>

<p><b>每个 <code>.cpp</code> 是独立编译的</b>，编译器不会自动去看别的文件。
所以需要把「这个函数长什么样」<b>抄一份</b>给每个用它的文件 ——
这份「抄件」就是<b>头文件</b>。</p>

<div class="stages">
  <div class="c p1">
    <div class="h">tools.h（头文件）</div>
    <div class="note">
      <b>只写声明</b>：告诉别人「有这么个函数，长这样」<br><br>
      <code>int add(int a, int b);</code>
    </div>
  </div>
  <div class="c p2">
    <div class="h">tools.cpp（实现）</div>
    <div class="note">
      <b>写定义</b>：真正怎么做<br><br>
      <code>#include "tools.h"</code><br>
      <code>int add(int a,int b){ return a+b; }</code>
    </div>
  </div>
  <div class="c p3">
    <div class="h">main.cpp（使用）</div>
    <div class="note">
      <b>包含头文件</b>，就有声明可用了<br><br>
      <code>#include "tools.h"</code><br>
      <code>cout &lt;&lt; add(1,2);</code>
    </div>
  </div>
</div>

<div class="card key">
  <div class="card-t">头文件的核心规则</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:26%"></th><th>放哪里</th></tr></thead>
  <tbody>
  <tr><td><b>函数声明</b></td><td class="c">头文件（.h）</td></tr>
  <tr><td><b>函数定义</b>（函数体）</td><td class="c"><b>.cpp 文件</b></td></tr>
  <tr><td><b>类 / 结构体的定义</b></td><td class="c">头文件（成员函数可以只写声明）</td></tr>
  <tr><td><b>常量</b></td><td class="c">头文件里用 <code>const</code> 或 <code>constexpr</code></td></tr>
  <tr><td><b>全局变量</b></td><td class="c">头文件写 <code>extern</code>，<b>某一个</b> .cpp 里定义</td></tr>
  </tbody></table>
</div>

<h4>为什么头文件里不能随便写函数体</h4>
<p>因为 <code>#include</code> 是粘贴。如果头文件里写了函数体，
被两个 <code>.cpp</code> 包含，那这个函数就<b>被定义了两遍</b> ——
链接时报 <code>multiple definition</code>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* tools.h */</span>
<span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) { <span class="hl-k">return</span> a + b; }   <span class="hl-c">/* ❌ 被两个 .cpp 包含就重复定义 */</span>

<span class="hl-c">/* ✅ 头文件里只写声明 */</span>
<span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b);

<span class="hl-c">/* ✅ 例外：加 inline 可以放头文件（多个定义会被合并） */</span>
<span class="hl-k">inline</span> <span class="hl-k">int</span> <span class="hl-f">add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) { <span class="hl-k">return</span> a + b; }</pre></div>

<h4>头文件的第一行和最后一行</h4>
<p>同一个头文件可能被间接包含多次（<code>a.h</code> 包含 <code>b.h</code>，
<code>main.cpp</code> 两个都包含）。这会导致「同一个类定义了两遍」。
所以每个头文件都要加保护：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">include guard</span><span class="cp">复制</span></div><pre><span class="hl-p">#ifndef</span> UME_TOOLS_H          <span class="hl-c">/* 如果没定义过这个名字 */</span>
<span class="hl-p">#define</span> UME_TOOLS_H          <span class="hl-c">/* 那就定义它 */</span>

<span class="hl-c">/* ... 头文件真正的全部内容 ... */</span>

<span class="hl-p">#endif</span>                       <span class="hl-c">/* 结束 */</span></pre></div>

<p>或者更省事地写一行：<code>#pragma once</code>（几乎所有编译器都支持）。
<b>两种任选一种，但每个头文件都必须有。</b></p>

<!-- ============================================================ -->
<h2 id="s6"><span class="n">6</span>三种错误怎么分</h2>

<p>这一节是全篇最实用的部分。看报错信息里的关键字，就能判断问题在哪一步：</p>

<table>
<thead><tr>
  <th style="width:16%">阶段</th><th style="width:34%">典型关键字</th><th>说明</th>
</tr></thead>
<tbody>
<tr><td><b>预处理</b></td>
    <td class="c">fatal error: xxx.h: No such file or directory</td>
    <td>找不到文件。<b>检查路径、拼写、<code>-I</code> 目录</b></td></tr>
<tr><td><b>编译</b></td>
    <td class="c">error: expected ...<br>error: 'x' was not declared<br>error: no matching function</td>
    <td>代码本身有问题。<b>看行号列号去改</b></td></tr>
<tr><td><b>链接</b></td>
    <td class="c">undefined reference to ...<br>multiple definition of ...<br>ld returned 1 exit status</td>
    <td>找不到实现 / 重复定义。<b>检查源文件是否都加进来了、头文件里有没有写函数体</b></td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">一个实用的排查顺序</div>
  <ol>
    <li>先看<b>有几个错误</b>。如果几百个，通常只有<b>第一个</b>是真的 ——
      它把后面的都带崩了。先只改第一个。</li>
    <li>看是<b>哪一步</b>（上表）。预处理错先查文件路径。</li>
    <li>如果是链接错，第一反应是：<b>我是不是漏了某个 .cpp？</b></li>
    <li>从<b>最上面那一条</b>开始改，改完重新编译再看。</li>
  </ol>
</div>

<!-- ============================================================ -->
<h2 id="s7"><span class="n">7</span>库</h2>

<p><b>库就是「别人写好、编译好的一堆 .o 的打包」</b>，
提供现成的函数给你用，省得自己写。</p>

<table>
<thead><tr><th style="width:24%">类型</th><th style="width:20%">Windows 后缀</th><th>特点</th></tr></thead>
<tbody>
<tr><td><b>静态库</b></td><td class="c">.a / .lib</td>
    <td>链接时把用到的代码<b>复制进 exe</b>。
      exe 变大，但<b>不依赖外部文件</b></td></tr>
<tr><td><b>动态库</b></td><td class="c">.dll</td>
    <td>代码<b>留在 dll 里</b>，exe 运行时才加载。
      exe 小，但<b>必须带着 dll</b></td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">这就是「换个电脑就打不开」的原因</div>
  <p>如果 exe 依赖某个 <code>.dll</code>，而目标电脑上没有它，
  程序会<b>启动即失败</b>，弹一句「找不到 xxx.dll」。</p>
  <p>用 MinGW 编译的 Qt 程序尤其常见：需要
  <code>libstdc++-6.dll</code>、<code>libgcc_s_seh-1.dll</code>、
  <code>libwinpthread-1.dll</code> 以及一堆 Qt 的 dll。</p>
  <p><b>解决办法</b>：用 <code>windeployqt</code> 自动把需要的 dll
  拷到 exe 旁边；或者用静态链接把它们打进 exe。</p>
</div>

<h4>怎么告诉编译器用哪个库</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>链接库的两类参数</span></div>
<pre><span class="pr">E:\demo&gt;</span><span class="cmd">g++ main.cpp -L C:\libs\mylib\lib -l mylib -o main.exe</span>
<span class="warn">              ↑ 库在哪（-L 大写）        ↑ 用哪个库（-l 小写）</span></pre>
</div>

<table>
<thead><tr><th style="width:20%">参数</th><th>含义</th><th style="width:32%">例子</th></tr></thead>
<tbody>
<tr><td class="c">-I 目录</td><td>去哪找<b>头文件</b>（大写 i）</td><td class="c">-I C:\libs\mylib\include</td></tr>
<tr><td class="c">-L 目录</td><td>去哪找<b>库文件</b></td><td class="c">-L C:\libs\mylib\lib</td></tr>
<tr><td class="c">-l 名字</td><td>链接哪个库（小写 L）</td><td class="c">-l mylib</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">大写 I、大写 L、小写 l 别弄混</div>
  <p>记法：<b>大写对应「大东西」（目录），小写对应「小东西」（库名）</b>。</p>
  <ul>
    <li><code>-I</code>（大写 i）= include 目录</li>
    <li><code>-L</code> = library 目录</li>
    <li><code>-l</code>（小写 L）= 具体哪个 library</li>
  </ul>
</div>

<!-- ============================================================ -->
<h2 id="s8"><span class="n">8</span>实际编译命令</h2>

<p>把常用的参数列一下，够用了：</p>

<table>
<thead><tr><th style="width:30%">参数</th><th>作用</th></tr></thead>
<tbody>
<tr><td class="c">-o 文件名</td><td>指定输出的 exe 名字</td></tr>
<tr><td class="c">-std=c++17</td><td>用哪个 C++ 标准</td></tr>
<tr><td class="c">-c</td><td>只编译不链接，产生 <code>.o</code></td></tr>
<tr><td class="c">-E</td><td>只预处理，产生 <code>.i</code></td></tr>
<tr><td class="c">-Wall</td><td><b>打开常用警告</b> —— 强烈建议always 加</td></tr>
<tr><td class="c">-g</td><td>带调试信息（能下断点、看变量）</td></tr>
<tr><td class="c">-O2</td><td>优化（发布版用；调试时别加，会打乱行号）</td></tr>
<tr><td class="c">-I / -L / -l</td><td>头文件目录 / 库目录 / 库名</td></tr>
</tbody>
</table>

<h4>单文件</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>编译一个源文件</span></div>
<pre><span class="pr">E:\demo&gt;</span><span class="cmd">g++ -std=c++17 -Wall main.cpp -o main.exe</span>
<span class="pr">E:\demo&gt;</span><span class="cmd">.\main.exe</span></pre>
</div>

<h4>多文件</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>一次把多个源文件都写上</span></div>
<pre><span class="pr">E:\demo&gt;</span><span class="cmd">g++ -std=c++17 -Wall main.cpp tools.cpp font.cpp -o ume.exe</span>
<span class="warn">（文件多的时候，手敲不现实 —— 这就是构建系统存在的原因）</span></pre>
</div>

<h4>分步做（看清中间产物）</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>分三步，每步都能单独检查</span></div>
<pre><span class="pr">E:\demo&gt;</span><span class="cmd">g++ -std=c++17 -Wall -c main.cpp -o main.o</span>
<span class="pr">E:\demo&gt;</span><span class="cmd">g++ -std=c++17 -Wall -c tools.cpp -o tools.o</span>
<span class="pr">E:\demo&gt;</span><span class="cmd">g++ main.o tools.o -o ume.exe</span>
<span class="out">（第三步只做链接，报错就一定是链接问题）</span></pre>
</div>

<div class="card key">
  <div class="card-t">为什么需要「构建系统」</div>
  <p>文件一多，「哪些 <code>.cpp</code> 要编、改了一个要不要全重编」
  手工管不过来。构建系统（<code>make</code>、CMake、qmake）替你管这些：
  <b>只重编改动过的文件，并把链接命令拼对</b>。</p>
  <p>Qt 项目通常用 <code>.pro</code> 文件（qmake）或
  <code>CMakeLists.txt</code>，里面写的就是「有哪些源文件、要链接哪些库」。</p>
</div>

<div class="card key">
  <div class="card-t">这一篇要记住的五件事</div>
  <ol>
    <li><b>编译器做三步：预处理 → 编译 → 链接</b>。</li>
    <li><b><code>#include</code> 是「把文件内容粘进来」</b>，
      所以头文件里写函数体会导致重复定义。</li>
    <li><b>每个头文件都要有 include guard</b>（或 <code>#pragma once</code>）。</li>
    <li><b><code>undefined reference</code> 是链接错</b> ——
      第一反应是「漏了某个 .cpp 或某个库」。</li>
    <li><b>编译时永远加 <code>-Wall</code></b>，让编译器把可疑的地方都说出来。</li>
  </ol>
</div>

<div class="card note">
  <div class="card-t">下一步</div>
  <p>语言部分到这里就完整了。接下来是两篇收尾：</p>
  <ul>
    <li><b>09《vector 和 array》</b> —— C++ 标准库里的「数组」，
      比裸数组安全得多，实际项目里基本都用它。</li>
    <li><b>09-F04《Unicode 和编码》</b> ——
      直接关系到本项目：为什么 <code>char</code> 处理不了蒙文。</li>
  </ul>
</div>

<footer>
UME 项目组内部教程 · 08-F03（File）《编译与链接、头文件与库》<br>
文中所有报错信息均使用 g++ 13.1.0 实际编译产生；代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

build("_ds_08_F03_编译与链接、头文件与库.html", "实用 · 编译与链接、头文件与库", TOC, BODY, EXTRA)
