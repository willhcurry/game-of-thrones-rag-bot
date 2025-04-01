import http.server
import socketserver
import os
import sys
import traceback

# Print detailed environment info
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT: {os.environ.get('PORT')}")
print(f"Files in current dir: {os.listdir('.')}")

try:
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            try:
                print(f"Handling GET request to {self.path}")
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                
                if self.path == "/health":
                    self.wfile.write(b'{"status": "healthy"}')
                else:
                    self.wfile.write(b'{"status": "running"}')
                print("GET request handled successfully")
            except Exception as e:
                print(f"Error in do_GET: {str(e)}")
                traceback.print_exc()
                
        def do_OPTIONS(self):
            try:
                print(f"Handling OPTIONS request to {self.path}")
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                print("OPTIONS request handled successfully")
            except Exception as e:
                print(f"Error in do_OPTIONS: {str(e)}")
                traceback.print_exc()

        def do_POST(self):
            try:
                print(f"Handling POST request to {self.path}")
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                print(f"Received POST data: {post_data.decode('utf-8')}")
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                
                if self.path == "/ask":
                    # Echo back a simple response for now
                    self.wfile.write(b'{"response":"This is a placeholder response while the chatbot is being configured.","status":"success"}')
                else:
                    self.wfile.write(b'{"status":"unknown endpoint"}')
                
                print("POST request handled successfully")
            except Exception as e:
                print(f"Error in do_POST: {str(e)}")
                traceback.print_exc()
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b'{"status":"error","message":"Internal server error"}')

    # Try to get the port with extra error handling
    try:
        PORT = int(os.environ.get("PORT", 10000))
        print(f"Using port: {PORT}")
    except Exception as e:
        print(f"Error getting PORT: {str(e)}")
        PORT = 8000
        print(f"Defaulting to port {PORT}")

    print(f"Setting up server on port {PORT}")
    server = socketserver.TCPServer(("", PORT), Handler)
    print(f"Server initialized, starting serve_forever()")
    server.serve_forever()
    
except Exception as e:
    print(f"Critical error: {str(e)}")
    traceback.print_exc()
