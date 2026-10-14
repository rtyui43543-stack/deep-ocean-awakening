'use strict';

const VERSION = '20.0.1';
const EXPECTED_GAME_BYTES = 41178065;
const SCOPE_URL = new URL(self.registration.scope);
const scopedURL = path => new URL(path, SCOPE_URL).href;
// Each repository path has its own cache namespace, even on the same GitHub Pages origin.
const CACHE_PREFIX = `deep-ocean-${encodeURIComponent(SCOPE_URL.pathname)}-`;
const CACHE_NAME = `${CACHE_PREFIX}${VERSION}`;
const READY_URL = scopedURL('./_offline-ready.json');
const REQUIRED = [
  { path: './index.html', label: '完整遊戲', mime: /text\/html/i, bytes: EXPECTED_GAME_BYTES },
  { path: './game.html', label: '舊網址相容入口', mime: /text\/html/i },
  { path: './downloads.html', label: '下載與離線說明', mime: /text\/html/i },
  { path: './offline.js', label: '離線啟動功能', mime: /(?:java|ecma)script/i },
  { path: './manifest.webmanifest', label: '主畫面設定', mime: /(?:json|manifest)/i },
  { path: './icons/icon-192.png', label: '主畫面圖示', mime: /image\/png/i },
  { path: './icons/icon-512.png', label: '高解析度圖示', mime: /image\/png/i },
  { path: './icons/app-icon.svg', label: '海洋圖示', mime: /image\/svg\+xml/i }
];
const REQUIRED_URLS = REQUIRED.map(asset => scopedURL(asset.path));
const BOOT_URLS = new Set(['./downloads.html', './offline.js', './manifest.webmanifest'].map(scopedURL));
let preparation = null;
const ports = new Set();

const report = message => {
  for (const port of ports) {
    try { port.postMessage(message); } catch { ports.delete(port); }
  }
};

async function readReadyCache(name, expectedVersion) {
  const cache = await caches.open(name);
  const response = await cache.match(READY_URL);
  if (!response) return null;
  let marker;
  try { marker = await response.json(); } catch { return null; }
  if (!marker || !Array.isArray(marker.assets) || typeof marker.version !== 'string') return null;
  if (expectedVersion && (marker.version !== expectedVersion || marker.assets.length !== REQUIRED_URLS.length || !REQUIRED_URLS.every(url => marker.assets.includes(url)))) return null;
  if (!marker.assets.includes(scopedURL('./index.html')) || !marker.assets.includes(scopedURL('./game.html'))) return null;
  if (!marker.assets.every(url => typeof url === 'string' && url.startsWith(SCOPE_URL.href))) return null;
  for (const url of marker.assets) if (!await cache.match(url)) return null;
  return { cache, name, version: marker.version };
}

async function findReadyCache() {
  const names = await caches.keys();
  if (names.includes(CACHE_NAME)) {
    const current = await readReadyCache(CACHE_NAME, VERSION);
    if (current) return current;
  }
  // A newly activated worker may still use the previous complete release until preparation succeeds.
  for (const name of names.filter(name => name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME).reverse()) {
    const old = await readReadyCache(name);
    if (old) return old;
  }
  return null;
}

async function cleanupOldReadyCaches() {
  if (!await readReadyCache(CACHE_NAME, VERSION)) return;
  for (const name of await caches.keys()) {
    if (name.startsWith(CACHE_PREFIX) && name !== CACHE_NAME && await readReadyCache(name)) await caches.delete(name);
  }
}

async function putAsset(cache, asset, completed) {
  const url = scopedURL(asset.path);
  const notify = receivedBytes => report({ type: 'PROGRESS', version: VERSION, completed, total: REQUIRED.length, label: asset.label, receivedBytes });
  notify(0);
  const response = await fetch(new Request(url, { cache: 'reload', credentials: 'same-origin' }));
  if (!response.ok || response.type === 'opaque' || response.type === 'opaqueredirect' || !asset.mime.test(response.headers.get('content-type') || '')) {
    throw new Error(`未能取得完整的${asset.label}`);
  }
  let received = 0;
  if (response.body && typeof ReadableStream !== 'undefined') {
    const reader = response.body.getReader();
    let lastUpdate = 0;
    const stream = new ReadableStream({
      async pull(controller) {
        try {
          const result = await reader.read();
          if (result.done) { controller.close(); return; }
          received += result.value.byteLength;
          if (Date.now() - lastUpdate >= 250) { lastUpdate = Date.now(); notify(received); }
          controller.enqueue(result.value);
        } catch (error) { controller.error(error); }
      },
      cancel(reason) { return reader.cancel(reason); }
    });
    const headers = new Headers(response.headers);
    // Fetch already decoded network compression before yielding these bytes.
    headers.delete('content-encoding');
    headers.delete('content-length');
    try { await cache.put(url, new Response(stream, { status: response.status, statusText: response.statusText, headers })); }
    catch (error) { try { await reader.cancel(error); } catch {} throw error; }
  } else {
    const bytes = await response.arrayBuffer();
    received = bytes.byteLength;
    await cache.put(url, new Response(bytes, { status: response.status, statusText: response.statusText, headers: response.headers }));
  }
  if (asset.bytes && received !== asset.bytes) {
    const error = new Error('遊戲檔案未完整下載');
    error.code = 'INCOMPLETE_GAME';
    throw error;
  }
  notify(received);
}

async function prepareOffline() {
  if (await readReadyCache(CACHE_NAME, VERSION)) {
    await self.skipWaiting();
    report({ type: 'READY', ready: true, version: VERSION });
    return;
  }
  // Only the incomplete candidate is removed; an older complete release remains usable.
  await caches.delete(CACHE_NAME);
  const cache = await caches.open(CACHE_NAME);
  try {
    for (let i = 0; i < REQUIRED.length; i++) await putAsset(cache, REQUIRED[i], i);
    await cache.put(READY_URL, new Response(JSON.stringify({ version: VERSION, assets: REQUIRED_URLS, preparedAt: new Date().toISOString() }), { headers: { 'content-type': 'application/json' } }));
    if (!await readReadyCache(CACHE_NAME, VERSION)) throw new Error('離線資料不完整');
  } catch (error) {
    await caches.delete(CACHE_NAME);
    throw error;
  }
  await cleanupOldReadyCaches();
  await self.skipWaiting();
  report({ type: 'READY', ready: true, version: VERSION });
}

self.addEventListener('install', event => {
  // No automatic 40 MB download. An update does not replace the active release before explicit preparation.
  event.waitUntil(Promise.resolve());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    await cleanupOldReadyCaches();
    await self.clients.claim();
  })());
});

self.addEventListener('message', event => {
  const port = event.ports?.[0];
  if (!port) return;
  if (event.data?.type === 'CHECK_STATUS') {
    event.waitUntil((async () => {
      const ready = await findReadyCache();
      port.postMessage({ type: 'STATUS', ready: Boolean(ready), version: ready?.version || VERSION });
    })());
  } else if (event.data?.type === 'PREPARE_OFFLINE') {
    ports.add(port);
    if (!preparation) {
      preparation = prepareOffline().catch(error => {
        report({ type: 'ERROR', ready: false, version: VERSION, name: error.name || 'Error', code: error.code, message: error.message });
      }).finally(() => { preparation = null; ports.clear(); });
    }
    event.waitUntil(preparation);
  }
});

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const requestURL = new URL(event.request.url);
  if (requestURL.origin !== SCOPE_URL.origin || !requestURL.href.startsWith(SCOPE_URL.href)) return;
  requestURL.search = '';
  requestURL.hash = '';
  if (requestURL.href === SCOPE_URL.href) requestURL.href = scopedURL('./index.html');
  const key = requestURL.href;
  if (!REQUIRED_URLS.includes(key)) return;
  event.respondWith((async () => {
    const ready = await findReadyCache();
    const cached = ready && await ready.cache.match(key);
    if (BOOT_URLS.has(key)) {
      // The small download/settings page can show updates without replacing the cached complete game.
      try {
        const online = await fetch(event.request);
        if (online.ok) return online;
        if (cached) return cached;
        return online;
      } catch (error) { if (cached) return cached; throw error; }
    }
    if (cached) return cached;
    return fetch(event.request);
  })());
});
