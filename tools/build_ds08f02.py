# -*- coding: utf-8 -*-
"""生成 _ds_08_F02_相对文件路径与宏.html"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from tut import build

EXTRA = """
/* 目录树 */
.tree{margin:16px 0;font-family:var(--mono);font-size:13.5px;line-height:1.85;
  background:var(--bg-soft);border:1px solid var(--line-2);border-radius:10px;
  padding:13px 16px;overflow:auto;color:var(--fg)}
.tree .d{color:var(--blue);font-weight:600}
.tree .f{color:var(--fg-2)}
.tree .c{color:var(--fg-3)}
.tree .me{background:var(--amber-soft);border-radius:4px;padding:0 4px;font-weight:600}

/* 路径解析示意 */
.resolve{margin:16px 0;border:1px solid var(--line-2);border-radius:10px;
  overflow:hidden;background:#fff}
.resolve .row{display:flex;align-items:baseline;gap:10px;padding:9px 14px;
  border-bottom:1px solid var(--line);font-family:var(--mono);font-size:13px;
  transition:background .14s}
.resolve .row:last-child{border-bottom:0}
.resolve .row:hover{background:var(--blue-soft)}
.resolve .row .k{color:var(--fg-3);font-family:var(--sans);font-size:12.5px;
  min-width:96px;flex:0 0 auto}
.resolve .row .v{color:var(--fg);word-break:break-all}
.resolve .row .v b{color:var(--blue)}
"""

TOC = """  <a href="#s1">1 · 绝对路径与相对路径</a>
  <a href="#s2">2 · 三个特殊符号</a>
  <a href="#s3">3 · 相对路径「相对于谁」</a>
  <a href="#s4">4 · 宏是什么</a>
  <a href="#s5">5 · 预定义宏与自定义宏</a>
  <a href="#s6">6 · 项目里的实际用处</a>
  <a href="#s7">7 · 常见坑</a>"""

BODY = r"""<h1>相对文件路径与宏</h1>
<p class="sub-title">UME 项目组内部教程 · 08-F02（File）· 与本项目施行密切相关</p>
<p>
  <span class="tag">已学：cmd 初步</span>
  <span class="tag">已学：字符串</span>
  <span class="tag b">本讲：文件放在哪、怎么找到它</span>
</p>

<div class="card note">
  <div class="card-t">为什么这一篇对本项目重要</div>
  <p>UME 要<b>读取字体文件</b>、加载配置、导出 SVG —— 这些都涉及「文件在哪」。</p>
  <p>而实际开发中最常遇到的一类怪事就是：</p>
  <p style="margin-left:14px"><b>「我在 IDE 里跑得好好的，双击 exe 就找不到字体了。」</b></p>
  <p>原因几乎总是<b>相对路径</b>。这一篇把它讲清楚，很短。</p>
  <p>文中所有演示均在 Windows 上实际运行核对。</p>
</div>

<!-- ============================================================ -->
<h2 id="s1"><span class="n">1</span>绝对路径与相对路径</h2>

<table>
<thead><tr><th style="width:24%"></th><th>绝对路径</th><th>相对路径</th></tr></thead>
<tbody>
<tr><td><b>长相</b></td>
    <td class="c" style="font-size:12.5px">E:\QKMansion\UME\font\NotoSansMongolian-Regular.ttf</td>
    <td class="c" style="font-size:12.5px">font\NotoSansMongolian-Regular.ttf</td></tr>
<tr><td><b>含不含盘符</b></td><td>含，从磁盘根开始</td><td>不含</td></tr>
<tr><td><b>唯一吗</b></td><td><b>唯一</b>，写死了</td><td><b>不唯一</b>，要看你在哪</td></tr>
<tr><td><b>换台机器</b></td><td><span class="tag r">会失效</span>（盘符可能不同）</td>
    <td><span class="tag g">通常还能用</span></td></tr>
<tr><td><b>适合</b></td><td>临时调试、写脚本</td><td><b>项目里正式使用</b></td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">为什么项目里要用相对路径</div>
  <p>因为绝对路径会写死「你机器上的位置」。同事 clone 到
  <code>D:\work\UME</code>，你的 <code>E:\...</code> 就全废了。</p>
  <p>相对路径描述的是<b>「相对于项目根目录的位置」</b>，
  只要项目内部结构不变，换到谁机器上都能用。</p>
</div>

<!-- ============================================================ -->
<h2 id="s2"><span class="n">2</span>三个特殊符号</h2>

<p>假设项目结构是这样，你正站在 <code>UME</code> 目录里：</p>

<div class="tree">
<span class="d">E:\QKMansion\UME\</span>          <span class="c">← 当前目录（CWD）</span>
├─ <span class="d">font\</span>
│   └─ <span class="f">NotoSansMongolian-Regular.ttf</span>
├─ <span class="d">web\</span>
│   └─ <span class="f">UME.html</span>
├─ <span class="d">report\</span>
└─ <span class="f">FONT_ANALYSIS.md</span>
</div>

<div class="resolve">
  <div class="row"><span class="k">.\ 或 什么都不写</span>
    <span class="v"><b>当前目录</b> —— <code>font\Noto....ttf</code>
      等于 <code>.\font\Noto....ttf</code></span></div>
  <div class="row"><span class="k">..\</span>
    <span class="v"><b>上一级目录</b> —— <code>..\</code> 就是
      <code>E:\QKMansion\</code></span></div>
  <div class="row"><span class="k">. （单个点）</span>
    <span class="v">就是「当前目录」本身</span></div>
  <div class="row"><span class="k">\ （开头一个反斜杠）</span>
    <span class="v">当前盘符的<b>根目录</b> —— <code>\Windows</code> 指
      <code>E:\Windows</code></span></div>
</div>

<p>所以 <code>..\..\font\x.ttf</code> 的意思是
「往上两级，再进 font 目录，找 x.ttf」。</p>

<div class="card warn">
  <div class="card-t">千万别把 <code>\</code> 和 <code>.\</code> 搞混</div>
  <table style="margin:8px 0 0">
  <tbody>
  <tr><td class="c" style="width:26%">.\font\a.ttf</td>
      <td>当前目录下的 <code>font</code> 文件夹里 → <b>你要的</b></td></tr>
  <tr><td class="c">\font\a.ttf</td>
      <td><b>当前盘符根目录</b>下的 <code>font</code> → 通常是
        <code>E:\font\a.ttf</code>，<b>不是你要的</b></td></tr>
  </tbody></table>
  <p style="margin-top:10px">少了那个点，位置会跑到磁盘根目录去 ——
  这是很难一眼看出的错误。</p>
</div>

<!-- ============================================================ -->
<h2 id="s3"><span class="n">3</span>相对路径「相对于谁」</h2>

<p>这是本篇最重要的一点。</p>

<div class="card key">
  <div class="card-t">结论</div>
  <p><b>相对路径是相对于「当前工作目录」（CWD），
  不是相对于 exe 文件所在的位置。</b></p>
  <p>而 CWD 是<b>「你敲命令时待在哪个目录」</b>。</p>
</div>

<p>下面这个实验能一次说清。程序只做一件事：打印 CWD 和它自己的路径。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">打印 CWD 与程序自身路径</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;direct.h&gt;</span>          <span class="hl-c">/* Windows 下的 _getcwd */</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">int</span> argc, <span class="hl-k">char</span> *argv[]) {
    <span class="hl-k">char</span> buf[<span class="hl-n">4096</span>];
    <span class="hl-f">_getcwd</span>(buf, <span class="hl-k">sizeof</span>(buf));

    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"当前工作目录 (CWD) = "</span> &lt;&lt; buf &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"程序自己的路径     = "</span> &lt;&lt; (argc &gt; <span class="hl-n">0</span> ? argv[<span class="hl-n">0</span>] : <span class="hl-s">"?"</span>) &lt;&lt; <span class="hl-f">endl</span>;
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<p>把编译出的 <code>path1.exe</code> 放到 <code>build\</code> 里，
然后在<b>两个不同的目录</b>各运行一次：</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>在 build 目录里运行</span></div>
<pre><span class="pr">E:\...\build&gt;</span><span class="cmd">path1.exe</span>
<span class="out">当前工作目录 (CWD) = E:\...\build</span>
<span class="out">程序自己的路径     = E:\...\build\path1.exe</span></pre>
</div>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>在上一级目录里运行同一个 exe</span></div>
<pre><span class="pr">E:\...&gt;</span><span class="cmd">build\path1.exe</span>
<span class="out">当前工作目录 (CWD) = E:\...</span>
<span class="out">程序自己的路径     = E:\...\build\path1.exe</span></pre>
</div>

<p>两次的<b>程序路径一样</b>，但 <b>CWD 不同</b>。
这说明：CWD 由「你从哪运行」决定，与 exe 放哪无关。</p>

<h4>这会导致什么后果</h4>
<p>写一个只做一件事的程序：用相对路径打开 <code>data.txt</code>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">用相对路径读文件</span><span class="cp">复制</span></div><pre><span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;fstream&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;string&gt;</span>
<span class="hl-k">using</span> <span class="hl-k">namespace</span> std;

<span class="hl-k">int</span> <span class="hl-f">main</span>() {
    ifstream in(<span class="hl-s">"data.txt"</span>);          <span class="hl-c">/* 相对路径 */</span>
    <span class="hl-k">if</span> (in.<span class="hl-f">is_open</span>()) {
        string line;
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"打开成功，内容:"</span> &lt;&lt; <span class="hl-f">endl</span>;
        <span class="hl-k">while</span> (<span class="hl-f">getline</span>(in, line)) <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"  "</span> &lt;&lt; line &lt;&lt; <span class="hl-f">endl</span>;
        in.<span class="hl-f">close</span>();
    } <span class="hl-k">else</span> {
        <span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"打开 data.txt 失败（当前目录里没有它）"</span> &lt;&lt; <span class="hl-f">endl</span>;
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}</pre></div>

<p>把 <code>pathread.exe</code> 放进 <code>build\</code>，
<code>data.txt</code> 也放在 <code>build\</code>，然后做三次实验：</p>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>A · 在 build 目录里运行（data.txt 就在旁边）</span></div>
<pre><span class="pr">E:\...\build&gt;</span><span class="cmd">pathread.exe</span>
<span class="out">打开 data.txt 成功，内容:</span>
<span class="out">  hello from build dir</span></pre>
</div>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>B · 在上一级目录里运行同一个 exe（那里没有 data.txt）</span></div>
<pre><span class="pr">E:\...&gt;</span><span class="cmd">build\pathread.exe</span>
<span class="out">打开 data.txt 失败（当前目录里没有它）</span></pre>
</div>

<div class="term">
  <div class="tbar"><span class="d r"></span><span class="d y"></span><span class="d g"></span>
    <span>C · 把 data.txt 也放到上一级，再在上一级运行同一个 exe</span></div>
<pre><span class="pr">E:\...&gt;</span><span class="cmd">build\pathread.exe</span>
<span class="out">打开 data.txt 成功，内容:</span>
<span class="out">  hello from parent dir</span></pre>
</div>

<div class="card key">
  <div class="card-t">三次实验说明了什么</div>
  <p><b>完全相同的 exe，读到的文件却不一样</b> ——
  因为 <code>"data.txt"</code> 这个相对路径每次都从 <b>CWD</b> 开始找。</p>
  <p>这正好解释了那个经典现象：</p>
  <ul>
    <li><b>IDE 里运行正常</b> —— IDE 通常把 CWD 设成项目目录</li>
    <li><b>双击 exe 就找不到文件</b> —— CWD 变成了 exe 所在目录</li>
    <li><b>从命令行运行有时行有时不行</b> —— 取决于你在哪敲命令</li>
  </ul>
</div>

<div class="card tip">
  <div class="card-t">怎么避免</div>
  <p>三条实用做法：</p>
  <ol>
    <li><b>资源文件跟着 exe 一起放</b>（比如统一放 <code>assets\</code>），
      并约定「程序从自己的目录找资源」。</li>
    <li><b>Qt 里用资源系统</b>：把文件写进 <code>.qrc</code>，
      用 <code>:/font/x.ttf</code> 访问。
      <b>资源被编译进 exe，彻底没有路径问题</b> —— 这是 Qt 项目最省心的做法。</li>
    <li><b>需要时自己算绝对路径</b>：
      用 <code>QCoreApplication::applicationDirPath()</code> 拿到 exe 所在目录，
      再拼上资源子路径。</li>
  </ol>
</div>

<!-- ============================================================ -->
<h2 id="s4"><span class="n">4</span>宏是什么</h2>

<p>「宏」这个词听起来玄，其实就是<b>编译之前的一次文字替换</b>。</p>

<div class="mnemonic">
  <b>宏 = 编译器正式开工前，先做的一遍「查找并替换」。</b>
</div>

<p>过程分两步：</p>
<div class="lifecycle">
  <div class="st"><div class="t">预处理</div>
    <div class="d">处理 <code>#</code> 开头的行：<br>替换宏、展开 <code>#include</code></div></div>
  <div class="st"><div class="t">编译</div>
    <div class="d">把处理后的代码<br>真正翻译成机器指令</div></div>
</div>

<h4><code>#define</code>：定义一个宏</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">宏替换</span><span class="cp">复制</span></div><pre><span class="hl-p">#define</span> MAX_HP <span class="hl-n">9999</span>          <span class="hl-c">/* 定义 */</span>

<span class="hl-k">int</span> hp = MAX_HP;              <span class="hl-c">/* 预处理后变成：int hp = 9999; */</span></pre></div>

<p>所以宏<b>不是变量</b>，它没有类型、不占内存 ——
只是在编译前把那个名字换成了后面的内容。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">带参数的宏</span><span class="cp">复制</span></div><pre><span class="hl-p">#define</span> SQUARE(x) ((x) * (x))

<span class="hl-f">SQUARE</span>(<span class="hl-n">3</span>)                  <span class="hl-c">/* 变成 ((3) * (3)) = 9 */</span></pre></div>

<div class="card warn">
  <div class="card-t">带参数的宏要加括号，而且尽量别用</div>
  <p><code>#define SQUARE(x) x * x</code> 少了括号，
  那 <code>SQUARE(1+2)</code> 会变成 <code>1+2 * 1+2</code> = <b>5</b>，
  而不是 9。<b>这是宏最经典的坑。</b></p>
  <p>更好的做法是用 <code>const</code> 常量或 <code>inline</code> 函数：</p>
  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">const</span> <span class="hl-k">int</span> kMaxHp = <span class="hl-n">9999</span>;              <span class="hl-c">/* 有类型，能调试 */</span>
<span class="hl-k">inline</span> <span class="hl-k">int</span> <span class="hl-f">square</span>(<span class="hl-k">int</span> x) { <span class="hl-k">return</span> x * x; }  <span class="hl-c">/* 有类型检查 */</span></pre>
  <p><b>宏只在确实做不到的时候才用</b>（下面第 6 节会看到确实需要的场合）。</p>
</div>

<!-- ============================================================ -->
<h2 id="s5"><span class="n">5</span>预定义宏与自定义宏</h2>

<p>编译器自带一批宏，直接就能用。最常用的几个：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">常用预定义宏</span><span class="cp">复制</span></div><pre><span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"程序编译于 "</span> &lt;&lt; __DATE__ &lt;&lt; <span class="hl-s">" "</span> &lt;&lt; __TIME__ &lt;&lt; <span class="hl-f">endl</span>;
<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"这是第 "</span> &lt;&lt; __LINE__ &lt;&lt; <span class="hl-s">" 行"</span> &lt;&lt; <span class="hl-f">endl</span>;
<span class="hl-f">cout</span> &lt;&lt; <span class="hl-s">"文件名   "</span> &lt;&lt; __FILE__ &lt;&lt; <span class="hl-f">endl</span>;</pre></div>

<div class="out-wrap"><div class="cap">运行结果</div><pre>程序编译于 Oct 15 2026 15:31:19
这是第 35 行
文件名   E:\QKMansion\CSX10\w\UME\tools\_c_check\path1.cpp</pre></div>

<table>
<thead><tr><th style="width:22%">宏</th><th>内容</th><th style="width:26%">典型用途</th></tr></thead>
<tbody>
<tr><td class="c">__FILE__</td><td>当前源文件的路径</td><td>打印「出错在哪个文件」</td></tr>
<tr><td class="c">__LINE__</td><td>当前行号</td><td>打印「出错在第几行」</td></tr>
<tr><td class="c">__DATE__</td><td>编译日期</td><td>版本信息</td></tr>
<tr><td class="c">__TIME__</td><td>编译时间</td><td>「这个 exe 是什么时候编的」</td></tr>
<tr><td class="c">__func__</td><td>当前函数名</td><td>日志</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t"><code>__FILE__</code> 和 <code>__LINE__</code> 是调试利器</div>
  <p>写一个自己用的「检查并报错」宏：</p>
  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-p">#define</span> CHECK(cond) \\
    <span class="hl-k">do</span> { <span class="hl-k">if</span> (!(cond)) \\
        <span class="hl-f">cerr</span> &lt;&lt; __FILE__ &lt;&lt; <span class="hl-s">":"</span> &lt;&lt; __LINE__ \\
             &lt;&lt; <span class="hl-s">" 检查失败: "</span> &lt;&lt; #cond &lt;&lt; <span class="hl-f">endl</span>; \\
    } <span class="hl-k">while</span> (<span class="hl-n">0</span>)</pre>
  <p>用的时候写 <code>CHECK(p != NULL);</code>，
  失败时会自动打印<b>哪个文件、哪一行、什么条件</b>。
  （<code>#cond</code> 是「把参数变成字符串」的写法。）</p>
</div>

<h4>条件编译：按环境选代码</h4>
<p>宏还能用来「编不编这段代码」：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">条件编译</span><span class="cp">复制</span></div><pre><span class="hl-p">#ifdef</span> _WIN32
    <span class="hl-c">/* 只有 Windows 才编译这段 */</span>
    <span class="hl-f">_getcwd</span>(buf, <span class="hl-k">sizeof</span>(buf));
<span class="hl-p">#else</span>
    <span class="hl-c">/* 其他平台编译这段 */</span>
    <span class="hl-f">getcwd</span>(buf, <span class="hl-k">sizeof</span>(buf));
<span class="hl-p">#endif</span></pre></div>

<p>这就是「跨平台代码」的常见写法：<b>同一份源文件，不同平台编译出不同结果</b>。
上面的打印 CWD 那个例子里就用了它。</p>

<!-- ============================================================ -->
<h2 id="s6"><span class="n">6</span>项目里的实际用处</h2>

<h4>① 资源路径：把绝对路径变相对</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">不要写死盘符</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 写死绝对路径：换台机器就废 */</span>
QFontDatabase::<span class="hl-f">addApplicationFont</span>(
    <span class="hl-s">"E:/QKMansion/UME/font/NotoSansMongolian-Regular.ttf"</span>);

<span class="hl-c">/* ✅ 相对项目结构；或直接用 Qt 资源（推荐） */</span>
QFontDatabase::<span class="hl-f">addApplicationFont</span>(<span class="hl-s">"assets/font/NotoSansMongolian-Regular.ttf"</span>);
QFontDatabase::<span class="hl-f">addApplicationFont</span>(<span class="hl-s">":/font/NotoSansMongolian-Regular.ttf"</span>);</pre></div>

<h4>② 用宏做「编译开关」</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">调试开关</span><span class="cp">复制</span></div><pre><span class="hl-p">#define</span> UME_DEBUG <span class="hl-n">1</span>

<span class="hl-p">#if</span> UME_DEBUG
    <span class="hl-f">qDebug</span>() &lt;&lt; <span class="hl-s">"字形匹配: gid ="</span> &lt;&lt; gid;
<span class="hl-p">#endif</span></pre></div>
<p>发布时把 <code>1</code> 改成 <code>0</code>，调试输出<b>整段消失</b>
（连编译都不编），不拖慢正式版本。</p>

<h4>③ 避免头文件被重复包含</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">include guard</span><span class="cp">复制</span></div><pre><span class="hl-p">#ifndef</span> UME_FONT_H
<span class="hl-p">#define</span> UME_FONT_H

<span class="hl-c">/* 头文件内容写在这里 */</span>

<span class="hl-p">#endif</span></pre></div>
<p>或者用更省事的 <code>#pragma once</code>。
这是每个头文件都该有的第一行和最后一行，08-F03 会讲为什么需要它。</p>

<h4>④ 构建模式判断</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">区分调试版与发布版</span><span class="cp">复制</span></div><pre><span class="hl-p">#ifdef</span> QT_NO_DEBUG
    <span class="hl-c">/* 发布版：不做耗时检查 */</span>
<span class="hl-p">#else</span>
    <span class="hl-c">/* 调试版：加额外校验 */</span>
<span class="hl-p">#endif</span></pre></div>

<!-- ============================================================ -->
<h2 id="s7"><span class="n">7</span>常见坑</h2>

<h4>坑 1 · 以为相对路径是相对 exe</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 想当然：以为从 exe 所在目录找 */</span>
ifstream in(<span class="hl-s">"data.txt"</span>);       <span class="hl-c">/* 实际是从 CWD 找！ */</span>

<span class="hl-c">/* ✅ 明确从 exe 所在目录找 */</span>
QString dir = QCoreApplication::<span class="hl-f">applicationDirPath</span>();
ifstream in((dir + <span class="hl-s">"/data.txt"</span>).<span class="hl-f">toStdString</span>());</pre></div>

<h4>坑 2 · 反斜杠被当成转义符</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ C++ 字符串里 \f 是转义符（换页），\n 是换行 */</span>
<span class="hl-k">const</span> <span class="hl-k">char</span> *p = <span class="hl-s">"font\NotoSans.ttf"</span>;    <span class="hl-c">/* \N 不是合法转义，\f 是换页！ */</span>

<span class="hl-c">/* ✅ 三种正确写法 */</span>
<span class="hl-k">const</span> <span class="hl-k">char</span> *a = <span class="hl-s">"font\\NotoSans.ttf"</span>;   <span class="hl-c">/* 双反斜杠 */</span>
<span class="hl-k">const</span> <span class="hl-k">char</span> *b = <span class="hl-s">"font/NotoSans.ttf"</span>;    <span class="hl-c">/* 正斜杠，Windows 也认 */</span>
<span class="hl-k">const</span> <span class="hl-k">char</span> *c = <span class="hl-s">R"(font\NotoSans.ttf)"</span>;  <span class="hl-c">/* 原始字符串，C++11 */</span></pre></div>
<p><b>实用建议：代码里的路径统一用正斜杠 <code>/</code></b>。
Windows 和 Linux 都认，而且不用转义。</p>

<h4>坑 3 · 宏的括号</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">#define</span> SQUARE(x) x * x           <span class="hl-c">/* ❌ SQUARE(1+2) = 1+2*1+2 = 5 */</span>
<span class="hl-p">#define</span> SQUARE(x) ((x) * (x))     <span class="hl-c">/* ✅ = 9 */</span></pre></div>
<p><b>带参数的宏，参数和整体都要加括号</b>，一个都不能省。</p>

<h4>坑 4 · 宏名和变量名撞车</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">#define</span> max <span class="hl-n">100</span>
<span class="hl-k">int</span> max = <span class="hl-n">5</span>;              <span class="hl-c">/* ❌ 预处理后变成 int 100 = 5; 莫名其妙的错 */</span>

<span class="hl-c">/* ✅ 宏名用全大写，避免撞车（这是通用约定） */</span>
<span class="hl-p">#define</span> MAX_HP <span class="hl-n">100</span></pre></div>

<div class="card key">
  <div class="card-t">这一篇要记住的四件事</div>
  <ol>
    <li><b>相对路径相对于「当前工作目录」（CWD）</b>，
      不是相对于 exe 所在位置 —— 这是大多数「找不到文件」的根因。</li>
    <li><b><code>.\</code> 是当前目录，<code>..\</code> 是上一级</b>；
      别把 <code>\font</code> 当成 <code>.\font</code>。</li>
    <li><b>代码里的路径用正斜杠 <code>/</code></b>，
      不用转义，跨平台都能认。</li>
    <li><b>宏只是编译前的文字替换</b>：
      能不用就不用，要用就全大写、参数加括号。</li>
  </ol>
</div>

<div class="card note">
  <div class="card-t">下一步</div>
  <p>你已经会敲命令、也知道文件在哪了。下一个问题是：</p>
  <p><b>「<code>g++ main.cpp -o main.exe</code> 这一行，到底做了什么？」</b>
  为什么有时候报 <code>undefined reference</code>？
  <code>#include</code> 是把文件内容粘进来吗？
  为什么头文件里不能写函数体？</p>
  <p>08-F03《编译与链接、头文件与库》就讲这些 ——
  理解了它，编译报错就不再是天书。</p>
</div>

<footer>
UME 项目组内部教程 · 08-F02（File）《相对文件路径与宏》<br>
路径演示中的 CWD 行为、文件打开成败、预定义宏输出均在 Windows 上实际运行核对；
代码示例以 <b>Consolas</b> 等宽字体呈现。
</footer>"""

build("_ds_08_F02_相对文件路径与宏.html", "实用 · 相对文件路径与宏", TOC, BODY, EXTRA)
