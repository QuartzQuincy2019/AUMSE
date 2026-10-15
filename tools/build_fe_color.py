# -*- coding: utf-8 -*-
"""给 FE-03-F01（颜色模型）加颜色拾取器，并把这一篇的重点收敛到
   「十六进制颜色模型」和「Alpha 通道」两条。"""
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
import build_fe_b
from build_fe import build
import re

body = build_fe_b.BODY3F1
toc = build_fe_b.TOC3F1

# 在「一页速查」之前插入拾取器
marker = '<h2 id="s8"><span class="n">8</span>一页速查</h2>'
if marker not in body:
    print("!! 找不到 s8 标题，检查 TOC 编号")
    raise SystemExit(1)

picker_intro = """<h2 id="s7"><span class="n">7</span>颜色拾取器</h2>

<p>下面这个拾取器可以亲手拖一拖。<b>拖动任意一个滑块，看四个数值怎么一起变。</b></p>

<p>几个建议试的动作：</p>
<ul>
  <li>把 <b>R</b> 拉到 255、G 和 B 都拉到 0 →
    看十六进制变成 <code>#FF0000</code></li>
  <li>把 <b>透明度 A</b> 慢慢拉小 →
    看 <code>#RRGGBB</code> 后面多出两位、色块变透明</li>
  <li>把 R、G、B 调成同一个数 →
    得到灰色，同时 <b>HSL 里的 S 变成 0%</b></li>
  <li>随便选一个颜色，然后<b>只改 L（亮度）</b> →
    色相不变，只变深浅 —— 这就是 HSL 比 RGB 好用的地方</li>
  <li>点下面的色板快速跳到常用色</li>
</ul>

<p><b>拾取器在本页最下方</b>（速查表之后）。</p>

<div class="card key">
  <div class="card-t">从拾取器里能看出来的三件事</div>
  <ol>
    <li><b>十六进制和 rgb() 是同一个东西的两种写法</b> ——
      拖滑块时两组数字同步变化。</li>
    <li><b>Alpha 加进去就是第四个数</b>；
      写成十六进制时占最后两位，<code>80</code> ≈ 50%。</li>
    <li><b>HSL 的三个数各管一件事</b>（色相 / 饱和 / 亮度），
      而 RGB 的三个数各管一盏灯 —— 前者更适合「调」，后者更适合「抄」。</li>
  </ol>
</div>

<h2 id="s8"><span class="n">8</span>一页速查</h2>"""

body = body.replace(marker, picker_intro, 1)

print(build("fe-03-F01.html", "FE-03-F01", "十六进制颜色模型、HSV 与 Alpha",
            body, toc, with_picker=True))
