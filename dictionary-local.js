// Local dictionary UI for the NGSL subset bundled with this site.
// Dictionary data: Open Dictionary v2.0, CC BY-SA 4.0.
// Upstream: English Wiktionary via Wiktextract.

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
function posLabel(pos){
  const labels={noun:'名词',verb:'动词',adj:'形容词',adjective:'形容词',adv:'副词',adverb:'副词',prep:'介词',preposition:'介词',conj:'连词',conjunction:'连词',pron:'代词',pronoun:'代词',det:'限定词',determiner:'限定词',interj:'感叹词',interjection:'感叹词',num:'数词',numeral:'数词',particle:'小品词',phrase:'短语'};
  return labels[String(pos||'').toLowerCase()]||pos||'';
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
    $('senseBox').innerHTML=`<strong>本句义</strong><div class="zh">${escapeHtml(cs)}</div>${extra?`<div style="border-top:1px solid var(--line);margin-top:12px;padding-top:10px"><strong>词典常用义</strong>${extra}</div>`:''}<div class="def" style="margin-top:10px">词典数据：Open Dictionary v2.0 · CC BY-SA 4.0</div>`;
  }else if(d){
    $('senseBox').innerHTML=`<strong>词典义</strong>${renderLocalDictionary(d)}<div class="def" style="margin-top:10px">Open Dictionary v2.0 · CC BY-SA 4.0 · 源自 English Wiktionary/Wiktextract</div>`;
  }else{
    $('senseBox').innerHTML='<strong>词义</strong><div class="zh">本地词典暂无这个词</div><div class="def">仍可使用当前句、搭配和发音。这个页面不会再访问境外中文词典。</div>';
  }

  const csList=collocationsForSentence(sentence);
  $('collocSection').style.display=csList.length?'block':'none';
  $('collocChips').innerHTML=csList.map(c=>`<span class="chip">${escapeHtml(c)}</span>`).join('');
  $('knownBtn').textContent=known.has(head)?'✓ 已学':'✓ 标记已学';
  $('favBtn').textContent=favs.has(head)?'★ 已收藏':'☆ 收藏';
  openSheet();

  // Only fall back to the online phonetic API when the bundled dictionary has no IPA.
  if(!localIpa){
    const online=await getOnlinePhonetic(head);
    if(selected?.head===head&&online)$('ipa').textContent=online;
  }
};

const foot=document.querySelector('.drawer-foot');
if(foot&&!foot.dataset.dictionaryNotice){
  foot.dataset.dictionaryNotice='1';
  foot.insertAdjacentHTML('beforeend','<br><br>普通词典释义和 NGSL 音标已随网页本地打包：Open Dictionary v2.0（CC BY-SA 4.0，源自 English Wiktionary/Wiktextract）。重点多义词优先显示本项目校过的语境义。');
}
