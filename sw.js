const CACHE='river-year-v3';
const ASSETS=["./","./icon.svg","./index.html","./manifest.json","app.js","chapters-1.js","chapters-2.js","chapters-3.js","chapters-4.js","collocations-1.js","data-init.js","headwords.js","ipa-1.js","ipa-2.js","ipa-3.js","ipa-4.js","poly-1.js","poly-2.js","surface-1.js","surface-2.js","surface-3.js","sw.js"];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return res}))) });
