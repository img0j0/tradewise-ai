// Service Worker for TradeWise AI PWA
const CACHE_NAME = 'tradewise-ai-v1.0.0';
const OFFLINE_URL = '/offline';

// Assets to cache for offline use
const urlsToCache = [
    '/',
    '/offline',
    '/static/css/main.css',
    '/static/js/dashboard.js',
    '/static/js/micro_interactions.js',
    '/static/js/error_recovery.js',
    '/manifest.json'
];

// Install event - cache essential resources
self.addEventListener('install', event => {
    console.log('[SW] Installing service worker');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching essential resources');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('[SW] Installation complete');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('[SW] Installation failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('[SW] Activating service worker');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[SW] Activation complete');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip external requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version if available
                if (response) {
                    console.log('[SW] Serving from cache:', event.request.url);
                    return response;
                }

                // Try to fetch from network
                return fetch(event.request)
                    .then(response => {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response for caching
                        const responseToCache = response.clone();

                        // Cache successful responses for future use
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                // Only cache GET requests for static resources
                                if (event.request.method === 'GET' && 
                                    (event.request.url.includes('/static/') || 
                                     event.request.url === self.location.origin + '/')) {
                                    cache.put(event.request, responseToCache);
                                }
                            });

                        return response;
                    })
                    .catch(() => {
                        // Network failed, try to serve appropriate offline content
                        console.log('[SW] Network failed, serving offline content');
                        
                        // For navigation requests, serve offline page
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                        
                        // For API requests, return cached watchlist/portfolio data if available
                        if (event.request.url.includes('/api/')) {
                            return caches.match(event.request)
                                .then(cachedResponse => {
                                    if (cachedResponse) {
                                        return cachedResponse;
                                    }
                                    // Return offline API response
                                    return new Response(JSON.stringify({
                                        offline: true,
                                        message: 'This data is not available offline'
                                    }), {
                                        headers: { 'Content-Type': 'application/json' }
                                    });
                                });
                        }
                        
                        // For other requests, just fail
                        return new Response('Offline', { status: 503 });
                    });
            })
    );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
    console.log('[SW] Background sync event:', event.tag);
    
    if (event.tag === 'background-sync-watchlist') {
        event.waitUntil(syncWatchlistData());
    }
    
    if (event.tag === 'background-sync-alerts') {
        event.waitUntil(syncAlertData());
    }
});

// Push notification handler
self.addEventListener('push', event => {
    console.log('[SW] Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New market update available',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/icons/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icons/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('TradeWise AI', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
    console.log('[SW] Notification click received');
    
    event.notification.close();
    
    if (event.action === 'explore') {
        // Open the app to the relevant section
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

// Helper functions for background sync
async function syncWatchlistData() {
    try {
        // Sync any offline watchlist changes
        const offlineChanges = await getOfflineWatchlistChanges();
        if (offlineChanges.length > 0) {
            await postDataToServer('/api/watchlists/sync', offlineChanges);
            await clearOfflineWatchlistChanges();
        }
        console.log('[SW] Watchlist sync completed');
    } catch (error) {
        console.error('[SW] Watchlist sync failed:', error);
        throw error;
    }
}

async function syncAlertData() {
    try {
        // Sync any offline alert changes
        const offlineChanges = await getOfflineAlertChanges();
        if (offlineChanges.length > 0) {
            await postDataToServer('/api/alerts/sync', offlineChanges);
            await clearOfflineAlertChanges();
        }
        console.log('[SW] Alert sync completed');
    } catch (error) {
        console.error('[SW] Alert sync failed:', error);
        throw error;
    }
}

async function getOfflineWatchlistChanges() {
    // Get offline changes from IndexedDB or localStorage
    return JSON.parse(localStorage.getItem('offline-watchlist-changes') || '[]');
}

async function getOfflineAlertChanges() {
    // Get offline changes from IndexedDB or localStorage
    return JSON.parse(localStorage.getItem('offline-alert-changes') || '[]');
}

async function clearOfflineWatchlistChanges() {
    localStorage.removeItem('offline-watchlist-changes');
}

async function clearOfflineAlertChanges() {
    localStorage.removeItem('offline-alert-changes');
}

async function postDataToServer(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
    }
    
    return response.json();
}

// Message handler for communication with main thread
self.addEventListener('message', event => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_PORTFOLIO_DATA') {
        // Cache portfolio data for offline access
        caches.open(CACHE_NAME).then(cache => {
            cache.put('/api/portfolio', new Response(JSON.stringify(event.data.portfolio)));
        });
    }
    
    if (event.data && event.data.type === 'CACHE_WATCHLIST_DATA') {
        // Cache watchlist data for offline access
        caches.open(CACHE_NAME).then(cache => {
            cache.put('/api/watchlists', new Response(JSON.stringify(event.data.watchlist)));
        });
    }
});

console.log('[SW] Service Worker loaded successfully');