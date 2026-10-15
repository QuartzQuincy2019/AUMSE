# -*- coding: utf-8 -*-
"""06 收尾：把「构造函数与析构函数」一节改成 C 的说法，
   并把剩下那处内联的 class Buffer 片段改成 C 的写法。"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_06_类、结构体.html"

with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()

done = []


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        print("  !! %s：命中 %d 次" % (label, n))
        return
    t = t.replace(old, new, 1)
    done.append(label)


# 1) 本节标题与引导语改成 C 的说法
sub('<span class="name">构造函数与析构函数</span>',
    '<span class="name">C 里的「构造」与「析构」：init / destroy 约定</span>',
    "代码块标题")

sub('<div class="card-t">析构函数最重要的用途</div>',
    '<div class="card-t">「析构」最重要的用途：归还资源</div>',
    "卡片标题")

# 2) 那处内联的 class Buffer → C 写法
sub(
    '''  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-k">class</span> Buffer {
    <span class="hl-k">int</span> *data;
<span class="hl-k">public</span>:
    <span class="hl-f">Buffer</span>(<span class="hl-k">int</span> n)  { data = <span class="hl-k">new</span> <span class="hl-k">int</span>[n]; }   <span class="hl-c">/* 申请 */</span>
    ~<span class="hl-f">Buffer</span>()       { <span class="hl-k">delete</span>[] data; }        <span class="hl-c">/* 归还，自动！ */</span>
};</pre>
  <p>这就是第五讲「谁申请谁释放」在类里的落地方式：
  <b>申请写在构造函数，释放写在析构函数</b>，
  只要对象正常销毁，就不会泄漏。</p>''',
    '''  <pre style="background:#f2f4f8;border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-family:var(--mono);font-size:13px;color:var(--fg);overflow:auto"><span class="hl-c">/* 把「申请」和「释放」包成一对函数，成对调用 */</span>
<span class="hl-k">struct</span> Buffer {
    <span class="hl-k">int</span>  *data;
    <span class="hl-k">int</span>   n;
};

<span class="hl-k">void</span> <span class="hl-f">buffer_init</span>(<span class="hl-k">struct</span> Buffer *b, <span class="hl-k">int</span> n) {
    b-&gt;n = n;
    b-&gt;data = <span class="hl-f">malloc</span>(<span class="hl-k">sizeof</span>(<span class="hl-k">int</span>) * n);   <span class="hl-c">/* 申请 */</span>
}
<span class="hl-k">void</span> <span class="hl-f">buffer_destroy</span>(<span class="hl-k">struct</span> Buffer *b) {
    <span class="hl-f">free</span>(b-&gt;data);                     <span class="hl-c">/* 归还 */</span>
    b-&gt;data = <span class="hl-n">NULL</span>;
}</pre>
  <p>这就是第五讲「谁申请谁释放」在结构体上的落地方式：
  <b>申请写在 <code>xxx_init</code>，释放写在 <code>xxx_destroy</code></b>。</p>
  <p><b>代价是：你必须记得调用 <code>xxx_destroy</code>。</b>
  C++ 的构造函数 / 析构函数之所以受欢迎，正是因为它们
  <b>自动</b>在对象创建和销毁时被调用，不会忘 ——
  这部分属于 C++，本讲不展开。</p>''',
    "class Buffer → C 的 init/destroy")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("06 收尾完成：")
for d in done:
    print("  ✓ " + d)
