# -*- coding: utf-8 -*-
"""FE-01 / FE-02 / FE-03-F01 / FE-03 的内容"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build

# =====================================================================
# FE-01  HTML 入门与标签语法
# =====================================================================
TOC01 = """  <a href="#s1">1 · HTML 是什么</a>
  <a href="#s2">2 · 所写即所得</a>
  <a href="#s3">3 · 标签语法</a>
  <a href="#s4">4 · 注释语法</a>
  <a href="#s5">5 · 空格无效性</a>
  <a href="#s6">6 · 完整的骨架</a>
  <a href="#s7">7 · 常见错误</a>"""

BODY01 = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p>HTML 是<b>描述网页内容</b>的语言。它不负责好看（那是 CSS 的事），
  只负责「<b>这里是一段话</b>」「<b>这里是一个列表</b>」「<b>这里是一张图</b>」。</p>
  <p>前端系列从这里开始。<b>不需要任何编程基础。</b></p>
</div>

<h2 id="s1"><span class="n">1</span>HTML 是什么</h2>

<p><b>HTML = HyperText Markup Language（超文本标记语言）</b>。
它不是编程语言 —— 没有变量、没有循环、不会「运行」。
它只是<b>给内容打标记</b>。</p>

<table>
<thead><tr><th style="width:26%">它是什么</th><th>说明</th></tr></thead>
<tbody>
<tr><td><b>标记语言</b></td><td>用成对的标记（标签）把内容包起来，说明「这是什么」</td></tr>
<tr><td><b>不是编程语言</b></td><td>没有逻辑、没有计算。<b>写什么就是什么</b></td></tr>
<tr><td><b>浏览器负责渲染</b></td>
    <td>你写的标签，浏览器按规则画成页面</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">三件套的分工</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:18%"></th><th>管什么</th><th>类比</th></tr></thead>
  <tbody>
  <tr><td class="c">HTML</td><td><b>内容</b>：有什么东西</td><td>房子的<b>结构</b>（墙、门、窗）</td></tr>
  <tr><td class="c">CSS</td><td><b>样式</b>：长什么样</td><td>房子的<b>装修</b>（颜色、地板）</td></tr>
  <tr><td class="c">JavaScript</td><td><b>行为</b>：能做什么</td><td>房子的<b>电器</b>（开关、电梯）</td></tr>
  </tbody></table>
  <p style="margin-top:10px">本系列先讲 HTML 与 CSS。<b>UME.html 就是这三者合起来的产物。</b></p>
</div>

<h2 id="s2"><span class="n">2</span>所写即所得</h2>

<p>HTML 最让人安心的一点：<b>你写什么，浏览器就显示什么。</b>
把下面的内容存成 <code>test.html</code>，双击用浏览器打开：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">最小的网页</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p&gt;</span>你好，这是第一段话。<span class="hl-p">&lt;/p&gt;</span>
<span class="hl-p">&lt;p&gt;</span>这是第二段话。<span class="hl-p">&lt;/p&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">浏览器里看到</div><pre>你好，这是第一段话。

这是第二段话。</pre></div>

<p>注意三件事：</p>
<ul>
  <li><code>&lt;p&gt;</code> 和 <code>&lt;/p&gt;</code> <b>自己不会显示出来</b> ——
    它们只是标记，浏览器看了就收起来</li>
  <li>两个 <code>&lt;p&gt;</code> 之间<b>自动多了一个空行</b> ——
    因为 <code>p</code> 就是「段落」，段落之间天然有空隙</li>
  <li>你<b>没有写任何 CSS</b>，浏览器用默认样式渲染 ——
    黑字白底、宋体或雅黑</li>
</ul>

<div class="card tip">
  <div class="card-t">为什么说「所写即所得」</div>
  <p>因为它<b>没有编译步骤、不会报错</b>。你改一个字，刷新浏览器立刻能看到。</p>
  <p>对比一下 C 语言：写完要编译，报错要查行号。
  HTML 错了不报错 —— 它<b>只是默默不按你想的显示</b>。
  这既方便（改得快），也麻烦（错了没提示，靠眼睛看）。</p>
</div>

<h2 id="s3"><span class="n">3</span>标签语法</h2>

<p>一个标签长这样：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">标签的解剖</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p</span> <span class="hl-f">class</span>=<span class="hl-s">"intro"</span><span class="hl-p">&gt;</span>内容<span class="hl-p">&lt;/p&gt;</span>
<span class="arw">└┬┘ └────┬─────┘ └┬┘      └─┬─┘</span>
<span class="arw"> │       │        │          │</span>
<span class="arw"> │       │        │          └─ 结束标签</span>
<span class="arw"> │       │        └─ 开始标签的尖括号闭合</span>
<span class="arw"> │       └─ 属性（名=值）</span>
<span class="arw"> └─ 标签名</span></pre></div>

<table>
<thead><tr><th style="width:22%">部分</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">&lt;p&gt;</td><td><b>开始标签</b>（开标签）</td></tr>
<tr><td class="c">&lt;/p&gt;</td><td><b>结束标签</b>（闭标签）——
  比开始标签多一个 <code>/</code></td></tr>
<tr><td class="c">class="intro"</td>
    <td><b>属性</b>，写在开始标签里。一个标签可以有多个属性，
      用空格隔开</td></tr>
<tr><td class="c">内容</td><td>被包在中间的东西</td></tr>
</tbody>
</table>

<h4>两种标签：成对的与自闭合的</h4>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- 成对：有开始有结束，中间放内容 --&gt;</span>
<span class="hl-p">&lt;p&gt;</span>一段话<span class="hl-p">&lt;/p&gt;</span>
<span class="hl-p">&lt;div&gt;</span>一个块<span class="hl-p">&lt;/div&gt;</span>

<span class="hl-c">&lt;!-- 自闭合：没有内容，写一个就行 --&gt;</span>
<span class="hl-p">&lt;br&gt;</span>              <span class="hl-c">&lt;!-- 换行 --&gt;</span>
<span class="hl-p">&lt;hr&gt;</span>              <span class="hl-c">&lt;!-- 一条横线 --&gt;</span>
<span class="hl-p">&lt;img</span> <span class="hl-f">src</span>=<span class="hl-s">"a.png"</span><span class="hl-p">&gt;</span>   <span class="hl-c">&lt;!-- 图片 --&gt;</span></pre></div>

<div class="card warn">
  <div class="card-t">忘记闭合会怎样</div>
  <p>浏览器<b>不报错</b>，它会自己猜 —— 通常把后面的内容全包进你这个标签里。
  结果就是「样式突然影响了后面一大片」。</p>
  <p><b>所以：成对标签一定要写完整。</b>
  写开标签时顺手把闭标签也打上，回头再填内容。</p>
</div>

<h4>大小写？</h4>
<p>HTML 标签<b>不区分大小写</b>，<code>&lt;P&gt;</code> 和 <code>&lt;p&gt;</code> 一样。
但业界一律<b>写小写</b> —— 看起来整齐，也和 XHTML、框架的写法一致。</p>

<h2 id="s4"><span class="n">4</span>注释语法</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">HTML 注释</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- 这是一条注释，浏览器不会显示它 --&gt;</span>

<span class="hl-p">&lt;p&gt;</span>这段话会显示<span class="hl-p">&lt;/p&gt;</span>
<span class="hl-c">&lt;!-- &lt;p&gt;这段话被注释掉了，不会显示&lt;/p&gt; --&gt;</span></pre></div>

<table>
<thead><tr><th style="width:30%">写法</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">&lt;!-- 注释 --&gt;</td><td>HTML 注释，可跨多行</td></tr>
<tr><td class="c">不能嵌套</td>
    <td><code>&lt;!-- a &lt;!-- b --&gt; c --&gt;</code> 是错的 ——
      注释里不能再写注释</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">注释有什么用</div>
  <ul>
    <li><b>临时屏蔽</b>：不想显示某段，先注释掉，不用删</li>
    <li><b>做标记</b>：<code>&lt;!-- 导航开始 --&gt;</code>，
      长文件里方便定位</li>
    <li><b>留说明</b>：为什么这里要这么写</li>
  </ul>
  <p><b>注意</b>：注释会随文件发给浏览者，右键「查看源代码」就能看到。
  <b>别在注释里写密码或内部信息。</b></p>
</div>

<h4>对照：三种语言的注释</h4>
<table>
<thead><tr><th style="width:22%">语言</th><th>写法</th></tr></thead>
<tbody>
<tr><td class="c">HTML</td><td class="c">&lt;!-- 注释 --&gt;</td></tr>
<tr><td class="c">CSS</td><td class="c">/* 注释 */</td></tr>
<tr><td class="c">C / C++ / JS</td><td class="c">// 单行　　/* 多行 */</td></tr>
</tbody>
</table>

<h2 id="s5"><span class="n">5</span>空格无效性</h2>

<p>这是新手最容易困惑的一点：<b>HTML 会把连续的空格、换行、Tab 全部压成一个空格。</b></p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">写了很多空格和换行</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p&gt;</span>你好          世界<span class="hl-p">&lt;/p&gt;</span>

<span class="hl-p">&lt;p&gt;</span>你好


     世界<span class="hl-p">&lt;/p&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">浏览器里看到的（两段完全一样）</div><pre>你好 世界

你好 世界</pre></div>

<div class="card key">
  <div class="card-t">规则</div>
  <p><b>连续空白 → 一个空格。</b>不管你在源码里敲了多少个空格或多少行。</p>
  <p>所以你可以放心地<b>用换行和缩进把源码排整齐</b> ——
  不会影响显示效果。这是好事：源码可读性全靠它。</p>
</div>

<h4>那想要多个空格怎么办</h4>
<table>
<thead><tr><th style="width:34%">办法</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">&amp;nbsp;</td>
    <td>「不换行空格」，写几个就是几个。
      例：<code>a&amp;nbsp;&amp;nbsp;b</code> → a&nbsp;&nbsp;b</td></tr>
<tr><td class="c">&lt;br&gt;</td><td>换行</td></tr>
<tr><td class="c">&lt;pre&gt;...&lt;/pre&gt;</td>
    <td><b>保留原始格式</b>，空格换行都照原样。代码块就用它</td></tr>
</tbody>
</table>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">pre 保留格式</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;pre&gt;</span>
  第一行
      缩进了四个空格
  第三行
<span class="hl-p">&lt;/pre&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">浏览器里看到</div><pre>  第一行
      缩进了四个空格
  第三行</pre></div>

<h4>还有几个「打不出来」的符号</h4>
<p>有些字符在 HTML 里有特殊含义，要用<b>实体（entity）</b>写：</p>

<table>
<thead><tr><th style="width:22%">想显示</th><th style="width:24%">要写</th><th>为什么</th></tr></thead>
<tbody>
<tr><td class="c">&lt;</td><td class="c">&amp;lt;</td><td><code>&lt;</code> 是标签的开始，直接写会被当成标签</td></tr>
<tr><td class="c">&gt;</td><td class="c">&amp;gt;</td><td>同上</td></tr>
<tr><td class="c">&amp;</td><td class="c">&amp;amp;</td><td><code>&amp;</code> 是实体的开始</td></tr>
<tr><td class="c">"</td><td class="c">&amp;quot;</td><td>属性值用引号包着时会冲突</td></tr>
<tr><td class="c">空格</td><td class="c">&amp;nbsp;</td><td>上面讲过</td></tr>
</tbody>
</table>

<p><code>lt</code> = <b>l</b>ess <b>t</b>han，<code>gt</code> = <b>g</b>reater <b>t</b>han，
<code>amp</code> = <b>amp</b>ersand。<b>记住这三个就够用了。</b></p>

<h2 id="s6"><span class="n">6</span>完整的骨架</h2>

<p>前面都是片段。一个正式的 HTML 文件有固定骨架：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">完整骨架（建议背下来）</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;!DOCTYPE html&gt;</span>
<span class="hl-p">&lt;html</span> <span class="hl-f">lang</span>=<span class="hl-s">"zh-CN"</span><span class="hl-p">&gt;</span>
<span class="hl-p">&lt;head&gt;</span>
  <span class="hl-p">&lt;meta</span> <span class="hl-f">charset</span>=<span class="hl-s">"utf-8"</span><span class="hl-p">&gt;</span>
  <span class="hl-p">&lt;meta</span> <span class="hl-f">name</span>=<span class="hl-s">"viewport"</span> <span class="hl-f">content</span>=<span class="hl-s">"width=device-width, initial-scale=1"</span><span class="hl-p">&gt;</span>
  <span class="hl-p">&lt;title&gt;</span>页面标题<span class="hl-p">&lt;/title&gt;</span>
<span class="hl-p">&lt;/head&gt;</span>
<span class="hl-p">&lt;body&gt;</span>
  <span class="hl-p">&lt;p&gt;</span>这里才是给用户看的内容<span class="hl-p">&lt;/p&gt;</span>
<span class="hl-p">&lt;/body&gt;</span>
<span class="hl-p">&lt;/html&gt;</span></pre></div>

<table>
<thead><tr><th style="width:26%">部分</th><th>作用</th></tr></thead>
<tbody>
<tr><td class="c">&lt;!DOCTYPE html&gt;</td>
    <td>第一行，声明「这是 HTML5」。<b>不写会让浏览器进入怪异模式</b></td></tr>
<tr><td class="c">&lt;html lang="zh-CN"&gt;</td>
    <td>整份文档的根。<code>lang</code> 说明语言，影响断词和朗读</td></tr>
<tr><td class="c">&lt;head&gt;</td>
    <td><b>给浏览器看的信息</b>，不在页面上显示</td></tr>
<tr><td class="c">charset="utf-8"</td>
    <td><b>必须写</b>，否则中文会乱码</td></tr>
<tr><td class="c">viewport</td>
    <td><b>手机上必须写</b>，否则页面被缩得很小</td></tr>
<tr><td class="c">&lt;title&gt;</td>
    <td>浏览器标签页上的文字</td></tr>
<tr><td class="c">&lt;body&gt;</td>
    <td><b>用户能看到的内容</b>全在这里</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">head 与 body 的分工</div>
  <p><b>head = 给机器看的</b>：编码、标题、样式表、脚本。</p>
  <p><b>body = 给人看的</b>：文字、图片、表格、按钮。</p>
  <p>写在 head 里的 <code>&lt;p&gt;</code> <b>不会被显示</b> ——
  这是新手常见的「我写了怎么不出现」。</p>
</div>

<div class="card warn">
  <div class="card-t">那两句 meta 千万别省</div>
  <p><b><code>charset="utf-8"</code></b>：不写，中文可能变成
  <code>ä½ å¥½</code> 这种乱码。</p>
  <p><b><code>viewport</code></b>：不写，手机浏览器会假装自己有 980px 宽，
  把整个页面缩小塞进屏幕 —— 字小到看不清。
  这就是本系列文档为什么在手机上也能正常看的原因。</p>
</div>

<h2 id="s7"><span class="n">7</span>常见错误</h2>

<h4>错误 1 · 标签没闭合</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p&gt;</span>第一段
<span class="hl-p">&lt;p&gt;</span>第二段<span class="hl-p">&lt;/p&gt;</span>     <span class="hl-c">&lt;!-- 第一个 p 没关，第二段被吞进去了 --&gt;</span>

<span class="hl-p">&lt;p&gt;</span>第一段<span class="hl-p">&lt;/p&gt;</span>       <span class="hl-c">&lt;!-- ✅ --&gt;</span>
<span class="hl-p">&lt;p&gt;</span>第二段<span class="hl-p">&lt;/p&gt;</span></pre></div>

<h4>错误 2 · 中文乱码</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;head&gt;</span>
  <span class="hl-p">&lt;title&gt;</span>中文<span class="hl-p">&lt;/title&gt;</span>          <span class="hl-c">&lt;!-- ❌ 没声明编码，可能乱码 --&gt;</span>
<span class="hl-p">&lt;/head&gt;</span>

<span class="hl-p">&lt;head&gt;</span>
  <span class="hl-p">&lt;meta</span> <span class="hl-f">charset</span>=<span class="hl-s">"utf-8"</span><span class="hl-p">&gt;</span>  <span class="hl-c">&lt;!-- ✅ 放在 head 第一行 --&gt;</span>
  <span class="hl-p">&lt;title&gt;</span>中文<span class="hl-p">&lt;/title&gt;</span>
<span class="hl-p">&lt;/head&gt;</span></pre></div>

<h4>错误 3 · 直接写 <code>&lt;</code> 和 <code>&amp;</code></h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p&gt;</span>当 a &lt; b 时<span class="hl-p">&lt;/p&gt;</span>      <span class="hl-c">&lt;!-- ❌ 浏览器把 &lt;b 当成标签了 --&gt;</span>

<span class="hl-p">&lt;p&gt;</span>当 a &amp;lt; b 时<span class="hl-p">&lt;/p&gt;</span>   <span class="hl-c">&lt;!-- ✅ --&gt;</span></pre></div>

<h4>错误 4 · 属性值没加引号</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;a</span> <span class="hl-f">href</span>=<span class="hl-s">index.html</span><span class="hl-p">&gt;</span>首页<span class="hl-p">&lt;/a&gt;</span>       <span class="hl-c">&lt;!-- ⚠ 能跑，但别这么写 --&gt;</span>

<span class="hl-p">&lt;a</span> <span class="hl-f">href</span>=<span class="hl-s">"index.html"</span><span class="hl-p">&gt;</span>首页<span class="hl-p">&lt;/a&gt;</span>     <span class="hl-c">&lt;!-- ✅ 一律加引号 --&gt;</span></pre></div>
<p>值里<b>有空格时</b>不加引号必错。养成习惯：<b>属性值一律用双引号。</b></p>

<h4>错误 5 · 内容写在 head 里</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;head&gt;</span>
  <span class="hl-p">&lt;p&gt;</span>你好<span class="hl-p">&lt;/p&gt;</span>            <span class="hl-c">&lt;!-- ❌ head 里的内容不显示 --&gt;</span>
<span class="hl-p">&lt;/head&gt;</span>

<span class="hl-p">&lt;body&gt;</span>
  <span class="hl-p">&lt;p&gt;</span>你好<span class="hl-p">&lt;/p&gt;</span>            <span class="hl-c">&lt;!-- ✅ --&gt;</span>
<span class="hl-p">&lt;/body&gt;</span></pre></div>

<div class="card key">
  <div class="card-t">这一篇要记住的五句话</div>
  <ol>
    <li><b>HTML 是标记语言，不是编程语言</b> —— 写什么就显示什么，
      不报错。</li>
    <li><b>标签成对出现</b>：<code>&lt;p&gt;</code> 内容 <code>&lt;/p&gt;</code>；
      自闭合的写一个就行（<code>&lt;br&gt;</code>）。</li>
    <li><b>注释是 <code>&lt;!-- --&gt;</code></b>，不能嵌套，
      而且浏览者能看到，别写敏感信息。</li>
    <li><b>连续空白会被压成一个空格</b> ——
      所以可以放心缩进排版；要多空格用 <code>&amp;nbsp;</code>，
      要保留格式用 <code>&lt;pre&gt;</code>。</li>
    <li><b>骨架四件套别省</b>：<code>&lt;!DOCTYPE html&gt;</code>、
      <code>charset="utf-8"</code>、<code>viewport</code>、<code>&lt;body&gt;</code>。</li>
  </ol>
</div>"""

# =====================================================================
# FE-02  HTML 常用标签
# =====================================================================
TOC02 = """  <a href="#s1">1 · 标签地图</a>
  <a href="#s2">2 · 文字：p / i / strong / span</a>
  <a href="#s3">3 · 列表：ul / ol / li</a>
  <a href="#s4">4 · 分块：div</a>
  <a href="#s5">5 · 链接：a 与 href</a>
  <a href="#s6">6 · 表格：table 系列</a>
  <a href="#s7">7 · 表单：form 系列</a>
  <a href="#s8">8 · 全局属性：title / class / id</a>
  <a href="#s9">9 · 一页速查</a>"""

BODY02 = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p>HTML 有 100 多个标签，但<b>日常真正用到的只有二十来个</b>。
  这一篇把它们一次讲完，每个都配「写什么 → 看到什么」。</p>
  <p>建议边看边在浏览器里试 —— <b>HTML 的学习成本极低，改一下刷新就见效。</b></p>
</div>

<h2 id="s1"><span class="n">1</span>标签地图</h2>

<table>
<thead><tr><th style="width:20%">分类</th><th>标签</th></tr></thead>
<tbody>
<tr><td><b>文字</b></td>
    <td class="c">p　i　em　strong　b　span　br　hr</td></tr>
<tr><td><b>标题</b></td>
    <td class="c">h1　h2　h3　h4　h5　h6</td></tr>
<tr><td><b>列表</b></td>
    <td class="c">ul　ol　li</td></tr>
<tr><td><b>分块</b></td>
    <td class="c">div　span</td></tr>
<tr><td><b>链接与图</b></td>
    <td class="c">a　img</td></tr>
<tr><td><b>表格</b></td>
    <td class="c">table　tr　th　td　thead　tbody</td></tr>
<tr><td><b>表单</b></td>
    <td class="c">form　input　label　textarea　select　option　button</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">先记住一个区分：块级 vs 行内</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:20%"></th><th>表现</th><th>例子</th></tr></thead>
  <tbody>
  <tr><td><b>块级</b></td><td><b>独占一行</b>，前后自动换行</td>
      <td class="c">p　div　h1　ul　table</td></tr>
  <tr><td><b>行内</b></td><td><b>跟着文字走</b>，不换行</td>
      <td class="c">span　a　strong　i　img</td></tr>
  </tbody></table>
  <p style="margin-top:10px">这个区分在 <b>FE-04</b> 讲 Display 时会再遇到，
  是 CSS 布局的地基。</p>
</div>

<h2 id="s2"><span class="n">2</span>文字：p / i / strong / span</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">四种文字标签</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p&gt;</span>普通段落。<span class="hl-p">&lt;/p&gt;</span>

<span class="hl-p">&lt;p&gt;</span>这段里 <span class="hl-p">&lt;i&gt;</span>倾斜<span class="hl-p">&lt;/i&gt;</span>
   和 <span class="hl-p">&lt;strong&gt;</span>加粗<span class="hl-p">&lt;/strong&gt;</span>
   还有 <span class="hl-p">&lt;span&gt;</span>一个行内小块<span class="hl-p">&lt;/span&gt;</span>。<span class="hl-p">&lt;/p&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">浏览器里看到</div><pre>普通段落。

这段里 倾斜 和 加粗 还有 一个行内小块 。</pre></div>

<table>
<thead><tr><th style="width:22%">标签</th><th style="width:22%">效果</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">&lt;p&gt;</td><td>段落</td>
    <td>块级，前后有间距。<b>正文都用它</b></td></tr>
<tr><td class="c">&lt;i&gt;</td><td><i>斜体</i></td>
    <td>行内。<code>i</code> = italic</td></tr>
<tr><td class="c">&lt;em&gt;</td><td><i>斜体</i></td>
    <td>和 <code>i</code> 长得一样，但语义是「<b>强调</b>」</td></tr>
<tr><td class="c">&lt;strong&gt;</td><td><b>加粗</b></td>
    <td>行内。语义是「<b>重要</b>」</td></tr>
<tr><td class="c">&lt;b&gt;</td><td><b>加粗</b></td>
    <td>和 <code>strong</code> 长得一样，但只是「样式上粗」，无语义</td></tr>
<tr><td class="c">&lt;span&gt;</td><td>没有默认效果</td>
    <td><b>纯容器</b>。它存在的唯一目的是「给一小段文字套个壳，
      好让 CSS 选中它」</td></tr>
<tr><td class="c">&lt;br&gt;</td><td>换行</td><td>自闭合</td></tr>
<tr><td class="c">&lt;hr&gt;</td><td>一条横线</td><td>自闭合，表示「分隔」</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t"><code>i</code> / <code>b</code> 和 <code>em</code> / <code>strong</code> 该用哪个</div>
  <p>长得一样，区别在<b>语义</b>：
  <code>em</code> 是「这里要重读」，<code>strong</code> 是「这里很重要」。</p>
  <p>屏幕阅读器（盲人用的）会<b>把 strong 读得重一些</b>。
  搜索引擎也拿它判断重点。</p>
  <p><b>实用建议</b>：正文里要加粗就用 <code>&lt;strong&gt;</code>，
  要倾斜就用 <code>&lt;em&gt;</code>。
  只有「纯粹想让它斜/粗，没有语义」时才用 <code>i</code> / <code>b</code>。</p>
</div>

<div class="card key">
  <div class="card-t"><code>&lt;span&gt;</code> 是前端最常用的标签之一</div>
  <p>它<b>自己不产生任何视觉效果</b> —— 这正是它的价值。</p>
  <p>比如一句话里想让某个词变红：</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">span 的典型用法</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p&gt;</span>状态：<span class="hl-p">&lt;span</span> <span class="hl-f">class</span>=<span class="hl-s">"err"</span><span class="hl-p">&gt;</span>失败<span class="hl-p">&lt;/span&gt;&lt;/p&gt;</span>

<span class="hl-c">/* 配 CSS */</span>
.err { color: red; }</pre></div>
  <p style="margin-top:10px">如果不用 span，就只能给整个 <code>&lt;p&gt;</code> 上色了 ——
  那就全红了。</p>
</div>

<h4>标题标签 h1~h6</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">六级标题</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;h1&gt;</span>一级标题<span class="hl-p">&lt;/h1&gt;</span>
<span class="hl-p">&lt;h2&gt;</span>二级标题<span class="hl-p">&lt;/h2&gt;</span>
<span class="hl-p">&lt;h3&gt;</span>三级标题<span class="hl-p">&lt;/h3&gt;</span>
<span class="hl-p">&lt;h4&gt;</span>四级标题<span class="hl-p">&lt;/h4&gt;</span>
<span class="hl-p">&lt;h5&gt;</span>五级标题<span class="hl-p">&lt;/h5&gt;</span>
<span class="hl-p">&lt;h6&gt;</span>六级标题<span class="hl-p">&lt;/h6&gt;</span></pre></div>

<p>它们默认<b>又大又粗、独占一行</b>。
注意 <code>h1</code> <b>一页最好只用一个</b>（页面主标题），
其余按层级往下用 —— <b>不要为了「字大」而用 h，那是 CSS 的活。</b></p>

<h2 id="s3"><span class="n">3</span>列表：ul / ol / li</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">两种列表</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- ul = unordered list，无序列表（圆点） --&gt;</span>
<span class="hl-p">&lt;ul&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>苹果<span class="hl-p">&lt;/li&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>香蕉<span class="hl-p">&lt;/li&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>樱桃<span class="hl-p">&lt;/li&gt;</span>
<span class="hl-p">&lt;/ul&gt;</span>

<span class="hl-c">&lt;!-- ol = ordered list，有序列表（数字） --&gt;</span>
<span class="hl-p">&lt;ol&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>第一步<span class="hl-p">&lt;/li&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>第二步<span class="hl-p">&lt;/li&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>第三步<span class="hl-p">&lt;/li&gt;</span>
<span class="hl-p">&lt;/ol&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">浏览器里看到</div><pre>• 苹果
• 香蕉
• 樱桃

1. 第一步
2. 第二步
3. 第三步</pre></div>

<div class="card warn">
  <div class="card-t">结构不能乱：<code>li</code> 必须在 <code>ul</code>/<code>ol</code> 里面</div>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;ul&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>苹果<span class="hl-p">&lt;/li&gt;</span>
<span class="hl-p">&lt;/ul&gt;</span>
<span class="hl-p">&lt;li&gt;</span>香蕉<span class="hl-p">&lt;/li&gt;</span>     <span class="hl-c">&lt;!-- ❌ 落单的 li，浏览器会自己瞎补 --&gt;</span>

<span class="hl-p">&lt;li&gt;</span>苹果<span class="hl-p">&lt;/li&gt;</span>        <span class="hl-c">&lt;!-- ❌ ul 不能直接放文字 --&gt;</span></pre></div>
  <p style="margin-top:10px">规则：<b><code>ul</code> / <code>ol</code> 的直接子元素只能是 <code>li</code></b>。
  列表就是「列表项」的容器。</p>
</div>

<p>列表可以嵌套（子列表放在某个 <code>li</code> 里面）：</p>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">嵌套列表</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;ul&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>前端
    <span class="hl-p">&lt;ul&gt;</span>
      <span class="hl-p">&lt;li&gt;</span>HTML<span class="hl-p">&lt;/li&gt;</span>
      <span class="hl-p">&lt;li&gt;</span>CSS<span class="hl-p">&lt;/li&gt;</span>
    <span class="hl-p">&lt;/ul&gt;</span>
  <span class="hl-p">&lt;/li&gt;</span>
  <span class="hl-p">&lt;li&gt;</span>后端<span class="hl-p">&lt;/li&gt;</span>
<span class="hl-p">&lt;/ul&gt;</span></pre></div>

<div class="card tip">
  <div class="card-t">导航菜单为什么用 ul</div>
  <p>因为「一堆链接」本质上<b>就是一个列表</b>。
  语义正确 + 浏览器和阅读器都懂 + CSS 好写。</p>
  <p><b>本系列文档左边的目录就是用 <code>&lt;ul&gt;</code> 做的</b>
  （你按 F12 看得到）。</p>
</div>

<h2 id="s4"><span class="n">4</span>分块：div</h2>

<p><code>&lt;div&gt;</code> 是「<b>块级容器</b>」—— 和 <code>span</code> 是一对：</p>

<table>
<thead><tr><th style="width:22%"></th><th>类型</th><th>用途</th></tr></thead>
<tbody>
<tr><td class="c">&lt;div&gt;</td><td>块级容器</td><td><b>把一大块内容圈起来</b>，好整体排版</td></tr>
<tr><td class="c">&lt;span&gt;</td><td>行内容器</td><td><b>把一小段文字圈起来</b>，好单独上色</td></tr>
</tbody>
</table>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">div 把内容分组</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"card"</span><span class="hl-p">&gt;</span>
  <span class="hl-p">&lt;h3&gt;</span>卡片标题<span class="hl-p">&lt;/h3&gt;</span>
  <span class="hl-p">&lt;p&gt;</span>卡片内容。<span class="hl-p">&lt;/p&gt;</span>
<span class="hl-p">&lt;/div&gt;</span>

<span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"card"</span><span class="hl-p">&gt;</span>
  <span class="hl-p">&lt;h3&gt;</span>另一张卡片<span class="hl-p">&lt;/h3&gt;</span>
  <span class="hl-p">&lt;p&gt;</span>另一段内容。<span class="hl-p">&lt;/p&gt;</span>
<span class="hl-p">&lt;/div&gt;</span></pre></div>

<div class="card key">
  <div class="card-t">div 自己什么效果都没有</div>
  <p>它不加粗、不上色、不缩进 —— <b>它就是个透明的盒子</b>。</p>
  <p>它的全部意义是「<b>给 CSS 一个可以选中的范围</b>」。
  所以 div 几乎<b>总是配着 <code>class</code> 出现</b>。</p>
  <p>本文档里的每一张卡片、每一个提示框，背后都是一个 <code>div</code>。</p>
</div>

<div class="card warn">
  <div class="card-t">别用 div 堆出一个假表格</div>
  <p>新手有时用一堆 div 加边框做出表格的样子。
  <b>如果内容真的是表格，就用 <code>&lt;table&gt;</code></b> ——
  语义正确、屏幕阅读器能读、还对打印友好。</p>
  <p>判断标准：<b>「这些数据有行和列的关系吗？」</b>有就用 table。</p>
</div>

<h2 id="s5"><span class="n">5</span>链接：a 与 href</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">最基本的链接</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;a</span> <span class="hl-f">href</span>=<span class="hl-s">"https://example.com"</span><span class="hl-p">&gt;</span>点我去 example<span class="hl-p">&lt;/a&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">浏览器里看到（蓝色带下划线，可点）</div><pre>点我去 example</pre></div>

<p><code>a</code> = <b>anchor</b>（锚），<code>href</code> = <b>h</b>ypertext <b>ref</b>erence。
<b><code>href</code> 是 <code>a</code> 最重要的属性</b> —— 没有它，链接就没目标。</p>

<h4><code>href</code> 能写什么</h4>
<table>
<thead><tr><th style="width:34%">写法</th><th>去哪里</th></tr></thead>
<tbody>
<tr><td class="c">https://example.com</td>
    <td><b>完整网址</b>（绝对地址），去别的网站</td></tr>
<tr><td class="c">page2.html</td>
    <td><b>同目录</b>下的另一个文件</td></tr>
<tr><td class="c">sub/page2.html</td><td>子目录里的文件</td></tr>
<tr><td class="c">../index.html</td><td>上一级目录（<code>..</code> 和文件系统一样）</td></tr>
<tr><td class="c">#s3</td>
    <td><b>跳到本页的某个位置</b> —— 那个元素的 <code>id</code></td></tr>
<tr><td class="c">#</td><td>回到页面顶部（空的锚点）</td></tr>
<tr><td class="c">mailto:a@b.com</td><td>打开邮件客户端</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t"><code>#锚点</code> 就是「目录跳转」的原理</div>
  <p>本文档左边的目录，每一条都是 <code>&lt;a href="#s3"&gt;</code>，
  而正文里对应的小节写着 <code>&lt;h2 id="s3"&gt;</code>。
  点目录 → 跳到那个 id。</p>
  <p><b>只需 id 对得上，不需要任何 JavaScript。</b></p>
</div>

<h4>在新标签页打开</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">target 属性</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;a</span> <span class="hl-f">href</span>=<span class="hl-s">"https://example.com"</span> <span class="hl-f">target</span>=<span class="hl-s">"_blank"</span><span class="hl-p">&gt;</span>新标签页打开<span class="hl-p">&lt;/a&gt;</span></pre></div>

<table>
<thead><tr><th style="width:26%">target 的值</th><th>行为</th></tr></thead>
<tbody>
<tr><td class="c">（不写）</td><td>当前标签页打开</td></tr>
<tr><td class="c">_blank</td><td><b>新标签页</b>打开</td></tr>
<tr><td class="c">_self</td><td>当前页（默认）</td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">别滥用 <code>target="_blank"</code></div>
  <p>每点一个链接就多一个标签页，用户很快会烦。
  只有<b>「跳到站外、不希望用户离开本站」</b>时才用。</p>
  <p>另外：用 <code>_blank</code> 打开外部网站时，
  那个页面能拿到你页面的控制权（<code>window.opener</code>）。
  加一句 <code>rel="noopener"</code> 更安全：</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">推荐写法</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;a</span> <span class="hl-f">href</span>=<span class="hl-s">"https://example.com"</span>
   <span class="hl-f">target</span>=<span class="hl-s">"_blank"</span> <span class="hl-f">rel</span>=<span class="hl-s">"noopener"</span><span class="hl-p">&gt;</span>站外链接<span class="hl-p">&lt;/a&gt;</span></pre></div>
</div>

<h2 id="s6"><span class="n">6</span>表格：table 系列</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">一个完整表格</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;table&gt;</span>
  <span class="hl-p">&lt;thead&gt;</span>                     <span class="hl-c">&lt;!-- 表头区 --&gt;</span>
    <span class="hl-p">&lt;tr&gt;</span>                      <span class="hl-c">&lt;!-- 一行 --&gt;</span>
      <span class="hl-p">&lt;th&gt;</span>名字<span class="hl-p">&lt;/th&gt;</span>            <span class="hl-c">&lt;!-- 表头格 --&gt;</span>
      <span class="hl-p">&lt;th&gt;</span>血量<span class="hl-p">&lt;/th&gt;</span>
    <span class="hl-p">&lt;/tr&gt;</span>
  <span class="hl-p">&lt;/thead&gt;</span>
  <span class="hl-p">&lt;tbody&gt;</span>                     <span class="hl-c">&lt;!-- 数据区 --&gt;</span>
    <span class="hl-p">&lt;tr&gt;</span>
      <span class="hl-p">&lt;td&gt;</span>Archer<span class="hl-p">&lt;/td&gt;</span>          <span class="hl-c">&lt;!-- 数据格 --&gt;</span>
      <span class="hl-p">&lt;td&gt;</span>100<span class="hl-p">&lt;/td&gt;</span>
    <span class="hl-p">&lt;/tr&gt;</span>
    <span class="hl-p">&lt;tr&gt;</span>
      <span class="hl-p">&lt;td&gt;</span>Mage<span class="hl-p">&lt;/td&gt;</span>
      <span class="hl-p">&lt;td&gt;</span>80<span class="hl-p">&lt;/td&gt;</span>
    <span class="hl-p">&lt;/tr&gt;</span>
  <span class="hl-p">&lt;/tbody&gt;</span>
<span class="hl-p">&lt;/table&gt;</span></pre></div>

<table>
<thead><tr><th style="width:22%">标签</th><th>含义</th><th style="width:26%">记忆</th></tr></thead>
<tbody>
<tr><td class="c">table</td><td>整张表</td><td>table</td></tr>
<tr><td class="c">tr</td><td><b>t</b>able <b>r</b>ow，一行</td><td>行</td></tr>
<tr><td class="c">th</td><td><b>t</b>able <b>h</b>eader，表头格</td><td><b>粗体居中</b></td></tr>
<tr><td class="c">td</td><td><b>t</b>able <b>d</b>ata，数据格</td><td>普通格</td></tr>
<tr><td class="c">thead</td><td>表头区（放 <code>tr</code>）</td><td>可选但推荐</td></tr>
<tr><td class="c">tbody</td><td>数据区（放 <code>tr</code>）</td><td>可选但推荐</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">结构规则：一层套一层</div>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">table
 └─ tr          ← 行只能放在 table / thead / tbody 里
     └─ td / th ← 格子只能放在 tr 里</pre>
  <p style="margin-top:10px"><b>不能跳级</b>：<code>table</code> 里直接写 <code>td</code> 是错的，
  <code>tr</code> 里直接写文字也是错的。</p>
</div>

<h4>合并单元格：colspan 与 rowspan</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">跨列与跨行</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;table&gt;</span>
  <span class="hl-p">&lt;tr&gt;</span>
    <span class="hl-p">&lt;th</span> <span class="hl-f">colspan</span>=<span class="hl-s">"2"</span><span class="hl-p">&gt;</span>横跨两列<span class="hl-p">&lt;/th&gt;</span>   <span class="hl-c">&lt;!-- col = column --&gt;</span>
  <span class="hl-p">&lt;/tr&gt;</span>
  <span class="hl-p">&lt;tr&gt;</span>
    <span class="hl-p">&lt;td</span> <span class="hl-f">rowspan</span>=<span class="hl-s">"2"</span><span class="hl-p">&gt;</span>竖跨两行<span class="hl-p">&lt;/td&gt;</span>   <span class="hl-c">&lt;!-- row = 行 --&gt;</span>
    <span class="hl-p">&lt;td&gt;</span>A<span class="hl-p">&lt;/td&gt;</span>
  <span class="hl-p">&lt;/tr&gt;</span>
  <span class="hl-p">&lt;tr&gt;</span>
    <span class="hl-p">&lt;td&gt;</span>B<span class="hl-p">&lt;/td&gt;</span>                  <span class="hl-c">&lt;!-- 这一行少一列，因为上面占了 --&gt;</span>
  <span class="hl-p">&lt;/tr&gt;</span>
<span class="hl-p">&lt;/table&gt;</span></pre></div>

<p><b>注意</b>：用了 <code>rowspan="2"</code> 之后，下一行就要<b>少写一个 <code>td</code></b>，
否则表格会错位。</p>

<h2 id="s7"><span class="n">7</span>表单：form 系列</h2>

<p>表单是「<b>让用户填东西</b>」的区域：登录框、搜索框、设置页都是。</p>

<h4>input：最核心的标签</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">input 靠 type 变身</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"text"</span>     <span class="hl-f">placeholder</span>=<span class="hl-s">"请输入名字"</span><span class="hl-p">&gt;</span>
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"password"</span> <span class="hl-f">placeholder</span>=<span class="hl-s">"密码"</span><span class="hl-p">&gt;</span>
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"number"</span>   <span class="hl-f">min</span>=<span class="hl-s">"0"</span> <span class="hl-f">max</span>=<span class="hl-s">"100"</span><span class="hl-p">&gt;</span>
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"checkbox"</span><span class="hl-p">&gt;</span> 记住我
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"radio"</span> <span class="hl-f">name</span>=<span class="hl-s">"lv"</span><span class="hl-p">&gt;</span> 简单
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"radio"</span> <span class="hl-f">name</span>=<span class="hl-s">"lv"</span><span class="hl-p">&gt;</span> 困难
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"file"</span><span class="hl-p">&gt;</span>
<span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"submit"</span> <span class="hl-f">value</span>=<span class="hl-s">"提交"</span><span class="hl-p">&gt;</span></pre></div>

<table>
<thead><tr><th style="width:22%">type</th><th>变成什么</th></tr></thead>
<tbody>
<tr><td class="c">text</td><td>单行文本框（默认）</td></tr>
<tr><td class="c">password</td><td>输入时显示成圆点</td></tr>
<tr><td class="c">number</td><td>只能输数字，带上下箭头</td></tr>
<tr><td class="c">checkbox</td><td><b>复选框</b>（可多选）</td></tr>
<tr><td class="c">radio</td><td><b>单选钮</b>（同 name 的互斥）</td></tr>
<tr><td class="c">file</td><td>选文件</td></tr>
<tr><td class="c">submit</td><td>提交按钮</td></tr>
<tr><td class="c">color / date / range</td><td>取色器 / 日期 / 滑块</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t"><code>radio</code> 靠 <code>name</code> 分组</div>
  <p>上面那两个 radio <b>都写了 <code>name="lv"</code></b> ——
  所以它们互斥，只能选一个。</p>
  <p>如果两个 radio 的 <code>name</code> 不同，就会<b>变成两组独立的单选</b>，
  可以同时选中。这是最常见的表单坑。</p>
</div>

<h4>label：让文字也能点</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">两种写法</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- ① 包起来 --&gt;</span>
<span class="hl-p">&lt;label&gt;</span>
  <span class="hl-p">&lt;input</span> <span class="hl-f">type</span>=<span class="hl-s">"checkbox"</span><span class="hl-p">&gt;</span> 记住我
<span class="hl-p">&lt;/label&gt;</span>

<span class="hl-c">&lt;!-- ② 用 for 指向 input 的 id --&gt;</span>
<span class="hl-p">&lt;label</span> <span class="hl-f">for</span>=<span class="hl-s">"pwd"</span><span class="hl-p">&gt;</span>密码<span class="hl-p">&lt;/label&gt;</span>
<span class="hl-p">&lt;input</span> <span class="hl-f">id</span>=<span class="hl-s">"pwd"</span> <span class="hl-f">type</span>=<span class="hl-s">"password"</span><span class="hl-p">&gt;</span></pre></div>

<p>加了 label 之后，<b>点文字就等于点控件</b> ——
复选框和单选钮尤其明显（不然只有那个小方块能点，很难点中）。
<b>正式页面都应该加。</b></p>

<h4>textarea / select / button</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">多行文本、下拉、按钮</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- 多行文本框（注意：有结束标签） --&gt;</span>
<span class="hl-p">&lt;textarea</span> <span class="hl-f">rows</span>=<span class="hl-s">"3"</span> <span class="hl-f">cols</span>=<span class="hl-s">"30"</span><span class="hl-p">&gt;</span>默认文字<span class="hl-p">&lt;/textarea&gt;</span>

<span class="hl-c">&lt;!-- 下拉框 --&gt;</span>
<span class="hl-p">&lt;select&gt;</span>
  <span class="hl-p">&lt;option</span> <span class="hl-f">value</span>=<span class="hl-s">"a"</span><span class="hl-p">&gt;</span>选项 A<span class="hl-p">&lt;/option&gt;</span>
  <span class="hl-p">&lt;option</span> <span class="hl-f">value</span>=<span class="hl-s">"b"</span><span class="hl-p">&gt;</span>选项 B<span class="hl-p">&lt;/option&gt;</span>
<span class="hl-p">&lt;/select&gt;</span>

<span class="hl-c">&lt;!-- 按钮 --&gt;</span>
<span class="hl-p">&lt;button&gt;</span>点我<span class="hl-p">&lt;/button&gt;</span></pre></div>

<h4>用 form 包起来</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">完整的表单</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;form</span> <span class="hl-f">action</span>=<span class="hl-s">"/login"</span> <span class="hl-f">method</span>=<span class="hl-s">"post"</span><span class="hl-p">&gt;</span>
  <span class="hl-p">&lt;label</span> <span class="hl-f">for</span>=<span class="hl-s">"u"</span><span class="hl-p">&gt;</span>用户名<span class="hl-p">&lt;/label&gt;</span>
  <span class="hl-p">&lt;input</span> <span class="hl-f">id</span>=<span class="hl-s">"u"</span> <span class="hl-f">name</span>=<span class="hl-s">"user"</span> <span class="hl-f">type</span>=<span class="hl-s">"text"</span><span class="hl-p">&gt;</span>

  <span class="hl-p">&lt;label</span> <span class="hl-f">for</span>=<span class="hl-s">"p"</span><span class="hl-p">&gt;</span>密码<span class="hl-p">&lt;/label&gt;</span>
  <span class="hl-p">&lt;input</span> <span class="hl-f">id</span>=<span class="hl-s">"p"</span> <span class="hl-f">name</span>=<span class="hl-s">"pwd"</span> <span class="hl-f">type</span>=<span class="hl-s">"password"</span><span class="hl-p">&gt;</span>

  <span class="hl-p">&lt;button</span> <span class="hl-f">type</span>=<span class="hl-s">"submit"</span><span class="hl-p">&gt;</span>登录<span class="hl-p">&lt;/button&gt;</span>
<span class="hl-p">&lt;/form&gt;</span></pre></div>

<table>
<thead><tr><th style="width:22%">属性</th><th>作用</th></tr></thead>
<tbody>
<tr><td class="c">action</td><td>提交到哪个地址</td></tr>
<tr><td class="c">method</td><td><code>get</code>（参数在网址里）/ <code>post</code>（在请求体里）</td></tr>
<tr><td class="c">name</td><td><b>提交时这一项的键名</b> —— 没写 name 的控件不会被提交</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">UME 的场景</div>
  <p>本项目是纯前端编辑器，<b>基本不用 <code>&lt;form&gt;</code></b>
  —— 搜索框、选字体这些用 <code>input</code> 就够了，
  交互靠 JavaScript 处理，不走「提交」。</p>
  <p>但桌面/网页版做「设置面板」时，
  <code>input</code> + <code>label</code> 的组合会用得非常多。</p>
</div>

<h2 id="s8"><span class="n">8</span>全局属性：title / class / id</h2>

<p>有三个属性<b>几乎所有标签都能写</b>，值得单独讲。</p>

<h4>title：鼠标悬停时的提示</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">title 属性</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;span</span> <span class="hl-f">title</span>=<span class="hl-s">"这里会显示提示文字"</span><span class="hl-p">&gt;</span>鼠标移上来看看<span class="hl-p">&lt;/span&gt;</span>

<span class="hl-p">&lt;abbr</span> <span class="hl-f">title</span>=<span class="hl-s">"HyperText Markup Language"</span><span class="hl-p">&gt;</span>HTML<span class="hl-p">&lt;/abbr&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">行为</div><pre>鼠标停在文字上约 1 秒 → 浮出一个黄色小提示框

手机上没有「悬停」，所以 title 在手机端通常看不到
  → 重要信息不要只放在 title 里</pre></div>

<p>本文档里就用了它 —— 比如导航页那些星号，
鼠标移上去会显示「与本项目施行密切相关」。</p>

<h4>class 与 id：给元素起名字</h4>
<table>
<thead><tr><th style="width:20%"></th><th>class</th><th>id</th></tr></thead>
<tbody>
<tr><td><b>能不能重复</b></td>
    <td><span class="tag g">可以</span> 多个元素共用一个 class</td>
    <td><span class="tag r">不能</span> <b>全页唯一</b></td></tr>
<tr><td><b>一个元素能有几个</b></td>
    <td>可以写多个，空格隔开</td>
    <td>只能一个</td></tr>
<tr><td><b>主要用途</b></td>
    <td><b>CSS 批量选中</b>同类元素</td>
    <td><b>唯一标识</b>：锚点跳转、JS 精确找</td></tr>
<tr><td><b>CSS 里怎么写</b></td><td class="c">.card { }</td>
    <td class="c">#header { }</td></tr>
</tbody>
</table>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- class：三个卡片共用一种样式 --&gt;</span>
<span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"card"</span><span class="hl-p">&gt;</span>卡片一<span class="hl-p">&lt;/div&gt;</span>
<span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"card"</span><span class="hl-p">&gt;</span>卡片二<span class="hl-p">&lt;/div&gt;</span>
<span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"card"</span><span class="hl-p">&gt;</span>卡片三<span class="hl-p">&lt;/div&gt;</span>

<span class="hl-c">&lt;!-- 一个元素可以有多个 class --&gt;</span>
<span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"card highlight"</span><span class="hl-p">&gt;</span>既是卡片，又高亮<span class="hl-p">&lt;/div&gt;</span>

<span class="hl-c">&lt;!-- id：唯一的锚点 --&gt;</span>
<span class="hl-p">&lt;h2</span> <span class="hl-f">id</span>=<span class="hl-s">"install"</span><span class="hl-p">&gt;</span>安装步骤<span class="hl-p">&lt;/h2&gt;</span>
<span class="hl-p">&lt;a</span> <span class="hl-f">href</span>=<span class="hl-s">"#install"</span><span class="hl-p">&gt;</span>跳到安装步骤<span class="hl-p">&lt;/a&gt;</span></pre></div>

<div class="card warn">
  <div class="card-t">id 重复是隐性 bug</div>
  <p>浏览器<b>不报错</b>，但 <code>href="#install"</code> 只会跳到<b>第一个</b>，
  JavaScript 的 <code>getElementById</code> 也只会拿到第一个。</p>
  <p><b>规则：id 全页唯一。</b>需要重复就用 class。</p>
</div>

<div class="card tip">
  <div class="card-t">命名习惯</div>
  <ul>
    <li>小写 + 连字符：<code>main-nav</code>、<code>card-title</code>（推荐）</li>
    <li>别用中文和空格（<code>class="我的 卡片"</code> 会被当成两个 class）</li>
    <li>别用纯数字开头</li>
  </ul>
</div>

<h2 id="s9"><span class="n">9</span>一页速查</h2>

<table>
<thead><tr><th style="width:32%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>一段话</td><td class="c">&lt;p&gt;文字&lt;/p&gt;</td></tr>
<tr><td>倾斜 / 强调</td><td class="c">&lt;em&gt;文字&lt;/em&gt;</td></tr>
<tr><td>加粗 / 重要</td><td class="c">&lt;strong&gt;文字&lt;/strong&gt;</td></tr>
<tr><td>给一小段套壳（好上色）</td><td class="c">&lt;span class="x"&gt;文字&lt;/span&gt;</td></tr>
<tr><td>换行 / 横线</td><td class="c">&lt;br&gt;　&lt;hr&gt;</td></tr>
<tr><td>标题</td><td class="c">&lt;h1&gt;…&lt;/h1&gt; ~ &lt;h6&gt;</td></tr>
<tr><td>无序 / 有序列表</td><td class="c">&lt;ul&gt;&lt;li&gt;…&lt;/li&gt;&lt;/ul&gt;　&lt;ol&gt;…&lt;/ol&gt;</td></tr>
<tr><td>把一块内容分组</td><td class="c">&lt;div class="x"&gt;…&lt;/div&gt;</td></tr>
<tr><td>链接</td><td class="c">&lt;a href="url"&gt;文字&lt;/a&gt;</td></tr>
<tr><td>跳本页某处</td><td class="c">&lt;a href="#id"&gt;　+　&lt;h2 id="id"&gt;</td></tr>
<tr><td>新标签页打开</td><td class="c">target="_blank" rel="noopener"</td></tr>
<tr><td>表格</td><td class="c">&lt;table&gt;&lt;tr&gt;&lt;th&gt;/&lt;td&gt;…</td></tr>
<tr><td>合并列 / 行</td><td class="c">colspan="2"　rowspan="2"</td></tr>
<tr><td>输入框</td><td class="c">&lt;input type="text"&gt;</td></tr>
<tr><td>复选框 / 单选</td><td class="c">type="checkbox"　type="radio" name="组名"</td></tr>
<tr><td>多行文本</td><td class="c">&lt;textarea&gt;&lt;/textarea&gt;</td></tr>
<tr><td>下拉框</td><td class="c">&lt;select&gt;&lt;option&gt;…</td></tr>
<tr><td>按钮</td><td class="c">&lt;button&gt;点我&lt;/button&gt;</td></tr>
<tr><td>点文字也能选中控件</td><td class="c">&lt;label for="id"&gt;　+　&lt;input id="id"&gt;</td></tr>
<tr><td>悬停提示</td><td class="c">title="提示文字"</td></tr>
<tr><td>批量上样式</td><td class="c">class="名字"　→ CSS 里 .名字 { }</td></tr>
<tr><td>唯一锚点</td><td class="c">id="名字"　→ CSS 里 #名字 { }</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的五句话</div>
  <ol>
    <li><b>块级独占一行（p / div / h / ul / table），行内跟着文字走（span / a / strong）。</b></li>
    <li><b><code>span</code> 和 <code>div</code> 自己没有视觉效果</b>，
      它们的价值是「给 CSS 一个可选的壳」。</li>
    <li><b><code>a</code> 靠 <code>href</code></b>；
      <code>#id</code> 就是目录跳转的原理，不需要 JavaScript。</li>
    <li><b>表格是 <code>table → tr → td/th</code> 一层套一层</b>，不能跳级。</li>
    <li><b><code>class</code> 可重复、用来批量上样式；<code>id</code> 全页唯一、用来做锚点。</b></li>
  </ol>
</div>"""

if __name__ == "__main__":
    print(build("fe-01.html", "FE-01", "HTML 入门与标签语法", BODY01, TOC01))
    print(build("fe-02.html", "FE-02", "HTML 常用标签", BODY02, TOC02))
