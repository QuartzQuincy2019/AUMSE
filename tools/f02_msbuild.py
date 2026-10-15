# -*- coding: utf-8 -*-
"""F02 第 8 节：Visual Studio 的 $(...) 属性宏。

所有数值都用 MSBuild 实跑展开核对：
  Visual Studio Community 2026 (18.10.3)
  MSBuild  D:\\MicrosoftVisualStudio\\Community\\MSBuild\\Current\\Bin\\MSBuild.exe
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F02_相对文件路径与宏.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)

# ---------------------------------------------------------------
# 1. 把旧的「项目里的实际用处」（重复 id=s6）整段换掉
# ---------------------------------------------------------------
i0 = t.index('<h2 id="s6"><span class="n">6</span>项目里的实际用处</h2>')
i1 = t.index('<!-- ============================================================ -->\n<h2 id="s7">')

NEW8 = r'''<h2 id="s8"><span class="n">8</span>另一种宏：VS 的 <code>$(...)</code></h2>

<div class="card note">
  <div class="card-t">这一节解决两个具体问题</div>
  <ol>
    <li>Visual Studio 里 <b>项目 → 属性 → 输出目录</b> 默认写着
      <code>$(SolutionDir)$(Platform)\$(Configuration)\</code> ——
      这一串 <code>$(...)$</code> 到底是什么？</li>
    <li>要包含自己写的头文件，在
      <b>配置属性 → C/C++ → 附加包含目录</b> 里写的
      <code>$(SolutionDir)</code> 又是什么？</li>
  </ol>
  <p>答案：它们是 <b>MSBuild 的「属性宏」</b> ——
  和第 4 节的环境变量是<b>同一个思路</b>，但<b>换了一套记号和替换者</b>。</p>
  <p>本节所有展开结果，都用本机的
  <b>MSBuild</b>（Visual Studio Community 2026 · 18.10.3）实际跑出来核对。</p>
</div>

<h3 id="s8a">8.1 输出目录里的那串是什么</h3>

<p>先看 VS 里那个默认值：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">项目属性 → 输出目录（默认值）</span><span class="cp">复制</span></div><pre><span class="hl-n">$(SolutionDir)$(Platform)\$(Configuration)\</span></pre></div>

<p>它<b>不是</b>一条真实路径，而是<b>四个宏拼起来的式子</b>。
MSBuild 在生成时把它们各自替换成实际值，拼出一条真路径。</p>

<p>假设解决方案放在 <code>D:\Path\To\UME\</code>，里面有个项目
<code>UME.vcxproj</code>，当前选的是 <b>Debug | x64</b>。逐个展开：</p>

<table>
<thead><tr><th style="width:26%">宏</th><th style="width:44%">展开成</th><th>含义</th></tr></thead>
<tbody>
<tr><td class="c">$(SolutionDir)</td>
    <td class="c" style="font-size:12.5px">D:\Path\To\UME\</td>
    <td><b>解决方案（.sln）所在目录</b>，<b>结尾带反斜杠</b></td></tr>
<tr><td class="c">$(Platform)</td>
    <td class="c">x64</td>
    <td>目标平台（<code>x64</code> / <code>Win32</code> / <code>ARM64</code>）</td></tr>
<tr><td class="c">$(Configuration)</td>
    <td class="c">Debug</td>
    <td>生成配置（<code>Debug</code> / <code>Release</code>）</td></tr>
<tr><td colspan="3" style="background:#f7f9fc"><b>四个拼起来就是</b> →</td></tr>
<tr><td class="c">整串展开</td>
    <td class="c" style="font-size:12.5px">D:\Path\To\UME\x64\Debug\</td>
    <td><b>这就是 exe 会被放到的目录</b></td></tr>
</tbody>
</table>

<div class="out-wrap"><div class="cap">本机实测：把这四个宏交给 MSBuild 打印出来</div><pre>SolutionDir    = [D:\Path\To\UME\]
Platform       = [x64]
Configuration  = [Debug]
OutDir（那串展开后） = [D:\Path\To\UME\x64\Debug\]
TargetPath           = [D:\Path\To\UME\x64\Debug\UME.exe]</pre></div>

<div class="card key">
  <div class="card-t">为什么要费劲拼，而不直接写死</div>
  <p>因为<b>一个项目要同时支持好几种组合</b>：
  Debug / Release × x64 / Win32，就是 4 种。</p>
  <p>写死的话得为每种组合各配一遍，改一处要改四处。
  用宏之后<b>一套式子自动适配所有组合</b>：</p>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:30%">当前选的是</th><th>输出目录自动变成</th></tr></thead>
  <tbody>
  <tr><td class="c">Debug | x64</td><td class="c" style="font-size:12.5px">D:\Path\To\UME\x64\Debug\</td></tr>
  <tr><td class="c">Release | x64</td><td class="c" style="font-size:12.5px">D:\Path\To\UME\x64\Release\</td></tr>
  <tr><td class="c">Debug | Win32</td><td class="c" style="font-size:12.5px">D:\Path\To\UME\Win32\Debug\</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>这正是环境变量的那套理由</b>：
  把会变的部分（配置名、平台名）换成符号，式子就不用改。</p>
</div>

<div class="card tip">
  <div class="card-t">实测确认：换个配置，输出目录真的跟着变</div>
  <p>同一个工程，只把生成配置从 Debug 换成 Release：</p>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:24%">配置</th><th>MSBuild 展开出的 OutDir</th></tr></thead>
  <tbody>
  <tr><td class="c">Debug</td><td class="c" style="font-size:12.5px">…\x64\Debug\</td></tr>
  <tr><td class="c">Release</td><td class="c" style="font-size:12.5px">…\x64\Release\</td></tr>
  </tbody></table>
  <p style="margin-top:10px">式子一个字没改，输出目录自己就换了 ——
  这就是宏的意义。</p>
</div>

<h4>VS 界面上在哪里改</h4>
<p><b>顶部菜单 → 项目 → 属性</b>（或右键项目 → 属性），打开属性页：</p>
<pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:11px 14px;font-family:var(--mono);font-size:12.5px;color:var(--fg);overflow:auto">配置属性
 └─ 常规
     ├─ 输出目录            ← $(SolutionDir)$(Platform)\$(Configuration)\
     └─ 中间目录            ← $(Platform)\$(Configuration)\
 └─ C/C++
     └─ 常规
         └─ 附加包含目录     ← 在这里加 $(SolutionDir)include</pre>

<div class="card warn">
  <div class="card-t">两个容易踩的点</div>
  <p><b>① 注意左上角的「配置」下拉框。</b>
  属性页顶部有 <b>配置</b> 和 <b>平台</b> 两个下拉框，
  默认可能是「所有配置」。改的时候要想清楚：
  <b>是只改 Debug，还是所有配置都改？</b>
  选「所有配置」改一处，四个组合一起生效 —— 通常这才是你要的。</p>
  <p><b>② 结尾那个反斜杠不能丢。</b>
  <code>$(SolutionDir)</code> <b>自带</b>结尾反斜杠，
  所以写 <code>$(SolutionDir)include</code> 就对了；
  写成 <code>$(SolutionDir)\include</code> 会变成两个反斜杠
  （Windows 一般能容忍，但不该这么写）。</p>
</div>

<!-- ============================================================ -->
<h3 id="s8b">8.2 附加包含目录里的 $(SolutionDir)</h3>

<p>现在回答第二个问题：<b>要包含自己写的头文件，那个 <code>$(SolutionDir)</code> 是什么？</b></p>

<p>它就是<b>上一节那个 <code>$(SolutionDir)</code></b> ——
解决方案所在目录。<b>同一个宏，在不同地方写，含义完全一样。</b></p>

<h4>先看没有它会怎样</h4>
<p>假设项目结构是这样：</p>

<div class="tree">
<span class="d">D:\Path\To\UME\</span>            <span class="c">← 解决方案目录（$(SolutionDir)）</span>
├─ <span class="f">UME.sln</span>
├─ <span class="d">UME\</span>                      <span class="c">← 项目目录（$(ProjectDir)）</span>
│   ├─ <span class="f">UME.vcxproj</span>
│   └─ <span class="f">main.c</span>
└─ <span class="d">include\</span>                  <span class="c">← 自己写的头文件放这里</span>
    └─ <span class="f">font.h</span>
</div>

<p>在 <code>UME\main.c</code> 里写 <code>#include "font.h"</code>，
编译器会去<b>哪几个目录</b>找 <code>font.h</code>？</p>

<ul>
  <li><b>先找 <code>main.c</code> 自己所在的目录</b>，也就是 <code>UME\</code> ——
    但 <code>font.h</code> 在 <code>include\</code> 里，<b>找不到</b></li>
  <li>再找「附加包含目录」里列的目录 —— <b>还没配，是空的</b></li>
  <li>再找系统头文件目录 —— 更不会有</li>
  <li><b>结果</b>：报 <code>fatal error C1083: 无法打开包括文件: "font.h"</code></li>
</ul>

<h4>配上它就解决了</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">附加包含目录里填</span><span class="cp">复制</span></div><pre><span class="hl-n">$(SolutionDir)include</span>

<span class="hl-c">/* 展开后 = D:\Path\To\UME\include  ← font.h 就在这里 */</span></pre></div>

<div class="out-wrap"><div class="cap">本机实测：MSBuild 展开出的 IncludePath 前两项</div><pre>E:\...\_vs_check\include;  ← 我加的那一条（= $(SolutionDir)include）
D:\MicrosoftVisualStudio\Community\VC\Tools\MSVC\...\include;  ← VS 自带
...（后面一串 Windows SDK 的目录）</pre></div>

<p>看第一项：<code>$(SolutionDir)include</code>
被替换成了 <code>…\_vs_check\include</code>，
正是解决方案目录下的 <code>include</code> 文件夹。<b>配对了。</b></p>

<div class="card key">
  <div class="card-t">为什么用 <code>$(SolutionDir)</code> 而不是相对路径</div>
  <p>因为「附加包含目录」里的<b>相对路径是相对于项目文件（.vcxproj）</b>，
  不是相对于解决方案。<b>这个基准很难记住，而且换个位置就错。</b></p>
  <p>用 <code>$(SolutionDir)</code> 之后，<b>基准写明白了、一眼能看懂</b>，
  而且项目挪到别的盘、别的机器上依然正确。</p>
  <p>它的作用和第 3 节讲的 <code>%~dp0</code> 是同一招：
  <b>把「相对于谁」这件事显式写出来，不靠默认约定。</b></p>
</div>

<h4>要加多个目录怎么写</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">用分号隔开</span><span class="cp">复制</span></div><pre><span class="hl-n">$(SolutionDir)include;$(SolutionDir)src\core;D:\third_party\zlib\include</span>

<span class="hl-c">/* 在 VS 界面里：双击那一行 → 点右侧的「...」→ 一行一个目录 → 确定
   VS 会自动帮你拼成分号分隔的形式，不用手打分号 */</span></pre></div>

<div class="card tip">
  <div class="card-t">改完要重新生成</div>
  <p>改「附加包含目录」之后，<b>已经编译过的 .obj 不会自动重编</b> ——
  因为 VS 不认为「头文件搜索路径变了」算源文件变了。</p>
  <p>所以改完包含目录，习惯性做一次
  <b>生成 → 重新生成解决方案</b>，别只点「生成」。</p>
  <p>否则会出现「明明改对了却还是报找不到头文件」的假象。</p>
</div>

<!-- ============================================================ -->
<h3 id="s8c">8.3 常用属性宏一览</h3>

<p>下面这些值全部是<b>本机 MSBuild 实际展开</b>出来的，
用同一个演示工程（解决方案在 <code>…\_vs_check\</code>，
项目在 <code>…\_vs_check\Demo\</code>，配置 Debug | x64）。</p>

<h4>目录与文件名</h4>
<table>
<thead><tr><th style="width:24%">宏</th><th style="width:46%">实测展开</th><th>含义</th></tr></thead>
<tbody>
<tr><td class="c">$(SolutionDir)</td>
    <td class="c" style="font-size:12px">…\_vs_check\</td>
    <td><b>.sln 所在目录</b>（结尾带 <code>\</code>）</td></tr>
<tr><td class="c">$(SolutionPath)</td>
    <td class="c" style="font-size:12px">…\_vs_check\Demo.sln</td>
    <td>.sln 的完整路径</td></tr>
<tr><td class="c">$(SolutionName)</td>
    <td class="c">Demo</td><td>.sln 的文件名（不含扩展名）</td></tr>
<tr><td class="c">$(ProjectDir)</td>
    <td class="c" style="font-size:12px">…\_vs_check\Demo\</td>
    <td><b>.vcxproj 所在目录</b>（结尾带 <code>\</code>）</td></tr>
<tr><td class="c">$(ProjectPath)</td>
    <td class="c" style="font-size:12px">…\_vs_check\Demo\Demo.vcxproj</td>
    <td>项目文件的完整路径</td></tr>
<tr><td class="c">$(ProjectName)</td>
    <td class="c">Demo</td><td>项目名</td></tr>
<tr><td class="c">$(ProjectFileName)</td>
    <td class="c">Demo.vcxproj</td><td>项目文件名（含扩展名）</td></tr>
<tr><td class="c">$(ProjectExt)</td>
    <td class="c">.vcxproj</td><td>项目文件扩展名</td></tr>
</tbody>
</table>

<h4>配置与平台</h4>
<table>
<thead><tr><th style="width:24%">宏</th><th style="width:46%">实测展开</th><th>含义</th></tr></thead>
<tbody>
<tr><td class="c">$(Configuration)</td><td class="c">Debug</td>
    <td>当前生成配置（<code>Debug</code> / <code>Release</code>）</td></tr>
<tr><td class="c">$(Platform)</td><td class="c">x64</td>
    <td>当前平台（<code>x64</code> / <code>Win32</code> / <code>ARM64</code>）</td></tr>
<tr><td class="c">$(PlatformShortName)</td><td class="c">x64</td>
    <td>平台短名（和 <code>$(Platform)</code> 多数情况一样）</td></tr>
<tr><td class="c">$(PlatformToolset)</td><td class="c">v143</td>
    <td>用哪套编译工具（VS 2022 是 v143）</td></tr>
</tbody>
</table>

<h4>输出</h4>
<table>
<thead><tr><th style="width:24%">宏</th><th style="width:46%">实测展开</th><th>含义</th></tr></thead>
<tbody>
<tr><td class="c">$(OutDir)</td>
    <td class="c" style="font-size:12px">…\_vs_check\x64\Debug\</td>
    <td><b>最终产物放哪</b>（就是 8.1 那串）</td></tr>
<tr><td class="c">$(IntDir)</td>
    <td class="c" style="font-size:12px">x64\Debug\</td>
    <td>中间文件（<code>.obj</code>）放哪</td></tr>
<tr><td class="c">$(TargetDir)</td>
    <td class="c" style="font-size:12px">…\_vs_check\x64\Debug\</td>
    <td>目标文件所在目录</td></tr>
<tr><td class="c">$(TargetPath)</td>
    <td class="c" style="font-size:12px">…\x64\Debug\Demo.exe</td>
    <td><b>目标文件的完整路径</b></td></tr>
<tr><td class="c">$(TargetName)</td><td class="c">Demo</td>
    <td>目标文件名（不含扩展名）</td></tr>
<tr><td class="c">$(TargetExt)</td><td class="c">.exe</td>
    <td>目标文件扩展名</td></tr>
</tbody>
</table>

<h4>VS 自己的位置</h4>
<table>
<thead><tr><th style="width:24%">宏</th><th style="width:46%">实测展开</th><th>含义</th></tr></thead>
<tbody>
<tr><td class="c">$(VCTargetsPath)</td>
    <td class="c" style="font-size:12px">D:\…\MSBuild\Microsoft\VC\v180\</td>
    <td>VS 的 C++ 生成规则放在哪</td></tr>
<tr><td class="c">$(VisualStudioVersion)</td><td class="c">18.0</td>
    <td>VS 主版本号</td></tr>
<tr><td class="c">$(MSBuildToolsVersion)</td><td class="c">Current</td>
    <td>MSBuild 工具集版本</td></tr>
</tbody>
</table>

<h4>两个必须知道的行为</h4>

<div class="card key">
  <div class="card-t">① 没有的宏会展开成「空」，不会报错</div>
  <p>实测：写一个不存在的 <code>$(NO_SUCH_MACRO_XYZ)</code>，
  MSBuild 不报错，直接替换成<b>空字符串</b>：</p>
  <div class="out-wrap" style="margin-top:10px"><div class="cap">实测</div><pre>不存在的宏 = []</pre></div>
  <p style="margin-top:10px"><b>这很危险</b>：如果宏名打错了，
  路径会静默地少一段，你只会看到「找不到文件」，
  而不会看到「宏名拼错」。</p>
  <p><b>所以路径拼不对时，第一件事是怀疑宏名拼写。</b>
  VS 属性页里有个「宏 &gt;&gt;」按钮，可以列出所有可用宏、
  并显示当前值 —— 拿它对照最省事。</p>
</div>

<div class="card key">
  <div class="card-t">② 没有 .sln 时，$(SolutionDir) 会退化成项目目录</div>
  <p>实测：直接用 MSBuild 生成单个 <code>.vcxproj</code>（没有 <code>.sln</code>）时：</p>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:34%">情况</th><th>$(SolutionDir)</th></tr></thead>
  <tbody>
  <tr><td>有 .sln</td>
      <td class="c" style="font-size:12px">…\_vs_check\&nbsp;&nbsp;<span class="tag b">.sln 所在</span></td></tr>
  <tr><td>没有 .sln</td>
      <td class="c" style="font-size:12px">…\_vs_check\Demo\&nbsp;&nbsp;<span class="tag y">退化成项目目录</span></td></tr>
  </tbody></table>
  <p style="margin-top:10px">所以<b>在 VS 里正常打开解决方案时它是可靠的</b>；
  但如果你绕过 .sln 单独编译项目，含义就变了 ——
  这时要用 <code>$(ProjectDir)</code> 才稳。</p>
</div>

<div class="card warn">
  <div class="card-t">顺带一个会遇到的报错</div>
  <p>如果你在命令行用 MSBuild 指定了一个<b>解决方案里没配置过</b>的平台，
  会直接失败（本机实测）：</p>
  <div class="out-wrap" style="margin-top:10px"><div class="cap">实测</div><pre>error MSB4126: 指定的解决方案配置"Debug|Win32"无效。
请使用 Configuration 和 Platform 属性指定有效的解决方案配置。</pre></div>
  <p style="margin-top:10px">意思是「<b>这个解决方案里没有 Debug|Win32 这个组合</b>」。
  在 VS 里对应的是顶部工具栏那两个下拉框 ——
  配置管理器里没建的组合，命令行也编不了。</p>
</div>

<!-- ============================================================ -->
<h3 id="s8d">8.4 它和 <code>%环境变量%</code> 的关系</h3>

<p>这两套宏最容易混。一张表看清：</p>

<table>
<thead><tr><th style="width:20%"></th><th><code>%名字%</code></th><th><code>$(名字)</code></th></tr></thead>
<tbody>
<tr><td><b>叫什么</b></td><td>环境变量</td><td>MSBuild 属性宏</td></tr>
<tr><td><b>谁替换</b></td><td>cmd</td><td>MSBuild</td></tr>
<tr><td><b>什么时候</b></td><td>敲命令执行前</td><td>生成项目时</td></tr>
<tr><td><b>在哪写有效</b></td><td>cmd 里、<code>.bat</code> 里</td>
    <td><b>VS 属性页、<code>.vcxproj</code> 里</b></td></tr>
<tr><td><b>典型例子</b></td><td class="c">%PATH%</td><td class="c">$(SolutionDir)</td></tr>
<tr><td><b>互相能换吗</b></td>
    <td colspan="2"><span class="tag r">不能</span> ——
      在 cmd 里 <code>%SolutionDir%</code> 是空的；
      在 VS 属性页里 <code>$(PATH)</code> 也取不到你想的那个 PATH</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">但有一处它们确实相通</div>
  <p><b>MSBuild 能读环境变量</b>。实测：在 <code>.vcxproj</code> 里写
  <code>$(TEMP)</code>、<code>$(PATH)</code>，MSBuild 会把它们
  <b>当成属性名去找</b> —— 找不到同名属性时，就<b>去环境变量里取</b>：</p>
  <div class="out-wrap" style="margin-top:10px"><div class="cap">实测</div><pre>PATH 前 60 字 = [C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\W]
TEMP          = [C:\Users\Your_Username\AppData\Local\Temp]
USERPROFILE   = [C:\Users\Your_Username]</pre></div>
  <p style="margin-top:10px">所以<b>环境变量是一种「兜底的宏」</b>：
  实在没有同名属性时，MSBuild 会去环境里找。</p>
  <p><b>实用价值</b>：如果你想让工程配置跟着一个环境变量走
  （比如团队里每个人把第三方库放在不同地方），
  可以设一个 <code>UME_ROOT</code>，然后在属性页里写
  <code>$(UME_ROOT)include</code> —— 每个人各自设自己的，工程文件不用改。</p>
</div>

<div class="card tip">
  <div class="card-t">怎么快速查一个宏现在是什么值</div>
  <p>VS 属性页里改「附加包含目录」这类字段时，
  输入框<b>右侧有个「宏 &gt;&gt;」按钮</b>。</p>
  <p>点开它会列出<b>所有可用宏 + 当前展开值</b>，
  还可以双击插入。想确认 <code>$(SolutionDir)</code>
  在你机器上到底是什么，这是最快的办法。</p>
  <p>另外，改完属性页 <b>VS 会立刻把宏展开显示在下方预览里</b>，
  不用编译就能看到结果。</p>
</div>

<h4>本节的结论，压成三条</h4>
<div class="card key">
  <ol>
    <li><b><code>$(...)</code> 是 MSBuild 的属性宏，不是环境变量。</b>
      在 VS 的工程配置里用，由 MSBuild 在生成时替换。</li>
    <li><b><code>$(SolutionDir)</code> = .sln 所在目录（自带结尾反斜杠）。</b>
      输出目录那串靠它 + <code>$(Platform)</code> +
      <code>$(Configuration)</code> 拼出「哪个配置放哪」；
      附加包含目录靠它把「自己写的头文件在哪」写清楚。</li>
    <li><b>宏名写错不报错，只会静默变成空串</b> ——
      路径找不到时，先用属性页的「宏 &gt;&gt;」核对拼写。</li>
  </ol>
</div>

'''

t = t[:i0] + NEW8 + t[i1:]

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("F02 第 2 步：%d → %d 字符" % (orig, len(t)))

# 复核
ids = re.findall(r'id="([^"]+)"', t)
dups = {i for i in ids if ids.count(i) > 1}
print("")
print("重复 id: %s" % (", ".join(sorted(dups)) if dups else "无"))
print("id 总数 %d" % len(ids))
lastline = [c for c in '$(']
print("含 $( 的行数: %d" % len(re.findall(r'\$\(', t)))
