# Potato Pai 網站 — 交接文件

最後更新：2026-11-25

## 網址（2026-11-25 起搬家中：新網址 potatopai.com）
- **新網站：https://potatopai.com/**（www 自動轉到這裡）；新遊戲網址：https://potatopai.com/AlphaPotato/
- 託管：Cloudflare Workers 靜態檔案，推 main 自動部署。
  - Worker「potatopai-site」：連網站 repo（根目錄 /），設定在 wrangler.toml＋.assetsignore（不公開 stats/、HANDOFF.md、wrangler.toml）。路由 potatopai.com/*。
  - Worker「alphapotato」：連 AlphaPotato main（根目錄 /），設定在 main 的 wrangler.toml（建置時把檔案複製到 dist/AlphaPotato/）。路由 potatopai.com/AlphaPotato*（比網站的路由精確，優先）。
  - DNS：potatopai.com、www 都是 A 192.0.2.1（Proxied，只是讓流量進 Cloudflare）；轉址規則「Redirect from WWW to root」。
  - 網域在 Cloudflare 註冊（自動續約，每年 $11.17）。
- 舊網址 GitHub Pages 不另外處理（Pai 2026-11-25 決定），但因為是同一個 repo，會跟著一起更新。主網址一律是 potatopai.com。

## 舊網址（GitHub Pages）
- 網站：https://georgepai.github.io/ （repo GeorgePai/GeorgePai.github.io，main 根目錄，GitHub Pages）
- Alpha Potato：https://georgepai.github.io/AlphaPotato/ （repo GeorgePai/AlphaPotato，main）
- 遊戲與網站同一個網域 → 玩家存檔（localStorage）、主畫面捷徑不受影響。不要搬遊戲、不要改自訂網域。

## 分工
- 遊戲開發 session（alpha potato - game dev）：改 AlphaPotato 的 source，打包推 release。
- 網站管理 session（本文件）：只管網站＋把 release 部署到 main（要等 Pai 說「OK，上架」）。開發者版預覽網址不放上網站，也不寫進這份公開文件。不讀不寫 source、leaderboard/、排行榜伺服器 lol-rank。

## 網站檔案
| 檔案 | 用途 |
|---|---|
| index.html | 整個網站（單檔，含 CSS/JS）：RPG 風標題「Potato Pai」（Lilita One＋雙層框＋流動光澤）＋左右滑遊戲卡片（影片封面、名稱、標籤、開始玩／更新內容） |
| games.json | 遊戲清單 `{updated, games:[game.json…]}`；icon 改成網站內路徑；**media（poster、mp4、webm）是網站自己加的欄位，從 game.json 重新整理時要保留** |
| games/alphapotato/highlight-v2.mp4/.webm、poster.jpg | 卡片封面精華影片（約 16 秒、2 MB，實機逐格錄製）與封面圖；換影片要用新檔名，避免快取 |
| assets/lilita-one.woff2 | 標題字體 Lilita One（SIL OFL，授權檔 lilita-one-LICENSE.txt） |
| games/<id>/icon-512.png | 從遊戲 release 複製來的圖示 |
| assets/cubic11.woff2 | 俐方體 11 號（從遊戲 index.html 的 G_FONT 抽出的子集，5658 字；缺字自動用系統字型） |
| assets/icon-32.png / icon-180.png | 網站 favicon、主畫面圖示（暫用 Alpha Potato 的） |
| stats/ | 瀏覽人數伺服器 pp-stats（Cloudflare Worker＋D1） |
| move/index.html | 一鍵搬存檔頁：在舊網址讀出 ap_ 存檔（不搬 ap_rk_ss、ap_sid、ap_dev、ap_pin、ap_adm），放在網址 # 後面帶到 https://potatopai.com/move/ 寫入；舊網址留備份並寫 ap_moved；新網址已有存檔時要玩家確認 |

設計：黑白灰像素風＋暖米色（--potato #e3d3ae）。手機直屏優先，檢查 390×844、360×780、1280×720；文字不可截斷/重疊/超框，並排元件等寬等距等高。

## 即時在線人數
- 每款讀 game.json 的 `online`（目前 https://ap-rank.alphapotato.workers.dev/online → `{ok,game,n,t}`），不寫死。
- 每 30 秒抓一次，分頁不可見時停止。失敗顯示「—」。

## 網站瀏覽人數（pp-stats）
- 程式：stats/src/index.js、stats/wrangler.toml。
- 端點：POST /hit（+1 並回傳 `{ok,views}`）、GET /stats。前端 localStorage 擋同裝置 30 分鐘，伺服器記憶體擋同 IP 30 分鐘。
- D1 表會在第一次請求時自動建立（counters: k, v）。
- 狀態：**已上線** https://pp-stats.alphapotato.workers.dev （/stats 可直接看總數）
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
4. 同步：清空 ap-main（保留 .git 和 **wrangler.toml**——Cloudflare 設定只在 main）→ 複製 release 全部檔案（含 .nojekyll）→ commit「deploy V版本」→ `git -c push.negotiate=true push origin HEAD:main`；1～2 分鐘後確認 https://potatopai.com/AlphaPotato/version.json（Cloudflare 自動建置）和 https://georgepai.github.io/AlphaPotato/version.json（GitHub Pages）。（環境沒有 rsync，用 tar 複製。）
5. 更新網站 games.json（從 game.json 整理，icon 改網站路徑並複製圖示，**保留 media 欄位**）→ 推網站 main。
6. 回報 Pai：版本、網站連結、遊戲連結。
- 回滾：main 退回前一個 deploy commit 再推（先問 Pai）。

## 部署紀錄
- 2026-11-25：AlphaPotato main ← release（V4.4，補上 game.json），commit 1e56506。
- 2026-11-25：網站第一版上線；pp-stats 上線，網站開始顯示瀏覽人數。
- 2026-11-25：AlphaPotato main ← release（V4.5），commit 50928ae；網站 games.json 同步 V4.5。
- 2026-11-25：AlphaPotato main ← release（V4.5.4，Pai 說上架）。
- 2026-11-25：Pai 決定：舊網址不另外處理、不提醒舊玩家，新網址 potatopai.com 為主。一鍵搬存檔頁 /move/ 留著備用，不主動公開。
- 2026-11-25：AlphaPotato main ← release（V4.5.3，Pai 說 OK 上架），commit 52b0b9c；兩個網址同時更新。
- 2026-11-25：AlphaPotato main ← release（V4.5.5，排行榜搬到 ap-rank），commit 2c065f0。
- 2026-11-25：新版首頁上線（RPG 標題、左右滑卡片、實機精華影片）；Cloudflare 子網域改名 alphapotato，瀏覽人數改 pp-stats.alphapotato.workers.dev，在線人數改 ap-rank.alphapotato.workers.dev。
- 2026-11-25：買 potatopai.com；網站與遊戲上線到 Cloudflare（Worker potatopai-site、alphapotato）；pp-stats 允許新網域。

## 待 Pai 決定 / 待辦
- 原始碼搬私人 repo 進行中（遊戲開發處理）。
- VPS 壓力測試：先等等。Workers Paid：每日請求接近 5 萬次再提醒 Pai。
- 網站自己的圖示目前沿用 Alpha Potato 圖示，要不要做 Potato Pai 專屬圖示。

## 工作規則
- 回覆繁中、結論先講、精簡，每次附網站與相關連結。
- 給 Pai 的東西要簡單：能自動就自動，要他動手只給一個步驟。
- Mac 備份資料夾：/Users/paiju/Desktop/Claude/PotatoPai/
- 「交接」：見下方「交接機制」。

## 交接機制（Pai 說「交接」時）
- 新 session 名稱一律「potato pai - 網站管理」；舊的改名「potato pai - 網站管理 (retired)」。
- 交接 prompt 是私人的：Potato Pai 專案文件 `claude/handoff-prompt.md`（Mac 備份：PotatoPai/HANDOFF-PROMPT.md）。私人資安備忘：`claude/security-notes.md`（Mac：PotatoPai/SECURITY-NOTES.md）。這兩份不放進公開 repo。
- 步驟：
  1. 更新本檔（部署紀錄、待辦、架構變動）→ 推網站 main。
  2. 更新交接 prompt 的「目前待辦」與最後更新時間、更新私人資安備忘 → 寫入專案文件＋備份 Mac。
  3. 網站檔案備份到 Mac 的 PotatoPai/site/。
  4. 回覆 Pai：交接 prompt 全文放在一個程式碼區塊方便複製，附 HANDOFF.md 連結，提醒舊 session 改名。
