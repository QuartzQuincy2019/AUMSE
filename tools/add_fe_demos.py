# -*- coding: utf-8 -*-
"""给 FE-05 / FE-06 / FE-07 补「示例展示」。

不重写整篇 —— 只在正文里插入渲染出来的示例，插在对应小节的代码块附近。
"""
import io
import os
import sys
sys.path.insert(0, r"E:\QKMansion\CSX10\w\UME\tools")
from build_fe import build
from fe_kit import pv

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

# =====================================================================
# 各篇要插入的示例：(锚点小节标题, 插入位置标记, 示例 HTML)
# =====================================================================
DEMOS = {}

# ---------------- FE-05 Display 与盒模型 ----------------
DEMOS["fe-05.html"] = [
    # 插在「四层一起写」的代码块之后
    ("四层一起写",
     pv(1, "盒模型四层",
        """/* 同一套尺寸，只改 padding / border / margin 看区别 */
.box1{width:180px;padding:0;border:0 solid #1f6feb;margin:0}
.box2{width:180px;padding:18px;border:0 solid #1f6feb;margin:0}
.box3{width:180px;padding:18px;border:4px solid #1f6feb;margin:0}
.box1,.box2,.box3{background:#e8f1fe;border-radius:6px;font-size:14px;margin-bottom:10px}""",
        demo=('<div class="box1">没有 padding、没有 border</div>'
              '<div class="box2">有 padding：文字离边框远了</div>'
              '<div class="box3">再加 4px 边框</div>'))),

    # 插在 box-sizing 提示卡之后
    ("五段式语法",
     pv(2, "box-sizing：默认 vs border-box",
        """/* 两个都是 width:180px + padding:20px + border:4px */
.a{box-sizing:content-box;width:180px;padding:20px;border:4px solid #c0392b;
   background:#fdeceb;font-size:13px}
.b{box-sizing:border-box;width:180px;padding:20px;border:4px solid #17864a;
   background:#e7f6ee;font-size:13px}
.a,.b{margin-bottom:10px;border-radius:6px}""",
        demo=('<div class="a">content-box（默认）：实际占 180+40+8 = <b>228px</b>，比标称宽</div>'
              '<div class="b">border-box：整体就是 <b>180px</b>，padding 和边框都算在里面</div>'))),

    # Display 三种值
    ("对比",
     pv(3, "block / inline / inline-block",
        """.blk{display:block;width:150px;height:38px;background:#e8f1fe;
  border:1px solid #1f6feb;margin:4px 0;line-height:38px;text-align:center;font-size:13px}
.inl{display:inline;width:150px;height:38px;background:#fdeceb;
  border:1px solid #c0392b;font-size:13px}
.ib{display:inline-block;width:150px;height:38px;background:#e7f6ee;
  border:1px solid #17864a;margin:4px;line-height:38px;text-align:center;font-size:13px}""",
        demo=('<div class="blk">block：独占一行，宽高有效</div>'
              '<span class="inl">inline：宽高被忽略，只跟着文字走</span>'
              '<span class="ib">inline-block</span>'
              '<span class="ib">可以并排</span>'
              '<span class="ib">又能设宽高</span>'))),

    # border 边框
    ("三段式语法",
     pv(4, "border 的样式与分方向",
        """.bd{padding:9px 13px;margin:5px 0;border-radius:6px;font-size:14px}
.bd1{border:1px solid #8b95a5}
.bd2{border:2px dashed #1f6feb}
.bd3{border:2px dotted #c0392b}
.bd4{border:none;border-bottom:2px solid #1a1f28}
.bd5{border:1px solid #e3e8f0;border-left:5px solid #1f6feb}
.bd6{border:none;border-top:3px solid #17864a;border-bottom:3px solid #17864a}""",
        demo=('<div class="bd bd1">1px solid</div>'
              '<div class="bd bd2">2px dashed 虚线</div>'
              '<div class="bd bd3">2px dotted 点线</div>'
              '<div class="bd bd4">只有下边框</div>'
              '<div class="bd bd5">左边框加粗 —— 提示框就是这么做的</div>'
              '<div class="bd bd6">只要上下边框</div>'))),

    # border-radius
    ("<h4>border-radius 圆角",
     pv(5, "border-radius 圆角的各种写法",
        """.rr{display:inline-block;width:110px;height:74px;margin:6px 10px 6px 0;
  background:#e8f1fe;border:1px solid #1f6feb;text-align:center;
  line-height:74px;font-size:12px;font-family:Consolas,monospace}
.r1{border-radius:0}
.r2{border-radius:8px}
.r3{border-radius:8px 8px 0 0}
.r4{border-radius:50%}
.r5{border-radius:999px;width:150px}""",
        demo=('<span class="rr r1">0</span>'
              '<span class="rr r2">8px</span>'
              '<span class="rr r3">8px 8px 0 0</span>'
              '<span class="rr r4">50%</span>'
              '<span class="rr r5">999px</span>'))),

    # box-shadow
    ("五段式语法",
     pv(6, "box-shadow 的五种典型用法",
        """.sh{display:inline-block;width:120px;height:70px;margin:10px 14px 16px 0;
  background:#fff;border-radius:8px;text-align:center;line-height:70px;
  font-size:11.5px;font-family:Consolas,monospace;border:1px solid #e3e8f0}
.s1{box-shadow:0 1px 3px rgba(0,0,0,.12)}
.s2{box-shadow:0 8px 24px rgba(0,0,0,.13)}
.s3{box-shadow:0 0 0 3px rgba(31,111,235,.3)}
.s4{box-shadow:inset 0 2px 4px rgba(0,0,0,.15);border:none}
.s5{box-shadow:3px 3px 0 #1a1f28;border:none}""",
        demo=('<span class="sh s1">0 1px 3px<br>轻微浮起</span>'
              '<span class="sh s2">0 8px 24px<br>悬停抬起</span>'
              '<span class="sh s3">0 0 0 3px<br>聚焦光圈</span>'
              '<span class="sh s4">inset<br>内阴影</span>'
              '<span class="sh s5">3px 3px 0<br>硬阴影</span>'))),

    # max-width 三件套
    ("限制高度并滚动",
     pv(7, "width 写死 vs max-width 上限",
        """.w1{width:420px;background:#fdeceb;border:1px solid #c0392b;
  padding:8px 12px;border-radius:6px;font-size:13px;margin-bottom:8px}
.w2{max-width:420px;background:#e7f6ee;border:1px solid #17864a;
  padding:8px 12px;border-radius:6px;font-size:13px;margin-bottom:8px}
.w3{max-width:420px;margin:0 auto;background:#e8f1fe;border:1px solid #1f6feb;
  padding:8px 12px;border-radius:6px;font-size:13px}""",
        demo=('<div class="w1">width:420px —— 容器窄了就溢出</div>'
              '<div class="w2">max-width:420px —— 窄了自动缩，不溢出</div>'
              '<div class="w3">max-width + margin:0 auto —— 宽屏时居中</div>'
              '<p style="font-size:12px;color:#8b95a5;margin-top:8px">'
              '把浏览器窗口拉窄，看第一个框怎么溢出的。</p>'))),
]

# ---------------- FE-06 Writing Mode ----------------
DEMOS["fe-06.html"] = [
    ("三个值",
     pv(1, "三个 writing-mode 值对比",
        """.wm{display:inline-block;vertical-align:top;margin:0 14px 12px 0;
  border:1px solid #ccd5e3;border-radius:8px;background:#fafbfd;
  font-size:17px;padding:8px;line-height:1.7}
.wm1{writing-mode:horizontal-tb;width:150px;height:110px}
.wm2{writing-mode:vertical-rl;height:150px;width:90px}
.wm3{writing-mode:vertical-lr;height:150px;width:90px}""",
        demo=('<div class="wm wm1">horizontal-tb 横排，行往下</div>'
              '<div class="wm wm2">vertical-rl 竖排，列往左</div>'
              '<div class="wm wm3">vertical-lr 竖排，列往右</div>'))),

    ("长串不断行的问题",
     pv(2, "长串撑破容器 vs 允许断行",
        """.wb{border:1px solid #ccd5e3;border-radius:6px;padding:9px 12px;
  margin:6px 0;font-family:Consolas,monospace;font-size:12.5px;background:#fafbfd}
.wb1{white-space:nowrap;overflow:auto}
.wb2{overflow-wrap:anywhere;word-break:break-word}
.wb3{word-break:break-all}""",
        demo=('<div class="wb wb1">nowrap：不换行，只能横向滚 → D:\\Path\\To\\project\\build\\UmeMath.lib</div>'
              '<div class="wb wb2">overflow-wrap:anywhere → D:\\Path\\To\\project\\build\\UmeMath.lib</div>'
              '<div class="wb wb3">word-break:break-all → D:\\Path\\To\\project\\build\\UmeMath.lib</div>'))),

    ("五个值",
     pv(3, "overflow 五个值",
        """.ov{display:inline-block;vertical-align:top;width:150px;height:76px;
  margin:0 10px 10px 0;padding:7px;border:1px solid #1f6feb;border-radius:6px;
  background:#f2f6fb;font-size:12.5px;line-height:1.6}
.o1{overflow:visible}
.o2{overflow:hidden}
.o3{overflow:auto}
.o4{overflow:scroll}""",
        demo=('<div class="ov o1">visible：内容直接画到框外，盖住下面的东西（这一段很长很长很长很长）</div>'
              '<div class="ov o2">hidden：超出部分被裁掉（这一段很长很长很长很长）</div>'
              '<div class="ov o3">auto：需要时才出现滚动条（这一段很长很长很长很长）</div>'
              '<div class="ov o4">scroll：永远显示滚动条（这一段很长很长很长很长）</div>'))),

    ("精细控制",
     pv(4, "自定义滚动条",
        """/* WebKit 浏览器（Chrome / Edge / Safari） */
.sc1{max-height:88px;overflow-y:auto;border:1px solid #ccd5e3;
  border-radius:8px;padding:8px 12px;margin:6px 0;font-size:13px}
.sc1::-webkit-scrollbar{width:11px}
.sc1::-webkit-scrollbar-track{background:#f7f9fc;border-radius:999px}
.sc1::-webkit-scrollbar-thumb{background:#ccd5e3;border-radius:999px}
.sc1::-webkit-scrollbar-thumb:hover{background:#8b95a5}
.sc1::-webkit-scrollbar-button{display:none}
/* 标准属性（Firefox） */
.sc2{scrollbar-width:thin;scrollbar-color:#1f6feb #e8f1fe;max-height:88px;
  overflow-y:auto;border:1px solid #ccd5e3;border-radius:8px;padding:8px 12px;
  margin:6px 0;font-size:13px}""",
        demo=('<div class="sc1">圆角细滚动条（WebKit）<br>' +
              '<br>'.join('第 %d 行内容，往下滚试试' % i for i in range(1, 9)) +
              '</div>'
              '<div class="sc2">标准的 thin + 配色（Firefox 生效）<br>' +
              '<br>'.join('第 %d 行内容' % i for i in range(1, 9)) +
              '</div>'))),
]

# ---------------- FE-07 transition ----------------
DEMOS["fe-07.html"] = [
    ("四类常用反馈",
     pv(1, "hover 的四类反馈 —— 鼠标逐个移上去",
        """.hd{display:inline-block;width:122px;height:76px;margin:8px 12px 12px 0;
  background:#fff;border:1px solid #ccd5e3;border-radius:10px;text-align:center;
  line-height:76px;font-size:12px;font-family:Consolas,monospace;
  cursor:pointer;transition:background .18s,border-color .18s,
  box-shadow .18s,transform .18s,color .18s}
.h1:hover{background:#f7f9fc}
.h2:hover{color:#1f6feb}
.h3:hover{border-color:#1f6feb}
.h4:hover{box-shadow:0 8px 24px rgba(0,0,0,.13);transform:translateY(-3px);
  border-color:#1f6feb}""",
        demo=('<span class="hd h1">换背景</span>'
              '<span class="hd h2">文字变色</span>'
              '<span class="hd h3">边框亮起</span>'
              '<span class="hd h4">抬起<br>（阴影+上移）</span>'))),

    ("四段式语法",
     pv(2, "不同时长的对比 —— 都是变背景色",
        """.tm{display:inline-block;width:104px;height:60px;margin:8px 12px 12px 0;
  background:#1f6feb;color:#fff;border-radius:9px;text-align:center;
  line-height:60px;font-size:12px;font-family:Consolas,monospace;cursor:pointer}
.t0{transition:none}
.t1{transition:background .1s}
.t2{transition:background .3s}
.t3{transition:background 1s}
.tm:hover{background:#c0392b}""",
        demo=('<span class="tm t0">无过渡</span>'
              '<span class="tm t1">0.1s</span>'
              '<span class="tm t2">0.3s</span>'
              '<span class="tm t3">1s（太慢）</span>'))),

    ("❌ 加在 hover 里",
     pv(3, "transition 写错位置 vs 写对位置",
        """/* ❌ 写在 :hover 里 —— 移出时瞬间跳回 */
.bad{background:#1f6feb;color:#fff;padding:9px 18px;border-radius:8px;
  display:inline-block;margin:8px 12px 12px 0;cursor:pointer;font-size:13px}
.bad:hover{background:#c0392b;transition:background .4s}

/* ✅ 写在基础规则里 —— 进出都平滑 */
.good{background:#1f6feb;color:#fff;padding:9px 18px;border-radius:8px;
  display:inline-block;margin:8px 12px 12px 0;cursor:pointer;font-size:13px;
  transition:background .4s}
.good:hover{background:#17864a}""",
        demo=('<span class="bad">移入平滑，移出跳回</span>'
              '<span class="good">进出都平滑</span>'
              '<p style="font-size:12px;color:#8b95a5;margin-top:6px">'
              '两个都慢慢移入再移开，对比移出时的差别。</p>'))),

    ("<h4>① 按钮：变色",
     pv(4, "按钮：变色 + 按下缩一点",
        """.btn1{background:#1f6feb;color:#fff;padding:9px 20px;border-radius:8px;
  display:inline-block;cursor:pointer;font-size:14px;user-select:none;
  transition:background .15s,transform .1s}
.btn1:hover{background:#1558b8}
.btn1:active{transform:scale(.96)}""",
        demo=('<span class="btn1">点我试试</span>'
              '<p style="font-size:12px;color:#8b95a5;margin-top:8px">'
              '悬停变深，按下缩到 96%。这两个反馈加起来就很「跟手」。</p>'))),

    ("<h4>③ 链接：下划线滑入",
     pv(5, "链接：下划线平滑出现（不抖动）",
        """.lk{color:#4b5563;text-decoration:none;border-bottom:1px solid transparent;
  padding-bottom:1px;margin-right:18px;cursor:pointer;
  transition:border-color .15s,color .15s}
.lk:hover{color:#1f6feb;border-bottom-color:#1f6feb}""",
        demo=('<a class="lk">首页</a><a class="lk">教程</a><a class="lk">关于</a>'
              '<p style="font-size:12px;color:#8b95a5;margin-top:8px">'
              '先留一条 transparent 的边框，悬停时只改颜色 —— '
              '不会因为突然多出一条边框而抖动。</p>'))),

    ("<h4>④ 输入框：聚焦光圈",
     pv(6, "输入框：聚焦光圈",
        """.fld{border:1px solid #ccd5e3;border-radius:8px;padding:9px 13px;
  outline:none;font:inherit;font-size:14px;width:min(100%,280px);
  transition:border-color .15s,box-shadow .15s}
.fld:focus{border-color:#1f6feb;box-shadow:0 0 0 3px rgba(31,111,235,.25)}""",
        demo=('<input class="fld" placeholder="点我获得焦点">'
              '<p style="font-size:12px;color:#8b95a5;margin-top:8px">'
              'box-shadow 前三个数是「水平 垂直 模糊」，这里是 0 0 0 —— '
              '第四个参数 3px 是扩散，才形成光圈。</p>'))),

    ("无障碍考量",
     pv(7, "缓动函数对比",
        """.ez{display:inline-block;width:120px;height:46px;margin:8px 12px 12px 0;
  background:#6b46c1;color:#fff;border-radius:9px;text-align:center;
  line-height:46px;font-size:12px;font-family:Consolas,monospace;cursor:pointer}
.e1{transition:transform .4s linear}
.e2{transition:transform .4s ease}
.e3{transition:transform .4s ease-out}
.ez:hover{transform:translateX(56px)}""",
        demo=('<span class="ez e1">linear</span>'
              '<span class="ez e2">ease</span>'
              '<span class="ez e3">ease-out</span>'
              '<p style="font-size:12px;color:#8b95a5;margin-top:8px">'
              '鼠标移上去，三个方块右移的过程不一样：'
              'linear 匀速（机械），ease-out 先快后慢（最自然）。</p>'))),
]


def _already_pv(html, pos):
    """pos 所在的那个块的**收尾位置之后**紧跟着 pv-wrap 吗？

    必须跳过整个 div —— 示例内容里有大段 HTML，
    只看固定窗口（比如 400 字符）会误判，导致重复插入。
    """
    i = html.find(">", pos)
    if i < 0 or not html[max(0, pos - 6):i].lstrip().startswith("<div"):
        return False
    depth = 0
    k = pos
    while k < len(html):
        m = re.compile(r'<(/?)div(\s[^>]*)?>', re.I).search(html, k)
        if not m:
            return False
        if m.group(1):
            depth -= 1
            if depth == 0:
                return html[m.end():m.end() + 200].lstrip().startswith('<div class="pv-wrap"')
        else:
            depth += 1
        k = m.end()
    return False


def insert_after_block(html, title, block):
    """按代码块标题定位，把示例插在**整个 code-wrap 之后**。

    要点：
      1. 只在 <main> 里找 —— 目录里也有 #s2 这类锚点，会误命中，
         把示例插进 <nav>，撑坏 href，整页 JS 报错。
      2. 找的是 <span class="name">标题</span>，不是裸文本。
      3. 标题可能重复（「对比」「五段式语法」）—— 逐个试，
         插在第一个**还没插过**的那个后面，然后立刻返回。
    """
    start = html.find("<main")
    if start < 0:
        return html, "没有 main"
    needle = '<span class="name">%s</span>' % title
    pos = start
    while True:
        i = html.find(needle, pos)
        if i < 0:
            return html, "找不到标题"
        close = html.find("</pre></div>", i)
        if close < 0:
            return html, "找不到 code-wrap 结尾"
        end = close + len("</pre></div>")
        if not _already_ok(html, end):
            return html[:end] + "\n" + block + html[end:], None
        pos = end


def _already_ok(html, after_pos):
    """这个位置之后是否已经是示例展示了。"""
    return html[after_pos:after_pos + 200].lstrip().startswith('<div class="pv-wrap"')


def insert_before_heading(html, heading_text, block):
    """按小标题定位，把示例插在它之前（同样幂等）。"""
    start = html.find("<main")
    if start < 0:
        return html, "没有 main"
    i = html.find(heading_text, start)
    if i < 0:
        return html, "找不到小标题"
    before = html[max(start, i - 200):i].rstrip()
    if before.endswith("</div>") and 'class="pv-wrap"' in html[max(start, i - 900):i]:
        # 小标题前面最近一段里已经有示例 → 视为插过
        seg = html[max(start, i - 900):i]
        if seg.rfind('class="pv-wrap"') > seg.rfind("</div>", 0, seg.rfind("</div>")):
            return html, "已插入过"
    return html[:i] + block + "\n" + html[i:], None


def main():
    total = 0
    for fn, items in DEMOS.items():
        p = os.path.join(TUT, fn)
        t = io.open(p, encoding="utf-8").read()
        ok = 0
        for item in items:
            anchor, block = item[0], item[-1]
            if anchor.startswith("#"):
                err = "锚点仍是 id，未替换"
                t2 = t
            elif anchor.startswith("<h"):
                t2, err = insert_before_heading(t, anchor, block)
            else:
                t2, err = insert_after_block(t, anchor, block)
            if err:
                print("  !! %s  %s  (%s)" % (fn, err, anchor[:50]))
            else:
                t = t2
                ok += 1
        io.open(p, "w", encoding="utf-8", newline="").write(t)
        print("  %-14s 插入 %d/%d 个示例展示" % (fn, ok, len(items)))
        total += ok
    print("")
    print("  合计插入 %d 个" % total)


if __name__ == "__main__":
    main()
