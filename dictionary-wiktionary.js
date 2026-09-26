const ZHWIKT_API='https://zh.wiktionary.org/w/api.php';

function cleanWikiDefinition(text){
  return (text||'')
    .replace(/\[[0-9]+\]/g,'')
    .replace(/\s+/g,' ')
    .replace(/编辑$/,'')
    .trim();
}

function pickChineseDefinitions(html){
  try{
    const doc=new DOMParser().parseFromString(html,'text/html');
    const headings=[...doc.querySelectorAll('h2,h3,h4,h5')];
    const english=headings.find(h=>/^(英语|英語|英文|English)$/i.test((h.textContent||'').replace(/\[.*?\]/g,'').trim()) || /(英语|英語|English)/i.test(h.textContent||''));
    const candidates=[];
    if(english){
      const level=Number(english.tagName.slice(1));
      let node=english.nextElementSibling;
      while(node){
        if(/^H[1-6]$/.test(node.tagName) && Number(node.tagName.slice(1))<=level)break;
        if(node.matches?.('ol,ul')) candidates.push(...node.querySelectorAll(':scope > li'));
        candidates.push(...(node.querySelectorAll?.('ol > li, ul > li')||[]));
        node=node.nextElementSibling;
      }
    }
    if(!candidates.length)candidates.push(...doc.querySelectorAll('ol > li'));
    const defs=[];
    for(const el of candidates){
      const t=cleanWikiDefinition(el.textContent||'');
      if(!/[\u3400-\u9fff]/.test(t))continue;
      if(t.length<1||t.length>180)continue;
      if(/^(参见|參見|另见|另見|维基|維基|发音|發音|词源|詞源)/.test(t))continue;
      if(!defs.includes(t))defs.push(t);
      if(defs.length>=3)break;
    }
    return defs;
  }catch(e){return []}
}

async function lookupChineseWiktionary(head){
  const key='river.zhwikt.'+head;
  try{
    const cached=localStorage.getItem(key);
    if(cached)return JSON.parse(cached);
  }catch(e){}
  try{
    const u=new URL(ZHWIKT_API);
    u.searchParams.set('action','parse');
    u.searchParams.set('page',head);
    u.searchParams.set('prop','text');
    u.searchParams.set('format','json');
    u.searchParams.set('origin','*');
    const r=await fetch(u.toString(),{cache:'force-cache'});
    if(!r.ok)throw new Error('wiktionary '+r.status);
    const j=await r.json();
    const defs=pickChineseDefinitions(j?.parse?.text?.['*']||'');
    if(defs.length){
      const result={zh:defs.join('；'),source:'中文维基词典'};
      try{localStorage.setItem(key,JSON.stringify(result))}catch(e){}
      return result;
    }
  }catch(e){}
  return null;
}

try{localStorage.removeItem('river.ngsl.dict')}catch(e){}

showWord=async function(el){
  document.querySelectorAll('.word.selected').forEach(x=>x.classList.remove('selected'));
  el.classList.add('selected');
  const surface=el.dataset.word,head=el.dataset.head||headFor(surface),sentence=el.closest('.sentence')?.dataset.text||'';
  selected={surface,head,sentence,el};currentSentenceText=sentence;currentHead=head;
  $('wordTitle').textContent=surface;
  $('ipa').textContent=IPA_FALLBACK[surface.toLowerCase()]||IPA_FALLBACK[head]||'…';
  $('wordContext').innerHTML=highlightWordInSentence(sentence,surface);
  $('sentenceZh').textContent='';
  const cs=contextualSense(head,sentence);
  if(cs){
    $('senseBox').innerHTML=`<strong>本句义</strong><div class="zh">${escapeHtml(cs)}</div><div class="def">这篇故事中人工校过的语境义</div>`;
  }else{
    $('senseBox').innerHTML='<strong>词义</strong><div class="zh">正在查询…</div><div class="def">来源：中文维基词典 · CC BY-SA 4.0</div>';
  }
  const csList=collocationsForSentence(sentence);
  $('collocSection').style.display=csList.length?'block':'none';
  $('collocChips').innerHTML=csList.map(c=>`<span class="chip">${escapeHtml(c)}</span>`).join('');
  $('knownBtn').textContent=known.has(head)?'✓ 已学':'✓ 标记已学';
  $('favBtn').textContent=favs.has(head)?'★ 已收藏':'☆ 收藏';
  openSheet();
  if(!cs){
    const d=await lookupChineseWiktionary(head);
    if(selected?.head===head){
      if(d)$('senseBox').innerHTML=`<strong>词典义</strong><div class="zh">${escapeHtml(d.zh)}</div><div class="def">来源：${d.source} · CC BY-SA 4.0</div>`;
      else $('senseBox').innerHTML='<strong>词义</strong><div class="zh">暂时没查到中文释义</div><div class="def">仍可使用音标、发音、当前句和搭配。</div>';
    }
  }
  const online=await getOnlinePhonetic(head);
  if(selected?.head===head&&online)$('ipa').textContent=online;
};

const foot=document.querySelector('.drawer-foot');
if(foot&&!foot.dataset.dictionaryNotice){
  foot.dataset.dictionaryNotice='1';
  foot.insertAdjacentHTML('beforeend','<br><br>普通词典释义：<a href="https://zh.wiktionary.org/" target="_blank" rel="noopener" style="color:inherit">中文维基词典</a>（CC BY-SA 4.0）。故事中的重点多义词优先显示本项目校过的语境义。');
}
