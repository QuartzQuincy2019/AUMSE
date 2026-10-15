# -*- coding: utf-8 -*-
"""让 T01 / T02 / T03 三篇连成一串。

改动：
  ① T02 的 s4「为什么 char 装不下蒙文」里插入 UMCompos 蒙文示例 ——
     这一节全在讲字节，插入渲染后就能看见「字节 → 码位 → 字形」的落点
  ② T02 结尾加「这一篇在理论系列里的位置」，说明 T01 → T02 → T03 的关系
  ③ T03 结尾的「下一步」改成指向 T02（原来指向 09-E03，编号已变）
  ④ T03 开头点明它承接 T02
  ⑤ T02 的补充样式进 assets/t02_unicode_and_encoding.css
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

R = r"E:\QKMansion\CSX10\w\UME"
T = os.path.join(R, "SharingGroup", "tutorials")

# T02 / T03 都从 tutorials/ 目录引用 web/ 下的插件
DEMO_SCRIPTS = ('<script src="../../web/UMCompos.js"></script>\n'
                '<script src="../../web/project-config.js"></script>\n')

DEMO_JS = r'''<script>
/* ------------------------------------------------------------------
   T02 的蒙文示例：把「码位 → UTF-8 字节 → 字形」串起来看。
   蒙文一律用 \uXXXX 写 —— 与 tools/cnmn.py 从官方转写方案表
   机械换算出的码位完全一致，不依赖编辑器能否输入蒙文。
   ------------------------------------------------------------------ */
(function () {
  if (typeof UMCompos === 'undefined') return;

  /* monggul（蒙古）：6 个码位 → 18 字节 UTF-8 */
  var MONGGUL = '\u182E\u1823\u1829\u182D\u1824\u182F';

  UMCompos.loadFont().then(function () {
    /* ① s4 里的渲染示例 */
    var box = document.getElementById('demo-bytes');
    if (box) {
      UMCompos.mount(box, { text: MONGGUL, fontSize: 40, height: '200px' });
    }
    /* ② 逐码位对照表 */
    var tb = document.getElementById('cp-table');
    if (tb) {
      var cps = Array.from(MONGGUL).map(function (c) { return c.codePointAt(0); });
      var bytes = new TextEncoder().encode(MONGGUL);
      var per = Math.ceil(bytes.length / cps.length);
      var html = '';
      for (var i = 0; i < cps.length; i++) {
        var hex = cps[i].toString(16).toUpperCase().padStart(4, '0');
        var bs = [];
        for (var k = 0; k < per; k++) {
          bs.push('%' + bytes[i * per + k].toString(16).toUpperCase()
                  .padStart(2, '0'));
        }
        html += '<tr><td class="c">' + (i + 1) + '</td>'
              + '<td class="c">U+' + hex + '</td>'
              + '<td class="c" lang="mn-Mong" style="font-family:'
              + UMCompos.config().fontStack + '">'
              + String.fromCodePoint(cps[i]) + '</td>'
              + '<td class="c">' + bs.join(' ') + '</td>'
              + '<td class="c">' + per + '</td></tr>';
      }
      tb.innerHTML = html;
      var tot = document.getElementById('cp-total');
      if (tot) {
        tot.textContent = cps.length + ' 个码位、' + bytes.length
                        + ' 个字节（每个码位 ' + per + ' 字节）';
      }
    }
  });
})();
</script>'''

SNIPPET_S4 = r'''
<h4>把字节和字形对上：<code>monggul</code>（蒙古）</h4>

<p>光看字节数字容易发懵。下面这个词就是上面那 18 个字节 ——
<b>由 <code>UMCompos</code> 插件实时渲染</b>，不再是十六进制：</p>

<div class="umc-demo" id="demo-bytes"></div>

<p>把它拆开逐字节对照：</p>

<table>
<thead><tr><th style="width:8%">#</th><th style="width:16%">码位</th>
  <th style="width:12%">字形</th><th style="width:36%">UTF-8 字节</th>
  <th>字节数</th></tr></thead>
<tbody id="cp-table"></tbody>
</table>

<p><b id="cp-total"></b>。这张表由浏览器用 <code>TextEncoder</code>
当场算出来，不是写死的。</p>

<div class="card key">
  <div class="card-t">从这 18 个字节到一个词，中间隔着三层</div>
  <div class="code-wrap" style="margin-top:8px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">三层转换</span><span class="cp">复制</span></div><pre>① 字节      E1 A0 AE  E1 A0 A3  …        18 个字节
                 ↓  UTF-8 解码
② 码位      U+182E  U+1823  U+1829 …     6 个码位
                 ↓  <b>字体 + 排版引擎</b>（本篇不讲，见 T03）
③ 字形      连写后的实际墨迹              可能少于 6 个字形
                                           —— 相邻字母会合成连字</pre></div>
  <p style="margin-top:10px">T02 讲的是 ① → ②。
  <b>② → ③ 那一步发生在字体文件里</b>，是 T03 的内容。</p>
  <p><b>注意最后一行</b>：6 个码位不一定画出 6 个字形 ——
  这正是「码位数 ≠ 字形数」的由来，T03 会给出具体数字（517 vs 3715）。</p>
</div>
'''

SNIPPET_FLOW = r'''
<h2 id="s9"><span class="n">9</span>这一篇在理论系列里的位置</h2>

<p>理论系列三篇是<b>从外到内</b>递进的：</p>

<table>
<thead><tr><th style="width:14%">篇目</th><th style="width:30%">回答的问题</th>
  <th>你学到的</th></tr></thead>
<tbody>
<tr><td class="c"><b>T01</b></td>
    <td>这门文字<b>是什么样</b>？</td>
    <td>拉丁转写、字形/连字/连写、竖排与四个位置形、
      中国—蒙古国联合蒙文转写</td></tr>
<tr><td class="c"><b>T02</b><br><span class="tag b">本篇</span></td>
    <td>这门文字在计算机里<b>怎么存</b>？</td>
    <td>码位、UTF-8 变长编码、<code>char</code> 为什么不够用</td></tr>
<tr><td class="c"><b>T03</b></td>
    <td>这些码位<b>怎么变成字形</b>？</td>
    <td>字体文件的 18 张表、GSUB、cmap 517 vs 字形 3715、
      字形名里的 448 种音节</td></tr>
</tbody>
</table>

<div class="card key">
  <div class="card-t">一句话记住三篇的分工</div>
  <p><b>T01 讲「文字」，T02 讲「编号」，T03 讲「画出来」。</b></p>
  <p>你在本篇学到的 <code>U+1820</code> 这类编号，正是 T03 里
  <code>cmap</code> 表的<b>查询键</b> —— T03 会给出一张
  「码位 → 字形名 → 推进量」的表，键就是这些编号。</p>
</div>

<div class="card note">
  <div class="card-t">动手</div>
  <p>本篇的蒙文示例由 <code>web/UMCompos.js</code> 实时渲染。
  想看这个插件的其他用法，或者自己换一串蒙文试试，
  可以打开仓库里的 <code>web/UME.html</code>（编辑器）。</p>
  <p>想把某个词换成蒙文，用 <code>tools/cnmn.py</code>：</p>
  <div class="code-wrap" style="margin-top:8px"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="name">换算</span><span class="cp">复制</span></div><pre>$ python tools/cnmn.py
monggul  → 'ᠮᠣᠩᠭᠤᠯ'   U+182E U+1823 U+1829 U+182D U+1824 U+182F
                          回读: m o ng g u l</pre></div>
</div>
'''

EXTRA_CSS = """
/* ---------- UMCompos 蒙文示例（T02） ---------- */
.umc-demo{margin:16px 0;padding:12px 14px;overflow-x:auto;
  background:var(--bg-soft);border:1px solid var(--line-2);border-radius:12px}
.umc-demo .umc{color:var(--fg)}
"""


def insert_before(src, marker, snippet):
    i = src.find(marker)
    if i < 0:
        return None
    return src[:i] + snippet + "\n" + src[i:]


def main():
    # ================= T02 =================
    p2 = os.path.join(T, "t02-unicode-and-encoding.html")
    t = io.open(p2, encoding="utf-8").read()

    if "demo-bytes" in t:
        print("  · T02 已有蒙文示例，跳过插入")
    else:
        # ① s4 里插在「于是 strlen 的含义就变了」之前
        r = insert_before(t, "<h4>于是 <code>strlen</code> 的含义就变了</h4>",
                          SNIPPET_S4)
        if r:
            t = r
            print("  ✓ T02 s4 插入蒙文渲染 + 字节对照表")
        else:
            print("  ! T02 s4 插入点未找到")

        # ② 结尾加系列位置（插在 footer 之前）
        r = insert_before(t, "<footer", SNIPPET_FLOW)
        if r:
            t = r
            print("  ✓ T02 结尾加「理论系列里的位置」")
        else:
            print("  ! T02 footer 未找到")

        # ③ 加载插件 + 演示脚本（插在 </body> 之前）
        t = t.replace("</body>", DEMO_SCRIPTS + DEMO_JS + "\n</body>", 1)
        print("  ✓ T02 加载 UMCompos 与演示脚本")

        # ④ 目录补一项
        t = t.replace('  <a href="#s8">8 · 一页速查</a>',
                      '  <a href="#s8">8 · 一页速查</a>\n'
                      '  <a href="#s9">9 · 系列里的位置</a>', 1)
        io.open(p2, "w", encoding="utf-8", newline="").write(t)
        print("  ✓ T02 目录补第 9 项")

    # 补样式
    cp = os.path.join(T, "assets", "t02_unicode_and_encoding.css")
    c = io.open(cp, encoding="utf-8").read()
    if ".umc-demo" not in c:
        io.open(cp, "w", encoding="utf-8", newline="\n").write(c + EXTRA_CSS)
        print("  ✓ T02 样式表补 .umc-demo")
    else:
        print("  · T02 样式表已有 .umc-demo")

    # ================= T03 =================
    b3 = os.path.join(R, "tools", "build_f04.py")
    u = io.open(b3, encoding="utf-8").read()
    if "承接 T02" in u:
        print("  · T03 已点明承接 T02")
    else:
        old = "<p>文中每个数字都可以自己复现，命令在最后一节。</p>"
        new = ("<p>文中每个数字都可以自己复现，命令在最后一节。</p>\n"
               "  <p><b>它承接 T02</b>：T02 讲到「码位」为止，"
               "T03 接着讲这些码位在字体文件里<b>怎么变成字形</b>。"
               "建议先看 T01 → T02。</p>")
        if old in u:
            u = u.replace(old, new, 1)
            print("  ✓ T03 开头点明承接 T02")

    # T03 的「下一步」改成指向 T02
    old2 = ("  <p>而竖排排版怎么用这些数据，见 <code>web/UMCompos.js</code>\n"
            "  与理论篇 <b>T01</b>。</p>")
    new2 = ("  <p>而竖排排版怎么用这些数据，见 <code>web/UMCompos.js</code>。</p>\n"
            "  <p><b>回到理论系列</b>：<b>T01</b> 讲文字本身、"
            "<b>T02</b> 讲码位与 UTF-8，本篇（<b>T03</b>）讲码位到字形。"
            "三篇连起来就是「文字 → 编号 → 画出来」。</p>\n"
            "  <p>本篇的渲染示例（如果有）同样由 "
            "<code>web/UMCompos.js</code> 完成 —— "
            "它用的推进量数据，正是下面这张表里量出来的。</p>")
    if old2 in u:
        u = u.replace(old2, new2, 1)
        print("  ✓ T03「下一步」改为指向 T01 → T02 系列")
    else:
        print("  ! T03「下一步」原文未匹配")
    io.open(b3, "w", encoding="utf-8", newline="").write(u)


if __name__ == "__main__":
    main()
