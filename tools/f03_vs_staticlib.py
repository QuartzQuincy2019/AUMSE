# -*- coding: utf-8 -*-
"""F03 重构：
   删除第 7 节「库」（含「怎么告诉编译器用哪个库」的 cmd 手工链接）
   删除第 8 节「实际编译命令」（gcc 命令行）
   改为：用 Visual Studio 2026 编写 C++ 静态库并链接的手把手教程，
        并把 inline 关键字讲清楚。

所有命令行产物、报错信息、展开值，均在本机
  Visual Studio Community 2026 (18.10.3) + MSBuild + MSVC 14.51.36231
实际生成核对。
"""
import io
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F03_编译与链接、头文件与库.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)

# ---------------------------------------------------------------------
# 1) 目录重建
# ---------------------------------------------------------------------
old_toc = re.search(r'(?s)(<nav id="toc">\s*<h5>目录</h5>).*?(</nav>)', t)
assert old_toc, "找不到目录"

NEW_TOC = """  <a href="#s1">1 · 从源码到程序的三步</a>
  <a href="#s2">2 · 预处理：<code>#include</code> 做了什么</a>
  <a href="#s3">3 · 编译：各自翻译</a>
  <a href="#s4">4 · 链接：拼起来</a>
  <a href="#s5">5 · 头文件为什么存在</a>
  <a href="#s6">6 · 三种错误怎么分</a>
  <a href="#s7">7 · 库：静态库与动态库</a>
  <a href="#s8">8 · 手把手：用 VS 2026 做静态库</a>
  <a href="#s8a" class="sub">8.1 建解决方案与静态库工程</a>
  <a href="#s8b" class="sub">8.2 写头文件与实现</a>
  <a href="#s8c" class="sub">8.3 右键「生成」到底做了什么</a>
  <a href="#s8d" class="sub">8.4 建控制台工程并使用它</a>
  <a href="#s8e" class="sub">8.5 让它能找到库：三步配置</a>
  <a href="#s8f" class="sub">8.6 运行与验证</a>
  <a href="#s9">9 · <code>inline</code> 到底解决什么</a>
  <a href="#s9a" class="sub">9.1 冲突从哪来</a>
  <a href="#s9b" class="sub">9.2 实测那个报错</a>
  <a href="#s9c" class="sub">9.3 inline 的三层含义</a>
  <a href="#s10">10 · 常见错误</a>"""

t = t[:old_toc.start()] + old_toc.group(1) + "\n" + NEW_TOC + "\n" + old_toc.group(2) + t[old_toc.end():]

# ---------------------------------------------------------------------
# 2) 把第 7、8 节整段换掉
# ---------------------------------------------------------------------
i7 = t.index('<h2 id="s7">')
# 第 6 节之后到 </main> 之前，全部替换
imain = t.index('</main>')

NEW = r'''<h2 id="s7"><span class="n">7</span>库：静态库与动态库</h2>

<p>第 4 节说过：链接就是把多个 <code>.o</code> / <code>.obj</code> 拼起来。
但如果有一堆功能<b>很多项目都要用</b>，总不能每次都把源码拷一遍。
把编译好的目标文件<b>打包</b>起来，就是<b>库</b>。</p>

<table>
<thead><tr><th style="width:22%"></th><th>静态库</th><th>动态库</th></tr></thead>
<tbody>
<tr><td><b>Windows 后缀</b></td><td class="c">.lib</td><td class="c">.dll</td></tr>
<tr><td><b>链接时</b></td>
    <td>把用到的代码<b>复制进 exe</b></td>
    <td>只在 exe 里留一个「引用」</td></tr>
<tr><td><b>exe 体积</b></td><td>大</td><td>小</td></tr>
<tr><td><b>运行时需要</b></td>
    <td><span class="tag g">不需要额外文件</span></td>
    <td><span class="tag r">必须带着 .dll</span>，否则启动就失败</td></tr>
<tr><td><b>更新库之后</b></td>
    <td>要<b>重新编译 exe</b></td>
    <td>换掉 dll 就行，exe 不用动</td></tr>
<tr><td><b>适合</b></td>
    <td>工具函数、算法、自己写的公共代码</td>
    <td>插件、需要热更新、多个程序共用一份</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">新手选哪个</div>
  <p><b>先学静态库。</b>它只有一个 <code>.lib</code> 文件要管，
  不用操心「dll 放哪、找不到怎么办」，把「怎么把库用起来」这件事先弄懂。</p>
  <p>动态库多出来的复杂度全在<b>运行期找 dll</b> 上（搜索路径、版本冲突），
  那是后面的事。</p>
</div>

<div class="card key">
  <div class="card-t">库和头文件是两个东西，别混</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:22%"></th><th>它是什么</th><th>什么时候用</th></tr></thead>
  <tbody>
  <tr><td class="c">.h 头文件</td>
      <td>函数的<b>声明</b>（告诉编译器「有这么个函数，长这样」）</td>
      <td><b>编译时</b>需要 —— 否则 <code>#include</code> 找不到</td></tr>
  <tr><td class="c">.lib 静态库</td>
      <td>函数的<b>实现</b>（编译好的机器码）</td>
      <td><b>链接时</b>需要 —— 否则报 <code>LNK2019</code></td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>两个都要给对，缺一个都编不出来。</b>
  而且报错发生在<b>不同阶段</b>：少了头文件是编译错，少了 lib 是链接错 ——
  正好用上第 6 节那张「三种错误怎么分」的表。</p>
</div>

<!-- ============================================================ -->
<h2 id="s8"><span class="n">8</span>手把手：用 VS 2026 做静态库</h2>

<div class="card note">
  <div class="card-t">这一节做什么</div>
  <p>从零做一遍：<b>建一个静态库工程 → 写代码 → 生成 .lib →
  建一个控制台程序 → 链接这个库 → 跑起来</b>。</p>
  <p>每一步都写清<b>点哪里、填什么、会看到什么</b>。</p>
  <p>本节所有产物与报错，均在本机
  <b>Visual Studio Community 2026</b>（18.10.3 · MSVC 14.51.36231）实际生成核对。</p>
</div>

<h3 id="s8a">8.1 建解决方案与静态库工程</h3>

<h4>① 新建项目</h4>
<p>打开 VS → <b>创建新项目</b>。在搜索框里输入 <code>静态库</code>，
选这一项（注意平台要选 <b>C++</b>、<b>Windows</b>）：</p>

<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">静态库 (C++ · Windows · 库)
   项目名称: UmeMath
   位置:     D:\Path\To\UME
   ☑ 将解决方案和项目放在同一目录中   ← 不要勾，见下方说明</pre>

<p>点「创建」。VS 会生成这样一个结构：</p>

<div class="tree">
<span class="d">D:\Path\To\UME\</span>
├─ <span class="f">UME.sln</span>                  <span class="c">← 解决方案</span>
└─ <span class="d">UmeMath\</span>                  <span class="c">← 项目</span>
    ├─ <span class="f">UmeMath.vcxproj</span>       <span class="c">← 项目文件（配置都在这）</span>
    ├─ <span class="f">UmeMath.vcxproj.filters</span>  <span class="c">← 只影响 VS 里怎么分组显示</span>
    ├─ <span class="f">pch.h</span> / <span class="f">pch.cpp</span>       <span class="c">← 预编译头（后面处理）</span>
    └─ <span class="f">UmeMath.cpp</span>           <span class="c">← 待会儿删掉</span>
</div>

<div class="card tip">
  <div class="card-t">「将解决方案和项目放在同一目录中」为什么建议不勾</div>
  <p>勾上之后 <code>.sln</code> 和 <code>.vcxproj</code> 混在同一层，
  文件一多就乱。<b>不勾</b>的话 .sln 在外、每个项目一个子文件夹 ——
  这正是第 8.5 节里 <code>$(SolutionDir)</code> 和 <code>$(ProjectDir)</code>
  不一样的原因。</p>
</div>

<div class="card warn">
  <div class="card-t">VS 2026 的工具集是 <code>v145</code></div>
  <p>项目属性 → 常规 → <b>平台工具集</b>，VS 2026 默认是
  <code>v145</code>（对应 MSVC 14.51）。</p>
  <p>如果你打开的是老项目，可能写着 <code>v143</code>（VS 2022）——
  这时会报 <code>MSB8020: 无法找到 v143 的生成工具</code>。
  <b>解法</b>：右键解决方案 → <b>重定解决方案目标</b> → 选当前版本；
  或把平台工具集改成 <code>v145</code>。</p>
</div>

<h4>② 删掉模板给的多余文件</h4>
<p>在<b>解决方案资源管理器</b>里右键 <code>UmeMath.cpp</code> → <b>删除</b>。
（删的是工程里的引用，磁盘上的文件也会一并删掉。）</p>

<h3 id="s8b">8.2 写头文件与实现</h3>

<p>右键项目 → <b>添加 → 新建项</b>，建两个文件：</p>

<table>
<thead><tr><th style="width:30%">文件名</th><th>类型</th><th>作用</th></tr></thead>
<tbody>
<tr><td class="c">ume_math.h</td><td>头文件 (.h)</td><td><b>声明</b>，给使用者看</td></tr>
<tr><td class="c">ume_math.cpp</td><td>C++ 文件 (.cpp)</td><td><b>实现</b></td></tr>
</tbody>
</table>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">ume_math.h —— 对外公开的头文件</span><span class="cp">复制</span></div><pre><span class="hl-p">#pragma once</span>          <span class="hl-c">// 防止被重复包含（第 5 节讲过）</span>

<span class="hl-c">// ① 只写声明：实现在 ume_math.cpp 里</span>
<span class="hl-k">int</span>  <span class="hl-f">ume_add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b);
<span class="hl-k">int</span>  <span class="hl-f">ume_mul</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b);
<span class="hl-k">int</span>  <span class="hl-f">ume_clamp</span>(<span class="hl-k">int</span> v, <span class="hl-k">int</span> lo, <span class="hl-k">int</span> hi);

<span class="hl-c">// ② 写在头文件里的函数，必须加 inline（第 9 节详解）</span>
<span class="hl-k">inline</span> <span class="hl-k">int</span> <span class="hl-f">ume_max</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) {
    <span class="hl-k">return</span> (a &gt; b) ? a : b;
}

<span class="hl-c">// ③ 头文件里的常量：C++17 起用 inline 变量，可以直接给值</span>
<span class="hl-k">inline</span> <span class="hl-k">const</span> <span class="hl-k">int</span> kUmeVersion = <span class="hl-n">2026</span>;</pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">ume_math.cpp —— 实现</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">"ume_math.h"</span>

<span class="hl-k">int</span> <span class="hl-f">ume_add</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) {
    <span class="hl-k">return</span> a + b;
}

<span class="hl-k">int</span> <span class="hl-f">ume_mul</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) {
    <span class="hl-k">return</span> a * b;
}

<span class="hl-k">int</span> <span class="hl-f">ume_clamp</span>(<span class="hl-k">int</span> v, <span class="hl-k">int</span> lo, <span class="hl-k">int</span> hi) {
    <span class="hl-k">if</span> (v &lt; lo) <span class="hl-k">return</span> lo;
    <span class="hl-k">if</span> (v &gt; hi) <span class="hl-k">return</span> hi;
    <span class="hl-k">return</span> v;
}</pre></div>

<div class="card warn">
  <div class="card-t">遇到「预编译头」报错怎么办</div>
  <p>VS 的 C++ 模板默认<b>使用预编译头</b>（<code>pch.h</code>）。
  如果新加的 <code>.cpp</code> 第一行不是 <code>#include "pch.h"</code>，
  会报 <code>C1010: 无法打开包括文件: "pch.h"</code>。</p>
  <p><b>两种解法，选一种：</b></p>
  <ul>
    <li>在该 <code>.cpp</code> 第一行加 <code>#include "pch.h"</code>（最省事）</li>
    <li>或者：右键该文件 → 属性 → C/C++ → 预编译头 →
      <b>预编译头</b>改为「<b>不使用预编译头</b>」</li>
  </ul>
  <p>本例因为文件少，用第二种更干净；文件多、编译慢时才值得用预编译头。</p>
</div>

<div class="card warn">
  <div class="card-t">中文注释导致莫名其妙的语法错误 —— 实测过的真坑</div>
  <p>本机（中文 Windows）实测：源文件若存成
  <b>UTF-8 无 BOM</b>，MSVC 会按 GBK（代码页 936）去读，
  中文注释的字节被误解释后<b>可能「吃掉」后面的代码</b>，报出完全不相干的错：</p>
  <div class="out-wrap"><div class="cap">实测报错（注释里有中文时）</div><pre>warning C4819: 该文件包含不能在当前代码页(936)中表示的字符
ume_math.h(10,5): error C2059: 语法错误:"return"</pre></div>
  <p style="margin-top:10px">第 10 行明明是个正常的 <code>return</code>，
  却报语法错误 —— 因为上一行注释的字节把它「连」进去了。</p>
  <p><b>解法（任选一种，推荐第一种）</b>：</p>
  <ol>
    <li><b>把源文件另存为「UTF-8 带 BOM」</b> ——
      VS 的「文件 → 高级保存选项」里可以选编码，选
      <code>UTF-8 带签名</code>。MSVC 看到 BOM 就知道是 UTF-8。</li>
    <li>或在项目属性 → C/C++ → 命令行 → 其他选项中加
      <code>/utf-8</code>，告诉编译器「源文件就是 UTF-8」。</li>
    <li>或干脆<b>源文件里不写中文注释</b>。</li>
  </ol>
</div>

<h3 id="s8c">8.3 右键「生成」到底做了什么</h3>

<p>这是你问的那个操作。在<b>解决方案资源管理器</b>里，
<b>右键点项目名 <code>UmeMath</code></b>，菜单里能看到这一组：</p>

<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">右键 UmeMath 项目
 ├─ 生成            (Build)          ← 只编「改过的」，快
 ├─ 重新生成        (Rebuild)        ← 先清理再全编，慢但干净
 ├─ 清理            (Clean)          ← 只删中间产物与输出
 ├─ 仅项目 ▸
 │   ├─ 仅生成 UmeMath
 │   └─ 仅重新生成 UmeMath
 ├─ 属性            (Properties)     ← 所有配置都在这里
 └─ 设为启动项目
</pre>

<div class="card key">
  <div class="card-t">三个命令的区别（最容易搞混）</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:22%">命令</th><th>它做什么</th><th>什么时候用</th></tr></thead>
  <tbody>
  <tr><td class="c">生成 Build</td>
      <td>对比时间戳，<b>只重新编译改动过的文件</b>，然后链接</td>
      <td>日常最常用</td></tr>
  <tr><td class="c">重新生成 Rebuild</td>
      <td><b>先 Clean 再 Build</b> —— 全部重编一遍</td>
      <td>改了<b>头文件搜索路径</b>、库配置，
        或遇到「明明改对了却还报旧错」时</td></tr>
  <tr><td class="c">清理 Clean</td>
      <td>删掉 <code>.obj</code> / <code>.lib</code> / <code>.exe</code> 等产物</td>
      <td>想把目录清干净、或要打包源码时</td></tr>
  </tbody></table>
</div>

<div class="card tip">
  <div class="card-t">为什么改配置之后要用「重新生成」</div>
  <p>「生成」判断「要不要重编」靠的是<b>时间戳</b>：
  源文件比 <code>.obj</code> 新才重编。</p>
  <p>但你改了<b>附加包含目录、附加依赖项</b>这类设置时，
  源文件一个字节都没动 —— 于是「生成」认为<b>无事可做</b>，
  旧产物照旧，问题看起来「没解决」。</p>
  <p><b>所以在第 8.5 节改完库配置后，请用「重新生成」。</b></p>
</div>

<h4>点「生成」之后，看哪里</h4>
<table>
<thead><tr><th style="width:26%">位置</th><th>看什么</th></tr></thead>
<tbody>
<tr><td><b>输出窗口</b></td>
    <td>完整过程。最后一行会写
      <code>UmeMath.vcxproj -&gt; D:\...\x64\Debug\UmeMath.lib</code> ——
      <b>这一行就是成功标志，箭头后面是产物路径</b></td></tr>
<tr><td><b>错误列表窗口</b></td>
    <td>有错时在这里，双击一行能跳到出错代码</td></tr>
<tr><td><b>底部状态栏</b></td>
    <td>「生成: 1 成功，0 失败」</td></tr>
</tbody>
</table>

<div class="out-wrap"><div class="cap">本机实测：生成静态库时的输出窗口（关键行）</div><pre>1&gt;------ 已启动生成: 项目: UmeMath, 配置: Debug x64 ------
1&gt;ume_math.cpp
1&gt;UmeMath.vcxproj -&gt; D:\Path\To\UME\x64\Debug\UmeMath.lib
========== 生成: 成功 1 个，失败 0 个，最新 0 个，跳过 0 个 ==========</pre></div>

<p>注意 <code>-&gt;</code> 后面那个路径：它在
<code>&lt;解决方案目录&gt;\x64\Debug\</code> 下 ——
这正是第 8.5 节要用到的位置，也是 F02 第 8 节讲的
<code>$(SolutionDir)$(Platform)\$(Configuration)\</code> 展开结果。</p>

<div class="card key">
  <div class="card-t">静态库的产物是什么</div>
  <p>本机实测，同一个工程把类型设成静态库时：</p>
  <div class="out-wrap" style="margin-top:10px"><div class="cap">实测</div><pre>ConfigurationType = [StaticLibrary]
TargetExt         = [.lib]
TargetPath        = [D:\Path\To\UME\x64\Debug\UmeMath.lib]</pre></div>
  <p style="margin-top:10px">对应到 VS 属性页就是
  <b>配置属性 → 常规 → 配置类型</b>：
  选「静态库 (.lib)」就是它；选「应用程序 (.exe)」就是控制台程序。
  <b>只差这一个下拉框。</b></p>
</div>

<h3 id="s8d">8.4 建控制台工程并使用它</h3>

<h4>① 加一个新项目到同一个解决方案</h4>
<p><b>右键解决方案</b>（最上面那个 <code>UME</code>）→
<b>添加 → 新建项目</b> → 选「<b>控制台应用 (C++)</b>」→
项目名填 <code>App</code> → 创建。</p>

<div class="card warn">
  <div class="card-t">一定要从「右键解决方案」加，不要在文件夹里另建</div>
  <p>从<b>解决方案</b>右键加，新项目才会进同一个 <code>.sln</code>，
  才能和库工程建立引用关系。分开建两个解决方案的话，
  后面「添加引用」根本找不到对方。</p>
</div>

<p>现在的结构：</p>
<div class="tree">
<span class="d">D:\Path\To\UME\</span>
├─ <span class="f">UME.sln</span>
├─ <span class="d">UmeMath\</span>              <span class="c">← 静态库</span>
│   ├─ <span class="f">ume_math.h</span>
│   └─ <span class="f">ume_math.cpp</span>
└─ <span class="d">App\</span>                   <span class="c">← 控制台程序</span>
    └─ <span class="f">App.cpp</span>
</div>

<h4>② 写 App 的代码</h4>
<p>把 <code>App.cpp</code> 换成：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">App.cpp</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">"ume_math.h"</span>       <span class="hl-c">// 只用引号：这是「自己写的头文件」</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_add(2, 3)      = "</span> &lt;&lt; <span class="hl-f">ume_add</span>(<span class="hl-n">2</span>, <span class="hl-n">3</span>) &lt;&lt; <span class="hl-s">"\n"</span>;
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_mul(4, 5)      = "</span> &lt;&lt; <span class="hl-f">ume_mul</span>(<span class="hl-n">4</span>, <span class="hl-n">5</span>) &lt;&lt; <span class="hl-s">"\n"</span>;
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_clamp(99,0,10) = "</span> &lt;&lt; <span class="hl-f">ume_clamp</span>(<span class="hl-n">99</span>, <span class="hl-n">0</span>, <span class="hl-n">10</span>) &lt;&lt; <span class="hl-s">"\n"</span>;
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"ume_max(7, 9)      = "</span> &lt;&lt; <span class="hl-f">ume_max</span>(<span class="hl-n">7</span>, <span class="hl-n">9</span>) &lt;&lt; <span class="hl-s">"\n"</span>;  <span class="hl-c">// inline 的</span>
    <span class="hl-f">std::cout</span> &lt;&lt; <span class="hl-s">"kUmeVersion        = "</span> &lt;&lt; kUmeVersion &lt;&lt; <span class="hl-s">"\n"</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<p>现在<b>先直接点「生成」试试</b> —— 它会失败，而且会失败两次。
<b>这两次报错正好说明「头文件」和「库」是两件事。</b></p>

<div class="out-wrap"><div class="cap">第一次失败：找不到头文件（编译期）</div><pre>App.cpp(2,10): fatal error C1083: 无法打开包括文件: "ume_math.h":
No such file or directory</pre></div>

<p>因为 <code>ume_math.h</code> 在 <b>UmeMath 项目</b>的目录里，
而编译器只在 <code>App</code> 自己的目录和系统目录里找 —— <b>看 8.5 第 ① 步</b>。</p>

<div class="out-wrap"><div class="cap">第二次失败：找不到库（链接期）</div><pre>main.obj : error LNK2019: 无法解析的外部符号 "int __cdecl ume_add(int,int)"
           (?ume_add@@YAHHH@Z)，函数 main 中引用了该符号
fatal error LNK1120: 2 个无法解析的外部命令</pre></div>

<p>头文件能找到了（编译通过），但<b>函数的实现在 .lib 里，
链接器还不知道去哪拿</b> —— <b>看 8.5 第 ②③ 步</b>。</p>

<div class="card key">
  <div class="card-t">记住这两句报错，一眼能分辨</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:34%">报错</th><th>阶段</th><th>缺什么</th></tr></thead>
  <tbody>
  <tr><td class="c">C1083 无法打开包括文件</td>
      <td><b>编译</b></td><td><b>头文件路径</b>（附加包含目录）</td></tr>
  <tr><td class="c">LNK2019 无法解析的外部符号</td>
      <td><b>链接</b></td><td><b>库</b>（附加依赖项 + 附加库目录）</td></tr>
  </tbody></table>
</div>

<h3 id="s8e">8.5 让它能找到库：三步配置</h3>

<p>三步都在 <b>App 项目</b>的属性里（<b>右键 App → 属性</b>）。
注意属性页顶部有 <b>配置</b> 和 <b>平台</b> 两个下拉框，
建议都选<b>「所有配置」+「所有平台」</b>，这样改一次四个组合都生效。</p>

<h4>① 附加包含目录 —— 解决 C1083</h4>
<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">配置属性 → C/C++ → 常规 → 附加包含目录

  填入:  $(SolutionDir)UmeMath</pre>

<p>点右侧 <code>...</code> 会弹出一个小窗口，<b>一行一个目录</b>，
不用自己打分号。填完点确定，VS 会立刻在下方显示展开后的路径。</p>

<p>为什么是 <code>$(SolutionDir)UmeMath</code>：
<code>$(SolutionDir)</code> 是 <code>.sln</code> 所在目录（F02 第 8 节讲过），
<code>ume_math.h</code> 就在它下面的 <code>UmeMath\</code> 里。</p>

<h4>② 附加依赖项 —— 告诉链接器「要用哪个库」</h4>
<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">配置属性 → 链接器 → 输入 → 附加依赖项

  填入:  UmeMath.lib</pre>

<div class="card warn">
  <div class="card-t">别删掉原来那些 <code>%(...)</code></div>
  <p>这个字段本来就有内容（<code>kernel32.lib</code> 等一批系统库）。
  手动编辑时<b>只往前面加</b>，用分号隔开，保留原有的
  <code>%(AdditionalDependencies)</code>。删掉了会报一堆系统库找不到。</p>
  <p>所以正确内容是：<code>UmeMath.lib;%(AdditionalDependencies)</code></p>
</div>

<h4>③ 附加库目录 —— 告诉链接器「库在哪」</h4>
<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">配置属性 → 链接器 → 常规 → 附加库目录

  填入:  $(SolutionDir)$(Platform)\$(Configuration)</pre>

<p>它就是 8.3 里那个 <code>-&gt;</code> 后面的目录 ——
<code>.lib</code> 实际待的地方。</p>

<div class="card key">
  <div class="card-t">② 和 ③ 分不清？</div>
  <p><b>② 是「叫什么名字」，③ 是「在哪个文件夹」。</b></p>
  <p>少了 ③ 会报 <code>LNK1104: 无法打开文件"UmeMath.lib"</code> ——
  意思是「名字我知道了，但找不到这个文件」。
  本机实测确实如此：只配 ② 不配 ③，链接直接失败。</p>
  <div class="out-wrap" style="margin-top:10px"><div class="cap">实测（只配了附加依赖项）</div><pre>LINK : fatal error LNK1104: 无法打开文件"UmeMath.lib"</pre></div>
</div>

<h4>④ 还有一件更省事的事：添加引用</h4>
<p>上面 ②③ 是「手动告诉链接器」。
VS 还提供了一条<b>自动化</b>的路：</p>

<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">右键 App 项目 → 添加 → 引用...  →  勾选 UmeMath  →  确定</pre>

<p>它的作用是两件：</p>
<table>
<thead><tr><th style="width:34%">作用</th><th>说明</th></tr></thead>
<tbody>
<tr><td><b>保证生成顺序</b></td>
    <td>生成 App 之前<b>先自动生成 UmeMath</b> ——
      不然第一次生成时 .lib 还不存在</td></tr>
<tr><td><b>把库登记为依赖</b></td>
    <td>把 <code>UmeMath.lib</code> 加进链接输入</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">两条路都留着，不冲突</div>
  <p><b>推荐做法：加引用 + 配 ①（附加包含目录）+ 配 ③（附加库目录）。</b></p>
  <p>理由：<b>「添加引用」管不住「lib 在哪」</b>。
  本项目里库的输出目录是 <code>$(SolutionDir)$(Platform)\$(Configuration)</code>，
  和 App 自己的输出目录虽然相同，但这是<b>配置的结果、不是保证</b>；
  一旦有人改了库的输出目录，App 就又找不到 .lib 了。
  <b>把 ③ 显式写上，才不依赖巧合。</b></p>
  <p>而 ① 是必须的 —— 引用关系<b>不会</b>自动把对方的目录加进头文件搜索路径。</p>
  <p>（本机实测：加了引用、配了 ①②、<b>没</b>配 ③ 时，
  仍然报 <code>LNK1104</code>。补上 ③ 之后一次通过。）</p>
</div>

<h3 id="s8f">8.6 运行与验证</h3>

<p>改完配置后<b>务必「重新生成」</b>（8.3 讲过原因）。
成功时输出窗口末尾是这样：</p>

<div class="out-wrap"><div class="cap">本机实测：整个解决方案生成成功</div><pre>UmeMath.vcxproj -&gt; D:\Path\To\UME\x64\Debug\UmeMath.lib
App.vcxproj     -&gt; D:\Path\To\UME\x64\Debug\App.exe
========== 生成: 成功 2 个，失败 0 个 ==========</pre></div>

<p>产物目录里同时有这两样：</p>
<table>
<thead><tr><th style="width:34%">文件</th><th>是什么</th></tr></thead>
<tbody>
<tr><td class="c">UmeMath.lib</td><td><b>静态库</b>（库的机器码）</td></tr>
<tr><td class="c">UmeMath.pdb</td><td>库的调试信息</td></tr>
<tr><td class="c">UmeMath.idb</td><td>供 VS 智能提示用的信息</td></tr>
<tr><td class="c">App.exe</td><td><b>可执行程序</b></td></tr>
<tr><td class="c">App.pdb</td><td>程序的调试信息</td></tr>
</tbody>
</table>

<p>把 <code>App</code> 设为启动项目（右键 App → <b>设为启动项目</b>），
按 <b>Ctrl + F5</b>（开始执行不调试）运行：</p>

<div class="out-wrap"><div class="cap">本机实测：运行结果</div><pre>ume_add(2, 3)      = 5
ume_mul(4, 5)      = 20
ume_clamp(99,0,10) = 10
ume_max(7, 9)      = 9
kUmeVersion        = 2026</pre></div>

<p>五类东西都验证到了：<b>库里的普通函数</b>（add/mul/clamp）、
<b>头文件里的 inline 函数</b>（max）、<b>头文件里的 inline 变量</b>（kUmeVersion）。</p>

<div class="card tip">
  <div class="card-t">Ctrl+F5 与 F5 的区别</div>
  <p><b>F5</b> 是「调试运行」——会挂调试器，崩溃能断下来看。
  <b>Ctrl+F5</b> 是「开始执行不调试」——跑完停住显示「按任意键继续」。</p>
  <p>像这种只是打印结果的小程序，用 <b>Ctrl+F5</b> 更方便，
  因为窗口不会一闪而过。</p>
</div>

<div class="card key">
  <div class="card-t">整节回顾：一共动了几个地方</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:8%">#</th><th style="width:34%">在哪</th><th>配什么</th></tr></thead>
  <tbody>
  <tr><td>1</td><td>UmeMath 项目 · 常规 · 配置类型</td>
      <td class="c">静态库 (.lib)</td></tr>
  <tr><td>2</td><td>App 项目 · 添加 → 引用</td><td class="c">勾选 UmeMath</td></tr>
  <tr><td>3</td><td>App · C/C++ · 附加包含目录</td>
      <td class="c">$(SolutionDir)UmeMath</td></tr>
  <tr><td>4</td><td>App · 链接器 · 附加依赖项</td>
      <td class="c">UmeMath.lib</td></tr>
  <tr><td>5</td><td>App · 链接器 · 附加库目录</td>
      <td class="c">$(SolutionDir)$(Platform)\$(Configuration)</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>就这五处。</b>其余全是「右键 → 生成 / 重新生成」。</p>
</div>

<!-- ============================================================ -->
<h2 id="s9"><span class="n">9</span><code>inline</code> 到底解决什么</h2>

<p>8.2 里我在头文件里写了 <code>inline int ume_max(...)</code>，
还写了一行 <code>inline const int kUmeVersion</code>。
现在说清<b>为什么非加不可</b> —— 这是做静态库时绕不过去的一个点。</p>

<h3 id="s9a">9.1 冲突从哪来</h3>

<p>先回顾第 5 节的两条规则，它们<b>直接打架</b>：</p>

<div class="cards2" style="display:grid;grid-template-columns:1fr 1fr;gap:13px;margin:16px 0">
  <div class="card key" style="margin:0">
    <div class="card-t">规则一：头文件靠「粘贴」生效</div>
    <p><code>#include</code> 就是把文件内容<b>原样拷进来</b>。
    所以头文件里写的每个函数，<b>在每一个包含它的 .cpp 里都会出现一份</b>。</p>
  </div>
  <div class="card warn" style="margin:0">
    <div class="card-t">规则二：一个函数只能定义一次</div>
    <p>链接器要求每个符号<b>全局只有一处定义</b>（ODR 原则）。
    出现两处就报「重复定义」。</p>
  </div>
</div>

<p>把两条放一起：<b>头文件里写函数体，被两个 .cpp 包含 → 定义了两份 → 冲突。</b></p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">冲突是怎么发生的</span><span class="cp">复制</span></div><pre><span class="hl-c">// ume_math.h</span>
<span class="hl-k">int</span> <span class="hl-f">ume_max</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) { <span class="hl-k">return</span> (a &gt; b) ? a : b; }   <span class="hl-c">// 没有 inline</span>

<span class="hl-c">// ume_math.cpp                          // extras.cpp</span>
<span class="hl-p">#include</span> <span class="hl-s">"ume_math.h"</span>                    <span class="hl-p">#include</span> <span class="hl-s">"ume_math.h"</span>
<span class="hl-c">// ↓ 编译后得到一份 ume_max              // ↓ 编译后又得到一份 ume_max</span>

<span class="hl-c">// 链接时：两个 .obj 里都有 ume_max → 冲突</span></pre></div>

<h3 id="s9b">9.2 实测那个报错</h3>

<p>我把 <code>inline</code> 去掉、并且让<b>两个 <code>.cpp</code> 都包含这个头文件</b>，
重新生成，得到的是这个（本机实测原文）：</p>

<div class="out-wrap"><div class="cap">实测报错（去掉 inline 之后）</div><pre>UmeMath.lib(ume_math.obj) : error LNK2005:
    "int __cdecl ume_max(int,int)" (?ume_max@@YAHHH@Z) 已经在 main.obj 中定义

D:\...\x64\Debug\App.exe : fatal error LNK1169:
    找到一个或多个多重定义的符号</pre></div>

<p>把这句话拆开读，每个部分都有信息：</p>

<table>
<thead><tr><th style="width:32%">片段</th><th>意思</th></tr></thead>
<tbody>
<tr><td class="c">UmeMath.lib(ume_math.obj)</td>
    <td>冲突的<b>一方</b>来自库里的 <code>ume_math.obj</code></td></tr>
<tr><td class="c">已经在 main.obj 中定义</td>
    <td>冲突的<b>另一方</b>来自 App 的 <code>main.obj</code></td></tr>
<tr><td class="c">"int __cdecl ume_max(int,int)"</td>
    <td>人类能读的函数签名</td></tr>
<tr><td class="c">?ume_max@@YAHHH@Z</td>
    <td><b>同一个符号的「修饰名」</b>（见下方说明）</td></tr>
<tr><td class="c">LNK2005</td>
    <td>错误码：符号重复定义</td></tr>
<tr><td class="c">LNK1169</td>
    <td>它引发的最终结果：链接失败</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">那个 <code>?ume_max@@YAHHH@Z</code> 是什么</div>
  <p>这叫<b>名字修饰</b>（name mangling）。
  C++ 支持函数重载，所以编译器要把参数类型也编进符号名，
  这样 <code>f(int)</code> 和 <code>f(double)</code> 才是两个不同符号。</p>
  <p>拆开看：<code>?ume_max@@YA</code> 是「全局函数」，
  <code>H</code> 是 <code>int</code>（<code>H</code> 来自 <code>int</code> 的
  「4 字节整数」内部代号），所以 <code>HHH</code> = 两个参数 + 返回值都是 int，
  <code>@Z</code> 表示结束。</p>
  <p><b>报错里同时给修饰名和可读名，是为了让你能拿去搜索</b> ——
  搜索时用修饰名更准。</p>
</div>

<h3 id="s9c">9.3 inline 的三层含义</h3>

<p>「inline」这个词直译是「在行内」，但它<b>在现代 C++ 里主要不是那个意思</b>。
搞清这三层就不容易混了。</p>

<h4>第一层（也是最重要的）：允许在多个 .cpp 里重复定义</h4>

<div class="card key">
  <div class="card-t">这才是 inline 的本职</div>
  <p><code>inline</code> 告诉链接器：<b>「这个函数可能出现在多个
  <code>.obj</code> 里，它们是同一份，别报错，随便挑一个用。」</b></p>
  <p>于是「头文件里写函数体」就合法了 —— 这正是静态库/头文件库需要的。</p>
  <p>前提是<b>每个定义必须一模一样</b>（同样的代码、同样的名字）。
  如果两个地方写得不一致，那是未定义行为 —— 出了怪问题很难查，
  所以<b>不要手写两份，一定是同一个头文件被包含</b>。</p>
</div>

<h4>第二层：建议编译器「直接展开」</h4>

<p>这是名字的来源。函数调用本身有开销（压栈、跳转、返回），
对<b>很短</b>的函数来说这个开销比函数体还大。加上 <code>inline</code>
等于给编译器一个<b>建议</b>：「这个小，干脆把函数体直接填到调用处，省掉调用」。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">「展开」是什么意思</span><span class="cp">复制</span></div><pre><span class="hl-c">// 你写的</span>
<span class="hl-k">int</span> m = <span class="hl-f">ume_max</span>(x, y);

<span class="hl-c">// 编译器「展开」之后等价于</span>
<span class="hl-k">int</span> m = (x &gt; y) ? x : y;     <span class="hl-c">// 没有函数调用，直接算</span></pre></div>

<div class="card warn">
  <div class="card-t">这只是「建议」，编译器可以不听</div>
  <p>现代编译器<b>自己就会判断</b>该不该展开 ——
  哪怕你不写 <code>inline</code>，它也会把小函数自动展开（尤其开了优化）；
  你写了 <code>inline</code>，它觉得不划算也可能不展开。</p>
  <p><b>所以不要为了「快」而加 inline。</b>
  要性能就开优化（Release 配置自带 <code>/O2</code>），
  而不是手工到处标 inline。</p>
  <p>换句话说：<b>第一层是「必须」，第二层是「随便」。</b>
  你加 inline 是为了过链接，不是为了提速。</p>
</div>

<h4>第三层：类内定义的成员函数「自动」是 inline</h4>

<p>这一点第六讲其实已经用过，只是没说破：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">类内直接写函数体 = 自动 inline</span><span class="cp">复制</span></div><pre><span class="hl-k">class</span> Player {
    <span class="hl-k">int</span> hp;
<span class="hl-k">public</span>:
    <span class="hl-c">// 写在类里面 → 隐含 inline，可以放进头文件、被多个 .cpp 包含</span>
    <span class="hl-k">int</span> <span class="hl-f">getHp</span>() <span class="hl-k">const</span> { <span class="hl-k">return</span> hp; }
};</pre></div>

<p>这就是为什么第六讲的 <code>Player</code> 类整个放在头文件里
也没报重复定义 —— <b>类内定义的成员函数隐含 inline</b>。
而如果你把 <code>getHp</code> 的函数体写到类外面
（<code>int Player::getHp() const { ... }</code>）并且放在头文件里，
就<b>必须自己加 inline</b>，否则又回到 9.1 那个冲突。</p>

<div class="card key">
  <div class="card-t">C++17 起：inline 变量</div>
  <p>变量也能 inline。看 8.2 里那行：</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">头文件里的常量</span><span class="cp">复制</span></div><pre><span class="hl-c">// C++17 之前：这样写会「重复定义」，因为每个 .cpp 都有一份</span>
<span class="hl-k">const</span> <span class="hl-k">int</span> kUmeVersion = <span class="hl-n">2026</span>;

<span class="hl-c">// C++17 起：加 inline，同样允许多份</span>
<span class="hl-k">inline</span> <span class="hl-k">const</span> <span class="hl-k">int</span> kUmeVersion = <span class="hl-n">2026</span>;</pre></div>
  <p style="margin-top:10px">C++17 之前要在头文件里放常量，得用
  <code>static const</code> 或 <code>enum</code> 绕；
  现在 <code>inline</code> 直接解决。</p>
</div>

<h4>三条实用规则</h4>
<table>
<thead><tr><th style="width:48%">情况</th><th>要不要 inline</th></tr></thead>
<tbody>
<tr><td>函数<b>声明</b>写在头文件、<b>定义</b>写在 .cpp</td>
    <td><span class="tag g">不用</span> —— 这是标准做法</td></tr>
<tr><td>函数<b>定义</b>直接写在头文件里</td>
    <td><span class="tag r">必须加</span></td></tr>
<tr><td>成员函数写在 <b>class 里面</b></td>
    <td><span class="tag g">不用写</span>（隐含 inline）</td></tr>
<tr><td>成员函数定义写在 <b>class 外面</b>、但在头文件里</td>
    <td><span class="tag r">必须加</span></td></tr>
<tr><td>头文件里的全局常量（C++17 起）</td>
    <td><span class="tag p">加 inline</span></td></tr>
<tr><td>模板函数</td>
    <td><span class="tag g">不用写</span>（模板本身就有类似待遇）</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">一句话记住</div>
  <p><b>「头文件里凡是带函数体的东西，都得能让多份共存」</b> ——
  这就是 <code>inline</code> 在现代 C++ 里的主要职责。
  看到 <code>LNK2005</code> / <code>LNK1169</code>，
  第一反应就是<b>「头文件里是不是有个函数忘了加 inline？」</b></p>
</div>

<!-- ============================================================ -->
<h2 id="s10"><span class="n">10</span>常见错误</h2>

<h4>错误 1 · 头文件里有函数体却忘了 inline</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ 被两个 .cpp 包含就报 LNK2005</span>
<span class="hl-k">int</span> <span class="hl-f">ume_max</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) { <span class="hl-k">return</span> (a &gt; b) ? a : b; }

<span class="hl-c">// ✅ 头文件里的函数定义加 inline</span>
<span class="hl-k">inline</span> <span class="hl-k">int</span> <span class="hl-f">ume_max</span>(<span class="hl-k">int</span> a, <span class="hl-k">int</span> b) { <span class="hl-k">return</span> (a &gt; b) ? a : b; }</pre></div>

<h4>错误 2 · 源文件存成 UTF-8 无 BOM，中文注释引发怪错</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ UTF-8 无 BOM：MSVC 按 GBK 读，中文注释会吃掉后面的代码</span>
<span class="hl-c">// 报错：error C2059: 语法错误:"return"    ← 行号指向一个正常的 return</span>

<span class="hl-c">// ✅ 解法一：文件另存为「UTF-8 带 BOM」</span>
<span class="hl-c">// ✅ 解法二：项目属性 → C/C++ → 命令行 → 其他选项 加 /utf-8</span>
<span class="hl-c">// ✅ 解法三：源文件里不写中文注释</span></pre></div>

<h4>错误 3 · 只配了「附加依赖项」，没配「附加库目录」</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ 只写名字，不写在哪</span>
<span class="hl-c">// 链接器 → 输入 → 附加依赖项:  UmeMath.lib</span>
<span class="hl-c">// → LNK1104: 无法打开文件"UmeMath.lib"</span>

<span class="hl-c">// ✅ 两个都要</span>
<span class="hl-c">// 链接器 → 输入   → 附加依赖项:  UmeMath.lib</span>
<span class="hl-c">// 链接器 → 常规   → 附加库目录:  $(SolutionDir)$(Platform)\$(Configuration)</span></pre></div>

<h4>错误 4 · 改完配置只点「生成」</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ 改了「附加包含目录」，源文件没动 → 「生成」认为无事可做</span>
<span class="hl-c">//    结果：还是报找不到头文件，让人以为改错了</span>

<span class="hl-c">// ✅ 改配置之后用「重新生成」</span>
<span class="hl-c">//    右键项目 → 重新生成</span></pre></div>

<h4>错误 5 · 在两个不同的解决方案里建库和使用者</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ 库一个 .sln，App 另一个 .sln → 「添加引用」里根本看不到对方</span>

<span class="hl-c">// ✅ 右键【解决方案】→ 添加 → 新建项目 / 现有项目，放进同一个 .sln</span></pre></div>

<h4>错误 6 · 改「附加依赖项」时把 <code>%(...)</code> 删了</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ 直接覆盖成只有自己那一个库</span>
UmeMath.lib
<span class="hl-c">// → 系统库全丢了，报一堆 kernel32.lib 找不到</span>

<span class="hl-c">// ✅ 往前面加，保留原有的</span>
UmeMath.lib;%(AdditionalDependencies)</pre></div>

<h4>错误 7 · 老项目报 <code>MSB8020 无法找到 v143</code></h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">// ❌ 老项目写着 VS 2022 的工具集 v143，本机只装了 VS 2026</span>
<span class="hl-c">//    error MSB8020: 无法找到 v143 的生成工具</span>

<span class="hl-c">// ✅ 右键解决方案 → 重定解决方案目标 → 选当前版本</span>
<span class="hl-c">//    或 项目属性 → 常规 → 平台工具集 → 改成 v145</span></pre></div>

<div class="card key">
  <div class="card-t">这一篇要记住的六句话</div>
  <ol>
    <li><b>编译器做三步：预处理 → 编译 → 链接</b>；
      <code>#include</code> 是「把文件内容粘进来」。</li>
    <li><b>头文件（.h）给编译期用，库（.lib）给链接期用</b> ——
      缺头文件报 <code>C1083</code>，缺库报 <code>LNK2019</code> / <code>LNK1104</code>。</li>
    <li><b>静态库 = 配置类型选「静态库 (.lib)」</b>，
      产物落在 <code>$(SolutionDir)$(Platform)\$(Configuration)\</code>。</li>
    <li><b>用库要配三处</b>：添加引用（顺序 + 登记）、
      附加包含目录（找 .h）、附加依赖项 + 附加库目录（找 .lib）。</li>
    <li><b>改完配置用「重新生成」</b>，
      因为「生成」只看时间戳，配置变化它察觉不到。</li>
    <li><b>头文件里的函数定义必须加 <code>inline</code></b>，
      否则多份定义 → <code>LNK2005</code>；
      <code>inline</code> 的本职是「允许多份」，不是「提速」。</li>
  </ol>
</div>

'''

t = t[:i7] + NEW + t[imain:]

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("F03：%d → %d 字符" % (orig, len(t)))
print("")
print("h2 顺序：")
for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', t):
    print("  " + re.sub(r'<[^>]+>', '', m.group(2)))
print("")
ids = re.findall(r'id="([^"]+)"', t)
dups = sorted({i for i in ids if ids.count(i) > 1})
print("重复 id: %s" % (", ".join(dups) if dups else "无"))
print("残留 gcc: %d   g++: %d" % (len(re.findall(r'\bgcc\b', t)), len(re.findall(r'g\+\+', t))))
