# -*- coding: utf-8 -*-
"""data/questions.json から学習ダッシュボード付きクイズHTMLを生成する。
リポジトリ直下で実行: python scripts/build_quiz.py
出力: index.html / 二等ドローン学科クイズ.html （同内容）
"""
import json

records = json.load(open('data/questions.json', encoding='utf-8'))
assert len(records) == 200, len(records)
DATA_JSON = json.dumps(records, ensure_ascii=False)

HTML = r'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>二等ドローン学科クイズ</title>
<style>
  :root{
    --accent:#2563eb; --accent-soft:#dbeafe;
    --bg:#eef2f7; --card:#ffffff; --ink:#0f172a; --mut:#64748b; --line:#e2e8f0;
    --ok:#16a34a; --ng:#dc2626; --warnbg:#fee2e2; --warnink:#b91c1c;
    --barA:#f59e0b; --barB:#22c55e;
  }
  *{ box-sizing:border-box; }
  html,body{ margin:0; }
  body{ font-family:"Yu Gothic","Hiragino Kaku Gothic ProN","Meiryo",system-ui,sans-serif;
        background:var(--bg); color:var(--ink); line-height:1.7; -webkit-font-smoothing:antialiased; }
  .top{ background:var(--card); border-bottom:1px solid var(--line); }
  .top .in{ max-width:980px; margin:0 auto; padding:12px 18px; display:flex; align-items:center; gap:12px; }
  .logo{ width:38px; height:38px; border-radius:11px; background:var(--accent); color:#fff;
         display:grid; place-items:center; font-size:20px; flex:none; }
  .brand b{ display:block; font-size:1rem; line-height:1.3; }
  .brand span{ font-size:.74rem; color:var(--mut); }
  .themes{ margin-left:auto; display:flex; align-items:center; gap:8px; }
  .themes label{ font-size:.74rem; color:var(--mut); margin-right:2px; }
  .dot{ width:20px; height:20px; border-radius:50%; border:2px solid #fff; outline:1.5px solid var(--line);
        cursor:pointer; padding:0; }
  .dot.active{ outline:2px solid var(--ink); transform:scale(1.12); }
  .wrap{ max-width:980px; margin:0 auto; padding:26px 18px 70px; }
  h1.title{ font-size:1.7rem; margin:6px 0 6px; font-weight:800; letter-spacing:.01em; }
  .lead{ color:var(--mut); margin:0 0 22px; font-size:.92rem; }
  .card{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:22px;
         box-shadow:0 2px 10px rgba(15,23,42,.04); }
  .sec-h{ font-size:1.05rem; font-weight:700; margin:30px 0 12px; display:flex; align-items:baseline; gap:10px; }
  .sec-h small{ font-weight:400; font-size:.78rem; color:var(--mut); }

  /* dashboard stats */
  .dash{ display:flex; align-items:center; gap:26px; flex-wrap:wrap; }
  .ring{ position:relative; width:104px; height:104px; flex:none; }
  .ring .lab{ position:absolute; inset:0; display:grid; place-items:center; text-align:center; }
  .ring .lab b{ font-size:1.5rem; font-weight:800; }
  .ring .lab span{ font-size:.7rem; color:var(--mut); }
  .stats{ display:flex; gap:30px; flex-wrap:wrap; }
  .stat b{ display:block; font-size:1.7rem; font-weight:800; }
  .stat b small{ font-size:.8rem; color:var(--mut); font-weight:600; }
  .stat span{ font-size:.78rem; color:var(--mut); }
  .stat.warn b{ color:var(--ng); }

  /* chapter cards */
  .grid2{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }
  .chap{ text-align:left; background:var(--card); border:1px solid var(--line); border-radius:14px;
         padding:16px 16px 14px; cursor:pointer; transition:.15s; }
  .chap:hover{ border-color:var(--accent); box-shadow:0 4px 14px rgba(37,99,235,.10); transform:translateY(-1px); }
  .chap .row1{ display:flex; align-items:flex-start; gap:9px; }
  .badge{ flex:none; font-size:.72rem; font-weight:700; color:#fff; background:var(--accent);
          padding:3px 9px; border-radius:7px; }
  .chap .nm{ font-weight:700; font-size:.98rem; line-height:1.4; }
  .weak{ margin-left:auto; flex:none; font-size:.7rem; font-weight:700; color:var(--warnink);
         background:var(--warnbg); padding:2px 8px; border-radius:99px; }
  .chap .meta2{ color:var(--mut); font-size:.78rem; margin:9px 0 8px; }
  .pbar{ display:flex; align-items:center; gap:10px; }
  .pbar .track{ flex:1; height:7px; background:var(--line); border-radius:99px; overflow:hidden; }
  .pbar .fill{ height:100%; background:linear-gradient(90deg,var(--barA),var(--barB)); border-radius:99px; width:0; }
  .pbar .pct{ font-size:.78rem; font-weight:700; color:var(--mut); min-width:34px; text-align:right; }

  /* quick start */
  .grid3{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:14px; }
  .qs{ text-align:left; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px;
       cursor:pointer; transition:.15s; }
  .qs:hover{ border-color:var(--accent); box-shadow:0 4px 14px rgba(37,99,235,.10); transform:translateY(-1px); }
  .qs[disabled]{ opacity:.5; cursor:not-allowed; }
  .qs .ic{ width:40px; height:40px; border-radius:11px; background:var(--accent-soft); color:var(--accent);
           display:grid; place-items:center; font-size:20px; margin-bottom:12px; }
  .qs .t{ font-weight:700; font-size:1rem; }
  .qs .d{ color:var(--mut); font-size:.78rem; margin-top:3px; }

  /* settings */
  .setrow{ display:flex; align-items:center; gap:26px; flex-wrap:wrap; }
  .setrow .lab{ font-size:.82rem; font-weight:600; margin-right:4px; }
  .seg{ display:inline-flex; border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .seg button{ font:inherit; border:none; background:var(--card); color:var(--ink); padding:8px 14px;
               cursor:pointer; border-right:1px solid var(--line); font-size:.85rem; }
  .seg button:last-child{ border-right:none; }
  .seg button.on{ background:var(--accent); color:#fff; }
  .tg{ display:inline-flex; align-items:center; gap:9px; font-size:.82rem; cursor:pointer; }
  .switch{ width:42px; height:24px; border-radius:99px; background:#cbd5e1; position:relative; transition:.2s; flex:none; }
  .switch::after{ content:""; position:absolute; top:2px; left:2px; width:20px; height:20px; border-radius:50%;
                  background:#fff; transition:.2s; box-shadow:0 1px 3px rgba(0,0,0,.2); }
  .tg input{ display:none; }
  .tg input:checked + .switch{ background:var(--accent); }
  .tg input:checked + .switch::after{ transform:translateX(18px); }

  /* quiz screen */
  .qmeta{ display:flex; justify-content:space-between; color:var(--mut); font-size:.85rem; margin-bottom:8px; }
  .qtrack{ height:6px; background:var(--line); border-radius:99px; overflow:hidden; margin-bottom:18px; }
  .qtrack>div{ height:100%; background:var(--accent); width:0; transition:.3s; }
  .chip{ display:inline-block; font-size:.72rem; padding:3px 10px; border-radius:99px;
         background:var(--accent-soft); color:var(--accent); font-weight:700; }
  .stem{ font-size:1.1rem; font-weight:700; margin:12px 0 18px; }
  .opt{ display:block; width:100%; text-align:left; padding:14px 16px; margin-bottom:11px; font:inherit;
        border:1.5px solid var(--line); border-radius:12px; background:var(--card); color:var(--ink); cursor:pointer; transition:.15s; }
  .opt:hover:not(:disabled){ border-color:var(--accent); }
  .opt:disabled{ cursor:default; }
  .opt .n{ display:inline-block; width:1.7em; font-weight:800; color:var(--accent); }
  .opt.ok{ border-color:var(--ok); background:#f0fdf4; }
  .opt.ng{ border-color:var(--ng); background:#fef2f2; }
  .fb{ margin-top:6px; padding:15px; border-radius:12px; font-size:.92rem; display:none; }
  .fb.show{ display:block; }
  .fb.ok{ background:#f0fdf4; border:1px solid var(--ok); }
  .fb.ng{ background:#fef2f2; border:1px solid var(--ng); }
  .fb .hd{ font-weight:800; margin-bottom:4px; }
  .fb.ok .hd{ color:var(--ok); } .fb.ng .hd{ color:var(--ng); }
  .btn{ display:inline-block; width:100%; padding:14px; border:none; border-radius:12px; font:inherit;
        background:var(--accent); color:#fff; font-weight:700; cursor:pointer; margin-top:16px; font-size:1rem; }
  .btn:hover{ filter:brightness(1.06); }
  .btn.sec{ background:#e2e8f0; color:var(--ink); }
  .btns{ display:flex; gap:12px; }

  /* result */
  .score{ font-size:2.6rem; font-weight:800; text-align:center; margin:8px 0; }
  .score small{ display:block; font-size:1rem; color:var(--mut); font-weight:600; }
  .rev{ border-top:1px solid var(--line); padding-top:12px; margin-top:12px; font-size:.9rem; }
  .rev .q{ color:var(--mut); }

  .tpill{ font-size:.74rem; font-weight:700; padding:3px 11px; border-radius:99px; }
  .tpill.ok{ background:#dcfce7; color:#16a34a; }
  .tpill.ng{ background:#fee2e2; color:#dc2626; }
  .tpill.none{ background:#e2e8f0; color:#64748b; }
  footer{ text-align:center; color:var(--mut); font-size:.75rem; margin-top:30px; }
  footer a{ color:var(--accent); }
  .hide{ display:none !important; }
  @media(max-width:680px){
    .grid2,.grid3{ grid-template-columns:1fr; }
    h1.title{ font-size:1.4rem; }
    .stats{ gap:20px; }
  }
</style>
</head>
<body>
<div class="top"><div class="in">
  <div class="logo">✦</div>
  <div class="brand"><b>二等学科クイズ</b><span>無人航空機操縦士 試験対策</span></div>
  <div class="themes">
    <label>テーマ</label>
    <button class="dot" data-t="blue"   style="background:#2563eb" title="ブルー"></button>
    <button class="dot" data-t="teal"   style="background:#0d9488" title="ティール"></button>
    <button class="dot" data-t="orange" style="background:#ea580c" title="オレンジ"></button>
  </div>
  <div id="acctbar" style="display:none;align-items:center;gap:10px">
    <span id="acct" style="font-size:.8rem;color:var(--mut);font-weight:600"></span>
    <a id="adminLink" href="管理者画面.html" class="btn sec" style="display:none;width:auto;margin:0;padding:6px 12px;font-size:.8rem;text-decoration:none">管理者画面</a>
    <button id="logout" class="btn sec" style="width:auto;margin:0;padding:6px 12px;font-size:.8rem">ログアウト</button>
  </div>
</div></div>

<div class="wrap">

  <div id="authgate"></div>

  <div id="app" style="display:none">

  <!-- ===== HOME ===== -->
  <div id="home">
    <h1 class="title">二等 無人航空機操縦士 学科対策</h1>
    <p class="lead">全200問・三肢択一。1問ずつ解いてその場で解説を確認できます。</p>

    <div class="card">
      <div class="dash">
        <div class="ring">
          <svg width="104" height="104" viewBox="0 0 104 104">
            <circle cx="52" cy="52" r="44" fill="none" stroke="var(--line)" stroke-width="9"/>
            <circle id="ring" cx="52" cy="52" r="44" fill="none" stroke="var(--accent)" stroke-width="9"
                    stroke-linecap="round" stroke-dasharray="276.46" stroke-dashoffset="276.46"
                    transform="rotate(-90 52 52)" style="transition:stroke-dashoffset .5s"/>
          </svg>
          <div class="lab"><b id="accPct">0%</b><span>正答率</span></div>
        </div>
        <div class="stats">
          <div class="stat"><b id="seen">0<small> / 200</small></b><span>学習済みの問題</span></div>
          <div class="stat"><b id="lastok">0</b><span>直近で正解</span></div>
          <div class="stat warn"><b id="todo">0</b><span>要復習</span></div>
        </div>
      </div>
    </div>

    <div class="sec-h">認定テスト <small>4科目×10問＝40問。全問正解で合格（不合格なら新しい40問で再テスト）</small></div>
    <div class="card" id="testcard">
      <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap">
        <span id="testStatus" class="tpill none">未受験</span>
        <div class="stats">
          <div class="stat"><b id="tAttempts">0</b><span>受験回数</span></div>
          <div class="stat"><b id="tBest">–</b><span>最高得点</span></div>
        </div>
        <button class="btn" style="width:auto;margin:0;margin-left:auto" onclick="startTest()">認定テストを開始</button>
      </div>
    </div>

    <div class="sec-h">章ごとに学習 <small>タップで出題（出題数は下の設定に従います）</small></div>
    <div class="grid2" id="chaps"></div>

    <div class="sec-h">クイックスタート</div>
    <div class="grid3">
      <button class="qs" onclick="startMini()">
        <div class="ic">🎲</div><div class="t">ミニテスト</div><div class="d">全範囲からランダム出題</div>
      </button>
      <button class="qs" onclick="startAll()">
        <div class="ic">📚</div><div class="t">全200問</div><div class="d">通しで挑戦（出題数設定は無視）</div>
      </button>
      <button class="qs" id="qsReview" onclick="startReview()">
        <div class="ic">🔁</div><div class="t">復習</div><div class="d" id="revDesc">間違いを復習</div>
      </button>
    </div>

    <div class="sec-h">設定</div>
    <div class="card">
      <div class="setrow">
        <span class="lab">1回の出題数</span>
        <div class="seg" id="numSeg">
          <button data-n="10">10</button><button data-n="20">20</button><button data-n="30">30</button>
          <button data-n="50">50</button><button data-n="0">全部</button>
        </div>
        <label class="tg"><input type="checkbox" id="shOpts"><span class="switch"></span>選択肢シャッフル</label>
        <label class="tg"><input type="checkbox" id="shQs"><span class="switch"></span>問題シャッフル</label>
        <button class="btn sec" style="width:auto;margin:0;padding:8px 14px;font-size:.82rem" onclick="resetProgress()">学習記録をリセット</button>
      </div>
    </div>
  </div>

  <!-- ===== QUIZ ===== -->
  <div id="quiz" class="card hide">
    <div class="qmeta"><span id="prog"></span><span id="sc"></span></div>
    <div class="qtrack"><div id="qfill"></div></div>
    <span class="chip" id="chip"></span>
    <div class="stem" id="stem"></div>
    <div id="opts"></div>
    <div class="fb" id="fb"></div>
    <button class="btn" id="next" style="display:none" onclick="nextQ()">次へ ▶</button>
    <button class="btn sec" onclick="goHome()">中断してホームへ</button>
  </div>

  <!-- ===== RESULT ===== -->
  <div id="result" class="card hide">
    <h2 style="margin-top:0">結果</h2>
    <div class="score" id="final"></div>
    <div id="review"></div>
    <div class="btns">
      <button class="btn sec" onclick="goHome()">ホームへ</button>
      <button class="btn" id="retryBtn" onclick="retry()">もう一度</button>
    </div>
  </div>

  </div><!-- /#app -->

  <footer>
    学習用に独自作成したものであり、実際の試験問題とは異なります。<br>
    © 2026 TechnoDroneKurashiki ／ <a href="https://github.com/TechnoDroneKurashiki/drone-license-workbook">GitHub</a>
  </footer>
</div>

<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="config.js"></script>
<script>
const DATA = __DATA__;
const CHAPTERS=[
  {key:'規則', no:'第1章', name:'無人航空機に関する規則'},
  {key:'システム', no:'第2章', name:'無人航空機のシステム'},
  {key:'操縦者・運航体制', no:'第3章', name:'無人航空機の操縦者及び運航体制'},
  {key:'リスク管理', no:'第4章', name:'運航上のリスク管理'},
];
const THEMES={blue:'#2563eb', teal:'#0d9488', orange:'#ea580c'};
const SOFT={blue:'#dbeafe', teal:'#ccfbf1', orange:'#ffedd5'};
const RING_C=276.46;

const LS={ get:(k,d)=>{ try{ const v=JSON.parse(localStorage.getItem(k)); return v==null?d:v; }catch(e){ return d; } },
           set:(k,v)=>localStorage.setItem(k,JSON.stringify(v)) };
let settings = LS.get('dq_settings', {num:10, shuffleOpts:true, shuffleQs:true});
let progress = LS.get('dq_progress', {});   // {id:{a,c,last:'o'|'x'}}
let theme    = LS.get('dq_theme','blue');

let session=[], idx=0, score=0, sessionWrong=[], lastSession=null, isTest=false;

function shuffle(a){ for(let i=a.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [a[i],a[j]]=[a[j],a[i]]; } return a; }
function esc(s){ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }
function $(id){ return document.getElementById(id); }

/* ---- theme ---- */
function applyTheme(t){
  theme=t; LS.set('dq_theme',t);
  document.documentElement.style.setProperty('--accent',THEMES[t]);
  document.documentElement.style.setProperty('--accent-soft',SOFT[t]);
  document.querySelectorAll('.dot').forEach(d=>d.classList.toggle('active', d.dataset.t===t));
}

/* ---- metrics ---- */
const seenCount=()=>Object.keys(progress).length;
const lastOk=()=>Object.values(progress).filter(p=>p.last==='o').length;
const wrongIds=()=>Object.keys(progress).filter(k=>progress[k].last==='x').map(Number);
const accuracy=()=>{ const s=seenCount(); return s?Math.round(lastOk()/s*100):0; };
function chapStat(key){
  const all=DATA.filter(q=>q.chapter===key);
  const learned=all.filter(q=>progress[q.id]);
  const weak=learned.filter(q=>progress[q.id].last==='x').length;
  return {total:all.length, learned:learned.length, weakPct: learned.length?Math.round(weak/learned.length*100):0};
}

/* ---- dashboard render ---- */
function renderHome(){
  const acc=accuracy();
  $('accPct').textContent=acc+'%';
  $('ring').style.strokeDashoffset = RING_C*(1-acc/100);
  $('seen').innerHTML=seenCount()+'<small> / 200</small>';
  $('lastok').textContent=lastOk();
  $('todo').textContent=wrongIds().length;

  $('chaps').innerHTML = CHAPTERS.map(c=>{
    const s=chapStat(c.key);
    return '<button class="chap" onclick="startChapter(\''+c.key+'\')">'+
      '<div class="row1"><span class="badge">'+c.no+'</span><span class="nm">'+esc(c.name)+'</span>'+
        '<span class="weak">苦手 '+s.weakPct+'%</span></div>'+
      '<div class="meta2">全'+s.total+'問 ・ 学習'+s.learned+'問</div>'+
      '<div class="pbar"><div class="track"><div class="fill" style="width:'+s.weakPct+'%"></div></div>'+
        '<span class="pct">'+s.weakPct+'%</span></div>'+
    '</button>';
  }).join('');

  const rc=wrongIds().length;
  $('revDesc').textContent = rc>0 ? (rc+'問の間違いを復習') : '間違いはまだありません';
  $('qsReview').disabled = rc===0;

  document.querySelectorAll('#numSeg button').forEach(b=>b.classList.toggle('on', parseInt(b.dataset.n,10)===settings.num));
  $('shOpts').checked=settings.shuffleOpts;
  $('shQs').checked=settings.shuffleQs;
  renderTestCard();
}

/* ---- session build ---- */
function buildSession(pool, respectNum, forceSeq){
  pool=pool.slice();
  if(settings.shuffleQs && !forceSeq) shuffle(pool); else pool.sort((a,b)=>a.id-b.id);
  if(respectNum && settings.num>0) pool=pool.slice(0,settings.num);
  session = pool.map(q=>{
    let os=q.options.map((t,i)=>({t:t, c:(i+1)===q.answer}));
    if(settings.shuffleOpts) shuffle(os);
    return {id:q.id, chapter:q.chapter, stem:q.stem, explanation:q.explanation,
            opts:os.map(o=>o.t), ans:os.findIndex(o=>o.c)+1};
  });
  if(!session.length){ alert('対象の問題がありません。'); return false; }
  isTest=false; idx=0; score=0; sessionWrong=[];
  return true;
}

/* ---- 認定テスト（4科目×10問＝40問・全問正解で合格）---- */
function buildTest(){
  let pool=[];
  CHAPTERS.forEach(function(c){
    let qs=DATA.filter(function(q){return q.chapter===c.key;});
    shuffle(qs);
    pool=pool.concat(qs.slice(0,10));
  });
  shuffle(pool);
  session=pool.map(function(q){
    let os=q.options.map(function(t,i){return {t:t,c:(i+1)===q.answer};});
    shuffle(os);
    return {id:q.id,chapter:q.chapter,stem:q.stem,explanation:q.explanation,
            opts:os.map(function(o){return o.t;}),ans:os.findIndex(function(o){return o.c;})+1};
  });
  isTest=true; idx=0; score=0; sessionWrong=[];
  return true;
}
function startTest(){ lastSession=function(){return buildTest();}; run(); }
function startChapter(key){ lastSession=function(){return buildSession(DATA.filter(q=>q.chapter===key),true,false);}; run(); }
function startMini(){ lastSession=function(){return buildSession(DATA,true,false);}; run(); }
function startAll(){ lastSession=function(){return buildSession(DATA,false,false);}; run(); }
function startReview(){ const ids=wrongIds(); lastSession=function(){return buildSession(DATA.filter(q=>ids.indexOf(q.id)>=0),false,false);}; run(); }
function run(){ if(lastSession && lastSession()){ show('quiz'); renderQ(); } }
function retry(){ run(); }

/* ---- quiz play ---- */
function show(which){ ['home','quiz','result'].forEach(s=>$(s).classList.toggle('hide', s!==which)); window.scrollTo(0,0); }
function goHome(){ renderHome(); show('home'); }

function renderQ(){
  const q=session[idx];
  $('prog').textContent='第 '+(idx+1)+' / '+session.length+' 問';
  $('sc').textContent='正解 '+score;
  $('qfill').style.width=(idx/session.length*100)+'%';
  $('chip').textContent=q.chapter;
  $('stem').textContent=q.stem;
  const ow=$('opts'); ow.innerHTML='';
  q.opts.forEach((o,i)=>{
    const b=document.createElement('button');
    b.className='opt'; b.innerHTML='<span class="n">'+(i+1)+'</span>'+esc(o);
    b.onclick=function(){ answerQ(i+1,b); }; ow.appendChild(b);
  });
  const fb=$('fb'); fb.className='fb'; fb.innerHTML='';
  $('next').style.display='none';
}
function answerQ(sel,btn){
  const q=session[idx];
  document.querySelectorAll('#opts .opt').forEach((b,i)=>{ b.disabled=true; if(i+1===q.ans) b.classList.add('ok'); });
  const ok=(sel===q.ans);
  session[idx].got=ok;
  if(ok) score++; else { btn.classList.add('ng'); sessionWrong.push(q); }
  // 認定テストは別枠。通常の学習記録（科目別の学習状況）には合算しない
  if(!isTest){
    const p=progress[q.id]||{a:0,c:0,last:''};
    p.a++; if(ok) p.c++; p.last=ok?'o':'x'; progress[q.id]=p; LS.set('dq_progress',progress);
  }
  const fb=$('fb'); fb.className='fb show '+(ok?'ok':'ng');
  fb.innerHTML='<div class="hd">'+(ok?'✅ 正解！':'❌ 不正解')+'（正解：'+q.ans+'）</div>'+esc(q.explanation);
  $('sc').textContent='正解 '+score;
  const nb=$('next'); nb.style.display='block';
  nb.textContent=(idx+1<session.length)?'次へ ▶':'結果を見る ▶';
}
function nextQ(){ idx++; if(idx<session.length) renderQ(); else showResult(); }
function showResult(){
  if(isTest){ showTestResult(); return; }
  show('result');
  $('retryBtn').style.display=''; $('retryBtn').textContent='もう一度';
  const pct=Math.round(score/session.length*100);
  $('final').innerHTML=score+' / '+session.length+'<small>正答率 '+pct+'%</small>';
  const rv=$('review');
  if(!sessionWrong.length){ rv.innerHTML='<p style="text-align:center">全問正解！おめでとうございます 🎉</p>'; }
  else { rv.innerHTML='<h3>復習（今回の不正解）</h3>'+sessionWrong.map(q=>
    '<div class="rev"><div class="q">［'+q.chapter+'］'+esc(q.stem)+'</div>'+
    '<div><b style="color:var(--accent)">正解：'+q.ans+'</b> '+esc(q.opts[q.ans-1])+'</div>'+
    '<div style="color:var(--mut);font-size:.85rem;margin-top:4px">'+esc(q.explanation)+'</div></div>').join(''); }
  syncProgress();
}

function showTestResult(){
  show('result');
  const passed = (score===session.length);
  const detail={};
  CHAPTERS.forEach(function(c){ detail[c.key]={correct:0,total:0}; });
  session.forEach(function(q){ const d=detail[q.chapter]; if(d){ d.total++; if(q.got) d.correct++; } });
  // ローカル保存（ホーム表示用）
  const t=LS.get('dq_test',{attempts:0,best:0,last:0,passed:false});
  t.attempts++; t.last=score; t.best=Math.max(t.best,score); if(passed) t.passed=true;
  LS.set('dq_test',t);
  // DB保存（管理画面用）
  saveTestResult(score, detail, passed);
  // 表示
  $('final').innerHTML=score+' / '+session.length+'<small>'+(passed?'🎉 合格！全問正解です':'不合格 — 全問正解で合格です')+'</small>';
  let html='<h3>科目別の正答</h3>';
  CHAPTERS.forEach(function(c){ const d=detail[c.key];
    html+='<div class="rev"><b>'+c.no+'　'+esc(c.name)+'</b>：'+d.correct+' / '+d.total+'</div>'; });
  if(!passed){
    html+='<h3 style="margin-top:14px">不正解の問題</h3>'+sessionWrong.map(function(q){
      return '<div class="rev"><div class="q">［'+q.chapter+'］'+esc(q.stem)+'</div>'+
      '<div><b style="color:var(--accent)">正解：'+q.ans+'</b> '+esc(q.opts[q.ans-1])+'</div></div>'; }).join('');
  }
  $('review').innerHTML=html;
  const rb=$('retryBtn');
  if(passed){ rb.style.display='none'; }
  else { rb.style.display=''; rb.textContent='再テスト（新しい40問）'; }
}

/* ---- DB同期（ログイン時のみ・Supabase）---- */
function currentUserId(){ return (window.__user && window.__user.id) || null; }
function chapterStatsObj(){
  const prog=LS.get('dq_progress',{}); const out={};
  CHAPTERS.forEach(function(c){ out[c.key]={learned:0,ok:0,ng:0}; });
  DATA.forEach(function(q){ const p=prog[q.id]; if(p){ const o=out[q.chapter]; o.learned++;
    if(p.last==='o') o.ok++; else if(p.last==='x') o.ng++; } });
  return out;
}
function syncProgress(){
  const uid=currentUserId(); if(!uid || !window.__sb) return;
  window.__sb.from('user_progress').upsert({user_id:uid, stats:chapterStatsObj(),
    updated_at:new Date().toISOString()}).then(function(){},function(){});
}
function saveTestResult(scoreVal, detail, passed){
  const uid=currentUserId(); if(!uid || !window.__sb) return;
  window.__sb.from('user_progress')
    .select('test_attempts,test_best_score,test_passed,test_passed_at')
    .eq('user_id',uid).maybeSingle().then(function(r){
      const d=(r&&r.data)||{};
      const attempts=(d.test_attempts||0)+1;
      const best=Math.max(d.test_best_score||0, scoreVal);
      const already=d.test_passed||false;
      window.__sb.from('user_progress').upsert({
        user_id:uid, stats:chapterStatsObj(),
        test_attempts:attempts, test_last_score:scoreVal, test_best_score:best,
        test_passed: already||passed,
        test_passed_at: already ? d.test_passed_at : (passed ? new Date().toISOString() : null),
        test_last_detail: detail, updated_at:new Date().toISOString()
      }).then(function(){},function(){});
    });
}
function renderTestCard(){
  const t=LS.get('dq_test',{attempts:0,best:0,last:0,passed:false});
  $('tAttempts').textContent=t.attempts;
  $('tBest').textContent=t.attempts ? (t.best+' / 40') : '–';
  const s=$('testStatus');
  if(t.passed){ s.textContent='合格'; s.className='tpill ok'; }
  else if(t.attempts){ s.textContent='未合格'; s.className='tpill ng'; }
  else { s.textContent='未受験'; s.className='tpill none'; }
}
window.DQonAuth=function(){ syncProgress(); };
function resetProgress(){
  if(confirm('この端末の学習記録（進捗・要復習）をすべて消去します。よろしいですか？')){
    progress={}; LS.set('dq_progress',progress); syncProgress(); renderHome();
  }
}

/* ---- wire settings ---- */
document.querySelectorAll('.dot').forEach(d=>d.onclick=function(){ applyTheme(d.dataset.t); });
document.querySelectorAll('#numSeg button').forEach(b=>b.onclick=function(){ settings.num=parseInt(b.dataset.n,10); LS.set('dq_settings',settings); renderHome(); });
$('shOpts').onchange=function(e){ settings.shuffleOpts=e.target.checked; LS.set('dq_settings',settings); };
$('shQs').onchange =function(e){ settings.shuffleQs =e.target.checked; LS.set('dq_settings',settings); };

/* ---- init ---- */
applyTheme(theme);
renderHome();
</script>
<script src="auth.js"></script>
</body>
</html>
'''

out = HTML.replace('__DATA__', DATA_JSON)
for name in ['index.html', '二等ドローン学科クイズ.html']:
    open(name, 'w', encoding='utf-8').write(out)
print('生成: index.html / 二等ドローン学科クイズ.html （', len(records), '問 ）')
