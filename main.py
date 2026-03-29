import os
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_message(text):
    url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

send_message("Bot is live on Render")

PORT = int(os.environ.get("PORT", 10000))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

server = HTTPServer(("0.0.0.0", PORT), handler)
server.serve_forever()
