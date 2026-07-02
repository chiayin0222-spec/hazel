# ⛅ 2026-07-02 工作成果與對話重點總結

## 📋 工作重點 (成果摘要)

### 1. 🗺️ 地圖與介面中文化 (繁體中文)
* **中文底圖**：將地圖切換為 **OpenStreetMap (OSM)**，以解決預設底圖過暗看不到海、以及地名非中文的問題。
* **Google 街景整合**：在每個測站標籤卡片中新增 **「開啟 Google 街景與地圖」** 按鈕，一鍵跳轉開啟 Google Maps 街景。

### 2. ⚙️ 功能選單與篩選優化 (UX 升級)
* **要素與底圖切換**：新增控制面板，可切換氣溫/雨量/濕度與底圖（OSM、暗黑、彩色、衛星影像），並對應更新圖例與統計。
* **防衝突搜尋機制**：優化 `app.js` 篩選邏輯——當用戶在搜尋欄輸入文字時，自動將縣市篩選重設為「全部」；當點選縣市時，自動清除搜尋文字，避免條件衝突查無資料。
* **圖層開關**：新增 CWA 觀測站與測站名稱（Labels）的開啟/隱藏 checkbox。

### 3. ☁️ Vercel 雲端伺服器建置
* **Serverless API**：在 `api/cwa-temperature.py` 實作雲端即時抓取與過濾無效值（如 `-99` 數據）。
* **網頁發布**：專案網址已正式啟用：🚀 [cwa-weather-dashboard.vercel.app](https://cwa-weather-dashboard.vercel.app)。

### 4. 💻 本地 Windows 相容性修正
* **MIME-Type 修復**：修復 Windows Python 本地伺服器將 CSS 當作 `text/plain` 傳輸而被瀏覽器阻擋的錯誤。現在已可完美載入毛玻璃（Glassmorphism）側邊欄。

### 5. 📦 Git 同步與文檔管理
* **`.gitignore`**：正確隔離敏感金鑰檔 (`.env`) 與快取。
* **Git 同步**：代碼全數同步推送到 GitHub 儲存庫 `chiayin0222-spec/hazel.git`。
* **`README.md`**：完成詳細的說明手冊撰寫。

---

## 💬 對話與排查重點

* **Vercel CLI 授權成功**：引導使用 **GitHub 直接授權登入 Vercel**，省去網頁端手動設定與憑證過期問題。
* **環境變數 typo 排除**：修正了 Vercel 後台將 `WINDY_API_KEY` 誤植為 `INDY_API_KEY` 的 typo，成功使 Windy 天氣流線圖層生效。
* **MIME 阻擋排查**：分析 `localhost:8000` 無樣式網頁截圖，判斷為 CSS MIME Type 錯誤並即時修改 `server.py` 搭配清除快取解決。
* **篩選無資料排查**：分析搜尋「太平區」但因選定「新竹市」導致查無資料的截圖，即時重構 `app.js` 加入互斥自動重設機制。
