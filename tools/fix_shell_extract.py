# -*- coding: utf-8 -*-
"""修 make_fe_shells.py 的抽取漏洞。

现象：前端 8 篇页面上 `<h1>` 与 `.sub-title` **各渲染了两次**。

根因：渲染器（fe-data.js）会用 P.title / P.num **新建** h1 与 .sub-title，
但抽取正文时没把原页面里的 h1 和 .sub-title 去掉 ——
于是「生成的一份 + 数据里的一份」叠在一起。
（子项目导航条 `.series-nav` 反而只有一份，因为它的类名和旧的
 `.page-nav` 不同，旧的那份已经在抽取时被删掉了。）

修法：抽取时把 h1、.sub-title、旧 .page-nav、footer、注入块一并剥掉，
并加一条断言式校验 —— 正文里若还残留 h1 / series-nav / home-fab 就直接报错，
不让这种「重复渲染」再悄悄溜过去。
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\make_fe_shells.py"
t = io.open(P, encoding="utf-8").read()

start = t.find("def extract(fn):")
end = t.find("def main():")
assert start > 0 and end > start, (start, end)

NEW = '''def extract(fn):
    """从生成好的页面里取出**正文**与标题。

    这里必须把「渲染器会自己生成的东西」全部剥掉，否则会重复渲染：
      * <h1> 与 .sub-title —— 渲染器用 P.title / P.num 新建，数据里不能再有
        （曾经漏掉这两步，结果页面上 h1 与 .sub-title 各出现两次）
      * 旧的 .page-nav / .series-nav / footer / 注入块 —— 渲染器会重新生成
    """
    t = io.open(os.path.join(TUT, fn), encoding="utf-8").read()
    m = re.search(r'(?s)<main[^>]*>(.*?)</main>', t)
    body = m.group(1) if m else ""

    # 一级标题与副标题：渲染器会生成，这里去掉
    body = re.sub(r'(?s)<h1\\b[^>]*>.*?</h1>', "", body, count=1)
    body = re.sub(r'(?s)<p class="sub-title">.*?</p>', "", body, count=1)

    # 页内导航 / 页脚 / 注入块：渲染器会生成
    body = re.sub(r'(?s)<div class="page-nav">.*?</div>\\s*', "", body)
    body = re.sub(r'(?s)<div class="series-nav">.*?</div>\\s*', "", body)
    body = re.sub(r'(?s)<footer>.*?</footer>', "", body)
    body = re.sub(r'(?s)<!-- NAV-AUTO -->.*?<!-- /NAV-AUTO -->', "", body)
    body = body.strip()

    # 标题：优先用 <title> 里「前端 · xxx」的 xxx，其次正文 h1
    tm = re.search(r'<title>\\s*前端\\s*·\\s*(.*?)\\s*</title>', t)
    if tm:
        title = tm.group(1).strip()
    else:
        hm = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
        title = re.sub(r'<[^>]+>', '', hm.group(1)).replace("★", "").strip() if hm else fn

    # 校验：这些标签不该出现在正文数据里，否则一定会重复渲染
    for bad in ('<h1', 'class="sub-title"', 'class="series-nav"',
                'class="page-nav"', 'home-fab'):
        if bad in body:
            raise SystemExit("  !! %s 的正文里仍有 %s —— 会重复渲染" % (fn, bad))
    return title, body


'''

t = t[:start] + NEW + t[end:]
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  ✓ make_fe_shells.py：抽取时剥掉 h1 / .sub-title，并加了残留校验")
