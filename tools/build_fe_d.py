# -*- coding: utf-8 -*-
"""FE-06（鼠标悬停与 transition）"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build

TOC06 = """  <a href="#s1">1 · 伪类：状态选择器</a>
  <a href="#s2">2 · hover 能改什么</a>
  <a href="#s3">3 · transition 语法</a>
  <a href="#s4">4 · 该给谁加 transition</a>
  <a href="#s5">5 · 常用动效配方</a>
  <a href="#s6">6 · 缓动与性能</a>
  <a href="#s7">7 · 一页速查</a>"""

BODY06 = r"""<div class="card note">
  <div class="card-t">这一篇讲什么</div>
  <p>前五篇讲的是「静态」的页面。<b>这一篇让它动起来</b> ——
  鼠标移上去有反馈，点了有回应。</p>
  <p>好消息：<b>不需要 JavaScript。</b>
  CSS 靠 <code>:hover</code> 和 <code>transition</code> 两样东西，
  就能做出大部分日常动效。</p>
</div>

<h2 id="s1"><span class="n">1</span>伪类：状态选择器</h2>

<p>FE-03 讲的选择器都是「选中某个元素」。
<b>伪类</b>更进一步：选中「<b>处在某种状态</b>的元素」。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">写法：冒号 + 状态名</span><span class="cp">复制</span></div><pre>.btn<span class="hl-f">:hover</span>  { }    <span class="hl-c">/* 鼠标悬停在上面时 */</span>
.btn<span class="hl-f">:active</span> { }    <span class="hl-c">/* 正在被按下时 */</span>
.btn<span class="hl-f">:focus</span>  { }    <span class="hl-c">/* 获得焦点时（Tab 键 / 点进去） */</span></pre></div>

<table>
<thead><tr><th style="width:22%">伪类</th><th>什么时候生效</th><th style="width:30%">典型用途</th></tr></thead>
<tbody>
<tr><td class="c">:hover</td><td><b>鼠标移上去</b></td>
    <td>按钮变色、卡片抬起、链接变色</td></tr>
<tr><td class="c">:active</td><td><b>鼠标正按着</b></td>
    <td>按钮「按下去」的瞬间</td></tr>
<tr><td class="c">:focus</td><td>获得键盘/输入焦点</td>
    <td>输入框高亮、无障碍必备</td></tr>
<tr><td class="c">:focus-visible</td><td>只有键盘操作才触发</td>
    <td>不想让鼠标点击也出现焦点框</td></tr>
<tr><td class="c">:first-child</td><td>是父元素的第一个孩子</td>
    <td>列表首项特殊处理</td></tr>
<tr><td class="c">:last-child</td><td>最后一个孩子</td>
    <td>去掉最后一项的分隔线</td></tr>
<tr><td class="c">:nth-child(2n)</td><td>第偶数个</td>
    <td>表格斑马纹</td></tr>
<tr><td class="c">:not(.x)</td><td><b>不是</b> .x 的</td>
    <td>排除某一个</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">写顺序有讲究</div>
  <p>这四个按 <b>LVHA</b> 顺序写（Link → Visited → Hover → Active），
  否则后面的会被前面的盖住：</p>
  <pre style="background:#0b1220;border:1px solid #33486b;border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:12.5px;color:#f8fbff;overflow:auto">a:link    { }   /* L */
a:visited { }   /* V */
a:hover   { }   /* H */
a:active  { }   /* A */</pre>
  <p style="margin-top:10px">记忆法：<b>「LoVe HAte」（爱恨）</b>。
  只写 <code>:hover</code> 和 <code>:active</code> 时，
  <b><code>:active</code> 放后面</b>就行。</p>
</div>

<h2 id="s2"><span class="n">2</span>hover 能改什么</h2>

<p><b>几乎任何属性都能改。</b>常用的是这几类：</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">四类常用反馈</span><span class="cp">复制</span></div><pre>.card {
    <span class="hl-k">background</span>: <span class="hl-n">#fff</span>;
    <span class="hl-k">border-color</span>: <span class="hl-n">#ccd5e3</span>;
    <span class="hl-k">box-shadow</span>: <span class="hl-n">0</span> <span class="hl-n">1px</span> <span class="hl-n">3px</span> <span class="hl-f">rgba</span>(<span class="hl-n">0</span>,<span class="hl-n">0</span>,<span class="hl-n">0</span>,<span class="hl-n">.10</span>);
    <span class="hl-k">transform</span>: <span class="hl-f">translateY</span>(<span class="hl-n">0</span>);
}

.card:hover {
    <span class="hl-k">background</span>: <span class="hl-n">#f7f9fc</span>;                            <span class="hl-c">/* ① 换背景 */</span>
    <span class="hl-k">border-color</span>: <span class="hl-n">#1f6feb</span>;                         <span class="hl-c">/* ② 换边框色 */</span>
    <span class="hl-k">box-shadow</span>: <span class="hl-n">0</span> <span class="hl-n">8px</span> <span class="hl-n">24px</span> <span class="hl-f">rgba</span>(<span class="hl-n">0</span>,<span class="hl-n">0</span>,<span class="hl-n">0</span>,<span class="hl-n">.13</span>);  <span class="hl-c">/* ③ 阴影变大 = 抬起 */</span>
    <span class="hl-k">transform</span>: <span class="hl-f">translateY</span>(<span class="hl-n">-2px</span>);                   <span class="hl-c">/* ④ 真的往上移 2px */</span>
}</pre></div>

<table>
<thead><tr><th style="width:22%">改什么</th><th>感觉</th><th style="width:26%">适合</th></tr></thead>
<tbody>
<tr><td class="c">background</td><td>变色</td><td>按钮、菜单项</td></tr>
<tr><td class="c">color</td><td>文字变色</td><td>链接</td></tr>
<tr><td class="c">border-color</td><td>边框亮起</td><td>卡片</td></tr>
<tr><td class="c">box-shadow</td><td><b>浮起来</b></td><td>卡片、按钮</td></tr>
<tr><td class="c">transform: translateY(-2px)</td><td><b>真的上移</b></td><td>卡片（配阴影最自然）</td></tr>
<tr><td class="c">transform: scale(1.05)</td><td>放大一点</td><td>图片、头像</td></tr>
<tr><td class="c">opacity</td><td>变亮/变淡</td><td>图标</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">「抬起」为什么要阴影 + 上移一起做</div>
  <p>只改阴影：元素没动，像「下面是脏了」。</p>
  <p>只上移：没有阴影，像「飘」。</p>
  <p><b>两个一起</b>：影子变大 + 东西升高 = 真的<b>离桌面更远</b>了。
  这是物理直觉，看着最自然。</p>
  <p>本文档导航页的卡片就是这么做的：
  <code>translateY(-2px)</code> + <code>0 8px 24px</code>。</p>
</div>

<h2 id="s3"><span class="n">3</span>transition 语法</h2>

<p>只写 <code>:hover</code> 的话，变化是<b>瞬间</b>发生的 ——
看起来很生硬。<code>transition</code> 让它<b>平滑过渡</b>。</p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">四段式语法</span><span class="cp">复制</span></div><pre><span class="hl-k">transition</span>: background <span class="hl-n">0.18s</span> ease;
<span class="arw">             └────┬───┘ └─┬─┘ └─┬┘</span>
<span class="arw">                  │       │     └─ 缓动函数（速度曲线）</span>
<span class="arw">                  │       └─ 时长（0.18s = 180 毫秒）</span>
<span class="arw">                  └─ 要过渡哪个属性</span></pre></div>

<table>
<thead><tr><th style="width:22%">部分</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="c">属性名</td>
    <td>要平滑变化的属性，如 <code>background</code>、<code>transform</code>、
      <code>box-shadow</code>；<code>all</code> 表示全部</td></tr>
<tr><td class="c">时长</td>
    <td><b>必须带单位</b>：<code>0.2s</code> 或 <code>200ms</code>。
      写 <code>200</code> 无效</td></tr>
<tr><td class="c">缓动</td>
    <td><code>ease</code>（默认）/ <code>linear</code> /
      <code>ease-out</code> / <code>cubic-bezier(...)</code></td></tr>
<tr><td class="c">延迟</td>
    <td>可选，第四个值，如 <code>0.05s</code></td></tr>
</tbody>
</table>

<h4>时长怎么选</h4>
<table>
<thead><tr><th style="width:24%">时长</th><th>感觉</th><th style="width:26%">适合</th></tr></thead>
<tbody>
<tr><td class="c">0.1s</td><td>几乎瞬间，很「跟手」</td><td>按钮按下</td></tr>
<tr><td class="c">0.15 ~ 0.2s</td><td><b>最舒服的区间</b></td>
    <td><span class="tag g">日常首选</span> 颜色、阴影</td></tr>
<tr><td class="c">0.3s</td><td>明显能感觉到「动」</td><td>位移、缩放、抽屉</td></tr>
<tr><td class="c">&gt; 0.5s</td><td><b>显得迟钝</b></td><td>除非刻意要慢</td></tr>
</tbody>
</table>

<div class="card warn">
  <div class="card-t">时长超过 0.3s 就会「黏」</div>
  <p>用户移上移下很快，如果过渡要半秒，鼠标早走了动画还在跑 ——
  感觉界面<b>反应迟钝</b>。</p>
  <p><b>经验值</b>：颜色类 <code>0.15s</code>，
  位移类 <code>0.2~0.3s</code>。<b>不要超过 0.4s。</b></p>
</div>

<h2 id="s4"><span class="n">4</span>该给谁加 transition</h2>

<p>这是最容易搞错的一点。<b>看下面的对比：</b></p>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">❌ 加在 hover 里</span><span class="cp">复制</span></div><pre>.btn { background: <span class="hl-n">#1f6feb</span>; }

.btn:hover {
    <span class="hl-k">background</span>: <span class="hl-n">#1558b8</span>;
    <span class="hl-k">transition</span>: background <span class="hl-n">0.2s</span>;    <span class="hl-c">/* ❌ 放错地方了 */</span>
}</pre></div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">✅ 加在基础规则里</span><span class="cp">复制</span></div><pre>.btn {
    <span class="hl-k">background</span>: <span class="hl-n">#1f6feb</span>;
    <span class="hl-k">transition</span>: background <span class="hl-n">0.2s</span>;    <span class="hl-c">/* ✅ 这里 */</span>
}

.btn:hover { <span class="hl-k">background</span>: <span class="hl-n">#1558b8</span>; }</pre></div>

<div class="card key">
  <div class="card-t">为什么</div>
  <p><code>transition</code> 的定义是「<b>当我的属性发生变化时，平滑地变</b>」。</p>
  <p>写在 <code>:hover</code> 里，意味着<b>只有「进入 hover」这个动作</b>
  才有过渡定义；<b>鼠标移开</b>时那条规则不再匹配，
  过渡定义也就没了 —— <b>移出时是瞬间跳回去的</b>。</p>
  <p>写在基础规则里，<b>进和出都平滑</b>。这才对。</p>
</div>

<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">多个属性一起过渡</span><span class="cp">复制</span></div><pre>.card {
    <span class="hl-c">/* 逗号分隔，各写各的时长 */</span>
    <span class="hl-k">transition</span>: box-shadow <span class="hl-n">0.18s</span>,
                transform  <span class="hl-n">0.18s</span>,
                border-color <span class="hl-n">0.18s</span>;
}

<span class="hl-c">/* 或者简写：所有属性都用同一套参数 */</span>
.card { <span class="hl-k">transition</span>: all <span class="hl-n">0.2s</span> ease; }</pre></div>

<div class="card warn">
  <div class="card-t"><code>all</code> 方便，但有两个代价</div>
  <ol>
    <li><b>性能</b>：浏览器要监听所有属性，可能触发多余的重排</li>
    <li><b>意外</b>：你不想过渡的属性（比如布局变化）也会被动画化，
      看起来很怪</li>
  </ol>
  <p><b>建议</b>：小 demo 用 <code>all</code> 没问题；
  正式项目<b>明确列出要过渡的属性</b>。</p>
</div>

<h2 id="s5"><span class="n">5</span>常用动效配方</h2>

<p>直接抄这几个，覆盖日常九成需求。</p>

<h4>① 按钮：变色</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">最简单也最常用</span><span class="cp">复制</span></div><pre>.btn {
    <span class="hl-k">background</span>: <span class="hl-n">#1f6feb</span>;
    <span class="hl-k">color</span>: <span class="hl-n">#fff</span>;
    <span class="hl-k">padding</span>: <span class="hl-n">8px</span> <span class="hl-n">18px</span>;
    <span class="hl-k">border-radius</span>: <span class="hl-n">8px</span>;
    <span class="hl-k">cursor</span>: pointer;
    <span class="hl-k">transition</span>: background <span class="hl-n">0.15s</span>;
}
.btn:hover  { <span class="hl-k">background</span>: <span class="hl-n">#1558b8</span>; }
.btn:active { <span class="hl-k">transform</span>: <span class="hl-f">scale</span>(<span class="hl-n">0.97</span>); }   <span class="hl-c">/* 按下去缩一点 */</span></pre></div>

<h4>② 卡片：抬起</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">导航页用的就是这个</span><span class="cp">复制</span></div><pre>.card {
    <span class="hl-k">border</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#ccd5e3</span>;
    <span class="hl-k">border-radius</span>: <span class="hl-n">12px</span>;
    <span class="hl-k">box-shadow</span>: none;
    <span class="hl-k">transition</span>: box-shadow <span class="hl-n">0.16s</span>, transform <span class="hl-n">0.16s</span>, border-color <span class="hl-n">0.16s</span>;
}
.card:hover {
    <span class="hl-k">box-shadow</span>: <span class="hl-n">0</span> <span class="hl-n">8px</span> <span class="hl-n">24px</span> <span class="hl-f">rgba</span>(<span class="hl-n">30</span>,<span class="hl-n">45</span>,<span class="hl-n">70</span>,<span class="hl-n">.13</span>);
    <span class="hl-k">transform</span>: <span class="hl-f">translateY</span>(<span class="hl-n">-2px</span>);
    <span class="hl-k">border-color</span>: <span class="hl-n">#1f6feb</span>;
}</pre></div>

<h4>③ 链接：下划线滑入</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">用 border-bottom 做动画</span><span class="cp">复制</span></div><pre>.link {
    <span class="hl-k">text-decoration</span>: none;
    <span class="hl-k">border-bottom</span>: <span class="hl-n">1px</span> solid <span class="hl-n">transparent</span>;   <span class="hl-c">/* 先留一条透明的 */</span>
    <span class="hl-k">transition</span>: border-color <span class="hl-n">0.15s</span>, color <span class="hl-n">0.15s</span>;
}
.link:hover {
    <span class="hl-k">color</span>: <span class="hl-n">#1f6feb</span>;
    <span class="hl-k">border-bottom-color</span>: <span class="hl-n">#1f6feb</span>;            <span class="hl-c">/* 只改颜色 → 平滑出现 */</span>
}</pre></div>

<p><b>小技巧</b>：先留一条 <code>transparent</code> 的边框，
悬停时只改颜色 —— 这样<b>不会因为突然多出一条边框而抖动</b>。</p>

<h4>④ 输入框：聚焦光圈</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">用 box-shadow 做光圈</span><span class="cp">复制</span></div><pre>.input {
    <span class="hl-k">border</span>: <span class="hl-n">1px</span> solid <span class="hl-n">#ccd5e3</span>;
    <span class="hl-k">border-radius</span>: <span class="hl-n">8px</span>;
    <span class="hl-k">padding</span>: <span class="hl-n">8px</span> <span class="hl-n">12px</span>;
    <span class="hl-k">outline</span>: none;
    <span class="hl-k">transition</span>: border-color <span class="hl-n">0.15s</span>, box-shadow <span class="hl-n">0.15s</span>;
}
.input:focus {
    <span class="hl-k">border-color</span>: <span class="hl-n">#1f6feb</span>;
    <span class="hl-k">box-shadow</span>: <span class="hl-n">0</span> <span class="hl-n">0</span> <span class="hl-n">0</span> <span class="hl-n">3px</span> <span class="hl-f">rgba</span>(<span class="hl-n">31</span>,<span class="hl-n">111</span>,<span class="hl-n">235</span>,<span class="hl-n">0.25</span>);
}</pre></div>

<p><b>注意</b>：<code>box-shadow</code> 的前三个数是
<code>水平 垂直 模糊</code>，这里分别是
<code>0 0 0</code> —— <b>不偏移也不模糊</b>，
第四个参数 <code>3px</code> 是<b>扩散</b>，才形成光圈。</p>

<h4>⑤ 图片：放大</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">注意要给外层加 overflow: hidden</span><span class="cp">复制</span></div><pre>.thumb {
    <span class="hl-k">overflow</span>: hidden;          <span class="hl-c">/* ← 不然放大会溢出到外面 */</span>
    <span class="hl-k">border-radius</span>: <span class="hl-n">10px</span>;
}
.thumb img {
    <span class="hl-k">display</span>: block;
    <span class="hl-k">width</span>: <span class="hl-n">100%</span>;
    <span class="hl-k">transition</span>: transform <span class="hl-n">0.3s</span>;
}
.thumb:hover img { <span class="hl-k">transform</span>: <span class="hl-f">scale</span>(<span class="hl-n">1.06</span>); }</pre></div>

<h2 id="s6"><span class="n">6</span>缓动与性能</h2>

<h4>缓动函数（easing）</h4>
<p>它决定「速度怎么变」—— 匀速、先快后慢、还是先慢后快。</p>

<table>
<thead><tr><th style="width:24%">值</th><th>速度曲线</th><th style="width:26%">感觉</th></tr></thead>
<tbody>
<tr><td class="c">ease</td><td>慢 → 快 → 慢</td><td>默认，柔顺</td></tr>
<tr><td class="c">linear</td><td>全程匀速</td><td><b>机械、生硬</b>，少用</td></tr>
<tr><td class="c">ease-out</td><td>快 → 慢</td>
    <td><b>进场</b>最自然（推荐）</td></tr>
<tr><td class="c">ease-in</td><td>慢 → 快</td><td><b>离场</b>（元素消失时）</td></tr>
<tr><td class="c">ease-in-out</td><td>慢 → 快 → 慢，两端更缓</td>
    <td>来回移动</td></tr>
<tr><td class="c">cubic-bezier(.4,0,.2,1)</td><td>自定义</td>
    <td>想要特定的「手感」</td></tr>
</tbody>
</table>

<div class="card tip">
  <div class="card-t">一个简单好记的规则</div>
  <p><b>东西「出现」用 <code>ease-out</code>，
  「消失」用 <code>ease-in</code>。</b></p>
  <p>原因：出现时要<b>快速到位</b>再稳住；消失时要先蓄力再走。
  这符合真实物体的运动。</p>
</div>

<h4>性能：优先动这两个属性</h4>

<div class="card key">
  <div class="card-t">只动 <code>transform</code> 和 <code>opacity</code> 最流畅</div>
  <p>因为这两个属性<b>不引起重新布局</b>，浏览器可以用 GPU 直接合成，
  60fps 毫无压力。</p>
  <table style="margin:8px 0 0">
  <thead><tr><th style="width:34%">属性</th><th>代价</th></tr></thead>
  <tbody>
  <tr><td class="c">transform</td><td><span class="tag g">最便宜</span> 只重绘，走 GPU</td></tr>
  <tr><td class="c">opacity</td><td><span class="tag g">最便宜</span></td></tr>
  <tr><td class="c">background / color</td><td>便宜（只重绘）</td></tr>
  <tr><td class="c">box-shadow</td><td>中等，阴影要重算</td></tr>
  <tr><td class="c">width / height</td>
      <td><span class="tag r">贵</span> 会引起整个页面重新布局</td></tr>
  <tr><td class="c">top / left</td>
      <td><span class="tag r">贵</span> 用 <code>transform: translate</code> 代替</td></tr>
  </tbody></table>
  <p style="margin-top:10px"><b>实用结论</b>：要做位移动画，
  用 <code>transform: translateY(-2px)</code>，
  <b>不要</b>用 <code>top: -2px</code>。</p>
</div>

<h4>尊重用户的「减少动画」设置</h4>
<div class="code-wrap"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">无障碍考量</span><span class="cp">复制</span></div><pre><span class="hl-p">@media</span> (prefers-reduced-motion: reduce) {
    * {
        <span class="hl-k">transition</span>: none <span class="hl-ok">!important</span>;
        <span class="hl-k">animation</span>: none <span class="hl-ok">!important</span>;
    }
}</pre></div>

<p>有些人对动效敏感（会头晕、恶心），系统里可以开启「减少动态效果」。
加上这段之后，<b>他们的系统设置会被尊重</b>。</p>

<h2 id="s7"><span class="n">7</span>一页速查</h2>

<table>
<thead><tr><th style="width:38%">想做的事</th><th>写法</th></tr></thead>
<tbody>
<tr><td>悬停 / 按下 / 聚焦</td>
    <td class="c">:hover　:active　:focus　:focus-visible</td></tr>
<tr><td>表格斑马纹</td><td class="c">tr:nth-child(2n) { background: #f7f9fc; }</td></tr>
<tr><td>排除某个</td><td class="c">:not(.last)</td></tr>
<tr><td>只过渡一个属性</td><td class="c">transition: background 0.2s;</td></tr>
<tr><td>过渡多个</td>
    <td class="c">transition: color .15s, transform .2s;</td></tr>
<tr><td>全部过渡</td><td class="c">transition: all 0.2s ease;</td></tr>
<tr><td>指定缓动</td><td class="c">transition: transform .3s ease-out;</td></tr>
<tr><td>加延迟</td><td class="c">transition: opacity .3s ease .1s;</td></tr>
<tr><td><b>transition 写在哪</b></td>
    <td class="c"><b>基础规则里</b>，不是 :hover 里</td></tr>
<tr><td>按钮变色</td><td class="c">.btn:hover { background: #1558b8; }</td></tr>
<tr><td>按钮按下缩一点</td><td class="c">.btn:active { transform: scale(0.97); }</td></tr>
<tr><td>卡片抬起</td>
    <td class="c">:hover { box-shadow: 0 8px 24px rgba(0,0,0,.13); transform: translateY(-2px); }</td></tr>
<tr><td>聚焦光圈</td>
    <td class="c">:focus { box-shadow: 0 0 0 3px rgba(31,111,235,.25); }</td></tr>
<tr><td>图片放大（要裁剪）</td>
    <td class="c">外层 overflow:hidden　内层 :hover img { transform: scale(1.06); }</td></tr>
<tr><td>尊重减弱动效设置</td>
    <td class="c">@media (prefers-reduced-motion: reduce)</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">这一篇要记住的六句话</div>
  <ol>
    <li><b>伪类选中「处于某种状态的元素」</b>：
      <code>:hover</code> 悬停、<code>:active</code> 按下、<code>:focus</code> 聚焦。</li>
    <li><b>链接伪类按 LVHA 顺序写</b>（LoVe HAte）。</li>
    <li><b><code>transition</code> 写在基础规则里</b>，
      写在 <code>:hover</code> 里会导致「移出时瞬间跳回」。</li>
    <li><b>时长 0.15~0.3s 最舒服</b>，超过 0.4s 就显迟钝；
      出现用 <code>ease-out</code>，消失用 <code>ease-in</code>。</li>
    <li><b>优先过渡 <code>transform</code> 和 <code>opacity</code></b>
      —— 它们不引起布局重算；位移别用 <code>top/left</code>。</li>
    <li><b>「抬起」= 阴影变大 + 上移 2px</b>，
      两个一起做才自然。</li>
  </ol>
</div>"""

if __name__ == "__main__":
    print(build("fe-07.html", "FE-07", "鼠标悬停与 transition", BODY06, TOC06))
