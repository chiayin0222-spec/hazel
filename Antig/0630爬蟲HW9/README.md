# 🎬 電影查詢與 AI 聊天機器人 Web 系統 (HW9)

本專案是一個基於 **Streamlit** 開發的電影查詢網頁系統。系統內建了從 https://ssr1.scrape.center 爬取的 100 部精選電影資料，採用精美的**輕奢銀灰色玻璃擬真 (Glassmorphism)** 視覺風格設計，並完美整合了 **Google Gemini AI 電影小助理** 與**電影主題動態線條圖**。

## 🌟 系統特色
- 🥈 **輕奢銀灰色主題**：採用金屬銀灰漸層背板，搭配半透明的白色乳膠磨砂玻璃卡片與高對比深色文字，視覺舒適且極具質感。
- 🏆 **電影排名 & 海報牆**：
  - **🏆 排名分頁**：展示評分 Top 10 與時長 Top 10 雙排行榜。
  - **📋 全部電影分頁**：以網格化海報牆展示 100 部電影的海報、年份、地區與詳細評分，支援直連詳情網頁。
- 🤖 **Gemini AI 側邊欄助理**：側邊欄內置 AI 電影助手，支援智慧推薦與問答，並提供豐富的引導提示語，協助您快速尋找心儀的電影。
- 🎨 **電影主題 SVG 動態頁尾**：網頁底部設有復古電影放映機、場記板、爆米花與電影票的向量 SVG 手繪線條動畫，具備微幅漂浮與呼吸燈特效。

## 📁 專案檔案結構
| 檔案 | 說明 |
|------|------|
| `app.py` | **Streamlit Web 系統主程式**（包含 UI 介面、排名展示、海報牆與側邊欄 AI 小助理） |
| `crawler.py` | 爬蟲主程式，爬取 ssr1.scrape.center 全部 100 部電影並產出 `movies.json` |
| `chatbot.py` | 本地規則匹配聊天機器人（舊版終端指令版） |
| `movie_rank.py` | 電影數據排行與統計分析腳本 |
| `movies.json` | 100 部電影的完整爬取資料（JSON 格式，由 crawler.py 產生） |
| `movies.xlsx` | 100 部電影的 Excel 格式資料 |
| `.gitignore` | 排除 `.env`（防金鑰洩露）、快取與暫存檔 |

## 🚀 快速開始

### 1. 安裝依賴項
請確認已安裝 Python 3.8+，並執行以下指令安裝所需套件：
```bash
pip install streamlit pandas openpyxl google-generativeai python-dotenv
```

### 2. 設定 API 金鑰
於專案根目錄下建立 `.env` 檔案，並填入您的 Gemini API Key：
```env
GEMINI_API_KEY=您的_GEMINI_API_KEY
```

### 3. 爬取電影數據
若尚未取得資料，請先執行爬蟲抓取：
```bash
python crawler.py
```

### 4. 啟動 Web 系統
執行 Streamlit 啟動網頁介面：
```bash
streamlit run app.py
```
啟動後會自動開啟瀏覽器視窗，預設網址為 `http://localhost:8501`。
