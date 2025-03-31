import http.server
import socketserver
import os

PORT = int(os.environ.get("PORT", 10000))
print(f"Starting basic HTTP server on port {PORT}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        if self.path == "/health":
            self.wfile.write(b'{"status": "healthy"}')
        else:
            self.wfile.write(b'{"status": "running"}')

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at port {PORT}")
    httpd.serve_forever()
