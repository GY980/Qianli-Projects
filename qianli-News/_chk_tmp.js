const fs = require('fs');
const s = fs.readFileSync('zhijia-monthly-202609.html', 'utf8');
const js = s.match(/<script>[\s\S]*?<\/script>/g).join('\n').replace(/<\/?script>/g, '');
new Function(js);
console.log('JS OK');
['div','tr','td','th','table','section','b','li'].forEach(t => {
  const o = (s.match(new RegExp('<' + t + '(\\s|>)', 'g')) || []).length;
  const c = (s.match(new RegExp('</' + t + '>', 'g')) || []).length;
  console.log(t, o + '/' + c, o === c ? 'OK' : '!!MISMATCH!!');
});
console.log('bytes', Buffer.byteLength(s));
