# -*- coding: utf-8 -*-
"""Q05：标题改为「单一职责原则和开闭原则」，并加入 SRP 与二者的联系。

用户要求
    Q05 标题改为「单一职责原则和开闭原则」，且内部要介绍 SRP 和 OCP 的联系
    （先不提及 SOLID）。

现在的结构（7 节）
    1 一个类是怎么长胖的
    2 开闭原则
    3 为什么它在实际开发里这么重要   ← key-h
    4 回头看：那些 set / get 和「角色能做的事」
    5 大致的方向
    6 目标状态
    7 一页速查

改后（9 节）
    1 一个类是怎么长胖的
    2 单一职责原则                       ← 新增
    3 开闭原则                           （原 2）
    4 为什么开闭原则在实际开发里这么重要     （原 3，key-h）
    5 SRP 与 OCP 的联系                   ← 新增
    6 回头看：那些 set / get …            （原 4）
    7 大致的方向                          （原 5）
    8 目标状态                            （原 6）
    9 一页速查                            （原 7）

    新增的两节都插在「为什么它这么重要」之后 / 开闭原则之前，
    不打断原有论述的节奏：先讲两种「坏」，再讲两者关系，再落到 Actor。
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

T = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"
P = T + r"\q05.html"

SRP = """<h2 id="s2"><span class="n">2</span>单一职责原则</h2>

<p>上一节那个 <code>Actor</code>，问题可以先精确地描述出来：</p>

<div class="card key">
  <div class="card-t">一句话</div>
  <p><b>一个类应该只有一个「改变它的理由」。</b></p>
  <p>不是「代码要少」，也不是「一个类只做一个动作」，而是
  <b>只有一个方向的变化会让它非改不可</b>。</p>
</div>

<p>为什么是「改变的理由」而不是「做几件事」？因为这两者常常不是一回事：</p>

<div class="vs">
<table>
<thead><tr><th style="width:34%">类的样子</th><th style="width:20%">职责数</th>
<th>为什么</th></tr></thead>
<tbody>
<tr><td class="c">一个 300 行的 <code>文本格式化</code>类，
    里面 30 个方法全都只处理「怎么排版」</td>
    <td class="c"><b>1 个</b></td>
    <td>行数很多，但改它的理由只有一个：排版规则变了</td></tr>
<tr><td class="c">一个 40 行的 <code>Actor</code>，
    同时有改血量和买东西</td>
    <td class="c"><b>2 个</b></td>
    <td>血量规则变了要改它，商店规则变了也要改它</td></tr>
</tbody>
</table>
</div>

<p>所以判据不看行数，看<b>「谁会来找它」</b>。</p>

<h3>怎么数职责</h3>

<p>一个很实用的办法：<b>把「需求变了」当成不同的人来找你</b>。</p>

<div class="alias">
  <div class="row"><span class="k">战斗策划说</span>
    <span class="v">「伤害公式要调整」→ 得改 <code>Actor::attack</code></span></div>
  <div class="row"><span class="k">经济策划说</span>
    <span class="v">「物品价格要分档」→ 得改 <code>Actor::buyItem</code></span></div>
  <div class="row"><span class="k">关卡策划说</span>
    <span class="v">「换地图要加过渡动画」→ 得改 <code>Actor::changeMap</code></span></div>
  <div class="row"><span class="k">结论</span>
    <span class="v"><b>三个不同的人，三个不同的理由，都指向同一个类</b> ——
    这就是职责不单一</span></div>
</div>

<div class="card tip">
  <div class="card-t">这个「人数」很好用</div>
  <p><b>一个类上挂着多少个「不同的人」，它就有多少个职责。</b></p>
  <p>而且这也解释了代价：三个人要同时改同一份代码 → 冲突、
  <b>而且谁都不敢保证没弄坏别人</b>。</p>
</div>

<h3>职责拆开之后，每个类都变小了</h3>

<p>把 <code>Actor</code> 按「谁提需求」拆开，得到的东西是：</p>

<table>
<thead><tr><th style="width:26%">拆出来的类</th><th style="width:30%">唯一的改变理由</th>
<th>谁会来找它</th></tr></thead>
<tbody>
<tr><td class="c"><code>Actor</code></td><td>角色的状态规则（血量上限等）</td>
    <td class="c">角色策划</td></tr>
<tr><td class="c"><code>BattleSystem</code></td><td>伤害怎么算</td>
    <td class="c">战斗策划</td></tr>
<tr><td class="c"><code>ShopSystem</code></td><td>价格与库存</td>
    <td class="c">经济策划</td></tr>
<tr><td class="c"><code>MapSystem</code></td><td>地图怎么走</td>
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

LINK = """<h2 id="s5"><span class="n">5</span>SRP 与 OCP 的联系</h2>

<p>两条原则讲的是不同的事，但它们咬合得很紧。</p>

<div class="vs">
<table>
<thead><tr><th style="width:22%"></th><th style="width:39%">单一职责（SRP）</th>
<th>开闭原则（OCP）</th></tr></thead>
<tbody>
<tr><td><b>问的是</b></td><td>这个类身上挂着<b>几个</b>改变的理由？</td>
    <td>加新需求时，要不要<b>回头改</b>老代码？</td></tr>
<tr><td><b>管的是</b></td><td><b>现在</b>这个类有多大</td>
    <td><b>将来</b>改动会波及谁</td></tr>
<tr><td><b>违反时</b></td><td>一个类被几个方向的需求同时拉扯</td>
    <td>每来一个新需求，都要动那块所有人都在踩的地面</td></tr>
</tbody>
</table>
</div>

<p>它们的关系可以压成两句话：</p>

<div class="card key">
  <div class="card-t">① SRP 是 OCP 的前提</div>
  <p>一个类身上有几个职责，就有几个方向的改动会碰到它。
  <b>职责越多，它就越不可能「对修改关闭」</b> ——
  因为总有某一条分支的需求会迫使你改它。</p>
  <p>所以想做到开闭原则，第一步不是设计扩展点，
  而是<b>先让每个类的改变理由只剩一个</b>。</p>
</div>

<div class="card key">
  <div class="card-t">② OCP 是 SRP 的结果</div>
  <p>职责拆干净之后，新需求自然会落到一个<b>新的、单一职责的类</b>上，
  而不是塞进老类里。这时「加东西不改老东西」就是自然结果，
  不需要额外费力去追求。</p>
</div>

<div class="mnemonic">
  <b>反过来也成立：</b>一个类如果只有单一职责，它的改动面就很窄；
  改动面窄，才敢说「对它关闭」。<br>
  <b>只谈 OCP 不谈 SRP</b>，容易造出一个「什么都能扩展、但谁也看不懂」的类。
</div>

<div class="card tip">
  <div class="card-t">落到 Actor 上</div>
  <p>上一节的三个问题，其实是同一条链：</p>
  <div class="steps">
    <div class="st"><span class="i">1</span><span class="t">职责不止一个</span>
      <code>Actor</code> 同时管状态、战斗、商店、地图</div>
    <div class="st"><span class="i">2</span><span class="t">于是改动理由很多</span>
      任何一个系统的需求变化都会改到它</div>
    <div class="st"><span class="i">3</span><span class="t">于是不可能「对修改关闭」</span>
      每加一种道具、一种技能，都得回来改它</div>
  </div>
  <p><b>所以拆 <code>Actor</code> 这件事，同时满足了两条原则</b> ——
  不是为了其中一条而做的取舍。</p>
</div>

"""


def main():
    t = io.open(P, encoding="utf-8").read()

    if "单一职责原则" in t:
        print("  Q05 已含 SRP，跳过")
        return

    # ---- 1. 插 SRP 到 s2（开闭原则）之前 ----
    a = t.find('<h2 id="s2">')
    if a < 0:
        print("  !! 找不到 s2")
        sys.exit(1)
    t = t[:a] + SRP + t[a:]

    # ---- 2. 插联系到「回头看」（原 s4）之前 ----
    b = t.find('<h2 id="s4">')
    if b < 0:
        print("  !! 找不到 s4")
        sys.exit(1)
    t = t[:b] + LINK + t[b:]

    # ---- 3. 重排 id 与编号 ----
    # 现在顺序是：s1, s2(SRP), s2(开闭), s3(为什么), s4(联系), s4(回头看), s5, s6, s7
    # 先把所有 h2 的 id 换成占位，再按出现顺序重新编号
    order = []

    def stash(m):
        order.append(m.group(0))
        return "@@H2_%d@@" % (len(order) - 1)

    t = re.sub(r'<h2 id="s\d+"[^>]*>', stash, t)

    # 逐个落位：清掉原编号 span，写入新 id + 新编号
    for i in range(len(order)):
        # 从占位后面的 <span class="n">N</span> 读正文
        marker = "@@H2_%d@@" % i
        j = t.find(marker)
        m = re.compile(r'<span class="n">\d+</span>').match(t, j + len(marker))
        title_start = m.end() if m else j + len(marker)
        t = (t[:j]
             + '<h2 id="s%d">' % (i + 1)
             + '<span class="n">%d</span>' % (i + 1)
             + t[title_start:])

    print("  Q05 小节重排为 %d 个" % len(order))

    # ---- 4. 标题 ----
    t = t.replace("<h1>开闭原则", "<h1>单一职责原则和开闭原则")
    t = t.replace("<title>Q05 · 开闭原则", "<title>Q05 · 单一职责原则和开闭原则")

    # ---- 5. 副标题 ----
    t = re.sub(
        r'(<p class="sub-title">[^<]*· Q05（Q） · )[^<]*(</p>)',
        r'\1先讲清一条类该有多大，再讲它该多难被改\2', t, count=1)

    # ---- 6. TOC 重建（Q05 原来没有 .sub 子项，可以整体重建）----
    rows = []
    for mm in re.finditer(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                          t, re.S):
        sid, no = mm.group(1), mm.group(2)
        txt = re.sub(r"<[^>]+>", "", mm.group(3)).strip()
        rows.append('  <a href="#%s">%s · %s</a>' % (sid, no, txt))
    toc = '<nav id="toc">\n  <h5>目录</h5>\n' + "\n".join(rows) + "\n</nav>"
    t = re.sub(r'(?s)<nav id="toc">.*?</nav>', toc, t, count=1)

    io.open(P, "w", encoding="utf-8", newline="").write(t)
    print("  Q05 已写入 %d 字符" % len(t))

    # ---- 自检 ----
    print()
    for mm in re.finditer(r'<h2 id="(s\d+)"><span class="n">(\d+)</span>(.*?)</h2>',
                          t, re.S):
        print("      %-4s %-3s %s" % (mm.group(1), mm.group(2),
                                      re.sub(r"<[^>]+>", "", mm.group(3)).strip()))


if __name__ == "__main__":
    main()
