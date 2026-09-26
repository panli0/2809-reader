// Local dictionary UI for the NGSL subset bundled with this site.
// Primary data: Open Dictionary v2.0, CC BY-SA 4.0.
// Supplement: FreeDict eng-zho 2025.11.23, CC BY-SA 3.0.

function resolveLocalHead(surface,proposed){
  const s=String(surface||'').toLowerCase().replace(/’/g,"'");
  try{
    if(LOCAL_DICTIONARY?.[proposed])return proposed;
    if(LOCAL_DICTIONARY?.[s])return s;
    if(LOCAL_FORM_MAP?.[s])return LOCAL_FORM_MAP[s];
  }catch(e){}
  return proposed||s;
}
function localDictionaryEntry(head){
  try{return LOCAL_DICTIONARY?.[head]||null}catch(e){return null}
}
function dictionaryAttribution(entry){
  return entry?.src==='freedict'
    ? 'FreeDict eng-zho 2025.11.23 · CC BY-SA 3.0'
    : 'Open Dictionary v2.0 · CC BY-SA 4.0 · 源自 English Wiktionary/Wiktextract';
}
function posLabel(pos){
  const labels={
    noun:'noun',
    verb:'verb',
    adj:'adjective',
    adjective:'adjective',
    adv:'adverb',
    adverb:'adverb',
    prep:'preposition',
    preposition:'preposition',
    conj:'conjunction',
    conjunction:'conjunction',
    pron:'pronoun',
    pronoun:'pronoun',
    det:'determiner',
    determiner:'determiner',
    interj:'interjection',
    interjection:'interjection',
    num:'numeral',
    numeral:'numeral',
    particle:'particle',
    phrase:'phrase'
  };
  const key=String(pos||'').toLowerCase();
  return labels[key]||pos||'';
}
function renderLocalDictionary(entry){
  if(!entry)return '';
  const rows=(entry.senses||[]).filter(x=>x.p==='core'||x.p==='common');
  const shown=(rows.length?rows:entry.senses||[]).slice(0,4);
  const html=[];
  if(entry.summary)html.push(`<div class="zh">${escapeHtml(entry.summary)}</div>`);
  for(const s of shown){
    const label=[posLabel(s.pos),s.g].filter(Boolean).join(' · ');
    html.push(`<div style="margin-top:9px"><b style="font-size:12px;color:var(--accent)">${escapeHtml(label||'常用义')}</b><div class="def" style="color:var(--ink);font-size:15px">${escapeHtml(s.z||s.g||'')}</div></div>`);
  }
  return html.join('');
}

showWord=async function(el){
  document.querySelectorAll('.word.selected').forEach(x=>x.classList.remove('selected'));
  el.classList.add('selected');
  const surface=el.dataset.word;
  const proposed=el.dataset.head||headFor(surface);
  const head=resolveLocalHead(surface,proposed);
  const sentence=el.closest('.sentence')?.dataset.text||'';
  selected={surface,head,sentence,el};currentSentenceText=sentence;currentHead=head;
  const d=localDictionaryEntry(head);
  $('wordTitle').textContent=surface;
  const localIpa=(d?.ipa||[]).filter(Boolean).join(' · ');
  $('ipa').textContent=localIpa||IPA_FALLBACK[surface.toLowerCase()]||IPA_FALLBACK[head]||'…';
  $('wordContext').innerHTML=highlightWordInSentence(sentence,surface);
  $('sentenceZh').textContent='';

  const cs=contextualSense(head,sentence);
  if(cs){
    const extra=d?renderLocalDictionary(d):'';
    $('senseBox').innerHTML=`<strong>本句义</strong><div class="zh">${escapeHtml(cs)}</div>${extra?`<div style="border-top:1px solid var(--line);margin-top:12px;padding-top:10px"><strong>词典常用义</strong>${extra}</div>`:''}${d?`<div class="def" style="margin-top:10px">${escapeHtml(dictionaryAttribution(d))}</div>`:''}`;
  }else if(d){
    $('senseBox').innerHTML=`<strong>词典义</strong>${renderLocalDictionary(d)}<div class="def" style="margin-top:10px">${escapeHtml(dictionaryAttribution(d))}</div>`;
  }else{
    $('senseBox').innerHTML='<strong>词义</strong><div class="zh">本地词典暂无这个词</div><div class="def">这个页面不会再访问境外中文词典；当前本地开放词典对 NGSL 1.2 覆盖 2803/2809。</div>';
  }

  const csList=collocationsForSentence(sentence);
  $('collocSection').style.display=csList.length?'block':'none';
  $('collocChips').innerHTML=csList.map(c=>`<span class="chip">${escapeHtml(c)}</span>`).join('');
  $('knownBtn').textContent=known.has(head)?'✓ 已学':'✓ 标记已学';
  $('favBtn').textContent=favs.has(head)?'★ 已收藏':'☆ 收藏';
  openSheet();

  // Most NGSL words now use bundled IPA. Online lookup is only a fallback.
  if(!localIpa){
    const online=await getOnlinePhonetic(head);
    if(selected?.head===head&&online)$('ipa').textContent=online;
  }
};

function installAudioClose(){
  const stop=document.getElementById('audioStop');
  if(!stop)return;
  const close=stop.cloneNode(false);
  close.id='audioClose';
  close.className=stop.className;
  close.textContent='×';
  close.setAttribute('aria-label','关闭朗读');
  close.setAttribute('title','关闭朗读');
  close.style.fontSize='20px';
  close.style.lineHeight='1';
  close.style.minWidth='36px';
  close.onclick=()=>{
    try{stopSpeech(false)}catch(e){
      if('speechSynthesis' in window)speechSynthesis.cancel();
      document.getElementById('audioBar')?.classList.add('hidden');
    }
  };
  stop.replaceWith(close);
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',installAudioClose);else installAudioClose();

const foot=document.querySelector('.drawer-foot');
if(foot&&!foot.dataset.dictionaryNotice){
  foot.dataset.dictionaryNotice='1';
  foot.insertAdjacentHTML('beforeend','<br><br>普通词典释义随网页本地打包：Open Dictionary v2.0（CC BY-SA 4.0）为主，少量缺词由 FreeDict eng-zho（CC BY-SA 3.0）补充。重点多义词优先显示本项目校过的语境义。');
}
