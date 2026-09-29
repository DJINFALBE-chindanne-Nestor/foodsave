// ============================================================
// SERVICE WORKER - Cache et mode hors ligne
// ============================================================

const CACHE_NAME = 'foodsave-v1';

const FICHIERS_CACHE = [
    '/',
    '/annonces',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('Service Worker : mise en cache initiale');
            return cache.addAll(FICHIERS_CACHE).catch((err) => {
                console.log('Cache partiel :', err);
            });
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((noms) => {
            return Promise.all(
                noms.filter((nom) => nom !== CACHE_NAME)
                    .map((nom) => caches.delete(nom))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    if (event.request.url.includes('/api/')) return;
    if (event.request.url.startsWith('chrome-extension://')) return;

    event.respondWith(
        fetch(event.request)
            .then((reponse) => {
                if (reponse && reponse.status === 200) {
                    const clone = reponse.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, clone);
                    });
                }
                return reponse;
            })
            .catch(() => {
                return caches.match(event.request).then((cache) => {
                    if (cache) return cache;
                    return new Response(
                        '<h1>Hors ligne</h1><p>Verifiez votre connexion internet.</p>',
                        { headers: { 'Content-Type': 'text/html' } }
                    );
                });
            })
    );
});
