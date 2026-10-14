const fs = require('fs');
const s = fs.readFileSync('zhijia-monthly-202609.html', 'utf8');
// 找 .wrap 开始的位置,从这里开始用栈追踪结构
const startIdx = s.indexOf('<div class="wrap">');
const html = s.slice(startIdx);
const tagRe = /<(\/)?(div|section|table|tbody|thead|tr|td|th|ul|li|p|h1|h2|h4|span|b|i|em|s|colgroup|col|br|header|footer)([^>]*)>/g;
const selfClosing = new Set(['br','col']);
const stack = [];
let m;
const parents = {};
while ((m = tagRe.exec(html)) !== null) {
  const closing = !!m[1], tag = m[2], attrs = m[3] || '';
  if (selfClosing.has(tag)) continue;
  if (!closing) {
    const blk = (attrs.match(/data-blk="([^"]+)"/) || [])[1];
    const cls = (attrs.match(/class="([^"]+)"/) || [])[1] || '';
    stack.push({tag, blk, cls});
    if (blk) {
      // 找最近的祖先
      const p = stack[stack.length - 2];
      parents[blk] = p ? (p.tag + (p.blk ? '[blk=' + p.blk + ']' : (p.cls ? '.' + p.cls : ''))) : 'ROOT';
    }
  } else {
    // 弹栈:找最近的同名标签
    for (let i = stack.length - 1; i >= 0; i--) {
      if (stack[i].tag === tag) { stack.length = i; break; }
    }
  }
}
Object.keys(parents).sort((a,b)=>a-b).forEach(k => {
  const ok = parents[k].startsWith('div.wrap') ? '' : '   <-- 不是 .wrap 直接子元素!';
  console.log('blk', k.padEnd(3), '父级:', parents[k], ok);
});
