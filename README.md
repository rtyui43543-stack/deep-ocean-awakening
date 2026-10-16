# 深海覺醒・海豚騎士的大冒險

繁體中文海洋冒險遊戲，包含三個關卡、冒險／挑戰兩種模式、珍珠技能與七張海洋知識圖卡。

- [線上遊玩](https://rtyui43543-stack.github.io/deep-ocean-awakening/)
- [下載與離線準備](https://rtyui43543-stack.github.io/deep-ocean-awakening/downloads.html)
- [下載玩家離線 ZIP](https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/download/v24.0.0/deep-ocean-awakening-v24-offline.zip)
- [直接下載單一 HTML](https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/download/v24.0.0/deep-ocean-awakening-v24-offline.html)
- [下載原始完整資料包（含 Word、文字文件與素材索引）](https://github.com/rtyui43543-stack/deep-ocean-awakening/releases/download/v24.0.0/deep-ocean-awakening-v24-complete.zip)

本次只打包與發佈。網站首頁、單檔下載與離線包裡的遊戲 HTML，均與提供的原檔逐位元一致，沒有新增遊戲畫面元素或修改玩法。

## 電腦離線遊玩

完整下載 ZIP，解壓縮後雙擊「開始遊戲.html」，用 Chrome、Edge 或 Firefox 開啟。圖片、配樂及海洋圖卡已內嵌，遊玩不需要連線；圖卡資料來源超連結仍需網路。

## 手機與平板

先連網開啟獨立的[下載與離線準備頁](https://rtyui43543-stack.github.io/deep-ocean-awakening/downloads.html)，按「準備手機／平板離線遊玩」並等待成功，再點「返回遊戲」。將遊戲網址加入書籤，之後從同一個瀏覽器進入。iPhone／iPad 使用 Safari，Android 可使用 Chrome。若改從主畫面捷徑開啟，請在該視窗確認離線準備完成。保留網站資料，清除後需重新準備；遊戲使用橫向畫面。

本機 HTML 能否直接執行取決於裝置的瀏覽器與檔案開啟方式，因此手機／平板以網站離線準備方式為主。

## 操作

方向鍵移動，Z 水砲，X 無敵衝刺，P／Esc 暫停。觸控裝置使用左下搖桿及右下技能鍵。暫停選單提供放棄闖關、返回首頁；已解鎖圖鑑保存在該瀏覽器本機。

水砲消耗3能量、冷卻1秒；無敵衝刺消耗5能量、持續2秒、冷卻6秒。所有畫面、素材、關卡與操作規則依提供的第24版原檔保留。

## 配樂與海洋資料

第一、二關："Call to Adventure" Kevin MacLeod (incompetech.com)，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。第三關："Chest of Adventure" — Eldritch Grim，[CC0](https://creativecommons.org/publicdomain/zero/1.0/)。原 MP3 未剪輯／轉碼，播放時有音量調整、淡入淡出、循環銜接與危險事件音量避讓。

完整作者、來源與修改說明見 [配樂署名](credits/配樂署名與修改說明.txt)，也保存在遊戲內「配樂來源」及學生 ZIP。海洋知識為繁體中文改寫，原始來源見 [海洋圖卡來源](credits/海洋圖卡來源.txt)。遊戲美術為使用者提供及製作的遊戲素材，不將圖片或配樂一概宣稱為 CC0。

## 專案與發佈

本次來源是 `29_深海覺醒_完整資料包.zip`；內含遊戲為第24版，25～29是文件流水編號。根目錄的 `24_深海覺醒_技能按鈕主題美化.html` 是此次發佈原檔，四份隨附文件原樣保存在 [handoff-v24](handoff-v24/)。完整 ZIP 發佈在 Releases，僅改為便於下載的英文檔名，壓縮檔內容與位元組完全不變。

`docs/index.html` 是原檔的完整複本，沒有注入按鈕、樣式或腳本。`docs/downloads.html` 獨立提供下載及離線準備；舊 `docs/game.html` 網址導向遊戲首頁。原檔頁籤仍顯示「23版」，為遵守原樣發佈而保留。

遊戲 SHA-256：`4f99402bb8aeb1cbf7833768be52fbfbd2e01ac5335af2c1fd3c24cb146d89ac`。Releases 的 `release-manifest.json` 提供遊戲、兩種 ZIP 及隨附文件校驗值。

`python scripts/build-site.py` 直接複製原檔並更新離線檔案大小檢查。`python scripts/build-release.py --site --source-package "原始完整資料包.zip的路徑"` 產生玩家 ZIP、單檔 HTML、完整資料包及校驗清單，輸出在 `.publish/release-v24`。GitHub Pages 由 `.github/workflows/pages.yml` 發布 `main` 分支的 `docs` 目錄。

下載版本為 `v24.0.0`。舊版保留供回溯；影片剪輯專案及其他無關工作檔不在此次發佈範圍。

