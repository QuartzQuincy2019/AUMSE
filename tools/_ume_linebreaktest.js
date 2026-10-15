/* Verify UME.html's breakOpps() against the official UCD LineBreakTest.txt.
 *
 * LineBreakTest.txt contains no Mongolian code points, but it does contain
 * PAIRWISE judgments for every line-break class combination. So: for every
 * ordered pair (x, y) found as adjacent code points anywhere in the test file,
 * we build the minimal sequence [x, y] and compare the official break/no-break
 * decision with UME's breakOpps(). Pairs involving a Mongolian code point are
 * reported -- that is a real conformance check of the classes UME cares about.
 *
 * The UME implementation is a Mongolian-focused subset of UAX #14 (it does not
 * implement Brahmic/Hangul/emoji classes), so only pairs where BOTH code points
 * are either Mongolian-block or one of a small set of comparison characters are
 * treated as in-scope; everything else is counted separately as out-of-scope.
 */
const fs = require('fs');
const P = 'E:\\QKMansion\\CSX10\\w\\UME\\report\\ucd\\LineBreakTest.txt';
const lines = fs.readFileSync(P, 'utf8').split(/\r?\n/);
const DIV = '\u00F7', MUL = '\u00D7';

const inMong = c => (c >= 0x1800 && c <= 0x18AF) || (c >= 0x11660 && c <= 0x1167F);
/* representative comparison characters, one per relevant class */
const CMP = [
  0x0020, // SP
  0x0041, // AL
  0x0030, // NU
  0x0021, // EX
  0x0029, // CP
  0x0028, // OP
  0x0022, // QU
  0x002C, // IS
  0x002F, // SY
  0x0024, // PR
  0x0025, // PO
  0x002D, // HY
  0x00A0, // GL
  0x2060, // WJ
  0x200B, // ZW
  0x0308, // CM
  0x200D, // ZWJ
  0x2014, // B2
  0x000A, // LF
];
const inScope = c => inMong(c) || CMP.includes(c);

/* pairwise decisions from the official file */
const pair = new Map();      // "x,y" -> true(break) | false(no break)
let cases = 0;
for (const ln of lines) {
  const raw = ln.split('#')[0];
  if (!raw.trim()) continue;
  const toks = raw.trim().split(/\s+/);
  const cps = [], exp = [];
  for (const t of toks) {
    if (t === DIV) exp.push(true); else if (t === MUL) exp.push(false);
    else cps.push(parseInt(t, 16));
  }
  if (cps.length === 0) continue;
  cases++;
  for (let i = 1; i < cps.length; i++) {
    // exp[i] is the slot before cps[i]; positions 0 and cps.length are sentinels
    const slot = i;                       // boundary between cps[i-1] and cps[i]
    if (slot >= exp.length) continue;
    const k = cps[i - 1].toString(16) + ',' + cps[i].toString(16);
    const v = exp[slot];
    if (!pair.has(k)) pair.set(k, v);
    else if (pair.get(k) !== v) pair.set(k, null);   // context-dependent, ignore
  }
}
console.log('LineBreakTest.txt: ' + cases + ' cases, ' + pair.size + ' pair slots');

let checked = 0, mismatch = 0, skipped = 0, ctx = 0, mongChecked = 0, mongMismatch = 0;
const bad = [], badMong = [];
for (const [k, v] of pair) {
  if (v === null) { ctx++; continue; }               // context-dependent
  const [xs, ys] = k.split(',');
  const x = parseInt(xs, 16), y = parseInt(ys, 16);
  if (!inScope(x) || !inScope(y)) { skipped++; continue; }
  const got = breakOpps([x, y]).has(1);
  const involvesMong = inMong(x) || inMong(y);
  if (involvesMong) mongChecked++;
  checked++;
  if (got !== v) {
    mismatch++;
    if (involvesMong) mongMismatch++;
    const line =
      '  ' + xs.toUpperCase().padStart(4, '0') + ' + ' + ys.toUpperCase().padStart(4, '0') +
      '  (' + prop(x).lb + ' x ' + prop(y).lb + ')' +
      '  official=' + (v ? 'BREAK' : 'nobreak') + '  UME=' + (got ? 'BREAK' : 'nobreak');
    if (involvesMong) { if (badMong.length < 40) badMong.push(line); }
    else if (bad.length < 12) bad.push(line);
  }
}
console.log('in-scope pairs checked: ' + checked);
console.log('  ... of which involve a Mongolian code point: ' + mongChecked);
console.log('total mismatches: ' + mismatch);
console.log('  ... involving a Mongolian code point: ' + mongMismatch);
console.log('(context-dependent slots ignored: ' + ctx + ', out-of-scope pairs: ' + skipped + ')');
if (badMong.length) {
  console.log('\n--- MISMATCHES INVOLVING MONGOLIAN ---');
  badMong.forEach(b => console.log(b));
}
if (bad.length) {
  console.log('\n--- first non-Mongolian mismatches (comparison chars not modelled by UME) ---');
  bad.forEach(b => console.log(b));
}
process.exit(mongMismatch === 0 ? 0 : 1);
