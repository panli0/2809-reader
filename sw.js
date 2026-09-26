const CACHE='river-year-v9';
const ASSETS=['./','./icon.svg','./index.html','./manifest.json','./app.js','./data-init.js','./dictionary-ngsl.js','./dictionary-local.js','./chapter-1.js','./chapter-2.js','./chapter-3.js','./chapter-4.js','./chapter-5.js','./chapter-6.js','./chapter-7.js','./chapter-8.js','./chapter-9.js','./poly-1.js','./poly-2.js','./poly-3.js','./poly-4.js','./collocations-1.js','./collocations-2.js'];
self.addEventListener('install',e=>{self.skipWaiting();e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)))});
self.addEventListener('activate',e=>e.waitUntil(Promise.all([caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))),self.clients.claim()])));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cp)).catch(()=>{});return res}).catch(()=>caches.match(e.request))) });
