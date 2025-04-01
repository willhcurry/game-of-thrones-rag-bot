import http.server
import socketserver
import os
import json
from urllib.parse import parse_qs

# Try to initialize the chatbot
try:
    from chatbot import GameOfThronesBot
    bot = GameOfThronesBot()
    print("Successfully initialized GameOfThronesBot")
    bot_available = True
except Exception as e:
    print(f"Failed to initialize chatbot: {str(e)}")
    bot_available = False

class Handler(http.server.SimpleHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self._set_cors_headers()
        self.end_headers()
        
        if self.path == "/health":
            self.wfile.write(b'{"status": "healthy"}')
        else:
            self.wfile.write(b'{"status": "running"}')
    
    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        if self.path == "/ask":
            # Get the length of the POST data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                question_data = json.loads(post_data.decode('utf-8'))
                
                if bot_available:
                    response = bot.ask(question_data.get('text', ''))
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "response": response,
                        "status": "success"
                    }).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "response": "Chatbot is not available",
                        "status": "error"
                    }).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "response": f"Error: {str(e)}",
                    "status": "error"
                }).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": "Not found"
            }).encode('utf-8'))

PORT = int(os.environ.get("PORT", 10000))
print(f"Starting HTTP server on port {PORT}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at port {PORT}")
    httpd.serve_forever()
