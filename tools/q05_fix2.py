# -*- coding: utf-8 -*-
"""Q05：把 SRP 的「理由」讲实，类的样子改用 Actor；补缩写的中文全称。

用户要求
    3. 「一个类应该只有一个『改变它的理由』」虽然官方，但不够明晰 ——
       什么叫「理由」？「类的样子」也应围绕 Actor 来写。
       「职责数」里职责有哪些？显式指出。
    4. 缩写第一次出现时必须给出中文名：单一职责原则(SRP)、开闭原则(OCP)。

改法
    把 §2 整节重写：
      · 一句话改为「一个类，应该只因为『一件事』而需要修改」，
        并立刻把「一件事」界定成「一个专门来找它的需求来源」
      · 新增「『理由』到底指什么」—— 给一个可操作、可数的判据：
        有人来让你改这个类，他是为了什么来的？答得出一个就单一。
      · 「类的样子」那张表全部换成 Actor 的三个版本，职责逐条列出来
      · 「怎么数职责」的那三个人也改成 Actor 上的具体需求

    缩写：§2 标题写「单一职责原则（SRP）」、§3 标题写「开闭原则（OCP）」——
    这两处是全文最早的缩写出现位置（正文里比 §5「SRP 与 OCP 的联系」更早）。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials\q05.html"
t = io.open(P, encoding="utf-8").read()

NEW_S2 = """<h2 id="s2"><span class="n">2</span>单一职责原则（SRP）</h2>

<p>上一节那个 <code>Actor</code>，问题可以先精确地描述出来：</p>

<div class="card key">
  <div class="card-t">一句话</div>
  <p><b>一个类，应该只因为「一件事」而需要修改。</b></p>
  <p>这里说的「一件事」＝ <b>一个专门来找它的需求来源</b>。</p>
</div>

<h3>「理由」到底指什么</h3>

<p>「改变的理由」听起来虚。其实可以问得非常具体 —— 具体到能数：</p>

<div class="mnemonic">
  <b>有人来让你改这个类，他是为了什么来的？</b><br>
  只答得出<b>一个</b>答案 → 职责单一<br>
  答得出<b>两个以上</b> → 职责不单一
</div>

<p>这样一换，「原则」就变成了一个<b>可数的问题</b>：数一数有几个不同的人会来找它。
而不是去争论「这算不算一件事」。</p>

<h3>拿 <code>Actor</code> 数一遍</h3>

<p>同一个类，长到不同的程度，「理由」的个数是这样变的：</p>

<table>
<thead><tr><th style="width:30%"><code>Actor</code> 里有哪几个函数</th>
<th style="width:26%">职责（＝能做的事）</th>
<th>会来找它的需求</th></tr></thead>
<tbody>
<tr><td class="c"><code>changeName</code>
    <code>setMaxHp</code><br><code>changeMap</code></td>
    <td><b>只有 1 个：<br>维护角色状态</b></td>
    <td class="c">「角色属性要调整」<br><b>→ 1 个理由</b></td></tr>
<tr><td class="c">上面 3 个<br>+ <code>attack</code>
    <code>defend</code></td>
    <td><b>2 个：<br>维护状态<br>战斗</b></td>
    <td class="c">「角色属性要调整」<br>「伤害公式要改」<br><b>→ 2 个理由</b></td></tr>
<tr><td class="c">上面 5 个<br>+ <code>buyItem</code>
    <code>changeMap 的逻辑</code></td>
    <td><b>4 个：<br>维护状态<br>战斗<br>商店<br>地图</b></td>
    <td class="c">「属性要调整」<br>「伤害公式要改」<br>「物品价格要分档」<br>「换地图要加动画」<br>
    <b>→ 4 个理由</b></td></tr>
</tbody>
</table>

<p>第二行有 <code>changeMap</code> 这个函数，但它只是「把坐标存下来」——
那还是维护状态。到第三行，<code>Actor</code> 开始真的处理
<b>地图怎么走</b>、<b>钱够不够</b>，职责才分裂成四个。</p>

<div class="card tip">
  <div class="card-t">注意「函数个数」不等于「职责个数」</div>
  <p>第一行 3 个函数、只有 1 个职责；第三行 7 个函数、却有 4 个职责。
  <b>数函数没用，要数「有几个方向会来提要求」。</b></p>
  <p>所以判据始终是那张表的最后一列 —— <b>会来找它的需求</b>，
  也就是最开头那句「专门来找它的需求来源」。</p>
</div>

<h3>把「来的人」列出来</h3>

<p>再具体一点：这些人彼此并不认识，但他们都要动同一个文件。</p>

<div class="alias">
  <div class="row"><span class="k">战斗策划</span>
    <span class="v">「伤害公式要调整」→ 得改 <code>Actor::attack</code></span></div>
  <div class="row"><span class="k">经济策划</span>
    <span class="v">「物品价格要分档」→ 得改 <code>Actor::buyItem</code></span></div>
  <div class="row"><span class="k">关卡策划</span>
    <span class="v">「换地图要加过渡动画」→ 得改 <code>Actor::changeMap</code></span></div>
  <div class="row"><span class="k">角色策划</span>
    <span class="v">「血量上限公式要改」→ 得改 <code>Actor::setMaxHp</code></span></div>
  <div class="row"><span class="k">结论</span>
    <span class="v"><b>四个人、四个理由、同一个类</b> —— 这就是职责不单一</span></div>
</div>

<p>这也顺带解释了代价：四个方向的人要同时改同一份代码 →
冲突、合并、<b>而且谁都不敢保证没弄坏别人那部分</b>。</p>

<h3>按「谁来提需求」拆</h3>

<p>拆法是现成的 —— 上面对照表的第二列就是拆完的类：</p>

<table>
<thead><tr><th style="width:26%">拆出来的类</th><th style="width:26%">唯一的职责</th>
<th>会来找它的需求</th></tr></thead>
<tbody>
<tr><td class="c"><code>Actor</code></td><td class="c">维护角色状态</td>
    <td class="c">角色策划</td></tr>
<tr><td class="c"><code>BattleSystem</code></td><td class="c">算伤害、定出手顺序</td>
    <td class="c">战斗策划</td></tr>
<tr><td class="c"><code>ShopSystem</code></td><td class="c">管价格与库存</td>
    <td class="c">经济策划</td></tr>
<tr><td class="c"><code>MapSystem</code></td><td class="c">管地图怎么走</td>
    <td class="c">关卡策划</td></tr>
</tbody>
</table>

<p>每个类都只被一类需求影响。<b>改战斗代码的人，碰不到商店代码。</b></p>

<div class="card note">
  <div class="card-t">别走过头</div>
  <p>SRP 不是「能拆就拆」。拆得过头会得到一堆只有两三行、互相还要传参数的类，
  <b>反而更难读</b>。</p>
  <p>判断标准还是那一条：<b>这个类上真的挂着两个不同方向的改变理由吗？</b>
  没有就别拆。</p>
</div>

"""

a = t.find('<h2 id="s2">')
b = t.find('<h2 id="s3">')
if a < 0 or b < 0:
    print("  !! 找不到 §2 边界")
    sys.exit(1)
t = t[:a] + NEW_S2 + t[b:]

# 缩写：§3 标题补中文全称（第一次出现 OCP 的地方）
t = t.replace('<span class="n">3</span>开闭原则</h2>',
              '<span class="n">3</span>开闭原则（OCP）</h2>', 1)
t = t.replace('  <a href="#s3">3 · 开闭原则</a>',
              '  <a href="#s3">3 · 开闭原则（OCP）</a>', 1)
t = t.replace('  <a href="#s2">2 · 单一职责原则</a>',
              '  <a href="#s2">2 · 单一职责原则（SRP）</a>', 1)

io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  Q05 已重写 §2，%d 字符" % len(t))

# ---- 自检 ----
print()
for mm in re.finditer(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                      t, re.S):
    print("      %-4s %-3s %s" % (mm.group(1), mm.group(2),
                                  re.sub(r"<[^>]+>", "", mm.group(3)).strip()))
print()
# 缩写首次出现顺序
for acro in ("SRP", "OCP", "ISP"):
    i = t.find(acro)
    if i < 0:
        print("      %-4s 未出现" % acro)
        continue
    ctx = re.sub(r"<[^>]+>", "", t[max(0, i - 40):i + 6]).strip()
    print("      %-4s 首次出现：…%s" % (acro, ctx[-40:]))
