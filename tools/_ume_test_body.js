/* UME.html logic regression tests.
   Expectations aligned with:
     - UAX #14 (rev 57 / Unicode 18.0.0) rules LB9, LB13(EX), LB18(SP), LB21(BA/BB), LB23, LB28
     - UAX #29 grapheme clusters
     - report/unicode-mongolian-editing.txt
   NOTE: a break opportunity is counted per UAX#14, so "AB<SP>CD" yields TWO
   opportunities (after the space, and at the boundary itself) -- see LD8. */
const out=[];
let fails=0;
const chk=(name,got,exp)=>{
  const ok = JSON.stringify(got)===JSON.stringify(exp);
  if(!ok) fails++;
  out.push((ok?'  OK  ':' FAIL ')+name.padEnd(14)+' got='+JSON.stringify(got)+'  exp='+JSON.stringify(exp));
};

/* ---- 1. character palette integrity ---- */
const seen=new Map(); let dup=0,total=0;
GROUPS.forEach(g=>g.items.forEach(([c,n,z])=>{
  total++;
  if(seen.has(c)){dup++; out.push('  !! duplicate '+cpHex(c)+' in '+g.n);}
  seen.set(c,g.n);
  if((c>=0x181A&&c<=0x181F)||(c>=0x1879&&c<=0x187F)||(c>=0x18AB&&c<=0x18AF))
    out.push('  !! reserved codepoint used: '+cpHex(c));
}));
out.push('palette keys='+total+'  unique='+seen.size+'  duplicates='+dup);
out.push('mongolian codepoints in palette='+[...seen.keys()].filter(isMong).length);

/* ---- 2. "all MNG" tab must cover every assigned cp in 1800..18AA ---- */
const missing=[];
for(let c=0x1800;c<=0x18AA;c++){
  if((c>=0x181A&&c<=0x181F)||(c>=0x1879&&c<=0x187F)) continue;
  if(!seen.has(c)) missing.push(cpHex(c));
}
chk('palette coverage', missing, []);

/* ---- 3. grapheme clusters + break opportunities ---- */
const M=[0x182E,0x1823,0x1829,0x182D,0x1823,0x182F];   // mongol
const S2=[0x1830,0x1820,0x1836,0x1822,0x1828];           // sayin
out.push('');
out.push('case            cps  clusters  breakOpps');
/* breakOpps 语义说明（与 UCD LineBreakTest.txt 成对判定一致）：
   - 空格：LB7 禁止在空格前断、LB18 允许在空格后断 => 只报「空格之后」那一个机会
   - EX（1802/1803/1808/1809）：LB13 禁止其前断行，报其后一个机会
   - BA（1804/1805）：LB21 禁止其后断、其前可断 => 报其前一个机会
   - BB（1806）：其前可断、其后不可断（afterBB 状态）
   - GL（180E）：两侧一律禁断
   - NU（1810-1819）：数字序列内部不断（与 AL 之间亦不断） */
const cases=[
  ['plain word',   M,                       6,  []],
  ['FVS1 final',   [...M,0x180B],           6,  []],
  ['FVS1 medial',  [M[0],0x180B,...M.slice(1)], 6, []],
  ['NIRUGU',       [...M,0x180A,...S2],    12,  []],
  ['MVS',          [...M,0x180E,...S2],    12,  []],
  ['space',        [...M,0x20,...S2],      12,  [7]],
  ['comma EX',     [...M,0x1802,...S2],    12,  [7]],
  ['stop EX',      [...M,0x1803,...S2],    12,  [7]],
  ['colon BA',     [...M,0x1804,...S2],    12,  [6]],
  ['hyphen BB',    [M[0],0x1806,...M.slice(1)], 7, [1]],
  ['hyphen BB+AL', [0x1806,0x182A],          2,  []],
  ['Sibe bdry AL', [...M,0x1807,...S2],    12,  []],
  ['Baluda',       [0x1887,0x1885],         1,  []],
  ['Dagalga',      [0x1889,0x18A9],         1,  []],
  ['ZWNJ',         [...M,0x200C,...S2],    11,  []],
  ['ZWJ',          [...M,0x200D,...S2],    11,  []],
  ['Mong digits',  [0x1810,0x1811,0x1812],  3,  []],
  ['letter+digit', [...M,0x1810],           7,  []],
];
for(const [nm,cps,expCl,expBr] of cases){
  const gc=graphemes(cps).length;
  const br=[...breakOpps(cps)].sort((a,b)=>a-b);
  const ok=(gc===expCl && JSON.stringify(br)===JSON.stringify(expBr));
  if(!ok) fails++;
  out.push((ok?'  OK  ':' FAIL ')+nm.padEnd(14)+String(cps.length).padStart(3)+
           String(gc).padStart(8)+'/'+expCl+'   '+JSON.stringify(br));
}

/* ---- 4. property spot checks ----
   UME.html 的 PROPS 现在只保留导出与断行真正需要的字段（gc / lb / ext / ign），
   所以这里只断言 gc 与 lb。 */
out.push('');
out.push('--- property spot checks (UCD 18.0.0) ---');
const props=[
  [0x1802,'Po','EX'], [0x1803,'Po','EX'],
  [0x1804,'Po','BA'], [0x1805,'Po','BA'],
  [0x1806,'Pd','BB'], [0x1807,'Po','AL'],
  [0x180A,'Po','AL'], [0x180B,'Mn','CM'],
  [0x180E,'Cf','GL'], [0x180F,'Mn','CM'],
  [0x1810,'Nd','NU'], [0x1820,'Lo','AL'],
  [0x1828,'Lo','AL'], [0x1885,'Mn','CM'],
  [0x18A9,'Mn','CM'], [0x18AA,'Lo','AL'],
];
for(const [c,gc,lb] of props){
  const p=prop(c);
  const ok = p.gc===gc && p.lb===lb;
  if(!ok) fails++;
  out.push((ok?'  OK  ':' FAIL ')+cpHex(c)+'  gc='+p.gc+' lb='+p.lb
           +'   expected '+gc+'/'+lb);
}

/* ---- 5. grapheme glue flags ---- */
out.push('');
for(const c of [0x180B,0x180C,0x180D,0x180F,0x1885,0x1886,0x18A9]){
  chk('prop('+cpHex(c)+').ext', prop(c).ext===1, true);
}
for(const c of [0x1820,0x182E,0x1810]){
  chk('prop('+cpHex(c)+').ext', !!prop(c).ext, false);
}

out.push('');
out.push(fails===0 ? 'ALL TESTS PASSED' : ('FAILURES: '+fails));
console.log(out.join('\n'));
process.exit(fails===0?0:1);
