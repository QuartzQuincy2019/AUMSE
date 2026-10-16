# -*- coding: utf-8 -*-
"""重写 Q01《std 与命名空间初步》—— 只留四节。

用户要求
    · 主要介绍「为什么使用」和「谁的谁」的概念（「谁的谁」标成重点）
    · 作用域解析运算符（标成重点）
    · 再加上 std 即可，其他的删掉（**包括速查表**）

原文 11 节 → 新 4 节
    删掉：3 四种写法与它们的代价 / 4 嵌套命名空间 / 5 匿名命名空间 /
          6 同一个程序：C 写法 vs C++ 写法 / 7 C → C++ 速查表 /
          8 标准库地图 / 10 常见错误 / 11 一页速查
    保留并重组：1（为什么需要）→ s1
                9（作用域解析运算符）里的「命名空间」与「全局名」两种用法
                    → 拆成 s2「谁的谁」+ s3「作用域解析运算符」
                2（std 是什么）→ s4

为什么用脚本拼而不是手抄
    Q01 是早期手工页，里面的代码块带大量 <span class="hl-*"> 高亮标记。
    手抄必然出错，所以直接从原文**按片段切**，只重写标题与连接性的散文。

顺带修掉原文的一个小毛病
    原 h2 是 `<h2 id="s1"><span class="n">1</span>为什么…` —— 数字紧跟
    `</span>`，没有分隔，渲染成「1为什么需要命名空间」。
    新写法在数字后加一个空格（与 Q02~Q05 一致）。
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
BODY_OUT = os.path.join(R, "tools", "_q01_body.html")

# 关键：**源片段必须来自那份 11 节的原始页面**，不能来自改写后的页面。
# 否则脚本第二次运行就找不到 s9 了（KeyError），而且第 2 节会重复。
# 所以先把原版导出成一个固定的快照文件，脚本只读快照。
SNAP = os.path.join(R, "tools", "_q01_orig_snapshot.html")
if not os.path.exists(SNAP):
    raise SystemExit("  !! 缺少快照 %s\n"
                     "     用 git show HEAD:SharingGroup/tutorials/"
                     "q01-std-and-namespace.html 生成它" % SNAP)

src = io.open(SNAP, encoding="utf-8").read()
mi = src.index("<main>")
nav = src.index("<!-- NAV-AUTO -->")
body = src[mi:nav]

# 按 h2 切段
ms = list(re.finditer(r'<h2[^>]*id="(s\d+)"[^>]*>', body))
segs = {}
for k, m in enumerate(ms):
    e = ms[k + 1].start() if k + 1 < len(ms) else len(body)
    segs[m.group(1)] = body[m.start():e]


def drop_heading(seg):
    """去掉片段开头的 <h2> 与紧随的空行。"""
    return re.sub(r'^\s*<h2[^>]*>.*?</h2>\s*', "", seg, count=1, flags=re.S)


def slice_between(seg, start_mark, end_marks):
    """取 seg 里 start_mark 到最近的某个 end_mark 之间的内容。"""
    i = seg.index(start_mark)
    j = len(seg)
    for em in end_marks:
        k = seg.find(em, i + len(start_mark))
        if k >= 0:
            j = min(j, k)
    return seg[i:j].rstrip()


s1 = segs["s1"]
s2 = segs["s2"]
s9 = segs["s9"]

# ---- 从 s9 里切出两种用法 ----
u1 = slice_between(s9, "<h4>① 定位命名空间里的东西</h4>",
                   ["<h4>② 访问类的静态成员</h4>"])
u4 = slice_between(s9, "<h4>④ 前面什么都不写",
                   ["<h4>Qt 真实代码里的"])
u_head = slice_between(s9, '<div class="card key">',
                       ["<p>下面把它的四种用法一次讲完"])

# ---- 「谁的谁」一节要用的那两个例子代码块 ----
# 要的是** C++ 那段**（ume / other 两个命名空间），不是开头那段 C 的重名代码。
# 第一版用 `other::hello` 结尾去匹配，结果非贪婪从**第一个** code-wrap 就开始了
# —— 于是把「C 里的重名问题」整段搬到了第 2 节，和第 1 节重复。
# 改法：以「C++ 的写法」这个 name 为起点切片，再截到该 code-wrap 的 </div>。
s2_code = ""
_ci = s1.find('<span class="name">C++ 的写法</span>')
if _ci >= 0:
    _st = s1.rfind('<div class="code-wrap">', 0, _ci)
    _en = s1.find("</pre></div>", _ci)
    if _st >= 0 and _en >= 0:
        s2_code = s1[_st:_en + len("</pre></div>")]
_wi = s1.find('<div class="out-wrap"><div class="cap">运行结果</div>')
if _wi >= 0:
    _we = s1.find("</pre></div>", _wi)
    s2_code += "\n" + s1[_wi:_we + len("</pre></div>")]
print("  「谁的谁」示例代码块：%d 字符 %s"
      % (len(s2_code), "OK" if s2_code else "!! 没取到"))
print("     取到的是: %s"
      % (re.search(r'<span class="name">(.*?)</span>', s2_code).group(1)
         if s2_code else "（无）"))

# ---- 组装新正文 ----
INTRO = """<p><span class="lang cpp">C++</span> <span class="tag b">本讲：命名空间</span></p>

<p>前八讲讲的是 <b>C</b>。从这一讲起转向 <b>C++</b> ——
而 C++ 代码里第一个让人不习惯的东西，就是一堆双冒号：

<code>std::cout</code>、<code>std::string</code>、<code>Qt::AlignCenter</code>。</p>

<p>它们都和同一个概念有关：<b>命名空间</b>。这一篇只讲三件事 ——
<b>为什么要它</b>、<b>「谁的谁」怎么读</b>、<b>那个 <code>::</code> 是什么</b>。</p>
"""

S2_HEAD = ('<h2 id="s2" class="key-h">'
           '<span class="key-mark" title="重点内容">★</span>'
           '<span class="n">2</span>'
           '谁的谁：给名字加上「姓」</h2>')

S2_BODY = """<p>命名空间的效果，一句话就能说清：
<b>它给名字加了一层「姓」，从此每个名字都归属于某个「谁」。</b></p>

<div class="card key">
  <div class="card-t">把 <code>::</code> 读作「的」</div>
  <p><code>A::b</code> 读成「<b>A 的 b</b>」。句子读得通，写法就对了。</p>
  <table>
  <thead><tr><th style="width:34%">写法</th><th style="width:22%">读作</th><th>是谁的</th></tr></thead>
  <tbody>
  <tr><td class="c">std::cout</td><td>std 的 cout</td><td>标准库</td></tr>
  <tr><td class="c">ume::version</td><td>ume 的 version</td><td>ume 这个命名空间</td></tr>
  <tr><td class="c">other::version</td><td>other 的 version</td><td>other 这个命名空间</td></tr>
  <tr><td class="c">::count</td><td>全局的 count</td><td>不属于任何命名空间</td></tr>
  </tbody>
  </table>
  <p><b>同名不怕</b>：<code>ume::version</code> 和 <code>other::version</code>
  可以同时存在，因为它们的「谁」不同。</p>
</div>

<p>回到开头那段代码，现在读起来应该没有障碍了 ——
两个 <code>version</code>、两个 <code>hello</code>，各归各的：</p>
"""

S2_TAIL = """
<div class="card tip">
  <div class="card-t">「谁的谁」这个读法为什么值得养成</div>
  <p>因为它把<b>「这个名字从哪来」</b>变成了看一眼就知道的事。</p>
  <p>读 <code>QMessageBox::warning(...)</code> 时，你不需要知道
  <code>QMessageBox</code> 内部长什么样，就知道
  <b>这个函数是它家的</b>；读 <code>::count</code> 就知道
  <b>这是全局那个</b>，不是某个局部的同名变量。</p>
  <p>以后看别人的代码，<b>先看 <code>::</code> 左边是谁</b>，
  一半的疑问就没了。</p>
</div>
"""

S3_HEAD = ('<h2 id="s3" class="key-h">'
           '<span class="key-mark" title="重点内容">★</span>'
           '<span class="n">3</span>'
           '<code>::</code> 作用域解析运算符</h2>')

S3_BODY_PRE = """<p>你已经一直在写 <code>std::cout</code>，但可能没细看中间那两个冒号。
它叫 <b>作用域解析运算符</b>（scope resolution operator），
是 C++ 里最不起眼、出现频率却最高的运算符之一。</p>

<p>它只有两种读法，记住这两个就够：</p>
"""

S4_HEAD = '<h2 id="s4"><span class="n">4</span><code>std</code> 是什么</h2>'


def main():
    parts = [
        INTRO,
        s1,                       # 原 s1（含标题，下面再把标题升级成 key-h）
        S2_HEAD, "\n\n",
        S2_BODY,
        s2_code,                  # 原 s1 里那段「两个 version、两个 hello」的代码
        S2_TAIL,
        S3_HEAD, "\n\n", S3_BODY_PRE, u_head, "\n\n",
        u1, "\n\n", u4,           # s9 里的两种用法
        S4_HEAD, "\n\n", drop_heading(s2),   # 原 s2「std 是什么」的正文
    ]
    new = "".join(parts)

    # s1 的标题要加 key-h 与空格
    # ★ 放在**数字徽标之前** —— .key-mark 自带 margin-right:8px，
    # 那是给「★ 在数字前」留的；放在数字后面会让留白跑到标题前面。
    # 手工页 T02 / F01 也是「★ 在前」，统一。
    new = new.replace(
        '<h2 id="s1"><span class="n">1</span>为什么需要命名空间</h2>',
        '<h2 id="s1" class="key-h">'
        '<span class="key-mark" title="重点内容">★</span>'
        '<span class="n">1</span>为什么需要命名空间</h2>')

    # 清掉多余空行
    new = re.sub(r"\n{3,}", "\n\n", new).strip() + "\n"

    # ---- 编号与 id 自检 ----
    # 允许 ★ 在数字前（本脚本现在用的排法）也允许在后，
    # 否则自检会把带 ★ 的小节整个漏掉 —— 实测漏到只剩 3 节。
    hs = re.findall(r'<h2 id="(s\d+)"[^>]*>'
                    r'(?:<span class="key-mark"[^>]*>[^<]*</span>)?'
                    r'<span class="n">(\d+)</span>', new)
    ids = [h[0] for h in hs]
    nos = [h[1] for h in hs]
    ok = (ids == ["s%d" % i for i in range(1, len(ids) + 1)]
          and nos == [str(i) for i in range(1, len(nos) + 1)])
    print("  小节 %d 个：%s" % (len(hs), " ".join(nos)))
    print("  id/编号连续 = %s" % ("是 OK" if ok else "否 !! %s / %s" % (ids, nos)))
    print("  key-h 小节 %d 个" % new.count('class="key-h"'))
    print("  正文 %d 字符" % len(new))

    if not ok:
        print("  !! 编号不连续，未写入")
        return

    io.open(BODY_OUT, "w", encoding="utf-8", newline="").write(new)
    print("  已写入 %s" % BODY_OUT)


if __name__ == "__main__":
    main()
