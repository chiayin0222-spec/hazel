import os
import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Read the Windy API key from Vercel's environment variables
        config = {
            "windyApiKey": os.environ.get("WINDY_API_KEY", "")
        }
        self.wfile.write(json.dumps(config).encode('utf-8'))
        return
