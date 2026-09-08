const CACHE='river-year-v4';
const ASSETS=['./','./icon.svg','./index.html','./manifest.json','./app.js','./data-init.js','./chapter-1.js','./chapter-2.js','./chapter-3.js','./chapter-4.js','./chapter-5.js','./chapter-6.js','./chapter-7.js','./chapter-8.js','./chapter-9.js','./sw.js'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return res}))) });
