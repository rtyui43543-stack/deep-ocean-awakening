# 深海覺醒・海豚騎士的大冒險

繁體中文海洋冒險遊戲，包含三個關卡、冒險／挑戰兩種模式、珍珠技能與七張海洋知識圖卡。

- [線上遊玩與離線準備](https://rtyui43543-stack.github.io/deep-ocean-awakening/)
- [下載學生離線 ZIP](https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/download/v20.0.0/deep-ocean-awakening-v20-offline.zip)
- [直接下載單一 HTML](https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/download/v20.0.0/deep-ocean-awakening-v20-offline.html)

## 電腦離線遊玩

完整下載 ZIP，解壓縮後雙擊「開始遊戲.html」，用 Chrome、Edge 或 Firefox 開啟。圖片、配樂及海洋圖卡已內嵌，遊玩不需要連線；圖卡資料來源超連結仍需網路。

## 手機與平板

iPhone/iPad 先使用 Safari 連網開啟網站，以分享選單「加入主畫面」，再從該圖示開啟，按「準備手機／平板離線遊玩」並等待完成。Android 或其他裝置可先在瀏覽器準備完成，再用安裝／加入主畫面選單。之後從同一個瀏覽器或主畫面圖示進入；請保留網站資料，清除後需重新連網準備。遊戲使用橫向畫面，旋轉為直向會暫停。

本機 HTML 能否直接執行取決於裝置的瀏覽器與檔案開啟方式，因此手機／平板以網站離線準備方式為主。

## 操作

方向鍵移動，Z 水砲，X 無敵衝刺，P／Esc 暫停。觸控裝置使用畫面下方按鈕。暫停選單提供放棄闖關、返回首頁；已解鎖圖鑑會保留。

第20版強化挑戰模式與技能視覺；遊戲本體與原第20版相同。水砲消耗3能量、冷卻1秒；無敵衝刺消耗5能量、持續2秒、冷卻6秒。

## 配樂與海洋資料

第一、二關："Call to Adventure" Kevin MacLeod (incompetech.com)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三關："Chest of Adventure" — Eldritch Grim，[CC0](https://creativecommons.org/publicdomain/zero/1.0/)。原 MP3 未剪輯／轉碼，播放時有音量調整、淡入淡出、循環銜接與危險事件音量避讓。

完整作者、來源與修改說明見 [配樂署名](credits/配樂署名與修改說明.txt)，也保存在遊戲內「配樂來源」及學生 ZIP。海洋知識為繁體中文改寫，原始來源見 [海洋圖卡來源](credits/海洋圖卡來源.txt)。遊戲美術為使用者提供及製作的遊戲素材，不將圖片或配樂一概宣稱為 CC0。

## 專案與發佈

根目錄的第20版 HTML 是完整遊戲原檔。`docs/game.html` 是內容完全一致的 Pages 遊戲檔；`docs/index.html` 提供學生入口，另有 Service Worker 與安裝資訊供網站離線準備。

`python scripts/build-release.py --site` 產生學生 ZIP 與單一 HTML，並更新 `docs/game.html`；輸出保存在 `.publish/release`。網站入口維護在 `docs`，首次發布時亦可從本機 `.publish/site` 準備目錄複製。若有本機準備目錄，腳本會優先使用它。GitHub Pages 由 `.github/workflows/pages.yml` 發布 `main` 分支的 `docs` 目錄，也可在 Actions 手動執行發布。

下載版本為 `v20.0.0`。製作／檢查暫存檔、原始素材重複檔與個人工作路徑不包含在發佈檔案中。

