# -*- coding: utf-8 -*-
"""F02 收尾：
   1. 两处 C++ 代码块（打印 CWD / 读文件）改成 C
   2. 删掉遗留的「用宏做编译开关 / include guard / 构建模式判断」三小节
      （宏已改为讲环境变量，这些属于 F03 的范围）
   3. 第 7 节的 ifstream 片段改成 C
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PATH = r"E:\QKMansion\CSX10\w\UME\共享群\教程\_ds_08_F02_相对文件路径与宏.html"
with io.open(PATH, encoding="utf-8") as fh:
    t = fh.read()
orig = len(t)
done = []


def sub(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        print("  !! %s：命中 %d" % (label, n))
        return
    t = t.replace(old, new, 1)
    done.append(label)


# ---------- 1. 打印 CWD 的示例 → C ----------
i0 = t.index('<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n'
             '<span class="hl-p">#include</span> <span class="hl-s">&lt;direct.h&gt;</span>')
i1 = t.index('</pre></div>', i0)
seg_new = '''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>
<span class="hl-p">#include</span> <span class="hl-s">&lt;direct.h&gt;</span>       <span class="hl-c">/* Windows 下的 _getcwd */</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">int</span> argc, <span class="hl-k">char</span> *argv[]) {
    <span class="hl-k">char</span> buf[<span class="hl-n">4096</span>];
    <span class="hl-f">_getcwd</span>(buf, <span class="hl-k">sizeof</span>(buf));

    <span class="hl-f">printf</span>(<span class="hl-s">"当前工作目录 (CWD) = %s\\n"</span>, buf);
    <span class="hl-f">printf</span>(<span class="hl-s">"程序自己的路径     = %s\\n"</span>, argc &gt; <span class="hl-n">0</span> ? argv[<span class="hl-n">0</span>] : <span class="hl-s">"?"</span>);
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}'''
t = t[:i0] + seg_new + t[i1:]
done.append("打印 CWD 示例 → C")

# ---------- 2. 读文件的示例 → C ----------
i0 = t.index('<span class="hl-p">#include</span> <span class="hl-s">&lt;iostream&gt;</span>\n'
             '<span class="hl-p">#include</span> <span class="hl-s">&lt;fstream&gt;</span>')
i1 = t.index('</pre></div>', i0)
seg_new = '''<span class="hl-p">#include</span> <span class="hl-s">&lt;stdio.h&gt;</span>

<span class="hl-k">int</span> <span class="hl-f">main</span>(<span class="hl-k">void</span>) {
    FILE *fp = <span class="hl-f">fopen</span>(<span class="hl-s">"data.txt"</span>, <span class="hl-s">"r"</span>);      <span class="hl-c">/* 相对路径 */</span>
    <span class="hl-k">if</span> (fp != <span class="hl-n">NULL</span>) {
        <span class="hl-k">char</span> line[<span class="hl-n">256</span>];
        <span class="hl-f">printf</span>(<span class="hl-s">"打开成功，内容:\\n"</span>);
        <span class="hl-k">while</span> (<span class="hl-f">fgets</span>(line, <span class="hl-k">sizeof</span>(line), fp) != <span class="hl-n">NULL</span>) {
            <span class="hl-f">printf</span>(<span class="hl-s">"  %s"</span>, line);
        }
        <span class="hl-f">fclose</span>(fp);
    } <span class="hl-k">else</span> {
        <span class="hl-f">printf</span>(<span class="hl-s">"打开 data.txt 失败（当前目录里没有它）\\n"</span>);
    }
    <span class="hl-k">return</span> <span class="hl-n">0</span>;
}'''
t = t[:i0] + seg_new + t[i1:]
done.append("读文件示例 → C")

# ---------- 3. 删掉遗留的三个 #define 小节 ----------
i0 = t.index('<h4>② 用宏做「编译开关」</h4>')
i1 = t.index('<!-- ============================================================ -->\n'
             '<h2 id="s7">')
t = t[:i0] + t[i1:]
done.append("删除遗留的 #define 三小节")

# ---------- 4. 第 7 节坑 1 的 ifstream → C ----------
sub('''<span class="hl-c">/* ❌ 想当然：以为从 exe 所在目录找 */</span>
ifstream in(<span class="hl-s">"data.txt"</span>);       <span class="hl-c">/* 实际是从 CWD 找！ */</span>

<span class="hl-c">/* ✅ 明确从 exe 所在目录找 */</span>
QString dir = QCoreApplication::<span class="hl-f">applicationDirPath</span>();
ifstream in((dir + <span class="hl-s">"/data.txt"</span>).<span class="hl-f">toStdString</span>());''',
'''<span class="hl-c">/* ❌ 想当然：以为从 exe 所在目录找 */</span>
FILE *fp = <span class="hl-f">fopen</span>(<span class="hl-s">"data.txt"</span>, <span class="hl-s">"r"</span>);   <span class="hl-c">/* 实际是从 CWD 找！ */</span>

<span class="hl-c">/* ✅ 明确从 exe 所在目录找（Qt 里用 applicationDirPath） */</span>
QString dir = QCoreApplication::<span class="hl-f">applicationDirPath</span>();
FILE *fp2 = <span class="hl-f">fopen</span>((dir + <span class="hl-s">"/data.txt"</span>).<span class="hl-f">toUtf8</span>().<span class="hl-f">constData</span>(), <span class="hl-s">"r"</span>);''',
    "坑 1 的 ifstream → C")

with io.open(PATH, "w", encoding="utf-8", newline="") as fh:
    fh.write(t)

print("F02：%d → %d 字符" % (orig, len(t)))
for d in done:
    print("  ✓ " + d)
print("")
print("剩余 cout=%d iostream=%d #define=%d #if=%d"
      % (len(re.findall(r'cout', t)), len(re.findall(r'iostream', t)),
         len(re.findall(r'#define', t)), len(re.findall(r'#if', t))))
for m in re.finditer(r'.{0,40}(cout|iostream|#define|#if).{0,40}', t):
    print("   ..." + m.group(0).replace("\n", " ").strip()[:92])
