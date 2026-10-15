# -*- coding: utf-8 -*-
"""把 build_fe.py 里的「示例展示」注入脚本换成支持多行/嵌套的版本。

旧版找**第一个** '}' 就结束，所以示例 CSS 一旦排成三行式
（或者含 @media 嵌套块）就会被截断 —— 必须先数花括号配平。
"""
import io
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

P = r"E:\QKMansion\CSX10\w\UME\tools\build_fe.py"
t = io.open(P, encoding="utf-8").read()

start = t.find("/* ================= 示例展示 =================")
end = t.find('"""', t.find("})();", start))
assert start > 0 and end > start, (start, end)
end += 3          # 连 """ 一起换掉

NEW = r'''/* ================= 示例展示 =================
   把代码块里的内容真的渲染出来。
   关键：CSS 示例里的 .card / div 之类选择器不能作用到文档本身，
   所以给每条规则的选择器加上 [data-pv="N"] 前缀，只在那个示例框内生效。
   前缀不改变任何偏移量，示例内部的优先级关系与真实页面一致。

   注意：必须**数花括号配平**，不能找第一个 '}' ——
   示例 CSS 已经排成三行式，而且可能有 @media 这类嵌套块。
   字符串里的花括号也要跳过，避免误判。 */
(function(){
  function scoped(css, scope){
    var out = '', i = 0, n = css.length;
    while (i < n) {
      if (css.substr(i, 2) === '/*') {            /* 跳过注释 */
        var ce = css.indexOf('*/', i + 2);
        i = ce < 0 ? n : ce + 2;
        continue;
      }
      var b = css.indexOf('{', i);
      if (b < 0) break;
      var sel = css.slice(i, b).replace(/\/\*[\s\S]*?\*\//g, '').trim();
      var depth = 1, k = b + 1, q = null;         /* 数配平，跳过字符串 */
      while (k < n && depth > 0) {
        var ch = css[k];
        if (q) { if (ch === q && css.charAt(k - 1) !== '\\') q = null; }
        else if (ch === '"' || ch === "'") q = ch;
        else if (ch === '{') depth++;
        else if (ch === '}') depth--;
        k++;
      }
      var body = css.slice(b + 1, k - 1);
      if (sel && sel.charAt(0) !== '@') {
        sel = sel.split(',').map(function(x){
          x = x.trim();
          return x ? scope + ' ' + x : x;
        }).join(', ');
      }
      out += sel + '{' + body + '}';
      i = k;
    }
    return out;
  }

  document.querySelectorAll('.pv-wrap[data-pv]').forEach(function(w){
    var scope = '[data-pv="' + w.dataset.pv + '"]';
    var body  = w.querySelector('.pv-body');
    var code  = w.querySelector('pre');
    if (!body || !code) return;
    var text = code.textContent;
    var kind = w.dataset.pvKind || 'html';

    if (kind === 'css') {
      var st = document.createElement('style');
      st.textContent = scoped(text, scope);
      w.appendChild(st);
    } else {
      body.innerHTML = text;
    }
  });
})();
"""'''

t = t[:start] + NEW + t[end:]
io.open(P, "w", encoding="utf-8", newline="").write(t)
print("  已替换示例展示注入脚本（%d 字符）" % len(NEW))
