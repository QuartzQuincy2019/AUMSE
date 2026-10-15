# -*- coding: utf-8 -*-
"""教程文档完整性检查。

升级点（每一条都是踩过的坑）：
  * 图片：原来只查 <link href>，`<img src>` 挂了查不出来 —— 现在一起查。
  * 预块：`<pre>` 里的内容和 &lt;…&gt; 转义文本都要遮罩掉，
    否则代码示例里写的 id="s3"、href="#top" 会被误报成重复 id / 断链。
  * 前端系列：正文装在 `<script>window.__FE_PAGE__ = "…"</script>` 里，
    里面的 `<pre>` 是 JS 字符串内容，本来就没有配对的 `</pre>`。
  * 注入的 <style>：后端每篇会注入一小段样式（返回按钮 + 小目录），
    这是**有意为之**，不算「没有分离 CSS」。用标记识别。
  * **重复计数**：前端曾经把 <h1> / .sub-title 同时留在数据里、
    又由渲染器新建一份，页面上各出现两次。静态 HTML 里查不出来
    （因为数据是转义的字符串），必须在**渲染后**的 DOM 里查 ——
    见 tools/check_dup_render.js。
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TUT = r"E:\QKMansion\CSX10\w\UME\SharingGroup\tutorials"

MASK = re.compile(r'(?s)<pre>.*?</pre>|&lt;[^&]{0,140}?&gt;|<script\b.*?</script>')


def mask(raw):
    out = list(raw)
    for m in MASK.finditer(raw):
        for i in range(m.start(), m.end()):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def main():
    files = sorted(f for f in os.listdir(TUT) if f.endswith(".html"))
    bad = 0
    for f in files:
        raw = io.open(os.path.join(TUT, f), encoding="utf-8").read()
        t = mask(raw)
        data_driven = "__FE_PAGE__" in raw

        toc = re.findall(r'<a href="#([^"]+)"', t)
        ids = re.findall(r'id="([^"]*)"', t)
        miss = [x for x in toc if x not in ids]
        dup = sorted({x for x in ids if ids.count(x) > 1})

        links = re.findall(r'<link[^>]*href="(assets/[^"]+)"', t)
        imgs = re.findall(r'<img[^>]*src="([^"]+)"', t)
        refs = [x for x in (links + imgs)
                if not re.match(r'^(https?:|data:|//|#)', x)]
        missL = [x for x in refs
                 if not os.path.exists(os.path.join(TUT, x.replace("/", os.sep)))]

        style_blocks = re.findall(r'(?s)<style>(.*?)</style>', raw)
        inline = [s for s in style_blocks
                  if "NAV-AUTO" not in s and ".home-fab{" not in s]

        probs = []
        if miss:
            probs.append("断链%s" % miss[:4])
        if dup:
            probs.append("重复id%s" % dup[:4])
        if missL:
            probs.append("资源缺失%s" % missL)
        if inline:
            probs.append("仍有内嵌 style %d 个" % len(inline))
        if not data_driven:
            op, cl = len(re.findall(r'<pre[\s>]', raw)), len(re.findall(r'</pre>', raw))
            if op != cl:
                probs.append("pre 不成对 %d/%d" % (op, cl))
        # 前端的数据里不能再出现渲染器会自己生成的元素
        if data_driven:
            m = re.search(r'__FE_PAGE__\s*=\s*(\{.*?\});', raw, re.S)
            if m:
                data = m.group(1)
                for bad_tag in ('<h1', 'class=\\"sub-title\\"', 'series-nav'):
                    if bad_tag in data:
                        probs.append("数据里混入 %s（会重复渲染）" % bad_tag)

        if probs:
            bad += 1
            print("  !! %-34s %s" % (f, "; ".join(probs)))
        else:
            extra = []
            if data_driven:
                extra.append("数据驱动")
            if imgs:
                extra.append("图 %d" % len(imgs))
            pv = raw.count('class="pv-wrap"')
            if pv:
                extra.append("示例 %d" % pv)
            marks = raw.count('class="key-mark"')
            if marks:
                extra.append("★ %d" % marks)
            if "series-nav" in raw:
                extra.append("系列目录")
            if "home-fab" in raw:
                extra.append("返回home")
            print("  OK %-34s 目录%2d 链接%d %s"
                  % (f, len(toc), len(links), "  ".join(extra)))

    print("")
    print("  共 %d 篇，问题 %d 篇  %s"
          % (len(files), bad, "✅ 全部通过" if bad == 0 else ""))


if __name__ == "__main__":
    main()
