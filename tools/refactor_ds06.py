# -*- coding: utf-8 -*-
"""重构 _ds_06：删除「接口」相关的一切内容，并把后续章节重新编号。

删除项：
  · 第 7 节「接口：约定必须会做什么」整节（含 7.1/7.2/7.3）
  · 错误 3「接口里漏写 = 0」、错误 6「用接口指针当元素」
  · 速查表里 4 行接口相关
  · 总结卡里的接口两条
  · .iface 示意图 CSS（本讲不再使用）
  · 第 10 节末尾那段「下一讲预告」（原指 07 引用与指针）
重新编号：8→7、9→8、10→9
"""
import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = r"E:\QKMansion\CSX10\w\UME\共享群\教程"
PATH = os.path.join(ROOT, "_ds_06_类、结构体.html")

with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()

orig_len = len(t)
done = []


def cut(start_mark, end_mark, label):
    """删掉 [start_mark, end_mark) 区间（end_mark 保留）"""
    global t
    i0 = t.index(start_mark)
    i1 = t.index(end_mark, i0)
    t = t[:i0] + t[i1:]
    done.append("%s（删 %d 字符）" % (label, i1 - i0))


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        raise SystemExit("命中 %d 次（应为 1）: %s" % (n, label))
    t = t.replace(old, new, 1)
    done.append(label)


# ---------- 1. 删除第 7 节整节 ----------
cut('<h2 id="s7"><span class="n">7</span>接口：约定「必须会做什么」</h2>',
    '<h2 id="s8"><span class="n">8</span>对象的生与死</h2>',
    "删除第 7 节「接口」整节")

# ---------- 2. 章节重新编号 8→7 / 9→8 / 10→9 ----------
sub('<h2 id="s8"><span class="n">8</span>对象的生与死</h2>',
    '<h2 id="s7"><span class="n">7</span>对象的生与死</h2>',
    "8 → 7（对象的生与死）")
sub('<h2 id="s9"><span class="n">9</span>常见错误</h2>',
    '<h2 id="s8"><span class="n">8</span>常见错误</h2>',
    "9 → 8（常见错误）")
sub('<h2 id="s10"><span class="n">10</span>一页速查</h2>',
    '<h2 id="s9"><span class="n">9</span>一页速查</h2>',
    "10 → 9（一页速查）")

# ---------- 3. 目录改造 ----------
sub("""  <a href="#s5c" class="sub">5.3 亲眼看看编译错误</a>
  <a href="#s6">6 · struct 与 class 的唯一区别</a>
  <div class="sep"></div>
  <a href="#s7">7 · 接口：约定「必须会做什么」</a>
  <a href="#s7a" class="sub">7.1 三个角色，一套动作</a>
  <a href="#s7b" class="sub">7.2 接口为什么省事</a>
  <a href="#s7c" class="sub">7.3 接口与实现分离</a>
  <a href="#s8">8 · 对象的生与死</a>
  <a href="#s9">9 · 常见错误</a>
  <a href="#s10">10 · 一页速查</a>""",
"""  <a href="#s5c" class="sub">5.3 亲眼看看编译错误</a>
  <a href="#s6">6 · struct 与 class 的唯一区别</a>
  <a href="#s7">7 · 对象的生与死</a>
  <a href="#s8">8 · 常见错误</a>
  <a href="#s9">9 · 一页速查</a>""",
    "目录：删掉接口三条，后续重编号")

# ---------- 4. 删除 .iface 示意图 CSS ----------
cut("/* 接口示意图：一个接口，多个实现 */", "/* 「值/引用/指针」三列对照 */",
    "删除 .iface 示意图 CSS")

# ---------- 5. 删除错误 3（接口里漏写 = 0）----------
cut('<h4>错误 3 · 接口里漏写 <code>= 0</code></h4>',
    '<h4>错误 4 · 用 <code>.</code> 去访问指针指向的对象</h4>',
    "删除错误 3（接口漏写 = 0）")

# ---------- 6. 删除错误 6（接口指针当元素）----------
cut('<h4>错误 6 · 数组或容器里放对象，却用了接口指针</h4>',
    '<!-- ============================================================ -->\n<h2 id="s9">',
    "删除错误 6（接口指针当元素）")

# 错误编号顺延：4→3, 5→4
sub('<h4>错误 4 · 用 <code>.</code> 去访问指针指向的对象</h4>',
    '<h4>错误 3 · 用 <code>.</code> 去访问指针指向的对象</h4>',
    "错误 4 → 3")
sub('<h4>错误 5 · 忘了构造函数导致成员没初始化</h4>',
    '<h4>错误 4 · 忘了构造函数导致成员没初始化</h4>',
    "错误 5 → 4")

# ---------- 7. 速查表：删掉接口 4 行 ----------
sub("""<tr><td>定义接口</td><td class="c">virtual void attack() = 0;</td></tr>
<tr><td>实现接口</td><td class="c">class Archer : public GameCharacter { ... }</td></tr>
<tr><td>标记重写</td><td class="c">void attack() override { ... }</td></tr>
<tr><td>用接口统一调用</td><td class="c">GameCharacter *c = &amp;a; c-&gt;attack();</td></tr>
""", "", "速查表：删掉接口 4 行")

# ---------- 8. 总结卡：删掉接口两条，改为五句话 ----------
sub("""    <li><b><code>private</code> 保护数据</b>，只留 <code>public</code> 的函数当出口 ——
      规矩写在一处，外面绕不过去。</li>
    <li><b><code>struct</code> 与 <code>class</code> 只差默认权限</b>：
      struct 默认 public，class 默认 private。</li>
    <li><b>接口用纯虚函数 <code>= 0</code> 定义</b>，只规定「必须会做什么」。</li>
    <li><b>依赖接口而非具体类</b>，加新角色不用改旧代码。</li>
  </ol>""",
"""    <li><b><code>private</code> 保护数据</b>，只留 <code>public</code> 的函数当出口 ——
      规矩写在一处，外面绕不过去。</li>
    <li><b><code>struct</code> 与 <code>class</code> 只差默认权限</b>：
      struct 默认 public，class 默认 private。</li>
    <li><b>构造函数保证对象一造出来就合法</b>，析构函数负责收尾（该释放的资源在那里放）。</li>
  </ol>""",
    "总结卡：删掉接口两条")
sub('<div class="card-t">本讲要记住的六句话</div>',
    '<div class="card-t">本讲要记住的五句话</div>',
    "总结卡标题：六句 → 五句")

# ---------- 9. 第 9 节末尾的「下一讲预告」整段替换 ----------
cut('<div class="card note">\n  <div class="card-t">下一讲预告</div>',
    '<footer>',
    "替换第 9 节末尾的预告")

NEW_NOTE = """<div class="card note">
  <div class="card-t">下一讲预告</div>
  <p>这一讲里，变量都写在很「显眼」的位置：成员变量在类里，局部变量在函数里。
  但程序一大，就会冒出一堆问题：</p>
  <ul>
    <li>写 <code>int hp = 100;</code> 的时候，这个 <code>hp</code> 到底属于谁？
      为什么另一个函数里的同名变量完全不相干？</li>
    <li>为什么 <code>for (int i = 0; ...)</code> 里的 <code>i</code> 出了循环就用不了？</li>
    <li>全局变量到处都能改，什么时候该用、什么时候是灾难？</li>
  </ul>
  <p>下一讲《作用域、全局与局部变量》就把这些问题讲清楚：
  <b>一个名字在哪些地方能被看见、活多久、被谁遮住</b>。</p>
</div>

"""
t = t.replace('<footer>', NEW_NOTE + '<footer>', 1)
done.append("插入新的「下一讲预告」（指向第 07 讲）")

# ---------- 10. 收尾：清理残留与页脚 ----------
sub('代码示例均以 <b>Consolas</b> 等宽字体呈现；文中所有「运行结果」与「编译错误」\n均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。',
    '代码示例均以 <b>Consolas</b> 等宽字体呈现；文中所有「运行结果」与「编译错误」\n均使用 g++ 13.1.0（<code>-std=c++17</code>）实际编译运行核对。',
    "页脚占位（无改动）")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("原始 %d 字符 → 现在 %d 字符" % (orig_len, len(t)))
for d in done:
    print("  ✓ " + d)

print("")
print("残留「接口」次数: %d" % t.count("接口"))
for m in __import__("re").finditer("接口", t):
    seg = t[max(0, m.start() - 60):m.start() + 40].replace("\n", " ")
    print("   ..." + seg.strip()[-92:])
