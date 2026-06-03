# -*- coding: utf-8 -*-
"""200問のデータからインタラクティブなクイズHTML（自己完結・外部依存なし）を生成する。"""
import re, glob, json, html

files = [f for f in sorted(set(glob.glob('二等学科対策問題集_0*.md') +
                               glob.glob('二等学科対策問題集_1*.md')))
         if '統合' not in f and '解答分離' not in f]

CHAP_SHORT = {
    '第1章　無人航空機に関する規則': '規則',
    '第2章　無人航空機のシステム': 'システム',
    '第3章　無人航空機の操縦者及び運航体制': '操縦者・運航体制',
    '第4章　運航上のリスク管理': 'リスク管理',
}

records = []
for f in files:
    lines = open(f, encoding='utf-8').read().split('\n')
    cur = None
    i = 0
    while i < len(lines):
        m = re.match(r'^## (第\d章.*)', lines[i])
        if m:
            cur = m.group(1).strip()
        mq = re.match(r'^### 問題(\d+)', lines[i])
        if mq:
            qn = int(mq.group(1))
            stem = lines[i + 1].strip()
            opts = []
            j = i + 2
            ans = None
            while j < len(lines):
                mo = re.match(r'^([123])\. (.*)', lines[j])
                if mo:
                    opts.append(mo.group(2))
                if lines[j].startswith('**正解'):
                    ans = int(re.search(r'([123])', lines[j]).group(1))
                    break
                j += 1
            k = j + 1
            expl = ''
            while k < len(lines):
                if lines[k].startswith('---'):
                    break
                if lines[k].strip():
                    expl = lines[k].strip()
                    break
                k += 1
            records.append({'id': qn, 'chapter': CHAP_SHORT.get(cur, cur),
                            'stem': stem, 'options': opts, 'answer': ans, 'explanation': expl})
        i += 1

records.sort(key=lambda r: r['id'])
assert len(records) == 200, len(records)

# data/questions.json
import os
os.makedirs('data', exist_ok=True)
open('data/questions.json', 'w', encoding='utf-8').write(
    json.dumps(records, ensure_ascii=False, indent=1))

DATA_JSON = json.dumps(records, ensure_ascii=False)

HTML = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>二等ドローン学科クイズ</title>
<style>
  :root{ --bg:#0f172a; --card:#1e293b; --accent:#38bdf8; --ok:#22c55e; --ng:#ef4444; --txt:#e2e8f0; --mut:#94a3b8; }
  *{ box-sizing:border-box; }
  body{ margin:0; font-family:"Yu Gothic","Hiragino Kaku Gothic ProN","Meiryo",system-ui,sans-serif;
        background:var(--bg); color:var(--txt); line-height:1.7; }
  .wrap{ max-width:760px; margin:0 auto; padding:20px 16px 60px; }
  header h1{ font-size:1.4rem; margin:0 0 4px; }
  header p{ color:var(--mut); margin:0 0 18px; font-size:.85rem; }
  .card{ background:var(--card); border-radius:14px; padding:22px; margin-bottom:16px;
         box-shadow:0 6px 20px rgba(0,0,0,.25); }
  h2{ font-size:1.1rem; margin:0 0 14px; }
  label{ display:block; font-size:.85rem; color:var(--mut); margin:14px 0 6px; }
  select,button{ font:inherit; }
  select{ width:100%; padding:10px 12px; border-radius:10px; border:1px solid #334155;
          background:#0b1220; color:var(--txt); }
  .btn{ display:inline-block; width:100%; padding:13px; border:none; border-radius:10px;
        background:var(--accent); color:#04293b; font-weight:700; cursor:pointer; margin-top:18px; font-size:1rem; }
  .btn:hover{ filter:brightness(1.07); }
  .btn.sec{ background:#334155; color:var(--txt); }
  .meta{ display:flex; justify-content:space-between; align-items:center; color:var(--mut); font-size:.85rem; margin-bottom:10px; }
  .bar{ height:6px; background:#334155; border-radius:99px; overflow:hidden; margin-bottom:18px; }
  .bar>div{ height:100%; background:var(--accent); width:0; transition:width .3s; }
  .chip{ display:inline-block; font-size:.72rem; padding:2px 9px; border-radius:99px;
         background:#0b1220; color:var(--accent); border:1px solid #334155; }
  .stem{ font-size:1.05rem; font-weight:600; margin:10px 0 18px; }
  .opt{ display:block; width:100%; text-align:left; padding:13px 15px; margin-bottom:10px;
        border:1.5px solid #334155; border-radius:11px; background:#0b1220; color:var(--txt); cursor:pointer; transition:.15s; }
  .opt:hover:not(:disabled){ border-color:var(--accent); }
  .opt:disabled{ cursor:default; }
  .opt .num{ display:inline-block; width:1.6em; font-weight:700; color:var(--accent); }
  .opt.ok{ border-color:var(--ok); background:rgba(34,197,94,.13); }
  .opt.ng{ border-color:var(--ng); background:rgba(239,68,68,.13); }
  .fb{ margin-top:6px; padding:14px; border-radius:11px; font-size:.92rem; display:none; }
  .fb.show{ display:block; }
  .fb.ok{ background:rgba(34,197,94,.12); border:1px solid var(--ok); }
  .fb.ng{ background:rgba(239,68,68,.12); border:1px solid var(--ng); }
  .fb b{ color:var(--accent); }
  .score{ font-size:2.4rem; font-weight:800; text-align:center; margin:6px 0; }
  .score small{ font-size:1rem; color:var(--mut); font-weight:500; }
  .rev{ border-top:1px solid #334155; padding-top:12px; margin-top:12px; font-size:.9rem; }
  .rev .q{ color:var(--mut); }
  footer{ text-align:center; color:var(--mut); font-size:.75rem; margin-top:24px; }
  a{ color:var(--accent); }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🛸 二等ドローン学科クイズ</h1>
    <p>二等無人航空機操縦士 学科試験対策／全200問・三肢択一式（学習用オリジナル）</p>
  </header>

  <div id="start" class="card">
    <h2>設定して開始</h2>
    <label for="chap">科目</label>
    <select id="chap">
      <option value="all">全科目（200問）</option>
      <option value="規則">① 無人航空機に関する規則（80問）</option>
      <option value="システム">② 無人航空機のシステム（48問）</option>
      <option value="操縦者・運航体制">③ 操縦者及び運航体制（36問）</option>
      <option value="リスク管理">④ 運航上のリスク管理（36問）</option>
    </select>
    <label for="num">出題数</label>
    <select id="num">
      <option value="10">10問</option>
      <option value="20" selected>20問</option>
      <option value="50">50問</option>
      <option value="0">全問</option>
    </select>
    <label for="ord">出題順</label>
    <select id="ord">
      <option value="rand" selected>ランダム</option>
      <option value="seq">番号順</option>
    </select>
    <button class="btn" onclick="start()">スタート</button>
  </div>

  <div id="quiz" class="card" style="display:none">
    <div class="meta"><span id="prog"></span><span id="sc"></span></div>
    <div class="bar"><div id="barfill"></div></div>
    <span class="chip" id="chip"></span>
    <div class="stem" id="stem"></div>
    <div id="opts"></div>
    <div class="fb" id="fb"></div>
    <button class="btn" id="next" style="display:none" onclick="next()">次へ ▶</button>
  </div>

  <div id="result" class="card" style="display:none">
    <h2>結果</h2>
    <div class="score" id="final"></div>
    <div id="review"></div>
    <button class="btn" onclick="location.reload()">もう一度</button>
  </div>

  <footer>
    学習用に独自作成したものであり、実際の試験問題とは異なります。<br>
    © 2026 TechnoDroneKurashiki ／ <a href="https://github.com/TechnoDroneKurashiki/drone-license-workbook">GitHub</a>
  </footer>
</div>

<script>
const DATA = __DATA__;
let quiz=[], idx=0, score=0, wrong=[];

function shuffle(a){ for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; }
function esc(s){ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

function start(){
  const chap=document.getElementById('chap').value;
  let pool=DATA.filter(q=> chap==='all'||q.chapter===chap);
  const ord=document.getElementById('ord').value;
  pool = ord==='rand' ? shuffle(pool.slice()) : pool.slice().sort((a,b)=>a.id-b.id);
  let n=parseInt(document.getElementById('num').value,10);
  if(n>0) pool=pool.slice(0,n);
  quiz=pool; idx=0; score=0; wrong=[];
  document.getElementById('start').style.display='none';
  document.getElementById('quiz').style.display='block';
  render();
}

function render(){
  const q=quiz[idx];
  document.getElementById('prog').textContent=`第 ${idx+1} / ${quiz.length} 問`;
  document.getElementById('sc').textContent=`正解 ${score}`;
  document.getElementById('barfill').style.width=(idx/quiz.length*100)+'%';
  document.getElementById('chip').textContent=q.chapter;
  document.getElementById('stem').textContent=q.stem;
  const ow=document.getElementById('opts'); ow.innerHTML='';
  q.options.forEach((o,i)=>{
    const b=document.createElement('button');
    b.className='opt';
    b.innerHTML=`<span class="num">${i+1}</span>${esc(o)}`;
    b.onclick=()=>answer(i+1,b);
    ow.appendChild(b);
  });
  const fb=document.getElementById('fb'); fb.className='fb'; fb.innerHTML='';
  document.getElementById('next').style.display='none';
}

function answer(sel,btn){
  const q=quiz[idx];
  const btns=document.querySelectorAll('#opts .opt');
  btns.forEach((b,i)=>{ b.disabled=true; if(i+1===q.answer) b.classList.add('ok'); });
  const ok = sel===q.answer;
  if(ok){ score++; } else { btn.classList.add('ng'); wrong.push(q); }
  const fb=document.getElementById('fb');
  fb.className='fb show '+(ok?'ok':'ng');
  fb.innerHTML=(ok?'✅ 正解！ ':'❌ 不正解 ')+`<b>正解：${q.answer}</b><br>`+esc(q.explanation);
  document.getElementById('sc').textContent=`正解 ${score}`;
  const nb=document.getElementById('next');
  nb.style.display='block';
  nb.textContent = (idx+1<quiz.length)?'次へ ▶':'結果を見る ▶';
}

function next(){
  idx++;
  if(idx<quiz.length){ render(); }
  else{ showResult(); }
}

function showResult(){
  document.getElementById('quiz').style.display='none';
  const r=document.getElementById('result'); r.style.display='block';
  const pct=Math.round(score/quiz.length*100);
  document.getElementById('final').innerHTML=`${score} / ${quiz.length}<br><small>正答率 ${pct}%</small>`;
  const rv=document.getElementById('review');
  if(wrong.length===0){ rv.innerHTML='<p style="text-align:center">全問正解！おめでとうございます 🎉</p>'; return; }
  rv.innerHTML='<h2>復習（不正解の問題）</h2>'+wrong.map(q=>
    `<div class="rev"><div class="q">［${q.chapter}］${esc(q.stem)}</div>`+
    `<div><b>正解：${q.answer}</b> ${esc(q.options[q.answer-1])}</div>`+
    `<div style="color:#94a3b8;font-size:.85rem;margin-top:4px">${esc(q.explanation)}</div></div>`
  ).join('');
}
</script>
</body>
</html>
'''

out = HTML.replace('__DATA__', DATA_JSON)
for name in ['index.html', '二等ドローン学科クイズ.html']:
    open(name, 'w', encoding='utf-8').write(out)
print('生成: index.html, 二等ドローン学科クイズ.html, data/questions.json （', len(records), '問 ）')
