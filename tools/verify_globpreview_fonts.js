/* 静态校验 web/globpreview.html 的字体表 (MN_FONTS)。
   ---------------------------------------------------------------------
   为什么是「静态」：本脚本**不需要浏览器**。
   受限沙箱里 msedge 起不来（Chromium 的多进程要开命名管道，被拒），
   所以任何依赖 CDP 的验证在这里都跑不通。这个脚本只读 HTML 文本，
   在正常机器与本机都能跑，用来挡住「表写错了」这一类低级错误。

   校验项：
     1. 条目总数与分组数（1 + 1 + 28 + 28 = 58）
     2. 族名唯一、无空值
     3. 缩放系数在合理区间、覆盖数非负
     4. 「Tig」与「StdEx」两组一一对应（同名系列不缺边）
     5. 给了 --fontlist（tools/list_local_mongolian_fonts.py 的输出）时，
        再核对表里每一支是否真的在本机装上了

   用法：
     node tools/verify_globpreview_fonts.js
     node tools/verify_globpreview_fonts.js --fontlist refs/fonts.txt
     （refs/fonts.txt 由 `python tools/list_local_mongolian_fonts.py > refs/fonts.txt`
       生成，属于本机快照，不入库；不给 --fontlist 就跳过与本机的对拍）
*/
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const PAGE = path.join(ROOT, 'web', 'globpreview.html');

const args = process.argv.slice(2);
const li = args.indexOf('--fontlist');
const FONTLIST = li >= 0 ? args[li + 1] : null;

const EXPECT = { total: 58, groups: 4, tig: 28, stdex: 28 };

let fail = 0;
const ok = (cond, msg) => {
  console.log((cond ? '  ✔ ' : '  ✘ ') + msg);
  if (!cond) fail++;
};

/* ---------- 取出 MN_FONTS ---------- */
const html = fs.readFileSync(PAGE, 'utf8');
const m = html.match(/const MN_FONTS = (\[[\s\S]*?\n\];)/);
if (!m) { console.error('✘ 找不到 const MN_FONTS = [ … ];'); process.exit(1); }
const table = new Function('return ' + m[1].slice(0, -1))();

console.log('字体表条目 :', table.length);

/* ---------- 1. 数量 ---------- */
ok(table.length === EXPECT.total,
  `条目数 = ${EXPECT.total}（实际 ${table.length}）`);

const groups = new Map();
for (const f of table) groups.set(f.g, (groups.get(f.g) || 0) + 1);
console.log('分组       :');
for (const [g, n] of groups) console.log('   ' + g + ' × ' + n);
ok(groups.size === EXPECT.groups, `分组数 = ${EXPECT.groups}（实际 ${groups.size}）`);

/* ---------- 2. 唯一性 ---------- */
const names = table.map(f => f.f);
ok(new Set(names).size === names.length, '族名无重复');
ok(names.every(n => typeof n === 'string' && n.trim()), '族名非空');

/* ---------- 3. 数值合理性 ---------- */
ok(table.every(f => Number.isFinite(f.s) && f.s > 0.5 && f.s < 1.6),
  '缩放系数都在 (0.5, 1.6) 内');
ok(table.every(f => Number.isInteger(f.c) && f.c > 0 && f.c <= 158),
  '覆盖数都是 1..158 的整数');

/* ---------- 4. Tig / StdEx 成对 ---------- */
/* 注意 Menk BudunTig 的族名里「Budun」与「Tig」之间**没有空格**，
   所以不能按 " Tig" 去切，只能按结尾的 Tig 切。 */
const stripMenk = s => s.replace(/^Menk\s+/, '').trim();
const tig = table
  .filter(f => !/StdEx/.test(f.f) && /Tig$/.test(f.f))
  .map(f => stripMenk(f.f.replace(/Tig$/, '')));
const std = table
  .filter(f => /StdEx Tig$/.test(f.f))
  .map(f => stripMenk(f.f.replace(/StdEx Tig$/, '')));
ok(tig.length === EXPECT.tig, `Tig 系列 = ${EXPECT.tig}（实际 ${tig.length}）`);
ok(std.length === EXPECT.stdex, `StdEx 系列 = ${EXPECT.stdex}（实际 ${std.length}）`);
/* 两代之间有两处族名写法不一致，是厂商自己起的，不是笔误 */
const norm = s => s.replace(/^Amglang$/, 'Amgalang');
const A = new Set(tig.map(norm));
const B = new Set(std);
const onlyA = [...A].filter(x => !B.has(x));
const onlyB = [...B].filter(x => !A.has(x));
ok(onlyA.length === 0 && onlyB.length === 0,
  'Tig 与 StdEx 一一对应' +
  (onlyA.length ? '（仅 Tig 有：' + onlyA.join(',') + '）' : '') +
  (onlyB.length ? '（仅 StdEx 有：' + onlyB.join(',') + '）' : ''));

/* ---------- 5. 与本机字体清单对拍 ---------- */
if (FONTLIST) {
  const raw = fs.readFileSync(FONTLIST, 'utf8');
  const installed = new Set();
  for (const line of raw.split(/\r?\n/)) {
    const mm = line.match(/\{ f:"([^"]+)"/);
    if (mm) installed.add(mm[1]);
  }
  console.log('本机清单   :', installed.size, '个族名（来自 ' + path.basename(FONTLIST) + '）');
  const missing = names.filter(n => n !== 'UME Mongolian' && !installed.has(n));
  ok(missing.length === 0,
    '表里的每一支本机都装了' + (missing.length ? '（缺：' + missing.join(', ') + '）' : ''));
} else {
  console.log('（跳过本机对拍：加 --fontlist refs/fonts.txt 可启用）');
}

console.log(fail === 0 ? '\n结果：全部通过 ✔' : `\n结果：${fail} 项未通过 ✘`);
process.exit(fail === 0 ? 0 : 1);
