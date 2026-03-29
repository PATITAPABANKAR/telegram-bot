import os

print("Bot running on Render")

# keep service alive
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 10000))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

server = HTTPServer(("0.0.0.0", PORT), handler)
server.serve_forever()
