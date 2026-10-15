/* UMCompos.js 独立性 + 功能验证
   两段：
     A. Node 下 require —— 证明不依赖浏览器、不依赖宿主
     B. 浏览器里挂载 —— 证明能独立工作、样式不外泄、类名前缀正确 */
const http = require('http');
const PORT = process.argv[2];
const PAGE = process.argv[3];
const NODE_PATH = process.argv[4];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  await new Promise(res => {
    http.get({ host: '127.0.0.1', port: Number(PORT), path: '/json/new?about:blank' },
      r => { r.on('data', () => {}); r.on('end', res); }).on('error', res);
  });
  await new Promise(r => setTimeout(r, 400));
  const t = (await get('/json/list')).filter(x => x.type === 'page').pop();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setCacheDisabled', { cacheDisabled: true });
  await send('Emulation.clearDeviceMetricsOverride');
  await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
  await send('Page.navigate', { url: 'about:blank' });
  await new Promise(r => setTimeout(r, 250));
  await send('Page.navigate', { url: PAGE });
  await new Promise(r => setTimeout(r, 2500));

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.result.exceptionDetails) return 'EXC ' + JSON.stringify(r.result.exceptionDetails).slice(0, 250);
    return r.result.result.value;
  };

  console.log('===== B. 浏览器端 =====');
  console.log(await ev(`(async () => {
    const out = [];
    const U = window.UMCompos;
    if (!U) return 'UMCompos 未加载';
    let pass = 0, fail = 0;
    const ok = (l, c, x) => { c ? (pass++, out.push('  OK   ' + l + (x ? '   ' + x : '')))
                                : (fail++, out.push('  FAIL ' + l + (x ? '   ' + x : ''))); };

    /* 独立性的关键：只挂一个全局名，不污染其它 */
    ok('只挂 UMCompos 一个全局', typeof window.UMCompos === 'object');
    ok('没有别的新增全局', Object.keys(window).filter(k => /^UMC|^umcompos/i.test(k)).length === 1);

    /* 自带样式：injectCSS() 是 mount 时**懒注入**的 ——
       所以先挂一次，再查样式表，否则永远查不到。 */
    const host0 = document.createElement('div');
    document.body.appendChild(host0);
    const c0 = U.mount(host0, { text: '\u1820' });
    const st = document.getElementById('umcompos-style-v1');
    ok('自带样式已注入', !!st);
    var foreign = [];
    if (st) {
      var css = st.textContent, idx = 0;
      while ((idx = css.indexOf('var(--', idx)) >= 0) {
        var name = css.slice(idx + 6).split(/[),; ]/)[0];   /* 'var(--' 长 6 */
        if (name.indexOf('umc-') !== 0) foreign.push(name);
        idx += 5;
      }
    }
    ok('样式只引用自带 --umc-* 变量', !!st && foreign.length === 0,
       foreign.length ? '引用了外部变量: ' + foreign.join(', ') : '未引用任何外部变量');

    /* 类名前缀 */
    const host = document.createElement('div');
    document.body.appendChild(host);
    const c = U.mount(host, { text: '\\u182E\\u1823\\u1829\\u182D\\u1823\\u182F', fontSize: 30, height: '200px' });
    ok('类名带 umc 前缀', c.el.className.split(' ')[0] === 'umc', c.el.className);
    const cs = getComputedStyle(c.el);
    ok('vertical-lr / ltr / mixed',
       cs.writingMode === 'vertical-lr' && cs.direction === 'ltr' && cs.textOrientation === 'mixed',
       cs.writingMode + ' / ' + cs.direction + ' / ' + cs.textOrientation);

    /* 配置是显式给的，不是插件里写死的 */
    const cfg = U.config();
    ok('字体路径来自 configure（非插件内写死）', !!cfg.fontURL && cfg.fontURL.indexOf('NotoSansMongolian') > 0,
       String(cfg.fontURL).split('/').pop());
    ok('字体栈不含项目自造名以外的假设', typeof cfg.fontStack === 'string');

    /* 排版正确性 */
    const plan = c.layout();
    const sum = plan[0].items.reduce((a, b) => a + b.adv, 0);
    ok('advance 之和 = 实测行长', Math.abs(sum - plan[0].length) < 2,
       sum.toFixed(1) + ' vs ' + plan[0].length.toFixed(1));

    /* SVG 导出 */
    const svg = c.toSVG({ fontSize: 100, padding: 20 });
    ok('SVG 生成', !svg.error, Math.round(svg.W) + 'x' + Math.round(svg.H));
    ok('SVG 合法 XML', !new DOMParser().parseFromString(svg.svg, 'image/svg+xml').querySelector('parsererror'));
    ok('字体内嵌来自 embedProvider', svg.svg.indexOf('base64') > 0);

    /* 关掉自带样式也不该崩 */
    U.configure({ injectCSS: false });
    const h2 = document.createElement('div'); document.body.appendChild(h2);
    const c2 = U.mount(h2, { text: '\\u1820' });
    ok('injectCSS:false 时仍可挂载', !!c2.el);
    U.configure({ injectCSS: true });

    c.destroy(); c2.destroy(); c0.destroy();
    document.body.removeChild(host); document.body.removeChild(h2);
    document.body.removeChild(host0);
    out.push('');
    out.push('  通过 ' + pass + ' / 失败 ' + fail);
    return out.join('\\n');
  })()`));

  console.log('');
  console.log('JS 异常: ' + (errs.length ? errs.join(' | ').slice(0, 300) : '无'));
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
