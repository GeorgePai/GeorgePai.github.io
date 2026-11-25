# Potato Pai 網站 — 交接文件

最後更新：2026-11-25

## 網址
- 網站：https://georgepai.github.io/ （repo GeorgePai/GeorgePai.github.io，main 根目錄，GitHub Pages）
- Alpha Potato：https://georgepai.github.io/AlphaPotato/ （repo GeorgePai/AlphaPotato，main）
- 遊戲與網站同一個網域 → 玩家存檔（localStorage）、主畫面捷徑不受影響。不要搬遊戲、不要改自訂網域。

## 分工
- 遊戲開發 session（alpha potato - game dev）：改 AlphaPotato 的 source，打包推 release。
- 網站管理 session（本文件）：只管網站＋把 release 部署到 main（要等 Pai 說「OK，上架」）。開發者版預覽網址不放上網站，也不寫進這份公開文件。不讀不寫 source、leaderboard/、排行榜伺服器 lol-rank。

## 網站檔案
| 檔案 | 用途 |
|---|---|
| index.html | 整個網站（單檔，含 CSS/JS） |
| games.json | 遊戲清單 `{updated, games:[game.json…]}`；icon 改成網站內路徑 |
| games/<id>/icon-512.png | 從遊戲 release 複製來的圖示 |
| assets/cubic11.woff2 | 俐方體 11 號（從遊戲 index.html 的 G_FONT 抽出的子集，5658 字；缺字自動用系統字型） |
| assets/icon-32.png / icon-180.png | 網站 favicon、主畫面圖示（暫用 Alpha Potato 的） |
| stats/ | 瀏覽人數伺服器 pp-stats（Cloudflare Worker＋D1） |

設計：黑白灰像素風＋暖米色（--potato #e3d3ae）。手機直屏優先，檢查 390×844、360×780、1280×720；文字不可截斷/重疊/超框，並排元件等寬等距等高。

## 即時在線人數
- 每款讀 game.json 的 `online`（目前 https://lol-rank.leafoflegends.workers.dev/online → `{ok,game,n,t}`），不寫死。
- 每 30 秒抓一次，分頁不可見時停止。失敗顯示「—」。

## 網站瀏覽人數（pp-stats）
- 程式：stats/src/index.js、stats/wrangler.toml。
- 端點：POST /hit（+1 並回傳 `{ok,views}`）、GET /stats。前端 localStorage 擋同裝置 30 分鐘，伺服器記憶體擋同 IP 30 分鐘。
- D1 表會在第一次請求時自動建立（counters: k, v）。
- 狀態：**已上線** https://pp-stats.leafoflegends.workers.dev （/stats 可直接看總數）
  - D1：pp-stats，id 0052c889-0e85-4b8b-8ced-3555b9947daa
  - Worker：pp-stats（Workers Builds 連 GeorgePai/GeorgePai.github.io，根目錄 /stats，main 推了就自動部署；Preview builds 關閉）
  - Cloudflare 帳號 33fe09f6bdada40ccd22be6e28edd124（和 lol-rank 同一個；Pai 用 Apple ID 登入）
  - 改程式：改 stats/ → 推 main → 到 Cloudflare 的 pp-stats → Deployments 確認 Success。
- 雲端 shell 連不到 Cloudflare／workers.dev：要看部署或測端點，用桌面 App 內建瀏覽器或 Claude in Chrome。

## 長期路線圖（2026-11-25 Pai 同意方向）

原則：最低成本、Pai 不用動手、不存密碼。資安細節不寫在這個公開 repo，放在 Pai 的 Mac 備份資料夾 SECURITY-NOTES.md 和 Potato Pai 專案文件。

1. 資安修正（遊戲開發 session 負責）：管理權限、頻率限制已修（2026-11-25）；原始碼搬私人 repo 待辦。
2. 壓力測試：用測試用伺服器（不打正式伺服器），在 Pai 的 VPS 模擬 500～1,000 位玩家。
3. 升級 Workers Paid（$5/月）：每日請求接近 5 萬次時升級並設帳單警示（付費，要 Pai 確認）。
4. 雲端存檔：掛在遊戲現有的玩家身分上，D1 每玩家一列，只在戰鬥結束／購買時寫入；存檔碼改成短期換機碼。
5. 「用 Google 登入」綁定：不存密碼，盡量不存 email；需要隱私權頁＋刪除帳號功能。
6. 全站帳號：同網域，存檔依（帳號, 遊戲）分開，新遊戲共用。

負載估算：每位玩家約 100～250 次請求／小時。Workers 免費每天 10 萬次（台灣 08:00 重置，超過就失敗）≈ 400～1,000 玩家·小時/天；Paid $5/月含 1,000 萬次/月 ≈ 1,300～3,300 玩家·小時/天。D1 免費每天寫入 10 萬列。

## 上架新版遊戲（AlphaPotato）
**2026-11-25 起：release 有新版不會自動上架。** 流程是遊戲開發推 release → Pai 用開發者版預覽試玩 → Pai 說「OK，上架」→ 才部署到 main。發現 release 比 main 新時，只回報版本，不部署。
1. `git ls-remote https://github.com/GeorgePai/AlphaPotato` 比對 release 與 main，或比對兩邊 game.json 的 version。
2. clone release（/home/claude/ap-release）與 main（/home/claude/ap-main），depth 1。
3. 驗證：release 的 game.json version＝version.json 的 v；Playwright＋/usr/bin/google-chrome 開 index.html，0 個 pageerror。
4. 同步：清空 ap-main（保留 .git）→ 複製 release 全部檔案（含 .nojekyll）→ commit「deploy V版本」→ `git -c push.negotiate=true push origin HEAD:main`；1～2 分鐘後確認 https://georgepai.github.io/AlphaPotato/version.json。（環境沒有 rsync，用 tar 複製。）
5. 更新網站 games.json（從 game.json 整理，icon 改網站路徑並複製圖示）→ 推網站 main。
6. 回報 Pai：版本、網站連結、遊戲連結。
- 回滾：main 退回前一個 deploy commit 再推（先問 Pai）。

## 部署紀錄
- 2026-11-25：AlphaPotato main ← release（V4.4，補上 game.json），commit 1e56506。
- 2026-11-25：網站第一版上線；pp-stats 上線，網站開始顯示瀏覽人數。
- 2026-11-25：AlphaPotato main ← release（V4.5），commit 50928ae；網站 games.json 同步 V4.5。

## 待 Pai 決定 / 待辦
- 網站自己的圖示目前沿用 Alpha Potato 圖示，要不要做 Potato Pai 專屬圖示。

## 工作規則
- 回覆繁中、結論先講、精簡，每次附網站與相關連結。
- 給 Pai 的東西要簡單：能自動就自動，要他動手只給一個步驟。
- Mac 備份資料夾：/Users/paiju/Desktop/Claude/PotatoPai/
- 「交接」：更新本檔、推 GitHub、備份 Mac，回覆可貼上的接手指令，提醒改名（目前 session 改「potato pai - 網站管理 (retired)」）。
