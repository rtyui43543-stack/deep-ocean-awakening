(() => {
  'use strict';
  const CURRENT_VERSION = '24.0.0';
  const button = document.getElementById('btn-prepare-offline');
  const status = document.getElementById('offline-status');
  if (!button || !status) return;

  let preparing = false;
  let showingReady = false;
  status.setAttribute('aria-live', 'polite');
  status.setAttribute('role', 'status');

  const show = (message, state) => {
    status.textContent = message;
    status.dataset.state = state;
  };
  const displayReady = () => {
    showingReady = true;
    button.textContent = '檢查離線更新';
    show('離線遊戲已準備完成。之後請從目前使用的瀏覽器或同一個主畫面圖示進入；清除網站資料後需重新準備。', 'ready');
  };
  const displayOutdated = () => {
    showingReady = true;
    button.textContent = '更新離線遊戲';
    show('舊版離線遊戲仍可使用。更新後可使用目前版本的遊戲內容。請在連網時按「更新離線遊戲」。', 'outdated');
  };
  const friendlyError = error => {
    if (error?.name === 'QuotaExceededError') return '裝置的儲存空間不足，請釋放空間後重試。';
    if (error?.code === 'INCOMPLETE_GAME') return '遊戲檔案未完整下載，請重新準備。';
    return '離線下載未完成，請確認網路與可用儲存空間後重試。';
  };
  const waitForWorker = (worker, activatedOnly = false) => new Promise((resolve, reject) => {
    const finish = () => {
      if ((!activatedOnly && worker.state === 'installed') || worker.state === 'activated') {
        cleanup(); resolve(worker);
      } else if (worker.state === 'redundant') {
        cleanup(); reject(new Error('離線更新中斷'));
      }
    };
    const cleanup = () => { clearTimeout(timer); worker.removeEventListener('statechange', finish); };
    const timer = setTimeout(() => { cleanup(); reject(new Error('離線更新逾時')); }, 30000);
    worker.addEventListener('statechange', finish);
    finish();
  });
  const waitForController = worker => new Promise((resolve, reject) => {
    const finish = () => {
      if (navigator.serviceWorker.controller === worker) { cleanup(); resolve(); }
    };
    const cleanup = () => { clearTimeout(timer); navigator.serviceWorker.removeEventListener('controllerchange', finish); };
    const timer = setTimeout(() => { cleanup(); reject(new Error('離線遊戲尚未接管此頁')); }, 10000);
    navigator.serviceWorker.addEventListener('controllerchange', finish);
    finish();
  });
  const send = (worker, type, progress) => new Promise((resolve, reject) => {
    const channel = new MessageChannel();
    let timer;
    const cleanup = () => { clearTimeout(timer); channel.port1.close(); };
    const resetTimer = () => {
      clearTimeout(timer);
      timer = setTimeout(() => { cleanup(); reject(new Error('離線下載逾時')); }, type === 'CHECK_STATUS' ? 5000 : 120000);
    };
    channel.port1.onmessage = event => {
      const data = event.data || {};
      resetTimer();
      if (data.type === 'PROGRESS') {
        progress?.(data);
      } else if (data.type === 'READY' || data.type === 'STATUS') {
        cleanup(); resolve(data);
      } else if (data.type === 'ERROR') {
        cleanup();
        const error = new Error(data.message || '離線下載失敗');
        error.name = data.name || 'Error';
        error.code = data.code;
        reject(error);
      }
    };
    resetTimer();
    worker.postMessage({ type }, [channel.port2]);
  });

  if (!('serviceWorker' in navigator) || !window.isSecureContext) {
    button.disabled = true;
    show('這個瀏覽器無法準備主畫面離線版。請使用上方的下載按鈕取得離線遊戲。', 'unavailable');
    return;
  }

  const checkCurrent = async () => {
    if (preparing || !navigator.serviceWorker.controller) return;
    try {
      const result = await send(navigator.serviceWorker.controller, 'CHECK_STATUS');
      if (result.ready && result.version === CURRENT_VERSION) displayReady();
      else if (result.ready) displayOutdated();
      else if (showingReady) {
        showingReady = false;
        button.textContent = '準備離線遊玩';
        show('離線資料已被清除，請連線後重新準備。', 'idle');
      }
    } catch { /* The download action remains available if an old worker does not reply. */ }
  };
  navigator.serviceWorker.addEventListener('controllerchange', checkCurrent);
  checkCurrent();

  button.addEventListener('click', async () => {
    if (preparing) return;
    preparing = true;
    button.disabled = true;
    button.textContent = '準備中…';
    show('正在準備完整離線遊戲。請保持此頁開啟。', 'preparing');
    try {
      const registration = await navigator.serviceWorker.register('./sw.js', { scope: './', updateViaCache: 'none' });
      const candidate = registration.installing || registration.waiting || registration.active;
      if (!candidate) throw new Error('沒有離線工作程式');
      const worker = await waitForWorker(candidate);
      const result = await send(worker, 'PREPARE_OFFLINE', progress => {
        const mb = progress.receivedBytes ? `（已下載 ${(progress.receivedBytes / 1048576).toFixed(1)} MB）` : '';
        show(`正在準備 ${progress.completed + 1}/${progress.total}：${progress.label}${mb}。請保持此頁開啟。`, 'preparing');
      });
      if (!result.ready || result.version !== CURRENT_VERSION) throw new Error('未確認目前版本完整下載');
      await waitForWorker(worker, true);
      await waitForController(worker);
      displayReady();
    } catch (error) {
      showingReady = false;
      button.textContent = '重新準備離線遊戲';
      show(friendlyError(error), 'error');
    } finally {
      preparing = false;
      button.disabled = false;
    }
  });
})();
