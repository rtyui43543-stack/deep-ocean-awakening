(() => {
  'use strict';
  // Update only an already-installed worker. Never reload a game in progress,
  // register for first-time visitors, clear player data, or download an offline pack.
  if (!('serviceWorker' in navigator) || !window.isSecureContext || !navigator.onLine) return;
  navigator.serviceWorker.getRegistration('./').then(registration => {
    if (registration) return registration.update();
  }).catch(() => { /* An unavailable network must not interrupt the game. */ });
})();
