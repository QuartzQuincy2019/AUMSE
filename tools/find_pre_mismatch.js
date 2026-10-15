/* 找出 HTML 里 <pre> / </pre> 不配对的确切位置 */
const fs = require('fs');
const file = process.argv[2];
const t = fs.readFileSync(file, 'utf8');

const re = /<pre[\s>]|<\/pre>/g;
let m, depth = 0, line = 1, idx = 0;
const events = [];
while ((m = re.exec(t)) !== null) {
  // 计算行号
  line = t.slice(0, m.index).split('\n').length;
  if (m[0] === '</pre>') {
    if (depth === 0) {
      events.push({ line, kind: 'EXTRA-CLOSE', idx: m.index });
    }
    depth = Math.max(0, depth - 1);
  } else {
    depth++;
    events.push({ line, kind: 'open', depth, idx: m.index });
  }
}
const opens = (t.match(/<pre[\s>]/g) || []).length;
const closes = (t.match(/<\/pre>/g) || []).length;
console.log('文件: ' + file);
console.log('  <pre   : ' + opens);
console.log('  </pre> : ' + closes);
console.log('  差值   : ' + (opens - closes));

const extra = events.filter(e => e.kind === 'EXTRA-CLOSE');
if (extra.length) {
  console.log('\n多余的 </pre>:');
  for (const e of extra) {
    console.log('  第 ' + e.line + ' 行  位置 ' + e.idx);
    console.log('    上下文: ' + JSON.stringify(t.slice(e.idx - 90, e.idx + 20)));
  }
}
if (depth > 0) console.log('\n结束时仍有 ' + depth + ' 个 <pre> 未闭合');
