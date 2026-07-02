# ⛅ 中央氣象署 x Windy.com 天氣觀測即時地圖儀表板

一個基於 Leaflet 地圖、中央氣象署（CWA）開放 API 與 Windy.com API 的精美氣象即時觀測儀表板。提供台灣各地觀測站的氣溫、雨量、相對濕度數據，並具備強大的動態篩選與極值分析功能。

🌐 **線上展示網址**：[https://cwa-weather-dashboard.vercel.app](https://cwa-weather-dashboard.vercel.app)

---

## ✨ 核心特色

### 1. 🗺️ 多樣化地圖模式
* **標準中文地圖 (OpenStreetMap)**：明亮、街道標示清晰，完全在地化的繁體中文標記。
* **動態天氣圖層 (Windy API)**：當提供有效的 Windy 金鑰時，地圖背景會自動啟用動態風速與溫度流線背景。
* **時尚暗黑地圖與精緻彩色地圖 (CartoDB)**：適合不同視覺偏好的地圖底圖切換。
* **高解析衛星影像地圖 (Esri)**：真實空拍地球影像。

### 2. 📊 即時觀測要素切換
* 一鍵切換 **氣溫 (°C)**、**時雨量 (mm)** 與 **相對濕度 (%)**。
* 地圖圓點標記的顏色會依據數值自動漸變（如低溫藍色、高溫紅色；無雨灰色、豪雨紫色）。
* 支援在地圖上直接開啟 **測站標籤（Station Labels）** 進行全局預覽。

### 3. 🔍 智慧篩選與互斥重設
* **搜尋欄位**：可快速輸入測站名稱、縣市或行政區（如：板橋、太平區）。
* **縣市選單**：支援個別縣市快速篩選。
* **UX 互斥防錯**：搜尋欄輸入文字時會自動重設縣市為「全部」；切換縣市時會自動清除搜尋欄文字，避免篩選條件衝突導致查無結果。

### 4. 📈 數據分析與極值統計
* 即時計算當前篩選範疇內的**平均數值**（均溫/平均雨量/平均相對濕度）。
* 動態抓出該範疇內的 **最高值與最低值測站**（如最高溫/最低溫測站名稱、數值及觀測時間）。

### 5. 📍 Google 街景與地圖整合
* 點擊任何測站標記，會在卡片中顯示豐富的詳細數據（氣壓、時雨量、觀測時間等）。
* 內嵌 **「開啟 Google 街景與地圖」** 連結，一鍵開啟該測站座標的 Google 實景。

---

## 🛠️ 技術棧

* **前端**：HTML5, Vanilla CSS3 (採用毛玻璃 Glassmorphism 設計), Vanilla JavaScript, Leaflet.js
* **後端 / API**：Python 3.12 (僅使用內建 Standard Library 以加速冷啟動)
* **部署平台**：Vercel Serverless Functions

---

## 💻 本地開發與執行

本專案無額外第三方依賴，直接使用 Python 內建函式庫即可啟動。

### 1. 設定環境變數 `.env`
在專案根目錄下建立一個 `.env` 檔案並填入您的 API Token：
```env
# 中央氣象署開放資料平台金鑰 (CWA-xxx)
CWA_TOKEN=您的氣象署Token

# Windy.com API 金鑰 (選填)
WINDY_API_KEY=您的WindyKey
```

### 2. 本地執行抓取與資料清洗
執行數據抓取腳本，從中央氣象署拉取即時觀測資料並生成清潔的 `weather_clean.json` 數據：
```bash
python scraper.py
```

### 3. 啟動本地開發伺服器
執行本地伺服器，將在本機 `http://localhost:8000` 提供服務：
```bash
python server.py
```
*(伺服器內建 Windows MIME-Type 修復機制，確保 CSS 正常載入)*

---

## 🚀 部署至 Vercel

本專案已完全設定好 Vercel 路由與 Serverless 雲端架構（`vercel.json` 及 `api/` 目錄）。

1. 登入您的 **Vercel 控制台**。
2. 匯入本 GitHub 專案。
3. 設定 **Root Directory** 為：`Antig/0625am中央氣象局`（或者依您的專案路徑而定）。
4. 在 **Environment Variables** 新增以下變數：
   * `CWA_TOKEN`：填入您的氣象署金鑰。
   * `WINDY_API_KEY`：填入您的 Windy 金鑰。
5. 點選 **Deploy** 即刻上線！
