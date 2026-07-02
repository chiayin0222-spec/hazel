import os
import json
import http.server
import socketserver

# 簡易載入 .env 檔案中的環境變數 (與 scraper.py 同步)
def load_env(filepath=".env"):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, _, value = line.partition('=')
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")

# 初始化載入 .env
load_env()

# 確保 MIME type 正確 (防止 Windows 登錄檔毀損導致 CSS 被當作 text/plain 而被瀏覽器阻擋)
http.server.SimpleHTTPRequestHandler.extensions_map.update({
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.html': 'text/html',
    '.json': 'application/json'
})

PORT = 8000

class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 處理 API 設定路徑
        if self.path == '/api/config':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # 支援跨網域請求 (CORS) 以利開發
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # 從環境變數讀取 Windy API Key (如果沒有則留空，前端會自動 fallback 至標準 Leaflet)
            config = {
                "windyApiKey": os.getenv("WINDY_API_KEY", "")
            }
            self.wfile.write(json.dumps(config).encode('utf-8'))
            return

        # 處理 CWA 溫度資料 API 路徑
        elif self.path == '/api/cwa-temperature':
            clean_json_path = os.path.join(os.path.dirname(__file__), "weather_clean.json")
            if os.path.exists(clean_json_path):
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                with open(clean_json_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.send_error(404, "Weather data file not found")
            return

        # 其他路徑直接交由 SimpleHTTPRequestHandler 處理靜態檔案
        else:
            return super().do_GET()

def run_server():
    # 確保 socket 可以重複使用，避免 "Address already in use" 錯誤
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), DashboardRequestHandler) as httpd:
        print(f"==================================================")
        print(f" 氣象觀測儀表板本地伺服器已啟動！")
        print(f" 請在瀏覽器中打開: http://localhost:{PORT}")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n伺服器正在關閉...")

if __name__ == "__main__":
    run_server()
