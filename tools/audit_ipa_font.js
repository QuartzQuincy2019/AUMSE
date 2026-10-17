/* 逐元素审计：页面里凡是含音标字符的元素，实际渲染用的是哪套字体。

为什么不用 getComputedStyle
    它回显声明值，不是真正取用的字体。
为什么不用 getPlatformFontsForNode
    它只给「这个元素用到了哪些字体 + 各自字形数」，分不清某个字符归谁。
做法
    量宽度。同一个音标字符在 DejaVu Serif 与 Consolas 下的宽度不同，
    用 Range 量出元素里那个字符的实际宽度，与两种候选字体在同样字号/字重下
    的宽度比对，谁近就是谁。

用法：node audit_ipa_font.js <端口> <URL>
*/
const http = require('http');

const PORT = parseInt(process.argv[2] || '9222', 10);
const URL = process.argv[3];
if (!URL) { console.error('用法：node audit_ipa_font.js <端口> <URL>'); process.exit(2); }

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: PORT, path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

const EVAL = String.raw`(function(){
  var IPA = /[\u0250-\u02ff\u0300-\u036f\u1d00-\u1dbf\ua700-\ua71f]/;

  function w(ch, family, size, weight){
    var s = document.createElement('span');
    s.style.cssText = 'position:absolute;left:-9999px;top:0;white-space:pre;'
      + 'font-family:' + family + ';font-size:' + size + ';font-weight:' + weight;
    s.textContent = ch;
    document.body.appendChild(s);
    var v = s.getBoundingClientRect().width;
    s.remove();
    return v;
  }

  function charWidth(el, node, idx){
    var r = document.createRange();
    r.setStart(node, idx);
    r.setEnd(node, idx + 1);
    var rects = r.getClientRects();
    return rects.length ? rects[0].width : 0;
  }

  var suspects = [];
  var els = document.querySelectorAll('main *');
  for (var i = 0; i < els.length; i++){
    var el = els[i];
    // 只看直接文字子节点，避免父子重复统计
    for (var n = 0; n < el.childNodes.length; n++){
      var node = el.childNodes[n];
      if (node.nodeType !== 3) continue;
      var txt = node.nodeValue;
      var m = IPA.exec(txt);
      if (!m) continue;
      var cs = getComputedStyle(el);
      var size = cs.fontSize, weight = cs.fontWeight;
      var idx = m.index;
      var ch = txt[idx];
      // 组合符号（0300–036F）单量没有意义，跳过
      if (ch.charCodeAt(0) >= 0x300 && ch.charCodeAt(0) <= 0x36f) {
        if (idx + 1 < txt.length) { ch = txt[idx + 1]; idx = idx + 1; } else continue;
      }
      var actual = charWidth(el, node, idx);
      var dv = w(ch, '"DejaVu Serif"', size, weight);
      var co = w(ch, 'Consolas', size, weight);
      if (!dv || !co) continue;
      var dDv = Math.abs(actual - dv), dCo = Math.abs(actual - co);
      // 两种候选字体宽度几乎一样时，宽度法分不出来（如 ʔ），不判失败
      var ambiguous = Math.abs(dv - co) < Math.max(0.2, dv * 0.015);
      suspects.push({
        ch: ch,
        actual: +actual.toFixed(2),
        dejavu: +dv.toFixed(2),
        consolas: +co.toFixed(2),
        // 宽度分不出来时，看结构：在 .ipa 里（或 pre 的 unicode-range 兜底里）就算过
        verdict: ambiguous ? ((el.closest('.ipa') || el.closest('pre')) ? '不可区分(在 .ipa/pre 内)' : '不可区分(且不在 .ipa 里!)')
                 : (dDv < dCo ? 'DejaVu' : (dCo < dDv ? 'Consolas' : '平手')),
        tag: el.tagName.toLowerCase(),
        cls: (el.className || '').toString().slice(0, 28),
        text: txt.trim().slice(0, 34)
      });
    }
  }
  return suspects;
})()`;

(async () => {
  const t = (await get('/json/list')).filter(x => x.type === 'page')[0];
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); let cb = null;
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Page.loadEventFired' && cb) { const f = cb; cb = null; f(); }
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => {
    const i = ++id; pend.set(i, r);
    ws.send(JSON.stringify({ id: i, method: me, params: p }));
  });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  const p = new Promise(r => { cb = r; setTimeout(() => { if (cb) cb = null; }, 12000); });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 60));
  await send('Page.navigate', { url: URL });
  await p;
  await new Promise(r => setTimeout(r, 1500));

  const r = await send('Runtime.evaluate', { expression: EVAL, returnByValue: true });
  if (r.result.exceptionDetails) {
    console.error('EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 300));
    process.exit(1);
  }
  const rows = r.result.result.value || [];
  const bad = rows.filter(x => x.verdict !== 'DejaVu' && x.verdict.indexOf('不可区分(在') !== 0);
  const byFont = {};
  rows.forEach(x => { byFont[x.verdict] = (byFont[x.verdict] || 0) + 1; });

  console.log('  含音标的文字节点：' + rows.length + ' 个');
  console.log('  判定：' + Object.keys(byFont).map(k => k + '=' + byFont[k]).join('  '));
  if (bad.length) {
    console.log('');
    console.log('  ✗ 仍在用非 DejaVu 字体的 ' + bad.length + ' 处：');
    bad.slice(0, 25).forEach(x => {
      console.log('      ' + x.ch + '  <' + x.tag + ' class="' + x.cls + '">  '
        + '实测 ' + x.actual + '  DejaVu ' + x.dejavu + '  Consolas ' + x.consolas
        + '  「' + x.text + '」');
    });
    if (bad.length > 25) console.log('      …还有 ' + (bad.length - 25) + ' 处');
    process.exit(1);
  }
  console.log('');
  console.log('  全部命中 DejaVu Serif ✅（其中不可区分的用宽度法证不了，但都在 .ipa 里）');
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
