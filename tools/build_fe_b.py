# -*- coding: utf-8 -*-
"""FE-03-F01（颜色模型）与 FE-03（CSS 入门）"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build

# =====================================================================
# FE-03-F01  颜色模型  ★ 重要
# =====================================================================
TOC3F1 = """  <a href="#s1">1 · 颜色在计算机里是什么</a>
  <a href="#s2">2 · 十六进制 RGB</a>
  <a href="#s3">3 · 十进制 RGB 表示法</a>
  <a href="#s4">4 · HSV / HSL 颜色模型</a>
  <a href="#s5">5 · Alpha 通道（透明度）</a>
  <a href="#s6">6 · 安全色与取色</a>
  <a href="#s7">7 · 颜色拾取器</a>
  <a href="#s8">8 · 一页速查</a>"""

BODY3F1 = r"""<div class="card note">
  <div class="card-t">为什么这一篇标了 *</div>
  <p>做界面、做字体、做导出图，<b>颜色是天天要碰的东西</b>。
  而颜色在代码里是用<b>数字</b>表示的 ——
  不懂这套表示法，就只能靠试，改一次看一次。</p>
  <p>这一篇把它讲透。<b>不用记，但要懂。</b></p>
</div>

<h2 id="s1"><span class="n">1</span>颜色在计算机里是什么</h2>

<p>显示器由无数个<b>发光的小点</b>组成。每个点里有<b>三个小灯</b>：
<b>红（R</b>ed<b>）、绿（G</b>reen<b>）、蓝（B</b>lue<b>）</b>。</p>

<div class="card key">
  <div class="card-t">核心原理</div>
  <p><b>调这三个灯的亮度，就能混出几乎所有颜色。</b></p>
  <p>所以「一个颜色」在代码里其实是一组三个数：<b>(红, 绿, 蓝)</b>。</p>
  <p>这叫 <b>RGB 颜色模型</b>。</p>
</div>

<table>
<thead><tr><th style="width:22%">灯的亮度</th><th>混出来</th></tr></thead>
<tbody>
<tr><td class="c">全灭 (0,0,0)</td><td><b>黑色</b></td></tr>
<tr><td class="c">全亮 (255,255,255)</td><td><b>白色</b></td></tr>
<tr><td class="c">只亮红 (255,0,0)</td><td>纯红</td></tr>
<tr><td class="c">红+绿 (255,255,0)</td><td><b>黄色</b></td></tr>
<tr><td class="c">红+蓝 (255,0,255)</td><td>品红（洋红）</td></tr>
<tr><td class="c">绿+蓝 (0,255,255)</td><td>青色</td></tr>
<tr><td class="c">三个都是中间值 (128,128,128)</td><td><b>灰色</b></td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">为什么是「加法」</div>
  <p>因为屏幕是<b>自己发光</b>的。灯越多越亮 → 全亮是白。</p>
  <p>而打印机是<b>反射光</b>的，颜料越多越暗 → 全混是黑。
  所以印刷用 CMY（青品黄）<b>减法</b>模型，和屏幕相反。</p>
</div>

<h4>为什么最大是 255</h4>
<p>因为每个灯用一个字节（8 位）存亮度：<b>2⁸ = 256 档</b>，从 0 到 255。</p>
<pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">0   → 0000 0000  → 灯全灭
255 → 1111 1111  → 灯最亮
128 → 1000 0000  → 一半亮度</pre>
<p>所以一个 RGB 颜色正好占 <b>3 字节</b> —— 这也解释了后面看到的
「6 位十六进制」为什么刚好够。</p>

<h2 id="s2"><span class="n">2</span>十六进制 RGB</h2>

<p>CSS 里最常写的颜色格式是 <code>#RRGGBB</code>：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">十六进制颜色</span><span class="cp">复制</span></div><pre><span class="hl-c">/*  # 红 绿 蓝   每两位一组 */</span>
   #<span class="hl-n">FF</span><span class="hl-n">00</span><span class="hl-n">00</span>    <span class="hl-c">/* 纯红 */</span>
   #<span class="hl-n">00</span><span class="hl-n">FF</span><span class="hl-n">00</span>    <span class="hl-c">/* 纯绿 */</span>
   #<span class="hl-n">00</span><span class="hl-n">00</span><span class="hl-n">FF</span>    <span class="hl-c">/* 纯蓝 */</span>
   #<span class="hl-n">FF</span><span class="hl-n">FF</span><span class="hl-n">FF</span>    <span class="hl-c">/* 白 */</span>
   #<span class="hl-n">00</span><span class="hl-n">00</span><span class="hl-n">00</span>    <span class="hl-c">/* 黑 */</span>
   #<span class="hl-n">1F</span><span class="hl-n">6F</span><span class="hl-n">EB</span>    <span class="hl-c">/* 本文档用的那个蓝 */</span></pre></div>

<div class="card key">
  <div class="card-t">怎么读 <code>#1F6FEB</code></div>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:16%">分组</th><th style="width:20%">十六进制</th><th>换算成十进制</th></tr></thead>
  <tbody>
  <tr><td class="c">1F</td><td>1×16 + 15</td><td><b>31</b> → 红</td></tr>
  <tr><td class="c">6F</td><td>6×16 + 15</td><td><b>111</b> → 绿</td></tr>
  <tr><td class="c">EB</td><td>14×16 + 11</td><td><b>235</b> → 蓝</td></tr>
  </tbody></table>
  <p style="margin-top:10px">所以 <code>#1F6FEB</code> 就是
  <code>rgb(31, 111, 235)</code> —— <b>两种写法是同一个颜色</b>。</p>
</div>

<h4>十六进制速记</h4>
<table>
<thead><tr><th style="width:26%">十六进制位</th><th>十进制</th><th style="width:30%">含义</th></tr></thead>
<tbody>
<tr><td class="c">0</td><td class="c">0</td><td>全灭</td></tr>
<tr><td class="c">F</td><td class="c">15</td><td>这一位满</td></tr>
<tr><td class="c">FF</td><td class="c">255</td><td><b>整个通道满</b></td></tr>
<tr><td class="c">80</td><td class="c">128</td><td>约一半</td></tr>
<tr><td class="c">40</td><td class="c">64</td><td>约四分之一</td></tr>
</tbody>
</table>

<p><b>十六进制只有 16 个符号</b>：<code>0-9</code> 然后 <code>A=10, B=11, C=12, D=13, E=14, F=15</code>。
凑不出 16 个数才用字母 —— 这就是「为什么有字母」的全部原因。</p>

<h4>六位可以缩成三位</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">缩写规则</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 每一组两位相同 → 可以各留一位 */</span>
#<span class="hl-n">FF</span><span class="hl-n">00</span><span class="hl-n">00</span>   →   #<span class="hl-n">F</span><span class="hl-n">0</span><span class="hl-n">0</span>       <span class="hl-c">/* 同一个红色 */</span>
#<span class="hl-n">FFFFFF</span>   →   #<span class="hl-n">FFF</span>       <span class="hl-c">/* 同一个白色 */</span>
#<span class="hl-n">1F6FEB</span>   →   <span class="hl-c">/* 缩不了：1F 两位不同 */</span></pre></div>

<h2 id="s3"><span class="n">3</span>十进制 RGB 表示法</h2>

<p>不想换算就用十进制写法，更直观：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三种常用的等价写法</span><span class="cp">复制</span></div><pre>.a { color: <span class="hl-n">#1F6FEB</span>; }               <span class="hl-c">/* 十六进制（最常用） */</span>
.b { color: <span class="hl-f">rgb</span>(<span class="hl-n">31</span>, <span class="hl-n">111</span>, <span class="hl-n">235</span>); }    <span class="hl-c">/* 十进制 0~255 */</span>
.c { color: <span class="hl-f">rgb</span>(<span class="hl-n">12%</span>, <span class="hl-n">44%</span>, <span class="hl-n">92%</span>); }    <span class="hl-c">/* 百分比 */</span></pre></div>

<table>
<thead><tr><th style="width:30%">写法</th><th>什么时候用</th></tr></thead>
<tbody>
<tr><td class="c">#1F6FEB</td><td><b>设计稿上抄来的值</b>，一般都用这个</td></tr>
<tr><td class="c">rgb(31,111,235)</td><td>想微调某个通道时更好读</td></tr>
<tr><td class="c">rgb(12%,44%,92%)</td><td>需要按比例算时</td></tr>
</tbody>
</table>

<h4>灰色系的写法</h4>
<p>三个通道相等就是灰。CSS 里有个更短的词 <code>gray</code> 系列，但<b>不够用</b>，
实际都自己写：</p>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">做界面最常用的几个灰</span><span class="cp">复制</span></div><pre><span class="hl-n">#000000</span>   <span class="hl-c">/* 纯黑 —— 正文别用，太刺眼 */</span>
<span class="hl-n">#1a1f28</span>   <span class="hl-c">/* 近黑，正文色（本文档就用它） */</span>
<span class="hl-n">#4b5563</span>   <span class="hl-c">/* 次级文字 */</span>
<span class="hl-n">#8b95a5</span>   <span class="hl-c">/* 辅助文字 / 注释 */</span>
<span class="hl-n">#ccd5e3</span>   <span class="hl-c">/* 边框 */</span>
<span class="hl-n">#e3e8f0</span>   <span class="hl-c">/* 浅分隔线 */</span>
<span class="hl-n">#f7f9fc</span>   <span class="hl-c">/* 浅灰背景 */</span>
<span class="hl-n">#ffffff</span>   <span class="hl-c">/* 纯白 */</span></pre></div>

<div class="card tip">
  <div class="card-t">为什么正文不用纯黑</div>
  <p><code>#000</code> 在白底上对比度过高，长时间看<b>容易累</b>。
  所以正经的界面正文都用 <code>#1a1f28</code> 这类「近黑」。</p>
  <p>同理，纯白背景也常调成 <code>#fafbfc</code> 这种「近白」。</p>
</div>

<h2 id="s4"><span class="n">4</span>HSV / HSL 颜色模型</h2>

<p>RGB 的问题是<b>不直观</b>：「这个蓝再亮一点」在 RGB 里要同时改三个数，还容易改偏色。</p>
<p>于是有了另一套模型 —— <b>HSV</b>（也叫 HSB）和它的近亲 <b>HSL</b>：</p>

<table>
<thead><tr><th style="width:14%">字母</th><th style="width:26%">含义</th><th>取值</th></tr></thead>
<tbody>
<tr><td class="c">H</td><td><b>Hue 色相</b>：什么颜色</td>
    <td>0~360 度（色环上的角度）</td></tr>
<tr><td class="c">S</td><td><b>Saturation 饱和度</b>：多鲜艳</td>
    <td>0% = 灰，100% = 最鲜艳</td></tr>
<tr><td class="c">V</td><td><b>Value 明度</b>（HSL 里是 <b>L</b>ightness 亮度）</td>
    <td>0% = 黑，100% = 最亮</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">色相环：0~360 度</div>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">   0°  红
  60°  黄
 120°  绿
 180°  青
 240°  蓝
 300°  品红
 360°  回到红</pre>
  <p style="margin-top:10px">所以「把红调成绿」就是 <b>H 从 0 改成 120</b> ——
  一个数的事，不用担心改出偏色。</p>
</div>

<h4>HSL 在 CSS 里能直接用</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">同一个蓝的四种写法</span><span class="cp">复制</span></div><pre><span class="hl-f">hsl</span>(<span class="hl-n">217</span>, <span class="hl-n">83%</span>, <span class="hl-n">52%</span>)      <span class="hl-c">/* ← 本文档那个蓝 */</span>
<span class="hl-f">rgb</span>(<span class="hl-n">31</span>, <span class="hl-n">111</span>, <span class="hl-n">235</span>)
<span class="hl-n">#1F6FEB</span>

<span class="hl-c">/* 想调亮一点点：只动 L */</span>
<span class="hl-f">hsl</span>(<span class="hl-n">217</span>, <span class="hl-n">83%</span>, <span class="hl-n">62%</span>)      <span class="hl-c">/* 同样的蓝，亮一档，色相没变 */</span></pre></div>

<div class="card tip">
  <div class="card-t">什么时候 HSL 比 RGB 好用</div>
  <ul>
    <li><b>做「同色系深浅」</b>：保持 H 和 S，只调 L ——
      自动得到一组和谐的颜色</li>
    <li><b>做 hover 效果</b>：<code>hsl(217,83%,52%)</code> →
      <code>hsl(217,83%,62%)</code>，只改一个数</li>
    <li><b>做灰阶</b>：S 设 0%，只调 L</li>
  </ul>
  <p>反过来，如果颜色是从设计稿抄来的，<b>直接用十六进制</b>，不用换算。</p>
</div>

<h2 id="s5"><span class="n">5</span>Alpha 通道（透明度）</h2>

<p>前面三个数定「什么颜色」。再加<b>第四个数</b>就能定「多透明」——
这叫 <b>Alpha 通道</b>。</p>

<table>
<thead><tr><th style="width:24%">Alpha 值</th><th>效果</th></tr></thead>
<tbody>
<tr><td class="c">1.0 或 100%</td><td><b>完全不透明</b>（默认）</td></tr>
<tr><td class="c">0.5 或 50%</td><td>半透明，能看到背后</td></tr>
<tr><td class="c">0.15 或 15%</td><td>很淡，常用于浅色背景</td></tr>
<tr><td class="c">0 或 0%</td><td><b>完全透明</b>（看不见，但仍占位置）</td></tr>
</tbody>
</table>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">四种写法</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ① 八位十六进制：最后两位是 alpha */</span>
<span class="hl-n">#1F6FEB80</span>              <span class="hl-c">/* 80 = 128/255 ≈ 50% 透明 */</span>

<span class="hl-c">/* ② rgba，第四个参数 0~1 */</span>
<span class="hl-f">rgba</span>(<span class="hl-n">31</span>, <span class="hl-n">111</span>, <span class="hl-n">235</span>, <span class="hl-n">0.5</span>)

<span class="hl-c">/* ③ hsla */</span>
<span class="hl-f">hsla</span>(<span class="hl-n">217</span>, <span class="hl-n">83%</span>, <span class="hl-n">52%</span>, <span class="hl-n">0.5</span>)

<span class="hl-c">/* ④ 现代写法：rgb 里直接给第四个值 */</span>
<span class="hl-f">rgb</span>(<span class="hl-n">31</span> <span class="hl-n">111</span> <span class="hl-n">235</span> / <span class="hl-n">50%</span>)</pre></div>

<div class="card warn">
  <div class="card-t">Alpha 在十六进制里也是 0~255</div>
  <p>最后两位虽是十六进制，但含义同 RGB 通道：
  <code>00</code> = 全透明，<code>FF</code> = 不透明，<code>80</code> ≈ 一半。</p>
  <p>所以 <code>#1F6FEB80</code> 里的 <code>80</code> 不是「80%」——
  它约等于 <b>50%</b>。<b>别想当然。</b></p>
</div>

<h4>半透明最有用的场景</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">常见的三种用法</span><span class="cp">复制</span></div><pre><span class="hl-c">/* ① 浅色背景：一个颜色兼顾白底和深色底 */</span>
.card { background: <span class="hl-f">rgba</span>(<span class="hl-n">31</span>, <span class="hl-n">111</span>, <span class="hl-n">235</span>, <span class="hl-n">0.08</span>); }

<span class="hl-c">/* ② 遮罩：盖住页面又不完全挡住 */</span>
.mask { background: <span class="hl-f">rgba</span>(<span class="hl-n">18</span>, <span class="hl-n">26</span>, <span class="hl-n">40</span>, <span class="hl-n">0.42</span>); }

<span class="hl-c">/* ③ 阴影：黑色加透明度，而不是用灰色 */</span>
box-shadow: 0 2px 8px <span class="hl-f">rgba</span>(<span class="hl-n">20</span>, <span class="hl-n">30</span>, <span class="hl-n">50</span>, <span class="hl-n">0.14</span>);</pre></div>

<p>本文档的提示框、目录抽屉的遮罩、卡片的阴影，
<b>全都用 rgba 而不是实色</b> —— 这样叠在任何背景上都自然。</p>

<h2 id="s6"><span class="n">6</span>安全色与取色</h2>

<h4>什么是「安全色」</h4>
<p>「Web 安全色」是<b>早期</b>（256 色显示器时代）的一套约定：
每个通道只取 <code>00 / 33 / 66 / 99 / CC / FF</code> 六个值，
共 <b>6×6×6 = 216 种</b>，保证在任何设备上都不抖动。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">安全色的样子</span><span class="cp">复制</span></div><pre><span class="hl-n">#FF0000</span>   <span class="hl-c">/* ✅ 安全（每通道是 00 或 FF） */</span>
<span class="hl-n">#336699</span>   <span class="hl-c">/* ✅ 安全（33/66/99 都在那六个数里） */</span>
<span class="hl-n">#1F6FEB</span>   <span class="hl-c">/* ❌ 不安全（1F/6F/EB 是中间值） */</span></pre></div>

<div class="card tip">
  <div class="card-t">现在还需要守安全色吗</div>
  <p><b>不需要了。</b>今天的显示器都是 1600 万色以上，
  安全色的限制早就没了意义。</p>
  <p><b>但知道有这回事有好处</b>：看到老代码里的
  <code>#336699</code>、<code>#CCCCCC</code> 这种「很整齐」的颜色，
  就知道它来自那个年代。</p>
</div>

<h4>怎么取到一个颜色</h4>
<table>
<thead><tr><th style="width:30%">办法</th><th>说明</th></tr></thead>
<tbody>
<tr><td><b>浏览器 F12</b></td>
    <td>最实用。Elements 面板里点颜色方块 → <b>吸管图标</b> →
      页面任意位置取色 → 直接给出十六进制</td></tr>
<tr><td><b>截图工具 / 取色器</b></td>
    <td>Windows 的「截图工具」、各类取色软件都能读数</td></tr>
<tr><td><b>设计稿</b></td>
    <td>Figma / PS 里点一下就能复制颜色值</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">对比度：比「好看」更重要的事</div>
  <p>文字和背景的<b>明暗差</b>不够，读者会看不清 ——
  这是无障碍（accessibility）的硬指标。</p>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:34%">对比度</th><th>评价</th></tr></thead>
  <tbody>
  <tr><td class="c">≥ 4.5 : 1</td><td><span class="tag g">合格</span> 正文的最低要求</td></tr>
  <tr><td class="c">≥ 7 : 1</td><td><span class="tag g">优秀</span> AAA 级</td></tr>
  <tr><td class="c">&lt; 3 : 1</td><td><span class="tag r">不合格</span> 大标题也勉强</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>本系列文档的代码区对比度做到了 18:1 以上</b> ——
  这不是「好看」，是「看得清」。</p>
</div>

<h2 id="s8"><span class="n">8</span>一页速查</h2>

<table>
<thead><tr><th style="width:32%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>十六进制</td><td class="c">#1F6FEB</td></tr>
<tr><td>三位缩写（每通道两位相同时）</td><td class="c">#F00　#FFF</td></tr>
<tr><td>十进制 RGB</td><td class="c">rgb(31, 111, 235)</td></tr>
<tr><td>百分比</td><td class="c">rgb(12%, 44%, 92%)</td></tr>
<tr><td>色相 / 饱和 / 亮度</td><td class="c">hsl(217, 83%, 52%)</td></tr>
<tr><td>带透明度</td><td class="c">rgba(31,111,235,0.5)　hsla(…)　#1F6FEB80</td></tr>
<tr><td>黑色 / 白色</td><td class="c">#000　#FFF</td></tr>
<tr><td>近黑正文色</td><td class="c">#1a1f28</td></tr>
<tr><td>浅灰背景</td><td class="c">#f7f9fc</td></tr>
<tr><td>边框灰</td><td class="c">#ccd5e3</td></tr>
<tr><td>调亮同一色系</td><td class="c">hsl 里只加 L</td></tr>
<tr><td>取色</td><td>F12 → 颜色方块 → 吸管</td></tr>
<tr><td>检查对比度</td><td>尽量 ≥ 4.5 : 1</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的六句话</div>
  <ol>
    <li><b>颜色 = 三个灯的亮度</b>：红、绿、蓝，各 0~255。</li>
    <li><b>十六进制两位一组</b>：<code>#RRGGBB</code>，
      <code>FF</code>=255、<code>00</code>=0；只有 16 个符号，所以有 A~F。</li>
    <li><b>每通道两位相同可缩写</b>：<code>#FF0000</code> → <code>#F00</code>。</li>
    <li><b>HSV / HSL 更直观</b>：H 是颜色（0~360 度），S 是鲜艳度，L/V 是明暗
      —— <b>做同色系深浅时用它</b>。</li>
    <li><b>Alpha 是第四个值</b>：<code>rgba(…, 0.5)</code>；
      写在十六进制里是最后两位，<code>80</code> ≈ 50% 不是 80%。</li>
    <li><b>安全色已经过时</b>，但<b>对比度永远要管</b> —— 正文至少 4.5 : 1。</li>
  </ol>
</div>"""

# =====================================================================
# FE-03  CSS 入门
# =====================================================================
TOC03 = """  <a href="#s1">1 · CSS 是什么</a>
  <a href="#s2">2 · 三种写 CSS 的位置</a>
  <a href="#s3">3 · 语法：选择器 + 声明块</a>
  <a href="#s4">4 · 常用选择器</a>
  <a href="#s5">5 · 字体相关</a>
  <a href="#s6">6 · 背景与文字颜色</a>
  <a href="#s7">7 · 文字装饰：text-decoration / text-shadow</a>
  <a href="#s8">8 · 鼠标光标：cursor</a>
  <a href="#s9">9 · 优先级与继承</a>
  <a href="#s10">10 · 一页速查</a>"""

BODY03 = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p>HTML 决定「<b>有什么</b>」，CSS 决定「<b>长什么样</b>」。</p>
  <p>这一篇讲 CSS 的<b>语法</b>和一批<b>最常用的属性</b>：
  字体、颜色、文字装饰、阴影、光标。
  学完你就能把 FE-01/02 写的裸页面变得像样。</p>
</div>

<h2 id="s1"><span class="n">1</span>CSS 是什么</h2>

<p><b>CSS = Cascading Style Sheets（层叠样式表）</b>。</p>

<table>
<thead><tr><th style="width:24%">词</th><th>含义</th></tr></thead>
<tbody>
<tr><td><b>Style</b></td><td>样式 —— 它只管外观，不管内容</td></tr>
<tr><td><b>Sheet</b></td><td>一张表 —— 一堆样式规则写在一起</td></tr>
<tr><td><b>Cascading</b></td><td><b>层叠</b> —— 多条规则可以同时作用于一个元素，
  按优先级决定谁赢（第 9 节讲）</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">核心思路：选中 + 描述</div>
  <p>CSS 的每一条规则都在回答两个问题：</p>
  <ol>
    <li><b>选中谁？</b>（选择器）</li>
    <li><b>把它怎么样？</b>（属性: 值）</li>
  </ol>
  <p>就这么简单。<b>难的不是语法，是「怎么组合出想要的效果」。</b></p>
</div>

<h2 id="s2"><span class="n">2</span>三种写 CSS 的位置</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">① 行内样式：直接写在标签上</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;p</span> <span class="hl-f">style</span>=<span class="hl-s">"color: red; font-size: 20px;"</span><span class="hl-p">&gt;</span>红字<span class="hl-p">&lt;/p&gt;</span></pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">② 内部样式表：写在 head 里的 style 标签</span><span class="cp">复制</span></div><pre><span class="hl-p">&lt;head&gt;</span>
  <span class="hl-p">&lt;style&gt;</span>
    p { color: red; }
  <span class="hl-p">&lt;/style&gt;</span>
<span class="hl-p">&lt;/head&gt;</span></pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">③ 外部样式表：单独一个 .css 文件（推荐）</span><span class="cp">复制</span></div><pre><span class="hl-c">&lt;!-- HTML 里只写一行链接 --&gt;</span>
<span class="hl-p">&lt;link</span> <span class="hl-f">rel</span>=<span class="hl-s">"stylesheet"</span> <span class="hl-f">href</span>=<span class="hl-s">"assets/style.css"</span><span class="hl-p">&gt;</span>

<span class="hl-c">/* style.css 里写规则 */</span>
p { color: red; }</pre></div>

<table>
<thead><tr><th style="width:20%"></th><th style="width:26%">优点</th><th>缺点</th></tr></thead>
<tbody>
<tr><td><b>行内</b></td><td>立刻生效，好调试</td>
    <td><b>优先级最高、难覆盖</b>；改一处要翻 HTML；
      不能复用</td></tr>
<tr><td><b>内部</b></td><td>一个文件搞定，适合单页小 demo</td>
    <td>多个页面要各写一遍</td></tr>
<tr><td><b>外部</b></td><td><span class="tag g">推荐</span>
      <b>多个页面共用一份</b>，浏览器还会缓存</td>
    <td>多一个文件要管</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">本系列文档用的是哪一种</div>
  <p>一开始是<b>内部样式表</b>（写在 <code>&lt;head&gt;</code> 里），
  后来改成了<b>外部样式表</b> ——
  每篇一个 <code>assets/fe-0N.css</code>。</p>
  <p>原因很实际：15 篇文档原本各自内嵌一份几乎相同的 CSS，
  总共 28 万字符；抽出来之后只剩 8 万。<b>这就是外部样式表的价值。</b></p>
</div>

<h2 id="s3"><span class="n">3</span>语法：选择器 + 声明块</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">一条规则的解剖</span><span class="cp">复制</span></div><pre><span class="hl-f">.card</span> <span class="arw">{</span>
    <span class="hl-k">color</span>: <span class="hl-n">red</span>;
    <span class="hl-k">font-size</span>: <span class="hl-n">16px</span>;
<span class="arw">}</span>
<span class="arw">└─┬─┘ │  └──┬──┘ └─┬┘ │</span>
<span class="arw">  │   │     │      │  └─ 分号结尾（最后一条可省，但建议都写）</span>
<span class="arw">  │   │     │      └─ 值</span>
<span class="arw">  │   │     └─ 冒号</span>
<span class="arw">  │   └─ 属性名</span>
<span class="arw">  └─ 选择器：选中谁</span></pre></div>

<div class="card warn">
  <div class="card-t">三个最容易写错的地方</div>
  <ol>
    <li><b>用冒号不是等号</b>：<code>color: red</code>，
      不是 <code>color = red</code></li>
    <li><b>用花括号不是圆括号</b>：<code>{ }</code></li>
    <li><b>每条声明末尾要有分号</b>（漏了会让下一条也失效）</li>
  </ol>
  <p><b>好消息</b>：CSS 出错不报错，只是那条不生效 ——
  靠 F12 的 Styles 面板能看到哪条被划掉了。</p>
</div>

<h4>注释</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">CSS 只有一种注释</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 这是 CSS 注释，可以跨行 */</span>
<span class="hl-k">color</span>: red;  <span class="hl-c">/* 也可以写在行尾 */</span>

<span class="hl-c">/* 注意：CSS 里不能用 // ，那是 JS 和 C 的 */</span></pre></div>

<h2 id="s4"><span class="n">4</span>常用选择器</h2>

<table>
<thead><tr><th style="width:24%">写法</th><th style="width:26%">选中什么</th><th>例子</th></tr></thead>
<tbody>
<tr><td class="c">p</td><td>所有 <code>&lt;p&gt;</code> 标签</td>
    <td class="c">p { }</td></tr>
<tr><td class="c">.card</td><td><b>class 含 card 的所有元素</b></td>
    <td class="c">.card { }&nbsp;&nbsp;← 最常用</td></tr>
<tr><td class="c">#header</td><td>id 是 header 的那<b>一个</b></td>
    <td class="c">#header { }</td></tr>
<tr><td class="c">*</td><td>所有元素</td><td class="c">* { }</td></tr>
<tr><td class="c">div p</td><td>div <b>里面</b>的所有 p（后代）</td>
    <td class="c">.card p { }</td></tr>
<tr><td class="c">div &gt; p</td><td>div 的<b>直接子元素</b>里的 p</td>
    <td class="c">.card &gt; p { }</td></tr>
<tr><td class="c">.a, .b</td><td>a <b>或</b> b（并列）</td>
    <td class="c">h1, h2 { }</td></tr>
<tr><td class="c">a:hover</td><td>鼠标<b>悬停</b>时的 a</td>
    <td class="c">.btn:hover { }&nbsp;&nbsp;← FE-06</td></tr>
<tr><td class="c">input[type="text"]</td><td>带该属性的元素</td>
    <td class="c">input[type="radio"] { }</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">实际写 CSS，九成时间用 <code>.class</code></div>
  <p>用标签名选（<code>p</code>）会影响<b>所有</b>段落，
  用 id 选（<code>#x</code>）只能选一个、还难复用。</p>
  <p><b>所以：给元素加个 class，然后用 class 选。</b>
  这也是为什么 HTML 里到处都是 <code>class="..."</code>。</p>
</div>

<h2 id="s5"><span class="n">5</span>字体相关</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">字体五件套</span><span class="cp">复制</span></div><pre>body {
    <span class="hl-k">font-family</span>: <span class="hl-s">"Microsoft YaHei"</span>, <span class="hl-s">"PingFang SC"</span>, sans-serif;
    <span class="hl-k">font-size</span>: <span class="hl-n">16px</span>;
    <span class="hl-k">font-weight</span>: <span class="hl-n">400</span>;
    <span class="hl-k">font-style</span>: normal;
    <span class="hl-k">line-height</span>: <span class="hl-n">1.8</span>;
    <span class="hl-k">letter-spacing</span>: <span class="hl-n">0.02em</span>;
}</pre></div>

<table>
<thead><tr><th style="width:22%">属性</th><th style="width:28%">作用</th><th>常用值</th></tr></thead>
<tbody>
<tr><td class="c">font-family</td><td>用哪个字体</td>
    <td>一串候选，逗号隔开（见下）</td></tr>
<tr><td class="c">font-size</td><td>字号</td>
    <td class="c">16px　1.2rem　120%</td></tr>
<tr><td class="c">font-weight</td><td>粗细</td>
    <td class="c">400 正常　700 粗　100~900</td></tr>
<tr><td class="c">font-style</td><td>斜体</td>
    <td class="c">normal　italic</td></tr>
<tr><td class="c">line-height</td><td><b>行高</b></td>
    <td class="c">1.8（<b>无单位 = 倍数</b>，推荐）</td></tr>
<tr><td class="c">letter-spacing</td><td>字间距</td>
    <td class="c">0.02em　1px</td></tr>
</tbody>
</table>

<h4>font-family 为什么要写一串</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">字体回退链</span><span class="cp">复制</span></div><pre><span class="hl-k">font-family</span>: <span class="hl-s">"Consolas"</span>, <span class="hl-s">"Cascadia Mono"</span>, <span class="hl-s">"Courier New"</span>, monospace;

<span class="hl-c">/* 浏览器的查找顺序：
     有 Consolas → 用它
     没有       → 试 Cascadia Mono
     还没有     → 试 Courier New
     全都没有   → 用系统默认的等宽字体（monospace） */</span></pre></div>

<div class="card tip">
  <div class="card-t">两条实用规则</div>
  <ul>
    <li><b>字体名有空格要用引号</b>：<code>"Microsoft YaHei"</code></li>
    <li><b>最后一定写一个通用族</b>：
      <code>sans-serif</code>（无衬线）/ <code>serif</code>（衬线）/
      <code>monospace</code>（等宽）—— 保证一定有字体可用</li>
  </ul>
  <p>本系列文档的代码用 <b>Consolas</b>，正文用
  <b>Microsoft YaHei</b> —— 都是这么写的。</p>
</div>

<h4>字号单位：px / em / rem</h4>
<table>
<thead><tr><th style="width:18%">单位</th><th style="width:30%">相对谁</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">px</td><td>绝对</td><td>最好理解，直接用</td></tr>
<tr><td class="c">em</td><td><b>父元素</b>的字号</td>
    <td>会层层累积，容易失控</td></tr>
<tr><td class="c">rem</td><td><b>根元素</b>（html）的字号</td>
    <td><span class="tag g">推荐</span> 改一处全站缩放</td></tr>
<tr><td class="c">%</td><td>父元素的字号</td><td>同 em</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t"><code>line-height</code> 为什么不写单位</div>
  <p><code>line-height: 1.8</code> 表示「<b>行高 = 当前字号的 1.8 倍</b>」。</p>
  <p>如果写成 <code>28.8px</code>，那么字号一变，行高就不匹配了。
  写成倍数，<b>字号怎么变行高都跟着变</b>。</p>
  <p>正文行高 <b>1.6~1.8</b> 读起来最舒服；标题可以小一点（1.3 左右）。</p>
</div>

<h2 id="s6"><span class="n">6</span>背景与文字颜色</h2>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">颜色与背景</span><span class="cp">复制</span></div><pre>.box {
    <span class="hl-k">color</span>: <span class="hl-n">#1a1f28</span>;                    <span class="hl-c">/* 文字色 */</span>
    <span class="hl-k">background-color</span>: <span class="hl-n">#f7f9fc</span>;       <span class="hl-c">/* 背景色 */</span>

    <span class="hl-c">/* 渐变背景 */</span>
    <span class="hl-k">background</span>: <span class="hl-f">linear-gradient</span>(<span class="hl-n">135deg</span>, <span class="hl-n">#fffdf5</span>, <span class="hl-n">#fdf3dc</span>);

    <span class="hl-c">/* 半透明背景 */</span>
    <span class="hl-k">background-color</span>: <span class="hl-f">rgba</span>(<span class="hl-n">31</span>, <span class="hl-n">111</span>, <span class="hl-n">235</span>, <span class="hl-n">0.08</span>);
}</pre></div>

<table>
<thead><tr><th style="width:26%">属性</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">color</td><td><b>文字颜色</b>（注意不是 <code>font-color</code>，
  就叫 <code>color</code>）</td></tr>
<tr><td class="c">background-color</td><td>背景色</td></tr>
<tr><td class="c">background</td><td>背景简写，可以写渐变、图片</td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">新手最常写错的属性名</div>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">font-color: red;        ❌ 没有这个属性
text-color: red;        ❌ 没有这个属性
color: red;             ✅ 文字颜色就是 color
<span class="hl-c">                       （是从「墨水的颜色」这个角度命名的）</span></pre>
</div>

<h2 id="s7"><span class="n">7</span>文字装饰：text-decoration / text-shadow</h2>

<h4>text-decoration：下划线、删除线</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">五种值</span><span class="cp">复制</span></div><pre>.a { <span class="hl-k">text-decoration</span>: underline; }       <span class="hl-c">/* 下划线 */</span>
.b { <span class="hl-k">text-decoration</span>: line-through; }    <span class="hl-c">/* 删除线 */</span>
.c { <span class="hl-k">text-decoration</span>: overline; }        <span class="hl-c">/* 上划线 */</span>
.d { <span class="hl-k">text-decoration</span>: none; }            <span class="hl-c">/* 去掉装饰 ← 最常用 */</span>
.e { <span class="hl-k">text-decoration</span>: underline dotted <span class="hl-n">#c0392b</span>; }  <span class="hl-c">/* 虚线下划线+颜色 */</span></pre></div>

<div class="card key">
  <div class="card-t">最常用的其实是 <code>none</code></div>
  <p>链接 <code>&lt;a&gt;</code> <b>默认带下划线</b>。做导航菜单时第一件事就是去掉它：</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">导航菜单的标准起手式</span><span class="cp">复制</span></div><pre>a {
    <span class="hl-k">text-decoration</span>: none;      <span class="hl-c">/* 去掉下划线 */</span>
    <span class="hl-k">color</span>: <span class="hl-n">#4b5563</span>;            <span class="hl-c">/* 别用默认的蓝 */</span>
}
a:hover { <span class="hl-k">color</span>: <span class="hl-n">#1f6feb</span>; }      <span class="hl-c">/* 悬停才变色 */</span></pre></div>
</div>

<h4>text-shadow：文字阴影</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">四段式语法</span><span class="cp">复制</span></div><pre><span class="hl-k">text-shadow</span>: <span class="hl-n">2px</span> <span class="hl-n">2px</span> <span class="hl-n">4px</span> <span class="hl-f">rgba</span>(<span class="hl-n">0</span>,<span class="hl-n">0</span>,<span class="hl-n">0</span>,<span class="hl-n">0.4</span>);
<span class="arw">             └┬┘ └┬┘ └┬┘ └──────┬──────┘</span>
<span class="arw">              │   │   │         └─ 颜色（含透明度）</span>
<span class="arw">              │   │   └─ 模糊半径，越大越糊</span>
<span class="arw">              │   └─ 垂直偏移（正数往下）</span>
<span class="arw">              └─ 水平偏移（正数往右）</span></pre></div>

<table>
<thead><tr><th style="width:38%">写法</th><th>效果</th></tr></thead>
<tbody>
<tr><td class="c">0 1px 2px rgba(0,0,0,.3)</td>
    <td><b>轻微浮起</b> —— 最实用，几乎是默认选择</td></tr>
<tr><td class="c">0 0 8px #1f6feb</td>
    <td><b>发光</b>（偏移 0，只有模糊）</td></tr>
<tr><td class="c">-1px -1px 0 #fff</td>
    <td><b>描边</b>（偏移且不模糊），常叠四份做外框</td></tr>
<tr><td class="c">2px 2px 0 #000</td>
    <td>硬阴影（复古、像素风）</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">文字阴影的三个实用场景</div>
  <ol>
    <li><b>图片上的文字</b>：加深色阴影，保证在任何背景上都读得清</li>
    <li><b>浅色文字在深底上</b>：加一点阴影增加「厚度」</li>
    <li><b>强调某个标题</b>：轻描一笔就够，<b>重了很土</b></li>
  </ol>
</div>

<h2 id="s8"><span class="n">8</span>鼠标光标：cursor</h2>

<p>鼠标移到元素上时显示什么形状，由 <code>cursor</code> 决定。
<b>它是最便宜的「可用性提升」</b> —— 一改就能让用户知道「这里能点」。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">常用值</span><span class="cp">复制</span></div><pre>.btn   { <span class="hl-k">cursor</span>: pointer; }      <span class="hl-c">/* 手形 ← 表示「可点击」，最常用 */</span>
.text  { <span class="hl-k">cursor</span>: text; }         <span class="hl-c">/* 文本竖线 I */</span>
.move  { <span class="hl-k">cursor</span>: move; }         <span class="hl-c">/* 十字箭头，表示可拖动 */</span>
.wait  { <span class="hl-k">cursor</span>: wait; }         <span class="hl-c">/* 转圈/沙漏，表示忙 */</span>
.help  { <span class="hl-k">cursor</span>: help; }         <span class="hl-c">/* 带问号 */</span>
.ban   { <span class="hl-k">cursor</span>: not-allowed; }  <span class="hl-c">/* 禁止符号，表示不可用 */</span>
.grab  { <span class="hl-k">cursor</span>: grab; }         <span class="hl-c">/* 张开的手，可抓取 */</span>
.none  { <span class="hl-k">cursor</span>: none; }         <span class="hl-c">/* 完全隐藏光标 */</span>
.auto  { <span class="hl-k">cursor</span>: default; }      <span class="hl-c">/* 默认箭头 */</span></pre></div>

<div class="card key">
  <div class="card-t"><code>pointer</code> 这个名字的坑</div>
  <p>它<b>不是</b>「指针箭头」的意思 ——
  它指的是「<b>手形</b>」（像指着东西的手指）。</p>
  <p>想要普通箭头是 <code>default</code>。
  <b>很多人第一次都写反了。</b></p>
</div>

<div class="card warn">
  <div class="card-t">别忘了加 <code>cursor: pointer</code></div>
  <p>浏览器<b>只给 <code>&lt;a&gt;</code> 和 <code>&lt;button&gt;</code>
  自动加手形</b>。用 <code>&lt;div&gt;</code> 或 <code>&lt;span&gt;</code>
  做出来的「假按钮」，鼠标移上去还是箭头 ——
  用户根本不知道那能点。</p>
  <div class="code-wrap" style="margin-top:10px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">检查清单</span><span class="cp">复制</span></div><pre><span class="hl-c">/* 做成可点击的样子，就要配套这四件事 */</span>
.my-btn {
    <span class="hl-k">cursor</span>: pointer;              <span class="hl-c">/* ① 手形 */</span>
    <span class="hl-k">background</span>: <span class="hl-n">#1f6feb</span>;          <span class="hl-c">/* ② 看起来是个按钮 */</span>
    <span class="hl-k">border-radius</span>: <span class="hl-n">8px</span>;           <span class="hl-c">/* ③ 圆角 */</span>
    <span class="hl-k">transition</span>: background <span class="hl-n">0.15s</span>;  <span class="hl-c">/* ④ 悬停有反馈（FE-06） */</span>
}
.my-btn:hover { <span class="hl-k">background</span>: <span class="hl-n">#1558b8</span>; }</pre></div>
</div>

<h2 id="s9"><span class="n">9</span>优先级与继承</h2>

<h4>多条规则冲突时谁赢</h4>
<table>
<thead><tr><th style="width:34%">来源</th><th style="width:16%">权重</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">行内 style="..."</td><td>最高</td>
    <td>直接写在标签上，几乎总能赢</td></tr>
<tr><td class="c">#id</td><td>高</td><td>100</td></tr>
<tr><td class="c">.class / :hover / [attr]</td><td>中</td><td>10</td></tr>
<tr><td class="c">标签名 p / div</td><td>低</td><td>1</td></tr>
<tr><td class="c">*</td><td>最低</td><td>0</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">三句话记住</div>
  <ol>
    <li><b>越具体越赢</b>：<code>#id</code> &gt; <code>.class</code> &gt; <code>标签</code></li>
    <li><b>同样具体时，后写的赢</b></li>
    <li><b>行内样式基本无敌</b> —— 所以尽量别用</li>
  </ol>
  <p><b>实用建议</b>：不要为了「赢」而堆选择器
  （<code>#a .b div p</code> 这种）——
  那是维护的噩梦。<b>把 class 用对，就不需要斗优先级。</b></p>
</div>

<h4>继承：有些属性会「传下去」</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">继承的效果</span><span class="cp">复制</span></div><pre>body {
    <span class="hl-k">font-family</span>: <span class="hl-s">"Microsoft YaHei"</span>, sans-serif;
    <span class="hl-k">color</span>: <span class="hl-n">#1a1f28</span>;
}

<span class="hl-c">/* body 里所有元素都会自动用这个字体和颜色 ——
   不需要给每个 p、每个 div 各写一遍 */</span></pre></div>

<table>
<thead><tr><th style="width:44%">会继承的（文字相关）</th><th>不会继承的（盒子相关）</th></tr></thead>
<tbody>
<tr><td class="c">font-*　color　line-height</td>
    <td class="c">background　border　padding　margin　width</td></tr>
<tr><td class="c">text-align　letter-spacing</td>
    <td class="c">display　position　box-shadow</td></tr>
</tbody>
</table>

<p><b>规律</b>：<b>「文字长什么样」会继承，「盒子怎么摆」不会。</b>
这也符合直觉 —— 字体自然是全篇统一，但每个盒子各管各的边距。</p>

<h2 id="s10"><span class="n">10</span>一页速查</h2>

<table>
<thead><tr><th style="width:36%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>外部样式表</td><td class="c">&lt;link rel="stylesheet" href="x.css"&gt;</td></tr>
<tr><td>选中 class</td><td class="c">.card { }</td></tr>
<tr><td>选中 id</td><td class="c">#head { }</td></tr>
<tr><td>选中后代</td><td class="c">.card p { }</td></tr>
<tr><td>同时选多个</td><td class="c">h1, h2 { }</td></tr>
<tr><td>悬停状态</td><td class="c">.btn:hover { }</td></tr>
<tr><td>注释</td><td class="c">/* 注释 */</td></tr>
<tr><td>字体</td><td class="c">font-family: "Consolas", monospace;</td></tr>
<tr><td>字号</td><td class="c">font-size: 16px;</td></tr>
<tr><td>粗细</td><td class="c">font-weight: 700;</td></tr>
<tr><td>行高（倍数）</td><td class="c">line-height: 1.8;</td></tr>
<tr><td>字间距</td><td class="c">letter-spacing: 0.02em;</td></tr>
<tr><td>文字色</td><td class="c">color: #1a1f28;</td></tr>
<tr><td>背景色</td><td class="c">background-color: #f7f9fc;</td></tr>
<tr><td>渐变背景</td><td class="c">background: linear-gradient(135deg, #fff, #eee);</td></tr>
<tr><td>去链接下划线</td><td class="c">text-decoration: none;</td></tr>
<tr><td>删除线</td><td class="c">text-decoration: line-through;</td></tr>
<tr><td>文字阴影</td><td class="c">text-shadow: 0 1px 2px rgba(0,0,0,.3);</td></tr>
<tr><td>手形光标</td><td class="c">cursor: pointer;</td></tr>
<tr><td>禁止光标</td><td class="c">cursor: not-allowed;</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的五句话</div>
  <ol>
    <li><b>CSS = 选中谁 + 把它怎么样</b>：
      <code>选择器 { 属性: 值; }</code>，冒号不是等号，末尾要分号。</li>
    <li><b>九成时间用 <code>.class</code> 选</b>；
      行内样式优先级最高但最难维护，别用。</li>
    <li><b><code>font-family</code> 写一串候选</b>，最后兜一个
      <code>sans-serif</code> / <code>monospace</code>；
      <b><code>line-height</code> 不写单位</b>（写倍数）。</li>
    <li><b>文字色是 <code>color</code></b>（不是 <code>font-color</code>）；
      <code>cursor: pointer</code> 是<b>手形</b>，不是箭头。</li>
    <li><b>文字属性会继承、盒子属性不会</b>；
      同样具体时<b>后写的赢</b>。</li>
  </ol>
</div>"""

if __name__ == "__main__":
    print(build("r04.html", "FE-03-F01", "十六进制颜色模型、HSV 与 Alpha",
                BODY3F1, TOC3F1))
    print(build("fe-03.html", "FE-03", "CSS 入门", BODY03, TOC03))
