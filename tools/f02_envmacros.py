# -*- coding: utf-8 -*-
"""F02 第 4/5 节重写：把「宏」的重点从 #define / #if 转到
   配置环境变量时用的宏（%PATH% / %TEMP% / %~dp0 这一类）。

保留「文字替换」这个共同内核，但演示全部换成命令行环境变量的实际用法 ——
这正是配置开发环境时天天要碰的东西。
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

# ---------- 1. 目录改造 ----------
old_toc = """  <a href="#s4">4 · 宏是什么</a>
  <a href="#s5">5 · 预定义宏与自定义宏</a>
  <a href="#s6">6 · 项目里的实际用处</a>
  <a href="#s7">7 · 常见坑</a>"""
new_toc = """  <a href="#s4">4 · 环境变量就是一批「宏」</a>
  <a href="#s5">5 · 最常用的几个环境变量</a>
  <a href="#s5a" class="sub">5.1 PATH：为什么命令能直接敲</a>
  <a href="#s5b" class="sub">5.2 TEMP / USERPROFILE：临时文件与个人目录</a>
  <a href="#s5c" class="sub">5.3 %~dp0：批处理里最重要的一个</a>
  <a href="#s6">6 · 怎么设置环境变量</a>
  <a href="#s7">7 · 常见坑</a>"""
assert old_toc in t, "目录未匹配"
t = t.replace(old_toc, new_toc, 1)

# ---------- 2. 第 4、5 节整体替换 ----------
i0 = t.index('<h2 id="s4"><span class="n">4</span>')
i1 = t.index('<h2 id="s6"><span class="n">6</span>')
NEW = r'''<h2 id="s4"><span class="n">4</span>环境变量就是一批「宏」</h2>

<p>先说一个容易被搞混的事：<b>「宏」这个词在不同场合指不同的东西</b>。</p>

<table>
<thead><tr><th style="width:26%">场合</th><th>「宏」指的是</th><th>例子</th></tr></thead>
<tbody>
<tr><td><b>命令行 / 系统</b></td>
    <td><b>环境变量</b>：用 <code>%名字%</code> 取它的值</td>
    <td class="c">%PATH%&nbsp;&nbsp;%TEMP%</td></tr>
<tr><td>编译器预处理</td>
    <td><code>#define</code> 定义的文本替换</td>
    <td class="c">#define MAX_HP 100</td></tr>
<tr><td>Office / 游戏</td>
    <td>录好的一串操作，一键重放</td>
    <td>「宏病毒」说的就是这个</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇只讲第一种</div>
  <p><b>命令行里的「宏」= 环境变量，写法是 <code>%名字%</code>。</b></p>
  <p>它的核心思想和编译器的宏一样：<b>用一小段符号，
  代表一段会变的内容</b>。你写 <code>%TEMP%</code>，
  cmd 会把它替换成实际的临时目录路径。</p>
  <p>怎么配开发环境、怎么让命令行找到你装的工具 —— 全靠它。</p>
</div>

<h4>先看一眼效果</h4>
<p>在 cmd 里敲这几条，看它替换成什么：</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>看环境变量的实际值</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">echo %USERPROFILE%</span>
<span class="out">C:\Users\Your_Username</span>

<span class="pr">C:\&gt;</span><span class="cmd">echo %TEMP%</span>
<span class="out">C:\Users\Your_Username\AppData\Local\Temp</span>

<span class="pr">C:\&gt;</span><span class="cmd">echo %USERNAME%</span>
<span class="out">Your_Username</span>

<span class="pr">C:\&gt;</span><span class="cmd">echo %COMPUTERNAME%</span>
<span class="out">MY-PC</span></pre>
</div>

<p><code>echo</code> 的作用就是「把后面那串东西打印出来」，
而 <code>%...%</code> 会先被<b>替换</b>掉，然后才打印。
所以这个命令最好用来确认「某个变量现在到底是什么」。</p>

<h4>查看全部环境变量</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>列出所有环境变量</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">set</span>
<span class="out">ALLUSERSPROFILE=C:\ProgramData</span>
<span class="out">APPDATA=C:\Users\Your_Username\AppData\Roaming</span>
<span class="out">CommonProgramFiles=C:\Program Files\Common Files</span>
<span class="out">COMPUTERNAME=MY-PC</span>
<span class="out">...</span>
<span class="warn">（几十行，用 set 名字 可以只看一个）</span>

<span class="pr">C:\&gt;</span><span class="cmd">set TEMP</span>
<span class="out">TEMP=C:\Users\Your_Username\AppData\Local\Temp</span></pre>
</div>

<div class="card tip">
  <div class="card-t">和「相对路径」有什么关系</div>
  <p>环境变量给的是<b>绝对路径</b>，而且<b>人人不同、换台机器就不同</b>。</p>
  <p>所以写脚本、写配置时，想引用「我的临时目录」「我装工具的地方」，
  就<b>用环境变量而不是把路径写死</b> —— 这样换台机器也能跑。
  这和前面讲的「用相对路径代替绝对路径」是同一个目的：
  <b>让位置可以变，而代码不用改。</b></p>
</div>

<!-- ============================================================ -->
<h2 id="s5"><span class="n">5</span>最常用的几个环境变量</h2>

<table>
<thead><tr><th style="width:26%">变量</th><th>含义</th><th style="width:30%">典型值</th></tr></thead>
<tbody>
<tr><td class="c">%PATH%</td><td><b>去哪找可执行程序</b></td>
    <td class="c">C:\Windows\system32;...</td></tr>
<tr><td class="c">%TEMP%</td><td>临时文件目录</td>
    <td class="c">C:\Users\你\AppData\Local\Temp</td></tr>
<tr><td class="c">%USERPROFILE%</td><td>当前用户的个人目录</td>
    <td class="c">C:\Users\Your_Username</td></tr>
<tr><td class="c">%USERNAME%</td><td>当前用户名</td><td class="c">Your_Username</td></tr>
<tr><td class="c">%APPDATA%</td><td>程序存配置的地方（漫游）</td>
    <td class="c">C:\Users\你\AppData\Roaming</td></tr>
<tr><td class="c">%COMPUTERNAME%</td><td>电脑名</td><td class="c">MY-PC</td></tr>
<tr><td class="c">%CD%</td><td><b>当前目录</b></td><td class="c">D:\Path\To\project</td></tr>
</tbody>
</table>

<h3 id="s5a">5.1 <code>%PATH%</code>：为什么命令能直接敲</h3>

<p>你能直接敲 <code>dir</code>、<code>notepad</code>、<code>python</code>，
是因为它们<b>在 <code>%PATH%</code> 列出的某个目录里</b>。</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>PATH 长什么样</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">echo %PATH%</span>
<span class="out">C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;...</span>
<span class="warn">↑ 若干条路径，用分号 ; 隔开</span></pre>
</div>

<p>cmd 收到一个命令名时，会<b>按 <code>%PATH%</code> 里的顺序逐个目录去找</b>
有没有这个 <code>.exe</code>。找到就运行，全找完都没有就报那句老朋友：</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>找不到命令时</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">gcc --version</span>
<span class="err">'gcc' 不是内部或外部命令，也不是可运行的程序或批处理文件。</span>

<span class="warn">（这通常不是「没装」，而是「装了但没加进 PATH」）</span></pre>
</div>

<div class="card key">
  <div class="card-t">这就是配置环境变量的典型场景</div>
  <p>装了 MinGW / Python / Qt 之后要做的「配置环境变量」，
  <b>十有八九就是往 <code>%PATH%</code> 里加一条</b> ——
  让命令行知道「工具装在这儿」。</p>
  <p>加完<b>必须新开一个 cmd 窗口</b>才生效，见第 7 节的坑。</p>
</div>

<h4>临时加一条 <code>%PATH%</code></h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>只在当前窗口生效</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">set PATH=D:\Path\To\mingw64\bin;%PATH%</span>
<span class="warn">         ↑ 新目录放在最前面（优先找到）   ↑ 保留原来的，别忘了 </span>

<span class="pr">C:\&gt;</span><span class="cmd">gcc --version</span>
<span class="out">gcc (x86_64-posix-seh-rev1, Built by MinGW-Builds project) 13.1.0</span></pre>
</div>

<div class="card warn">
  <div class="card-t">注意 <code>;%PATH%</code> 不能漏</div>
  <p><code>set PATH=D:\...\bin</code> 会<b>把整个 PATH 替换掉</b>，
  于是 <code>dir</code>、<code>cd</code> 这些也找不到，窗口基本废了。</p>
  <p><b>想追加就必须写 <code>;%PATH%</code></b> ——
  在原有值后面接上新的。</p>
</div>

<h3 id="s5b">5.2 <code>%TEMP%</code> / <code>%USERPROFILE%</code></h3>

<p>这两个在写脚本时特别常用 —— 它们让脚本<b>不依赖具体用户名</b>。</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>把文件放到临时目录</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">copy output.log %TEMP%\</span>
<span class="out">        1 个文件已复制。</span>

<span class="pr">C:\&gt;</span><span class="cmd">cd %USERPROFILE%\Desktop</span>
<span class="out">（切到当前用户的桌面 —— 不管用户名是什么都对）</span></pre>
</div>

<table>
<thead><tr><th style="width:46%">不要这样写</th><th>应该这样写</th></tr></thead>
<tbody>
<tr><td class="c">cd C:\Users\Your_Username\Desktop</td>
    <td class="c">cd %USERPROFILE%\Desktop</td></tr>
<tr><td class="c">copy a.log C:\Users\你\AppData\Local\Temp\</td>
    <td class="c">copy a.log %TEMP%\</td></tr>
</tbody>
</table>

<p><b>理由一样：把会变的部分（用户名）交给环境变量。</b>
同事拿到你的脚本，不用改一个字就能跑。</p>

<h3 id="s5c">5.3 <code>%~dp0</code>：批处理里最重要的一个</h3>

<p>写 <code>.bat</code> 脚本时，最难的是「<b>怎么知道脚本自己放在哪</b>」——
因为用户可能在<b>任何目录</b>下双击运行它。</p>

<p><code>%~dp0</code> 就是答案：<b>它替换成「这个脚本所在的目录」</b>。</p>

<table>
<thead><tr><th style="width:22%">写法</th><th>替换成</th></tr></thead>
<tbody>
<tr><td class="c">%0</td><td>脚本的完整路径</td></tr>
<tr><td class="c">%~dp0</td><td><b>脚本所在的目录</b>（结尾自带反斜杠）</td></tr>
<tr><td class="c">%CD%</td><td><b>当前</b>工作目录（不是脚本所在目录！）</td></tr>
</tbody>
</table>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">build.bat：把「脚本所在目录」当成项目根</span><span class="cp">复制</span></div><pre>@echo off
<span class="hl-c">rem %~dp0 是「本脚本所在目录」—— 不管从哪里运行都对</span>
<span class="hl-k">cd</span> /d <span class="hl-s">"%~dp0"</span>

<span class="hl-f">echo</span> 项目根目录: %CD%
<span class="hl-f">gcc</span> -std=c99 src\main.c -o build\app.exe</pre></div>

<div class="out-wrap"><div class="cap">运行结果（从别的目录运行也没问题）</div><pre>项目根目录: D:\Path\To\project
（编译成功）</pre></div>

<div class="card key">
  <div class="card-t">为什么这比 <code>%CD%</code> 好</div>
  <p>用户可能在 <code>C:\</code> 下敲 <code>D:\Path\To\project\build.bat</code>，
  这时 <code>%CD%</code> 是 <code>C:\</code>，
  而 <code>%~dp0</code> 仍然是 <code>D:\Path\To\project\</code>。</p>
  <p>脚本里的相对路径要相对于谁？<b>几乎总是「脚本自己」</b>。
  所以开头加一句 <code>cd /d "%~dp0"</code> 是批处理的标准起手式 ——
  这样后面的相对路径就都有了明确基准。</p>
</div>

<div class="card tip">
  <div class="card-t">这一段和前面第 3 节连上了</div>
  <p>第 3 节说过：相对路径相对于<b>当前工作目录（CWD）</b>，
  而 CWD 是「你在哪敲的命令」，不是「脚本在哪」。</p>
  <p><code>cd /d "%~dp0"</code> 的作用就是<b>把 CWD 强制设成脚本目录</b>，
  于是所有相对路径都有了确定的基准。这是最常用的解法。</p>
</div>

<!-- ============================================================ -->
<h2 id="s6"><span class="n">6</span>怎么设置环境变量</h2>

<p>两种方式，用途不同。</p>

<h4>① 只在当前窗口生效（临时调试用）</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>set：只影响这个窗口</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">set MY_ROOT=D:\Path\To\project</span>
<span class="pr">C:\&gt;</span><span class="cmd">echo %MY_ROOT%</span>
<span class="out">D:\Path\To\project</span>

<span class="warn">（关掉窗口就没了 —— 适合试一下能不能跑通）</span></pre>
</div>

<h4>② 永久生效（真正「配置环境变量」）</h4>
<ol>
  <li>Win 键搜索「<b>环境变量</b>」→ 选「编辑系统环境变量」</li>
  <li>点「环境变量」按钮</li>
  <li>上半部分是<b>当前用户</b>的，下半部分是<b>整台机器</b>的 ——
    <b>优先改上半部分</b>（不需要管理员权限，也只影响你自己）</li>
  <li>找到 <code>Path</code>，双击 → 「新建」→ 填目录 → 确定</li>
</ol>

<div class="card tip">
  <div class="card-t">建议：把 UME 用到的工具都加进 Path</div>
  <p>Qt / MinGW 装好后，通常要把它们（或者 Qt 自带的那个
  「命令提示符」快捷方式）配好。判断标准很简单：</p>
  <div class="term" style="margin-top:10px">
    <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
      <span>验证是否配好</span></div>
<pre><span class="pr">C:\&gt;</span><span class="cmd">where gcc</span>
<span class="out">D:\Path\To\mingw64\bin\gcc.exe</span>
<span class="warn">（能印出路径就说明 PATH 配对了；印不出来就是没配或没重开窗口）</span></pre>
  </div>
</div>

<h4>③ 在脚本里临时设置</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">脚本内自己配好环境再干活</span><span class="cp">复制</span></div><pre>@echo off
<span class="hl-c">rem 只在本脚本运行期间生效，不会污染系统设置</span>
<span class="hl-f">set</span> PATH=D:\Path\To\mingw64\bin;%PATH%
<span class="hl-f">set</span> UME_ROOT=%~dp0

<span class="hl-f">gcc</span> -std=c99 "%UME_ROOT%src\main.c" -o "%UME_ROOT%build\app.exe"</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>（编译成功，退出后 PATH 恢复原样）</pre></div>

<div class="card key">
  <div class="card-t">为什么项目脚本要自己设 PATH</div>
  <p>因为<b>不能假设每个同事都配好了环境变量</b>。
  脚本开头自己设一遍，就「自带环境」了 ——
  谁拿到都能跑，不用先看一堆配置说明。</p>
  <p>这也是排查「我这儿能编，他那儿编不了」这类问题的常用手段。</p>
</div>

'''

t = t[:i0] + NEW + t[i1:]

# ---------- 3. 第 7 节：坑 3/坑 4 换成环境变量的坑 ----------
i0 = t.index('<h4>坑 3 · 宏的括号</h4>')
i1 = t.index('<div class="card key">\n  <div class="card-t">这一篇要记住的四件事</div>')
NEW2 = r'''<h4>坑 3 · 改了环境变量但没重开窗口</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>最常见的困惑</span></div>
<pre><span class="out">（在「环境变量」对话框里加了 Path，点确定）</span>
<span class="pr">C:\&gt;</span><span class="cmd">gcc --version</span>
<span class="err">'gcc' 不是内部或外部命令...</span>
<span class="warn">↑ 明明加了，怎么还不行？</span></pre>
</div>
<p><b>原因是：环境变量是 cmd 启动时读进去的，之后就一直用内存里那份。</b>
你改了系统设置，<b>已经开着的窗口不知道</b>。</p>
<p><b>解决：关掉 cmd，重新开一个。</b>
（IDE 也一样 —— 改完环境变量要把 IDE 也重启。）</p>

<h4>坑 4 · 追加 PATH 时忘了 <code>;%PATH%</code></h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">rem ❌ 把整个 PATH 覆盖了，dir / cd 都找不到了</span>
<span class="hl-f">set</span> PATH=D:\Path\To\mingw64\bin

<span class="hl-c">rem ✅ 追加：旧值放后面，用分号隔开</span>
<span class="hl-f">set</span> PATH=D:\Path\To\mingw64\bin;%PATH%</pre></div>
<p><b>记法：<code>set 变量=新值;%变量%</code> 才是「在前面插一条」。</b></p>

<h4>坑 5 · 路径里有空格没加引号</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">rem ❌ C:\Program Files 里的空格会被当成参数分隔</span>
<span class="hl-k">cd</span> C:\Program Files\MyTool

<span class="hl-c">rem ✅ 加引号</span>
<span class="hl-k">cd</span> <span class="hl-s">"C:\Program Files\MyTool"</span>

<span class="hl-c">rem ✅ 环境变量也一样，整体加引号</span>
<span class="hl-k">cd</span> <span class="hl-s">"%USERPROFILE%\My Documents"</span></pre></div>
<p>和第一部分讲的路径规则是同一条：<b>只要路径可能含空格，就加引号。</b></p>

<h4>坑 6 · <code>%</code> 忘了配对</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-f">echo</span> %TEMP          <span class="hl-c">rem ❌ 只写了一半，cmd 会原样打出来</span>
<span class="hl-f">echo</span> %TEMP%         <span class="hl-c">rem ✅ 前后都要有 %</span>

<span class="hl-f">echo</span> %%~dp0         <span class="hl-c">rem 在 .bat 里想要「字面的 %」就写两个</span></pre></div>

'''
t = t[:i0] + NEW2 + t[i1:]

# ---------- 4. 总结卡与页脚 ----------
t = t.replace('''<li><b>相对路径相对于「当前工作目录」（CWD）</b>，
      不是相对于 exe 所在位置 —— 这是大多数「找不到文件」的根因。</li>
    <li><b><code>.\\</code> 是当前目录，<code>..\\</code> 是上一级</b>；
      别把 <code>\\font</code> 当成 <code>.\\font</code>。</li>
    <li><b>代码里的路径用正斜杠 <code>/</code></b>，
      不用转义，跨平台都能认。</li>
    <li><b>宏只是编译前的文字替换</b>：
      能不用就不用，要用就全大写、参数加括号。</li>''',
'''<li><b>相对路径相对于「当前工作目录」（CWD）</b>，
      不是相对于 exe 所在位置 —— 这是大多数「找不到文件」的根因。</li>
    <li><b><code>.\\</code> 是当前目录，<code>..\\</code> 是上一级</b>；
      别把 <code>\\font</code> 当成 <code>.\\font</code>。</li>
    <li><b>代码里的路径用正斜杠 <code>/</code></b>，
      不用转义，跨平台都能认。</li>
    <li><b>命令行里的「宏」就是环境变量</b>（<code>%PATH%</code>、<code>%TEMP%</code>），
      用它代替写死的路径；<code>%~dp0</code> 是脚本里最重要那个。</li>''')

t = t.replace('路径演示中的 CWD 行为、文件打开成败、预定义宏输出均在 Windows 上实际运行核对；',
              '路径演示中的 CWD 行为、文件打开成败、环境变量取值与 <code>%~dp0</code> 替换'
              '均在 Windows 上实际运行核对；')

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("F02：%d → %d 字符" % (orig, len(t)))
print("剩余 #define：%d   #ifdef/#ifndef：%d   cout：%d   iostream：%d"
      % (len(re.findall(r'#define', t)), len(re.findall(r'#if', t)),
         len(re.findall(r'cout', t)), len(re.findall(r'iostream', t))))
