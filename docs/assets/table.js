(function(){
var L=document.documentElement.lang==='ko';
var T={q:L?'이름 · 코드 · 계통 검색':'Search name, code or family',cat:L?'갈래':'Category',all:L?'전체':'All',flag:L?'표시':'Flag',
 cols:L?'모든 열 보기':'Show all columns',few:L?'주요 열만':'Main columns only',prev:L?'이전':'Previous',next:L?'다음':'Next',
 info:function(a,b,n,t){return L?(n+'행 가운데 '+a+'–'+b+' (전체 '+t+'행)'):('Rows '+a+'–'+b+' of '+n+' (table has '+t+')')},err:L?'표를 불러오지 못했다. 내려받기 링크를 써 주기 바란다.':'Could not load the table. Please use the download link.'};
var MAIN=['glottocode','name','family','category','Kc','Kc_types','Kv','vowel_features','S1c','S1x','T','T_basis','flags'];
var box=document.getElementById('tablebox');if(!box)return;
box.innerHTML='<div class="ctl"><input type="search" id="q" placeholder="'+T.q+'" size="26"><label>'+T.cat+' <select id="cat"></select></label><label>'+T.flag+' <select id="flg"></select></label><button id="colbtn">'+T.cols+'</button></div><div id="tinfo"></div><div class="tw"><table id="tbl"></table></div><div class="ctl"><button id="prev">'+T.prev+'</button><button id="next">'+T.next+'</button></div>';
var rows=[],head=[],view=[],page=0,PER=100,allc=false;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function draw(){var cols=allc?head:MAIN,ix=cols.map(function(c){return head.indexOf(c)});var a=page*PER,b=Math.min(view.length,a+PER);
 var h='<thead><tr>'+cols.map(function(c){return'<th>'+esc(c)+'</th>'}).join('')+'</tr></thead><tbody>';
 for(var i=a;i<b;i++){h+='<tr>'+ix.map(function(k,j){var c=cols[j];return c==='category'?'<td><code class="cat c-'+esc(view[i][k])+'">'+esc(view[i][k])+'</code></td>':'<td'+((c==='name'||c==='Kc_types'||c==='flags'||c==='T_basis')?' class="w"':'')+'>'+esc(view[i][k])+'</td>'}).join('')+'</tr>'}
 document.getElementById('tbl').innerHTML=h+'</tbody>';
 document.getElementById('tinfo').textContent=view.length?T.info(a+1,b,view.length,rows.length):T.info(0,0,0,rows.length);
 document.getElementById('prev').disabled=page===0;document.getElementById('next').disabled=b>=view.length}
function filt(){var q=document.getElementById('q').value.trim().toLowerCase(),c=document.getElementById('cat').value,f=document.getElementById('flg').value;
 var ci=head.indexOf('category'),fi=head.indexOf('flags');
 view=rows.filter(function(r){if(c&&r[ci]!==c)return false;if(f&&(';'+r[fi]+';').indexOf(';'+f+';')<0)return false;
  if(q&&(r[0]+' '+r[1]+' '+r[2]).toLowerCase().indexOf(q)<0)return false;return true});page=0;draw()}
fetch('../data/hangul-conditions-ed1.tsv').then(function(r){if(!r.ok)throw 0;return r.text()}).then(function(t){
 var ls=t.split('\n');if(ls[ls.length-1]==='')ls.pop();head=ls[0].replace(/\r$/,'').split('\t');
 rows=ls.slice(1).map(function(l){return l.replace(/\r$/,'').split('\t')});
 var ci=head.indexOf('category'),fi=head.indexOf('flags'),cs={},fs={};
 rows.forEach(function(r){cs[r[ci]]=1;r[fi].split(';').forEach(function(x){if(x)fs[x]=1})});
 function fill(id,o){var s=document.getElementById(id);s.innerHTML='<option value="">'+T.all+'</option>'+Object.keys(o).sort().map(function(k){return'<option>'+esc(k)+'</option>'}).join('')}
 fill('cat',cs);fill('flg',fs);
 ['q','cat','flg'].forEach(function(id){document.getElementById(id).addEventListener('input',filt)});
 document.getElementById('colbtn').addEventListener('click',function(){allc=!allc;this.textContent=allc?T.few:T.cols;draw()});
 document.getElementById('prev').addEventListener('click',function(){if(page>0){page--;draw()}});
 document.getElementById('next').addEventListener('click',function(){if((page+1)*PER<view.length){page++;draw()}});
 filt()}).catch(function(){box.innerHTML='<p>'+T.err+'</p>'});
})();
