/* 移动端验证：多种手机/平板视口下检查是否横向溢出、字号是否可读、目录抽屉是否可用
   用法: node verify_mobile.js <port> <fileurl> <tag> [outdir] */
const fs = require('fs');
const http = require('http');
const [PORT, URL_, TAG, OUTDIR] = process.argv.slice(2);

const DEVICES = [
  { name: 'iPhone SE      ', w: 375, h: 667, dpr: 2 },
  { name: 'iPhone 14 Pro  ', w: 393, h: 852, dpr: 3 },
  { name: 'iPhone 14 Pro Max', w: 430, h: 932, dpr: 3 },
  { name: 'Pixel 7        ', w: 412, h: 915, dpr: 2.6 },
  { name: 'Galaxy S20 Ultra', w: 360, h: 800, dpr: 4 },
  { name: 'iPad mini      ', w: 744, h: 1133, dpr: 2 },
];

const get = p => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: Number(PORT), path: p }, r => {
    let d = ''; r.on('data', c => d += c); r.on('end', () => res(JSON.parse(d)));
  }).on('error', rej);
});

(async () => {
  const t = (await get('/json/list')).find(x => x.type === 'page');
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pend = new Map(); const errs = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); }
    if (m.method === 'Runtime.exceptionThrown')
      errs.push((m.params.exceptionDetails.exception || {}).description || m.params.exceptionDetails.text);
  };
  const send = (me, p = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method: me, params: p })); });
  await new Promise(r => ws.onopen = r);
  await send('Page.enable'); await send('Runtime.enable');
  await send('Network.enable'); await send('Network.setCacheDisabled', { cacheDisabled: true });

  const ev = async expr => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result.exceptionDetails) return 'EXC ' + ((r.result.exceptionDetails.exception || {}).description);
    return r.result.result.value;
  };

  console.log('设备              视口     横向溢出  正文溢出  代码字号  输出字号  目录按钮  抽屉  表格可滚  代码可滚');
  console.log('-'.repeat(112));

  for (const d of DEVICES) {
    await send('Emulation.setDeviceMetricsOverride', {
      width: d.w, height: d.h, deviceScaleFactor: d.dpr, mobile: true,
    });
    await send('Page.navigate', { url: 'about:blank' });
    await new Promise(r => setTimeout(r, 200));
    await send('Page.navigate', { url: URL_ });
    await new Promise(r => setTimeout(r, 1800));

    const res = await ev(`(()=>{
      const de = document.documentElement;
      const over = de.scrollWidth - de.clientWidth;
      /* 找出真正超出视口右边界的元素 */
      let worst = null, worstR = de.clientWidth;
      document.querySelectorAll('main *').forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width > 0 && r.right > worstR + 1) { worstR = r.right; worst = el; }
      });
      const cs = s => { const e = document.querySelector(s);
        return e ? getComputedStyle(e).fontSize : 'n/a'; };
      const tbl = document.querySelector('main table');
      const pre = document.querySelector('.code-wrap pre');
      const btn = document.getElementById('tocToggle');
      const toc = document.getElementById('toc');
      return JSON.stringify({
        over: Math.round(over),
        worstTag: worst ? (worst.tagName.toLowerCase() +
          (worst.className ? '.' + String(worst.className).split(' ')[0] : '')) : '-',
        worstRight: Math.round(worstR), vw: de.clientWidth,
        codeFs: cs('.code-wrap pre'), outFs: cs('.out-wrap pre'),
        btnShown: !!btn && getComputedStyle(btn).display !== 'none',
        tocHidden: getComputedStyle(toc).transform !== 'none',
        tblScroll: tbl ? tbl.scrollWidth > tbl.clientWidth : null,
        preScroll: !!(pre && pre.scrollWidth > pre.clientWidth),
      });
    })()`);

    let o;
    try { o = JSON.parse(res); } catch (e) { console.log(d.name + '  EXC ' + res); continue; }
    console.log(
      d.name.padEnd(18) +
      String(d.w + 'x' + d.h).padEnd(9) +
      String(o.over === 0 ? '无' : ('有 ' + o.over + 'px ' + o.worstTag)).padEnd(10) +
      String(o.over === 0 ? '-' : (o.worstRight + '>' + o.vw)).padEnd(10) +
      o.codeFs.padEnd(10) + o.outFs.padEnd(10) +
      String(o.btnShown ? '有' : '无').padEnd(10) +
      String(o.tocHidden ? '已收起' : '展开').padEnd(6) +
      String(o.tblScroll === null ? 'n/a' : (o.tblScroll ? '是' : '否')).padEnd(10) +
      (o.preScroll ? '是' : '否')
    );

    /* 抽屉开关测试 */
    if (o.btnShown) {
      await ev(`document.getElementById('tocToggle').click(); 1`);
      await new Promise(r => setTimeout(r, 420));
      const opened = await ev(`document.getElementById('toc').classList.contains('open')`);
      const shifted = await ev(`(()=>{const r=document.getElementById('toc').getBoundingClientRect();
        return Math.round(r.left);})()`);
      await ev(`document.getElementById('tocToggle').click(); 1`);
      await new Promise(r => setTimeout(r, 420));
      const closed = await ev(`!document.getElementById('toc').classList.contains('open')`);
      console.log(' '.repeat(18) + `抽屉：点开 ${opened ? 'OK' : 'FAIL'}（left=${shifted}）  再点收起 ${closed ? 'OK' : 'FAIL'}`);
    }
  }

  console.log('');
  console.log('JS 异常 : ' + (errs.length ? errs.join(' | ') : 'none'));

  /* 截图：iPhone 14 Pro 尺寸下拍若干张 */
  if (OUTDIR) {
    await send('Emulation.setDeviceMetricsOverride', { width: 393, height: 852, deviceScaleFactor: 2, mobile: true });
    await send('Page.navigate', { url: URL_ });
    await new Promise(r => setTimeout(r, 2000));
    fs.mkdirSync(OUTDIR, { recursive: true });
    /* 顶部（含目录按钮） */
    let r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${OUTDIR}\\_${TAG}_top.png`, Buffer.from(r.result.data, 'base64'));
    /* 抽屉展开 */
    await ev(`document.getElementById('tocToggle').click(); 1`);
    await new Promise(r => setTimeout(r, 500));
    r = await send('Page.captureScreenshot', { format: 'png' });
    fs.writeFileSync(`${OUTDIR}\\_${TAG}_toc.png`, Buffer.from(r.result.data, 'base64'));
    await ev(`document.getElementById('tocToggle').click(); 1`);
    await new Promise(r => setTimeout(r, 400));
    /* 正文中段（表格 + 代码） */
    const H = await ev(`document.documentElement.scrollHeight`);
    for (const [i, frac] of [0.18, 0.42, 0.66].entries()) {
      await ev(`window.scrollTo(0, ${Math.round(H * frac)}); 1`);
      await new Promise(r => setTimeout(r, 450));
      r = await send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(`${OUTDIR}\\_${TAG}_m${i}.png`, Buffer.from(r.result.data, 'base64'));
    }
    console.log('截图已存 ' + OUTDIR);
  }
  ws.close();
})().catch(e => { console.error('ERR ' + e.message); process.exit(1); });
