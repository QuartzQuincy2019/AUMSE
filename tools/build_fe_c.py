# -*- coding: utf-8 -*-
"""FE-04（Display 与盒模型尺寸）、FE-05（Writing Mode ★）、FE-06（hover 与 transition）"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build
from fe_kit import pv

# =====================================================================
# FE-04  Display 与盒模型尺寸
# =====================================================================
TOC04 = """  <a href="#s1">1 · 每个元素都是一个盒子</a>
  <a href="#s2">2 · display 的三种基本值</a>
  <a href="#s3">3 · inline-block 为什么重要</a>
  <a href="#s4">4 · border 边框</a>
  <a href="#s5">5 · box-shadow 阴影</a>
  <a href="#s6">6 · width / height</a>
  <a href="#s7">7 · max-width 与 max-height</a>
  <a href="#s8">8 · 一页速查</a>"""

BODY04 = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p>FE-02 说过标签分「块级」和「行内」。这一篇把这个区分讲透
  —— 它就是 <code>display</code>。</p>
  <p>然后讲怎么控制盒子的大小和边框。
  <b>这三样（display、边框、尺寸）是 CSS 布局的地基。</b></p>
</div>

<h2 id="s1"><span class="n">1</span>每个元素都是一个盒子</h2>

<p>浏览器眼里，页面上<b>每一个元素都是一个矩形盒子</b>。盒子从里到外分四层：</p>

<figure class="fig">
  <img src="assets/img/box-model.png"
       alt="盒模型四层示意图：内容、内边距 padding、边框 border、外边距 margin，并标出上下左右四边的所有属性名"
       width="669" height="672" loading="lazy" decoding="async">
  <figcaption>盒模型从里到外四层：<b>内容</b> → <b>内边距 padding</b> → <b>边框 border</b> → <b>外边距 margin</b>。图里把上下左右四边的属性名都标出来了 —— 注意 <code>width</code> / <code>height</code> 只管最里面那一块内容区。</figcaption>
</figure>

<table>
<thead><tr><th style="width:18%">层</th><th style="width:22%">属性</th><th>作用</th></tr></thead>
<tbody>
<tr><td><b>content</b></td><td class="c">width / height</td><td>内容本身的大小</td></tr>
<tr><td><b>padding</b></td><td class="c">padding</td>
    <td><b>内容与边框之间的空白</b>（往里撑）</td></tr>
<tr><td><b>border</b></td><td class="c">border</td><td>边框线本身</td></tr>
<tr><td><b>margin</b></td><td class="c">margin</td>
    <td><b>这个盒子与别的盒子之间的距离</b>（往外推）</td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">padding 和 margin 到底怎么区分</div>
  <p><b>padding 是「盒子里面的填充」</b> —— 背景色会铺到 padding 上。</p>
  <p><b>margin 是「盒子外面的空隙」</b> —— 透明，背景色不铺过去。</p>
  <p>一句话：<b>想让背景变大用 padding，想让两个盒子离远用 margin。</b></p>
</div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">四层一起写</span><span class="cp">复制</span></div><pre>.box {
    <span class="hl-k">width</span>: <span class="hl-n">200px</span>;              <span class="hl-c">/* 内容区宽 */</span>
    <span class="hl-k">padding</span>: <span class="hl-n">16px</span>;              <span class="hl-c">/* 四周内边距 */</span>
    <span class="hl-k">border</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#ccd5e3</span>;  <span class="hl-c">/* 边框 */</span>
    <span class="hl-k">margin</span>: <span class="hl-n">16px</span>;               <span class="hl-c">/* 外边距 */</span>
    <span class="hl-k">background</span>: <span class="hl-n">#fff</span>;
}</pre></div>

<div class="card key">
  <div class="card-t"><code>box-sizing: border-box</code> —— 一定要设</div>
  <p>默认情况下 <code>width:200px</code> 指的是<b>内容区</b>200px，
  加上 padding 和 border，<b>实际占的宽度会超过 200</b>。算起来很烦。</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">全世界都在用的那一行</span><span class="cp">复制</span></div><pre>*, *::before, *::after {
    <span class="hl-k">box-sizing</span>: border-box;   <span class="hl-c">/* 让 width 包含 padding 和 border */</span>
}</pre></div>
  <p style="margin-top:10px">设了之后 <code>width:200px</code> 就是<b>「整体 200px」</b>，
  里面怎么加 padding 都不会撑破。<b>这是现代 CSS 的第一行。</b></p>
</div>

<h2 id="s2"><span class="n">2</span>display 的三种基本值</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre>.a { <span class="hl-k">display</span>: block; }          <span class="hl-c">/* 块级：独占一行 */</span>
.b { <span class="hl-k">display</span>: inline; }         <span class="hl-c">/* 行内：跟着文字走，宽高无效 */</span>
.c { <span class="hl-k">display</span>: inline-block; }   <span class="hl-c">/* 行内块：跟着文字走，但宽高有效 */</span></pre></div>

<table>
<thead><tr><th style="width:16%"></th><th style="width:20%">占行</th>
  <th style="width:24%">width / height</th><th>padding / margin</th></tr></thead>
<tbody>
<tr><td class="c">block</td><td><b>独占一行</b></td>
    <td><span class="tag g">有效</span></td><td>四方向都有效</td></tr>
<tr><td class="c">inline</td><td>跟着文字</td>
    <td><span class="tag r">无效</span>（写了也不理）</td>
    <td><b>上下方向无效</b>，左右有效</td></tr>
<tr><td class="c">inline-block</td><td>跟着文字</td>
    <td><span class="tag g">有效</span></td><td>四方向都有效</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t"><code>inline</code> 最反直觉的一点</div>
  <p>给 <code>&lt;span&gt;</code> 写 <code>width: 200px</code>
  <b>完全没用</b> —— 因为行内元素的宽度由<b>里面的文字</b>决定，
  不是由你决定。</p>
  <p>想让 span 有宽度，就得把它变成
  <code>inline-block</code> 或 <code>block</code>。</p>
</div>

<h4>常用标签的默认 display</h4>
<table>
<thead><tr><th style="width:24%">display</th><th>标签</th></tr></thead>
<tbody>
<tr><td class="c">block</td>
    <td class="c">div　p　h1~h6　ul　ol　li　table　form　header　footer　section</td></tr>
<tr><td class="c">inline</td>
    <td class="c">span　a　strong　em　b　i　code　label</td></tr>
<tr><td class="c">inline-block</td>
    <td class="c">img　input　button　select　textarea</td></tr>
</tbody>
</table>

<h2 id="s3"><span class="n">3</span>inline-block 为什么重要</h2>

<p>它解决了一个很实际的矛盾：<b>「想让几个盒子并排，又想控制它们的宽高」</b>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三个并排的卡片（经典写法）</span><span class="cp">复制</span></div><pre>.card {
    <span class="hl-k">display</span>: inline-block;   <span class="hl-c">/* 并排 + 可控宽高 */</span>
    <span class="hl-k">width</span>: <span class="hl-n">200px</span>;
    <span class="hl-k">vertical-align</span>: top;     <span class="hl-c">/* 顶部对齐，不然会错位 */</span>
    <span class="hl-k">margin</span>: <span class="hl-n">6px</span>;
}</pre></div>

%(ib)s

<div class="card warn">
  <div class="card-t">inline-block 的两个经典坑</div>
  <ol>
    <li><b>元素之间有缝隙</b> —— 因为 HTML 源码里标签之间的换行
      被当成一个空格（FE-01 讲的空格无效性）。
      <b>解法</b>：父元素设 <code>font-size: 0</code>，
      或把标签写在一行里，或用 <code>float</code> / flex。</li>
    <li><b>对齐不齐</b> —— inline-block 默认按 <b>基线</b>对齐，
      高度不同的卡片会歪。<b>解法</b>：加 <code>vertical-align: top</code>。</li>
  </ol>
</div>

<div class="card tip">
  <div class="card-t">那现代怎么做并排</div>
  <p>用 <b>flex</b>：</p>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">.row { display: flex; gap: 12px; }   <span class="hl-c">/* 一行搞定，没有缝隙问题 */</span></pre>
  <p style="margin-top:10px">flex 比 inline-block 好得多，<b>但它属于后面的内容</b>。
  这一篇先把 display 的三种基本值搞懂 ——
  flex 的值也是 <code>display: flex</code>，理解 display 是前提。</p>
</div>

<h2 id="s4"><span class="n">4</span>border 边框</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三段式语法</span><span class="cp">复制</span></div><pre><span class="hl-k">border</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#ccd5e3</span>;
<span class="arw">        └┬┘ └─┬─┘ └───┬───┘</span>
<span class="arw">         │    │       └─ 颜色</span>
<span class="arw">         │    └─ 样式（solid 实线 / dashed 虚线 / dotted 点线）</span>
<span class="arw">         └─ 粗细</span></pre></div>

<table>
<thead><tr><th style="width:26%">写法</th><th>效果</th></tr></thead>
<tbody>
<tr><td class="c">1px solid #ccc</td><td>实线（最常用）</td></tr>
<tr><td class="c">1px dashed #ccc</td><td>虚线</td></tr>
<tr><td class="c">2px dotted #ccc</td><td>点线</td></tr>
<tr><td class="c">none</td><td>没有边框（默认）</td></tr>
</tbody>
</table>

<h4>只给一边加边框</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">分方向写</span><span class="cp">复制</span></div><pre><span class="hl-k">border-bottom</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#e3e8f0</span>;       <span class="hl-c">/* 只有下边框 */</span>
<span class="hl-k">border-left</span>: <span class="hl-n">4px</span> solid <span class="hl-n">#1f6feb</span>;         <span class="hl-c">/* 只有左边框 */</span>
<span class="hl-k">border-top</span>: none;                        <span class="hl-c">/* 去掉上边框 */</span></pre></div>

<div class="card key">
  <div class="card-t"><code>border-left</code> 做「强调条」非常好用</div>
  <p>本文档里那些提示框，左侧那条彩色粗线就是
  <code>border-left: 4px solid …</code>：</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">提示框的做法</span><span class="cp">复制</span></div><pre>.card.note {
    <span class="hl-k">background</span>: <span class="hl-n">#e8f1fe</span>;
    <span class="hl-k">border</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#cfe1fb</span>;
    <span class="hl-k">border-left</span>: <span class="hl-n">4px</span> solid <span class="hl-n">#1f6feb</span>;   <span class="hl-c">/* ← 就是这一条 */</span>
    <span class="hl-k">border-radius</span>: <span class="hl-n">0</span> <span class="hl-n">10px</span> <span class="hl-n">10px</span> <span class="hl-n">0</span>;
}</pre></div>
  <p style="margin-top:10px">比整圈边框更「有指向性」，一眼知道这条是重点。</p>
</div>

<h4>border-radius 圆角</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">圆角的各种写法</span><span class="cp">复制</span></div><pre><span class="hl-k">border-radius</span>: <span class="hl-n">8px</span>;                 <span class="hl-c">/* 四角都是 8px */</span>
<span class="hl-k">border-radius</span>: <span class="hl-n">8px</span> <span class="hl-n">8px</span> <span class="hl-n">0</span> <span class="hl-n">0</span>;         <span class="hl-c">/* 上左 上右 下右 下左（顺时针） */</span>
<span class="hl-k">border-radius</span>: <span class="hl-n">50%</span>;                <span class="hl-c">/* 正圆（宽高相等时） */</span>
<span class="hl-k">border-radius</span>: <span class="hl-n">999px</span>;              <span class="hl-c">/* 胶囊形 —— 做药丸按钮 */</span></pre></div>

<h2 id="s5"><span class="n">5</span>box-shadow 阴影</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">五段式语法</span><span class="cp">复制</span></div><pre><span class="hl-k">box-shadow</span>: <span class="hl-n">0</span> <span class="hl-n">2px</span> <span class="hl-n">8px</span> <span class="hl-n">0</span> <span class="hl-f">rgba</span>(<span class="hl-n">20</span>,<span class="hl-n">30</span>,<span class="hl-n">50</span>,<span class="hl-n">0.14</span>);
<span class="arw">            └┬┘ └┬┘ └┬┘ └┬┘ └──────┬──────┘</span>
<span class="arw">             │   │   │   │         └─ 颜色</span>
<span class="arw">             │   │   │   └─ 扩散（一般写 0）</span>
<span class="arw">             │   │   └─ 模糊半径，越大越柔</span>
<span class="arw">             │   └─ 垂直偏移，正数往下</span>
<span class="arw">             └─ 水平偏移，正数往右</span></pre></div>

<table>
<thead><tr><th style="width:40%">写法</th><th>效果</th></tr></thead>
<tbody>
<tr><td class="c">0 1px 3px rgba(0,0,0,.12)</td><td><b>卡片轻微浮起</b> —— 默认选择</td></tr>
<tr><td class="c">0 8px 24px rgba(0,0,0,.13)</td><td><b>悬停时抬起</b>（配 transition）</td></tr>
<tr><td class="c">0 0 0 3px rgba(31,111,235,.3)</td>
    <td><b>聚焦光圈</b>（扩散不为 0，模糊为 0）</td></tr>
<tr><td class="c">inset 0 1px 0 #fff</td><td><b>内阴影</b>，做「顶部高光」</td></tr>
<tr><td class="c">2px 2px 0 #000</td><td>硬阴影（无模糊）</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">阴影的三条经验</div>
  <ol>
    <li><b>用 rgba 而不是灰色</b> —— 叠在什么背景上都自然</li>
    <li><b>偏移小、模糊大</b> = 柔和；<b>偏移大、模糊小</b> = 生硬</li>
    <li><b>要「浮起」就把阴影往下推</b>（<code>0 8px …</code>）；
      光从上方来是人的直觉</li>
  </ol>
  <p>本文档的代码块、卡片、抽屉，用的全是第 1、2 条。</p>
</div>

<h2 id="s6"><span class="n">6</span>width / height</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">常用单位</span><span class="cp">复制</span></div><pre><span class="hl-k">width</span>: <span class="hl-n">300px</span>;        <span class="hl-c">/* 固定像素 */</span>
<span class="hl-k">width</span>: <span class="hl-n">50%</span>;          <span class="hl-c">/* 父元素宽度的 50% */</span>
<span class="hl-k">width</span>: <span class="hl-n">20rem</span>;         <span class="hl-c">/* 相对根字号 */</span>
<span class="hl-k">width</span>: <span class="hl-f">calc</span>(<span class="hl-n">100%</span> - <span class="hl-n">40px</span>);  <span class="hl-c">/* 算出来 */</span>
<span class="hl-k">height</span>: <span class="hl-n">100vh</span>;       <span class="hl-c">/* 视口高度的 100% */</span></pre></div>

<table>
<thead><tr><th style="width:20%">单位</th><th>含义</th><th>典型用途</th></tr></thead>
<tbody>
<tr><td class="c">px</td><td>像素</td><td>边框、圆角、小间距</td></tr>
<tr><td class="c">%</td><td>父元素的百分比</td><td>宽度自适应</td></tr>
<tr><td class="c">vw / vh</td><td>视口宽/高的 1%</td>
    <td>全屏区域、侧边栏高度</td></tr>
<tr><td class="c">rem</td><td>根字号倍数</td><td>字号、大间距</td></tr>
<tr><td class="c">calc()</td><td>混合计算</td><td><code>calc(100% - 280px)</code></td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t"><code>height: 100%</code> 常常没反应</div>
  <p>因为<b>百分比高度要父元素有确定高度</b>才生效。
  父元素高度是 <code>auto</code>（由内容撑开）时，
  <code>height:100%</code> 就无从计算，浏览器忽略它。</p>
  <p><b>解法</b>：用 <code>100vh</code>（相对视口，不依赖父元素），
  或者给父元素也定高。</p>
</div>

<h2 id="s7"><span class="n">7</span>max-width 与 max-height</h2>

<p>它们是<b>上限</b>，不是固定值 —— 内容小的时候盒子就小，内容大才受限。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">对比</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 写死宽度：屏幕窄了会出现横向滚动条 */</span>
.container { <span class="hl-k">width</span>: <span class="hl-n">1120px</span>; }

<span class="hl-c">/* ✅ 上限 + 留白：窄屏自动缩，宽屏不超过 1120 */</span>
.container {
    <span class="hl-k">max-width</span>: <span class="hl-n">1120px</span>;
    <span class="hl-k">margin</span>: <span class="hl-n">0</span> auto;      <span class="hl-c">/* 水平居中 */</span>
    <span class="hl-k">padding</span>: <span class="hl-n">0</span> <span class="hl-n">24px</span>;
}</pre></div>

<div class="card key">
  <div class="card-t">这是响应式布局最常用的一个套路</div>
  <p><b><code>max-width</code> + <code>margin: 0 auto</code> +
  <code>padding</code></b> —— 三件套。</p>
  <ul>
    <li><b>宽屏</b>：内容居中，两侧大片留白，读起来不累</li>
    <li><b>窄屏</b>：自动缩到屏幕宽度，再靠 padding 留一点边距</li>
    <li><b>不用写任何媒体查询</b>就适配了所有屏幕</li>
  </ul>
  <p><b>本系列每一篇文档、导航页，用的都是这个套路</b>
  （导航页是 <code>max-width: 1120px</code>）。</p>
</div>

<h4>max-height 的典型用途</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">限制高度并滚动</span><span class="cp">复制</span></div><pre>.log {
    <span class="hl-k">max-height</span>: <span class="hl-n">300px</span>;
    <span class="hl-k">overflow-y</span>: auto;      <span class="hl-c">/* 超过就出现滚动条（FE-05 详讲） */</span>
}</pre></div>

<table>
<thead><tr><th style="width:26%">属性</th><th>作用</th></tr></thead>
<tbody>
<tr><td class="c">max-width</td><td>最宽不超过多少</td></tr>
<tr><td class="c">min-width</td><td>最窄不小于多少（防止被压扁）</td></tr>
<tr><td class="c">max-height</td><td>最高不超过多少</td></tr>
<tr><td class="c">min-height</td><td>最矮不小于多少</td></tr>
</tbody>
</table>

<h2 id="s8"><span class="n">8</span>一页速查</h2>

<table>
<thead><tr><th style="width:38%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>让 width 包含 padding 和 border</td>
    <td class="c">* { box-sizing: border-box; }</td></tr>
<tr><td>独占一行</td><td class="c">display: block;</td></tr>
<tr><td>跟着文字走</td><td class="c">display: inline;</td></tr>
<tr><td><b>并排且能设宽高</b></td><td class="c">display: inline-block;</td></tr>
<tr><td>并排对齐不歪</td><td class="c">vertical-align: top;</td></tr>
<tr><td>内边距（往里撑）</td><td class="c">padding: 16px;</td></tr>
<tr><td>外边距（往外推）</td><td class="c">margin: 16px;</td></tr>
<tr><td>水平居中</td><td class="c">margin: 0 auto;</td></tr>
<tr><td>边框</td><td class="c">border: 1px solid #ccd5e3;</td></tr>
<tr><td>只有下边框</td><td class="c">border-bottom: 1px solid #e3e8f0;</td></tr>
<tr><td>左侧强调条</td><td class="c">border-left: 4px solid #1f6feb;</td></tr>
<tr><td>圆角 / 胶囊 / 圆</td>
    <td class="c">border-radius: 8px / 999px / 50%;</td></tr>
<tr><td>卡片阴影</td><td class="c">box-shadow: 0 1px 3px rgba(0,0,0,.12);</td></tr>
<tr><td>悬停抬起</td><td class="c">box-shadow: 0 8px 24px rgba(0,0,0,.13);</td></tr>
<tr><td>聚焦光圈</td><td class="c">box-shadow: 0 0 0 3px rgba(31,111,235,.3);</td></tr>
<tr><td>顶部高光（内阴影）</td><td class="c">box-shadow: inset 0 1px 0 #fff;</td></tr>
<tr><td>响应式容器三件套</td>
    <td class="c">max-width: 1120px; margin: 0 auto; padding: 0 24px;</td></tr>
<tr><td>限制高度并滚动</td>
    <td class="c">max-height: 300px; overflow-y: auto;</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的五句话</div>
  <ol>
    <li><b>每个元素都是一个盒子</b>：content → padding → border → margin。</li>
    <li><b><code>box-sizing: border-box</code> 是现代 CSS 的第一行</b>，
      让 width 包含 padding 和 border。</li>
    <li><b><code>inline</code> 元素宽高无效</b>；
      要并排又要控宽高就用 <code>inline-block</code>。</li>
    <li><b>阴影用 rgba，偏移小模糊大</b>才柔和；
      <code>border-left</code> 是最好用的强调条。</li>
    <li><b><code>max-width</code> + <code>margin:0 auto</code> + <code>padding</code></b>
      三件套就能适配所有屏幕宽度。</li>
  </ol>
</div>"""

# =====================================================================
# FE-05  Writing Mode 与溢出滚动  ★ 重要
# =====================================================================
TOC05 = """  <a href="#s1">1 · 为什么这一篇标了 *</a>
  <a href="#s2">2 · writing-mode 是什么</a>
  <a href="#s3">3 · vertical-lr：竖向排版</a>
  <a href="#s4">4 · 竖排时的坐标全部换轴</a>
  <a href="#s5">5 · word-break 与换行控制</a>
  <a href="#s6">6 · overflow 溢出处理</a>
  <a href="#s7">7 · 滚动条及其样式</a>
  <a href="#s8">8 · 组合实战：一个竖排滚动容器</a>
  <a href="#s9">9 · 一页速查</a>"""

BODY05 = r"""<div class="card note">
  <div class="card-t">为什么这一篇标了 *</div>
  <p>因为 <b>UME 是「竖向编辑回鹘蒙文」的编辑器</b> ——
  竖排是这个项目的<b>核心需求</b>，不是选修内容。</p>
  <p>这一篇讲三件事，它们经常一起出现：</p>
  <ul>
    <li><b>writing-mode</b> —— 怎么把内容竖过来</li>
    <li><b>word-break</b> —— 怎么控制在哪里断行</li>
    <li><b>overflow + 滚动条</b> —— 内容装不下怎么办</li>
  </ul>
</div>

<h2 id="s1"><span class="n">1</span>为什么这一篇标了 *</h2>

<p>传统蒙文是<b>从上往下写、从左往右排</b>的。而网页默认是
「从左往右写、从上往下排」。这两者<b>正好差 90 度</b>。</p>

<table>
<thead><tr><th style="width:22%"></th><th>书写方向</th><th>行/列推进方向</th></tr></thead>
<tbody>
<tr><td><b>网页默认</b></td><td>从左往右</td><td>一行行往下</td></tr>
<tr><td><b>传统蒙文</b></td><td><b>从上往下</b></td><td><b>一列列往左</b>（也常用往右）</td></tr>
</tbody>
</table>

<p>好在 CSS 有现成的机制处理这件事 —— <b><code>writing-mode</code></b>。
它不是「把字旋转 90 度」，而是<b>真正换掉整个书写坐标系</b>。</p>

<div class="card key">
  <div class="card-t">旋转 vs 换轴，差别很大</div>
  <p><b>旋转</b>（<code>transform: rotate(90deg)</code>）：
  只是画的时候转一下，<b>文字还是横着排的</b>，
  宽度高度也没变，滚动条方向也不对。</p>
  <p><b>换轴</b>（<code>writing-mode</code>）：
  <b>整个坐标系换了</b> —— 文字真的竖排，
  <code>width</code> 变成「竖着的高度」，
  滚动条也跟着转。<b>这才是正确做法。</b></p>
</div>

<h2 id="s2"><span class="n">2</span>writing-mode 是什么</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三个值</span><span class="cp">复制</span></div><pre>.a { <span class="hl-k">writing-mode</span>: horizontal-tb; }  <span class="hl-c">/* 默认：横排，行从上到下 */</span>
.b { <span class="hl-k">writing-mode</span>: vertical-rl; }    <span class="hl-c">/* 竖排，列从右到左 */</span>
.c { <span class="hl-k">writing-mode</span>: vertical-lr; }    <span class="hl-c">/* 竖排，列从左到右 */</span></pre></div>

<table>
<thead><tr><th style="width:26%">值</th><th>文字方向</th><th>推进方向</th><th style="width:22%">典型用途</th></tr></thead>
<tbody>
<tr><td class="c">horizontal-tb</td><td>横</td><td>top → bottom</td><td>默认，绝大多数网页</td></tr>
<tr><td class="c">vertical-rl</td><td><b>竖</b></td><td>right → left</td>
    <td>中文/日文古籍、蒙文（右起）</td></tr>
<tr><td class="c">vertical-lr</td><td><b>竖</b></td><td>left → right</td>
    <td><b>蒙文常用</b>、表格侧栏标题</td></tr>
</tbody>
</table>

<p><b>名字怎么记</b>：<code>vertical-rl</code> = vertical（竖）+ rl（列从右往左）。</p>

<h2 id="s3"><span class="n">3</span>vertical-lr：竖向排版</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">最小示例</span><span class="cp">复制</span></div><pre>.vertical {
    <span class="hl-k">writing-mode</span>: vertical-lr;
    <span class="hl-k">height</span>: <span class="hl-n">200px</span>;          <span class="hl-c">/* 竖排时 height 是「一列的长度」 */</span>
}</pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">HTML</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;div</span> <span class="hl-f">class</span>=<span class="hl-s">"vertical"</span><span class="hl-p">&gt;</span>
  ᠮᠣᠩᠭᠣᠯ ᠪᠢᠴᠢᠭ
<span class="hl-p">&lt;/div&gt;</span></pre></div>

<div class="out-wrap"><div class="cap">效果（示意：一个字母一列往下，第二列在右边）</div><pre>ᠮ   ᠪ
ᠣ   ᠢ
ᠩ   ᠴ
ᠭ   ᠢ
ᠣ   ᠭ
ᠯ</pre></div>

<div class="card key">
  <div class="card-t">关键：宽高「换了含义」</div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:22%">属性</th><th style="width:38%">横排时</th><th>竖排时</th></tr></thead>
  <tbody>
  <tr><td class="c">width</td><td>横向的宽</td><td><b>横向的宽 = 有几列</b></td></tr>
  <tr><td class="c">height</td><td>纵向的高</td>
      <td><b>纵向的高 = 一列多长</b>（超出就换下一列）</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>所以竖排容器要设 <code>height</code>，
  不是 <code>width</code></b> —— 这正好和横排相反，
  是新手最容易搞错的一点。</p>
</div>

<h2 id="s4"><span class="n">4</span>竖排时的坐标全部换轴</h2>

<p>设了 <code>writing-mode</code> 之后，<b>所有和方向有关的属性都会跟着转</b>。
这不是 bug，是设计。</p>

<table>
<thead><tr><th style="width:30%">属性</th><th style="width:22%">横排时</th><th>竖排（vertical-lr）时</th></tr></thead>
<tbody>
<tr><td class="c">text-align: left</td><td>靠左</td>
    <td><b>靠上</b>（文字方向的起点）</td></tr>
<tr><td class="c">margin-top</td><td>上边距</td>
    <td><b>还是物理上的上</b>（margin 是物理属性）</td></tr>
<tr><td class="c">padding-left</td><td>左内边距</td>
    <td><b>还是物理上的左</b></td></tr>
<tr><td class="c">overflow-y</td><td>纵向滚动</td>
    <td><b>不转了</b> —— 竖排时「列溢出」是横向的</td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">这里有个容易混乱的点</div>
  <p><b>逻辑属性</b>（跟文字方向走的）会换轴：
  <code>text-align</code>、<code>block-size</code>、
  <code>inline-size</code>、<code>margin-block</code>…</p>
  <p><b>物理属性</b>（跟屏幕方向走的）<b>不换</b>：
  <code>margin-top</code>、<code>padding-left</code>、
  <code>top/left</code>、<code>width/height</code>。</p>
  <p><b>实用结论</b>：竖排时别用 <code>overflow-y</code> 猜方向 ——
  直接用 <code>overflow: auto</code> 让它两个方向都管。</p>
</div>

<h2 id="s5"><span class="n">5</span>word-break 与换行控制</h2>

<p>文字到边界要换行。但「在哪里可以断」是可以控制的 ——
这在处理长单词、长路径、以及<b>蒙文</b>时很关键。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">word-break 的常用值</span><span class="cp">复制</span></div><pre>.a { <span class="hl-k">word-break</span>: normal; }      <span class="hl-c">/* 默认：英文单词不断，可能溢出 */</span>
.b { <span class="hl-k">word-break</span>: break-all; }   <span class="hl-c">/* 任何位置都能断（连单词中间也断） */</span>
.c { <span class="hl-k">word-break</span>: keep-all; }    <span class="hl-c">/* 中日韩也不断，只在空格断 */</span></pre></div>

<h4>还有一个更常用的：overflow-wrap</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">长串不断行的问题</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ❌ 一个很长的路径，没有空格 → 直接把容器撑破 */</span>
.path { }
<span class="hl-c">   D:\Path\To\project\build\UmeMath.lib   ← 这一整串不会断</span>

<span class="hl-c">/* ✅ 允许在长串内部断行 */</span>
.path {
    <span class="hl-k">overflow-wrap</span>: anywhere;   <span class="hl-c">/* 只在「实在放不下」时才断 */</span>
    <span class="hl-k">word-break</span>: break-word;    <span class="hl-c">/* 兼容旧浏览器 */</span>
}</pre></div>

<div class="card key">
  <div class="card-t">本系列文档就踩过这个坑</div>
  <p>教程里有大量长路径（<code>D:\Path\To\project\build\path1.exe</code>）
  和长命令。<b>窄屏上它们把表格和终端块撑得比屏幕还宽</b>，
  出现横向滚动条。</p>
  <p>解法就是给这些容器加：</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">移动端断行规则（本文档实际在用的）</span><span class="cp">复制</span></div><pre><span class="hl-p">@media</span> (max-width: <span class="hl-n">980px</span>) {
    main table th, main table td, main td, main th {
        <span class="hl-k">overflow-wrap</span>: anywhere;
        <span class="hl-k">word-break</span>: break-word;
    }
}</pre></div>
</div>

<table>
<thead><tr><th style="width:30%">属性</th><th>管什么</th></tr></thead>
<tbody>
<tr><td class="c">white-space: nowrap</td>
    <td><b>完全不换行</b>（会溢出，常配 overflow）</td></tr>
<tr><td class="c">white-space: pre</td>
    <td>保留空格和换行（代码块用）</td></tr>
<tr><td class="c">word-break: break-all</td>
    <td>任意位置可断，<b>最激进</b></td></tr>
<tr><td class="c">overflow-wrap: anywhere</td>
    <td><b>只在必要时断</b>，日常首选</td></tr>
<tr><td class="c">hyphens: auto</td>
    <td>英文加连字符断词</td></tr>
</tbody>
</table>

<h2 id="s6"><span class="n">6</span>overflow 溢出处理</h2>

<p>内容比盒子大时怎么办 —— 这就是 <code>overflow</code>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">五个值</span><span class="cp">复制</span></div><pre>.a { <span class="hl-k">overflow</span>: visible; }   <span class="hl-c">/* 默认：不管，直接画到盒子外面 */</span>
.b { <span class="hl-k">overflow</span>: hidden; }    <span class="hl-c">/* 超出部分裁掉（看不见了） */</span>
.c { <span class="hl-k">overflow</span>: scroll; }    <span class="hl-c">/* 永远显示滚动条，哪怕装得下 */</span>
.d { <span class="hl-k">overflow</span>: auto; }      <span class="hl-c">/* 需要时才出现滚动条 —— 最常用 */</span>
.e { <span class="hl-k">overflow</span>: clip; }      <span class="hl-c">/* 裁掉，且不能滚动 */</span></pre></div>

<table>
<thead><tr><th style="width:22%">值</th><th>超出时</th><th>能滚吗</th><th style="width:20%">什么时候用</th></tr></thead>
<tbody>
<tr><td class="c">visible</td><td>画到外面</td><td>—</td><td>默认，一般不想要</td></tr>
<tr><td class="c">hidden</td><td>裁掉</td><td>不能</td>
    <td>做圆角容器（<code>overflow:hidden</code> 让子元素也被裁成圆角）</td></tr>
<tr><td class="c">auto</td><td>出现滚动条</td><td><b>能</b></td>
    <td><span class="tag g">最常用</span> 日志、长列表、代码块</td></tr>
<tr><td class="c">scroll</td><td>总是有滚动条</td><td><b>能</b></td>
    <td>想避免「出现滚动条时布局跳动」</td></tr>
<tr><td class="c">clip</td><td>裁掉</td><td>不能</td><td>同 hidden 但更彻底</td></tr>
</tbody>
</table>

<h4>分方向控制</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">只控制一个方向</span><span class="cp">复制</span></div><pre><span class="hl-k">overflow-x</span>: auto;    <span class="hl-c">/* 只在横向需要时滚动 —— 宽表格用这个 */</span>
<span class="hl-k">overflow-y</span>: auto;    <span class="hl-c">/* 只在纵向需要时滚动 —— 长列表用这个 */</span>

<span class="hl-c">/* 横竖都要管，直接写简写 */</span>
<span class="hl-k">overflow</span>: auto;</pre></div>

<div class="card tip">
  <div class="card-t">宽表格在手机上的标准解法</div>
  <p>表格宽 700px，手机只有 375px —— 怎么办？</p>
  <p><b>给表格外面套一个 <code>overflow-x: auto</code> 的容器</b>，
  表格本身不缩、文字不变小，用户左右滑就能看完。</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">本文档表格就是这么做的</span><span class="cp">复制</span></div><pre>.table-wrap {
    <span class="hl-k">overflow-x</span>: auto;
    <span class="hl-k">-webkit-overflow-scrolling</span>: touch;   <span class="hl-c">/* 手机上滑动更顺 */</span>
}</pre></div>
</div>

<h2 id="s7"><span class="n">7</span>滚动条及其样式</h2>

<p>滚动条<b>默认长得很丑</b>（灰色方块），而且不同浏览器不一样。
但它是可以改的。</p>

<h4>方案一：WebKit 伪元素（Chrome / Edge / Safari）</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">精细控制</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 整条滚动条 */</span>
::-webkit-scrollbar {
    <span class="hl-k">width</span>: <span class="hl-n">10px</span>;              <span class="hl-c">/* 竖向滚动条的宽 */</span>
    <span class="hl-k">height</span>: <span class="hl-n">10px</span>;             <span class="hl-c">/* 横向滚动条的高 */</span>
}

<span class="hl-c">/* 滑块（你拖的那个） */</span>
::-webkit-scrollbar-thumb {
    <span class="hl-k">background</span>: <span class="hl-n">#ccd5e3</span>;
    <span class="hl-k">border-radius</span>: <span class="hl-n">999px</span>;      <span class="hl-c">/* 圆头 */</span>
}
::-webkit-scrollbar-thumb:hover { <span class="hl-k">background</span>: <span class="hl-n">#8b95a5</span>; }

<span class="hl-c">/* 轨道（滑块走的槽） */</span>
::-webkit-scrollbar-track { <span class="hl-k">background</span>: <span class="hl-n">#f7f9fc</span>; }

<span class="hl-c">/* 两端的小箭头（去掉更好看） */</span>
::-webkit-scrollbar-button { <span class="hl-k">display</span>: none; }</pre></div>

<h4>方案二：标准属性（Firefox 等）</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">两行版</span><span class="cp">复制</span></div><pre>.scroll-box {
    <span class="hl-k">scrollbar-width</span>: thin;                  <span class="hl-c">/* auto / thin / none */</span>
    <span class="hl-k">scrollbar-color</span>: <span class="hl-n">#ccd5e3</span> <span class="hl-n">#f7f9fc</span>;      <span class="hl-c">/* 滑块色  轨道色 */</span>
}</pre></div>

<div class="card key">
  <div class="card-t">两套要一起写</div>
  <p><code>::-webkit-scrollbar</code> 在 Chrome / Edge / Safari 有效，
  Firefox 不认；<code>scrollbar-width</code> / <code>scrollbar-color</code>
  在 Firefox 有效，老 Chrome 不认。</p>
  <p><b>所以两个都写上</b>，各浏览器各取所需。
  本文档目录栏的细滚动条就是这么做的。</p>
</div>

<h4>完全隐藏滚动条（但仍能滚）</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三种写法</span><span class="cp">复制</span></div><pre>.hide-bar {
    <span class="hl-k">scrollbar-width</span>: none;             <span class="hl-c">/* Firefox */</span>
    <span class="hl-k">-ms-overflow-style</span>: none;          <span class="hl-c">/* 旧 Edge/IE */</span>
}
.hide-bar::-webkit-scrollbar { <span class="hl-k">display</span>: none; }   <span class="hl-c">/* Chrome/Edge/Safari */</span></pre></div>

<div class="card warn">
  <div class="card-t">隐藏滚动条要谨慎</div>
  <p>滚动条是<b>「这里还有内容」的唯一提示</b>。
  藏起来用户可能根本不知道能滚。</p>
  <p>如果一定要藏，请<b>同时给出别的提示</b> ——
  比如内容被裁掉一半，或者加个渐隐遮罩。</p>
</div>

<h2 id="s8"><span class="n">8</span>组合实战：一个竖排滚动容器</h2>

<p>把这一篇的三样东西合起来 —— 这正是 UME 编辑器需要的结构：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">竖排 + 滚动 + 细滚动条</span><span class="cp">复制</span></div><pre>.editor {
    <span class="hl-c">/* ① 竖排 */</span>
    <span class="hl-k">writing-mode</span>: vertical-lr;

    <span class="hl-c">/* ② 尺寸：竖排时 height 是「一列多长」 */</span>
    <span class="hl-k">height</span>: <span class="hl-n">70vh</span>;              <span class="hl-c">/* 70% 视口高 */</span>
    <span class="hl-k">max-height</span>: <span class="hl-n">600px</span>;
    <span class="hl-k">width</span>: <span class="hl-n">100%</span>;               <span class="hl-c">/* 横着能放几列 */</span>

    <span class="hl-c">/* ③ 装不下就滚 */</span>
    <span class="hl-k">overflow</span>: auto;
    <span class="hl-k">overflow-wrap</span>: anywhere;     <span class="hl-c">/* 长串别撑破 */</span>

    <span class="hl-c">/* ④ 滚动条样式 */</span>
    <span class="hl-k">scrollbar-width</span>: thin;
    <span class="hl-k">scrollbar-color</span>: <span class="hl-n">#ccd5e3</span> <span class="hl-n">transparent</span>;

    <span class="hl-c">/* ⑤ 好看一点 */</span>
    <span class="hl-k">padding</span>: <span class="hl-n">20px</span>;
    <span class="hl-k">border</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#ccd5e3</span>;
    <span class="hl-k">border-radius</span>: <span class="hl-n">10px</span>;
    <span class="hl-k">font-size</span>: <span class="hl-n">20px</span>;
    <span class="hl-k">line-height</span>: <span class="hl-n">1.9</span>;
}
.editor::-webkit-scrollbar { <span class="hl-k">height</span>: <span class="hl-n">8px</span>; }
.editor::-webkit-scrollbar-thumb {
    <span class="hl-k">background</span>: <span class="hl-n">#ccd5e3</span>; <span class="hl-k">border-radius</span>: <span class="hl-n">999px</span>;
}</pre></div>

<div class="card key">
  <div class="card-t">注意第 ④ 步的滚动条方向</div>
  <p>竖排之后，「列放不下」是<b>横向</b>溢出 ——
  所以滚动条出现在<b>底部</b>，要用
  <code>::-webkit-scrollbar { height: … }</code>
  （不是 <code>width</code>）。</p>
  <p><b>这就是「换轴」的体现</b>：横排时改 width，竖排时改 height。</p>
</div>

<h2 id="s9"><span class="n">9</span>一页速查</h2>

<table>
<thead><tr><th style="width:40%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>横排（默认）</td><td class="c">writing-mode: horizontal-tb;</td></tr>
<tr><td>竖排，列从右往左</td><td class="c">writing-mode: vertical-rl;</td></tr>
<tr><td><b>竖排，列从左往右</b></td><td class="c">writing-mode: vertical-lr;</td></tr>
<tr><td>竖排容器设长度</td><td class="c">height: 400px;　← 不是 width</td></tr>
<tr><td>任意位置可断行</td><td class="c">word-break: break-all;</td></tr>
<tr><td>只在必要时断行</td><td class="c">overflow-wrap: anywhere;</td></tr>
<tr><td>完全不换行</td><td class="c">white-space: nowrap;</td></tr>
<tr><td>保留空格换行</td><td class="c">white-space: pre;</td></tr>
<tr><td>超出就滚动</td><td class="c">overflow: auto;</td></tr>
<tr><td>只横向滚（宽表格）</td><td class="c">overflow-x: auto;</td></tr>
<tr><td>裁掉超出（做圆角）</td><td class="c">overflow: hidden;</td></tr>
<tr><td>滚动条粗细（Firefox）</td><td class="c">scrollbar-width: thin;</td></tr>
<tr><td>滚动条配色</td><td class="c">scrollbar-color: #ccd5e3 transparent;</td></tr>
<tr><td>滚动条圆角滑块</td><td class="c">::-webkit-scrollbar-thumb { border-radius: 999px; }</td></tr>
<tr><td>隐藏滚动条但仍能滚</td>
    <td class="c">scrollbar-width:none; ::-webkit-scrollbar{display:none}</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的六句话</div>
  <ol>
    <li><b><code>writing-mode</code> 是「换坐标系」，不是「旋转」</b> ——
      文字真的竖排，滚动条也跟着转。</li>
    <li><b>竖排时 <code>height</code> 才是「一列多长」</b>，
      <code>width</code> 是「能放几列」—— <b>和横排正好相反</b>。</li>
    <li><b>逻辑属性和文字方向走，物理属性和屏幕方向走</b>；
      分不清就用 <code>overflow: auto</code> 让它两个方向都管。</li>
    <li><b>长路径/长命令会撑破窄屏</b> ——
      用 <code>overflow-wrap: anywhere</code> 治它。</li>
    <li><b>宽表格用 <code>overflow-x: auto</code> 套一层</b>，
      不要缩字号。</li>
    <li><b>滚动条样式要写两套</b>（WebKit 伪元素 + 标准属性），
      而且<b>别轻易隐藏</b> —— 那是「还有内容」的唯一提示。</li>
  </ol>
</div>"""

IB = pv(30, "inline-block：三个并排的卡片",
        """.card {
    display: inline-block;
    width: 150px;
    height: 74px;
    vertical-align: top;    /* 顶部对齐，不然会错位 */
    margin: 6px;
    background: #e8f1fe;
    border: 1px solid #1f6feb;
    border-radius: 8px;
    text-align: center;
    line-height: 74px;
    font-size: 13px;
}""",
        demo=('<div class="card">卡片一</div>'
              '<div class="card">卡片二</div>'
              '<div class="card">卡片三</div>'))

if __name__ == "__main__":
    b4 = BODY04.replace("%(ib)s", IB)
    print(build("fe-05.html", "FE-05", "Display 与盒模型尺寸", b4, TOC04))
    print(build("fe-06.html", "FE-06", "Writing Mode 与溢出滚动", BODY05, TOC05))
