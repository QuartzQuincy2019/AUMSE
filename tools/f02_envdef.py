# -*- coding: utf-8 -*-
"""F02 两大补充 + 修掉一个结构 bug。

1) 「什么是环境变量」—— 之前只讲了怎么用，没讲定义。补一节明确的定义。
2) Visual Studio 的 $(...) 属性宏 —— 输出目录的
   $(SolutionDir)$(Platform)\\$(Configuration)\\ 和
   附加包含目录的 $(SolutionDir) 到底是什么。
   数值全部用 MSBuild（VS 2026 · 18.10.3）实际展开核对。
3) 修 bug：文件里有两个 id="s6"（旧的「项目里的实际用处」被漏删，
   只删掉了目录项）。把它改造成新的第 8 节。
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
done = []


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        print("  !! %s：命中 %d 次" % (label, n))
        return False
    t = t.replace(old, new, 1)
    done.append(label)
    return True


# =====================================================================
# 1) 目录：改写第 4 节标题 + 新增第 8 节
# =====================================================================
sub('  <a href="#s4">4 · 环境变量就是一批「宏」</a>',
    '  <a href="#s4">4 · 什么是环境变量</a>\n'
    '  <a href="#s4b" class="sub">4.1 它和「编译器宏」不是一回事</a>\n'
    '  <a href="#s4c" class="sub">4.2 它是怎么工作的</a>',
    "目录：第 4 节")

sub('  <a href="#s7">7 · 常见坑</a>',
    '  <a href="#s7">7 · 常见坑</a>\n'
    '  <a href="#s8">8 · 另一种宏：VS 的 <code>$(...)</code></a>\n'
    '  <a href="#s8a" class="sub">8.1 输出目录里的那串是什么</a>\n'
    '  <a href="#s8b" class="sub">8.2 附加包含目录里的 $(SolutionDir)</a>\n'
    '  <a href="#s8c" class="sub">8.3 常用属性宏一览</a>\n'
    '  <a href="#s8d" class="sub">8.4 和 %环境变量% 的关系</a>',
    "目录：新增第 8 节")

# =====================================================================
# 2) 第 4 节：补「什么是环境变量」的定义
# =====================================================================
sub('<h2 id="s4"><span class="n">4</span>环境变量就是一批「宏」</h2>\n\n'
    '<p>先说一个容易被搞混的事：<b>「宏」这个词在不同场合指不同的东西</b>。</p>',
    '''<h2 id="s4"><span class="n">4</span>什么是环境变量</h2>

<div class="card key">
  <div class="card-t">定义</div>
  <p><b>环境变量（environment variable）是操作系统为每个程序准备的一批
  「名字 = 值」的小纸条。</b></p>
  <p>程序启动时，系统把这一叠纸条交给它；程序想知道什么，
  就按<b>名字</b>去查<b>值</b>。</p>
  <p>在 cmd 里，用 <code>%名字%</code> 就能取到值。例如
  <code>%TEMP%</code> → <code>C:\\Users\\Your_Username\\AppData\\Local\\Temp</code>。</p>
</div>

<h4>具体一点：它长什么样</h4>
<p>在 cmd 里敲 <code>set</code>，会看到几十行「名字=值」，那就是全部环境变量：</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>set：列出全部</span></div>
<pre><span class="pr">C:\\&gt;</span><span class="cmd">set</span>
<span class="out">ALLUSERSPROFILE=C:\\ProgramData</span>
<span class="out">APPDATA=C:\\Users\\Your_Username\\AppData\\Roaming</span>
<span class="out">COMPUTERNAME=MY-PC</span>
<span class="out">PATH=C:\\Windows\\system32;C:\\Windows;...</span>
<span class="out">TEMP=C:\\Users\\Your_Username\\AppData\\Local\\Temp</span>
<span class="out">USERNAME=Your_Username</span>
<span class="out">...</span>

<span class="pr">C:\\&gt;</span><span class="cmd">set TEMP</span>
<span class="out">TEMP=C:\\Users\\Your_Username\\AppData\\Local\\Temp</span></pre>
</div>

<h4>三个关键性质</h4>
<table>
<thead><tr><th style="width:22%">性质</th><th>含义</th><th style="width:34%">为什么重要</th></tr></thead>
<tbody>
<tr><td><b>① 是「名字→值」的对照</b></td>
    <td>名字固定，值可以变</td>
    <td>代码里写名字，就<b>不依赖具体路径</b></td></tr>
<tr><td><b>② 由系统 / 用户设置</b></td>
    <td>不在代码里，在系统里</td>
    <td>换台电脑只改系统设置，<b>代码一个字不用动</b></td></tr>
<tr><td><b>③ 程序启动时读入</b></td>
    <td>启动后再改系统设置，<b>已经跑着的程序不知道</b></td>
    <td>这就是「改了 PATH 必须重开 cmd」的原因</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">用一句话说清它的价值</div>
  <p><b>环境变量是「把会变的东西从代码里搬出去」的标准做法。</b></p>
  <p>你的程序要用临时目录 —— 不要写死 <code>C:\\Users\\张三\\AppData\\...</code>，
  因为同事的用户名不叫张三。写 <code>%TEMP%</code>，
  <b>系统会替你填上对的那个</b>。</p>
</div>

<h3 id="s4b">4.1 它和「编译器宏」不是一回事</h3>

<p>「宏」这个词在不同场合指不同的东西，这是最容易混的地方：</p>

<table>
<thead><tr><th style="width:24%">场合</th><th>「宏」指的是</th><th style="width:22%">写法</th><th style="width:20%">谁替换它</th></tr></thead>
<tbody>
<tr><td><b>命令行 / 操作系统</b></td>
    <td><b>环境变量</b></td>
    <td class="c">%PATH%</td>
    <td>cmd（执行命令前）</td></tr>
<tr><td><b>Visual Studio（本篇第 8 节）</b></td>
    <td><b>属性宏</b></td>
    <td class="c">$(SolutionDir)</td>
    <td>MSBuild（生成时）</td></tr>
<tr><td>编译器预处理</td>
    <td><code>#define</code> 的文本替换</td>
    <td class="c">#define MAX 100</td>
    <td>预处理器（编译前）</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">它们共同的思路</div>
  <p><b>都是「用一小段符号，代表一段会变的内容」。</b>
  但<b>由谁替换、什么时候替换、在哪里能写</b>完全不同 ——
  不能互相通用。</p>
  <p>本节的 <code>%...%</code> 只在<b>命令行</b>里由 cmd 替换；
  <code>$(...)</code> 只在 <b>VS 的工程配置</b>里由 MSBuild 替换
  （见第 8 节）；<code>#define</code> 只在<b>源文件</b>里由预处理器替换。</p>
</div>

<h3 id="s4c">4.2 它是怎么工作的</h3>

<p>把「设置 → 启动 → 读取 → 替换」这条链走一遍，很多现象就都解释得通了。</p>

<div class="lifecycle">
  <div class="st"><div class="t">① 设置</div>
    <div class="d">在「环境变量」对话框里，<br>或 <code>set X=Y</code> 临时设</div></div>
  <div class="st"><div class="t">② 启动程序</div>
    <div class="d">你打开 cmd（或 IDE、<br>双击 exe）</div></div>
  <div class="st"><div class="t">③ 复制一份</div>
    <div class="d">系统把当时的全部变量<br><b>拷进这个进程</b></div></div>
  <div class="st"><div class="t">④ 读取 / 替换</div>
    <div class="d">程序或 cmd 按名字取值<br>（<code>%X%</code> 被替换成值）</div></div>
</div>

<div class="card key">
  <div class="card-t">第 ③ 步解释了几乎所有「环境变量怪现象」</div>
  <ul>
    <li><b>改了系统设置，已经开着的窗口不生效</b> ——
      它在第 ② 步就已经把旧的那份拷走了。<b>必须重开。</b></li>
    <li><b>在窗口里 <code>set X=Y</code>，别的窗口看不到</b> ——
      只改了当前进程自己那份副本，没写回系统。</li>
    <li><b>IDE 里能编、命令行不能（或反过来）</b> ——
      两者是不同时间启动的进程，拿到的可能是不同的两份。</li>
    <li><b>子进程能继承父进程的环境变量</b> ——
      cmd 里启动的程序，会拿到 cmd 那一份（加上你临时 set 的）。</li>
  </ul>
</div>

<h4>「临时设」与「永久设」的区别</h4>
<table>
<thead><tr><th style="width:26%"></th><th>临时（<code>set X=Y</code>）</th><th>永久（对话框里改）</th></tr></thead>
<tbody>
<tr><td><b>存在哪</b></td><td>当前进程的内存里</td><td>注册表（系统或用户）</td></tr>
<tr><td><b>影响范围</b></td><td><b>只有这个窗口</b>及其子进程</td><td>以后所有新进程</td></tr>
<tr><td><b>关掉窗口后</b></td><td><span class="tag r">消失</span></td><td><span class="tag g">还在</span></td></tr>
<tr><td><b>适合</b></td><td>试一下能不能跑通</td><td>真正配置开发环境</td></tr>
</tbody>
</table>

<h4>程序里怎么读它</h4>
<p>三种语言读环境变量的写法，可以对照着记：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">读取环境变量</span><span class="cp">复制</span></div><pre><span class="hl-c">/* C：用 getenv，取不到返回 NULL */</span>
<span class="hl-k">const</span> <span class="hl-k">char</span> *tmp = <span class="hl-f">getenv</span>(<span class="hl-s">"TEMP"</span>);
<span class="hl-k">if</span> (tmp != <span class="hl-n">NULL</span>) <span class="hl-f">printf</span>(<span class="hl-s">"临时目录: %s\\n"</span>, tmp);

<span class="hl-c">/* cmd 批处理 */</span>
<span class="hl-f">echo</span> 临时目录: %TEMP%

<span class="hl-c">/* Python */</span>
<span class="hl-k">import</span> os
<span class="hl-f">print</span>(os.environ.<span class="hl-f">get</span>(<span class="hl-s">"TEMP"</span>))</pre></div>

<div class="card tip">
  <div class="card-t">注意 <code>getenv</code> 可能返回 <code>NULL</code></div>
  <p>这个变量<b>不一定存在</b> —— 别的机器上可能没设。
  所以一定要判断，否则后面用这个指针就会崩。</p>
  <p>这和第五讲「<code>malloc</code> 之后要判 <code>NULL</code>」是同一条原则：
  <b>凡是「可能拿不到」的东西，都要先检查再使用。</b></p>
</div>

<h4>再看一眼效果</h4>
<p>在 cmd 里敲这几条，看它替换成什么：</p>''',
    "第 4 节：补入定义与工作原理")

# 「先看一眼效果」那一小节的标题降级（现在它在 4.2 之后）
sub('<h4>再看一眼效果</h4>\n<p>在 cmd 里敲这几条，看它替换成什么：</p>\n\n'
    '<div class="term">\n'
    '  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>\n'
    '    <span>看环境变量的实际值</span></div>',
    '<h4>再看一眼效果</h4>\n<p>在 cmd 里敲这几条，看它替换成什么：</p>\n\n'
    '<div class="term">\n'
    '  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>\n'
    '    <span>看环境变量的实际值</span></div>',
    "占位（无改动）")

# 删掉重复的旧「查看全部环境变量」小节（已并入上面的 set 演示）
sub('''<h4>查看全部环境变量</h4>
<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>列出所有环境变量</span></div>
<pre><span class="pr">C:\\&gt;</span><span class="cmd">set</span>
<span class="out">ALLUSERSPROFILE=C:\\ProgramData</span>
<span class="out">APPDATA=C:\\Users\\Your_Username\\AppData\\Roaming</span>
<span class="out">CommonProgramFiles=C:\\Program Files\\Common Files</span>
<span class="out">COMPUTERNAME=MY-PC</span>
<span class="out">...</span>
<span class="warn">（几十行，用 set 名字 可以只看一个）</span>

<span class="pr">C:\\&gt;</span><span class="cmd">set TEMP</span>
<span class="out">TEMP=C:\\Users\\Your_Username\\AppData\\Local\\Temp</span></pre>
</div>

''', '', "删除重复的「查看全部环境变量」小节")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("F02 第 1 步：%d → %d 字符" % (orig, len(t)))
for d in done:
    print("  ✓ " + d)
