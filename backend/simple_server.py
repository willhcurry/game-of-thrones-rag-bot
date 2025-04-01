import http.server
import socketserver
import os
import json

# Global variables
PORT = int(os.environ.get("PORT", 10000))

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to EVERY response
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Critical for preflight requests
        self.send_response(204)
        self.end_headers()
    
    def do_GET(self):
        # Handle GET requests
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {'status': 'healthy'}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Handle POST requests without any chatbot logic
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        # Get the request data but don't process it yet
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            # Parse request but return a simple static response
            request = json.loads(post_data)
            question = request.get('text', '')
            
            response = {
                'status': 'success',
                'response': f"You asked: {question}\n\nThis is a static test response while we solve CORS issues."
            }
            
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            error_response = {
                'status': 'error',
                'response': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())

# Start the server
with socketserver.TCPServer(("", PORT), CORSRequestHandler) as httpd:
    print(f"Server running at port {PORT}")
    httpd.serve_forever()
