import http.server
import socketserver
import os
import json

PORT = int(os.environ.get("PORT", 10000))
print(f"Starting server on port {PORT}")

# Global variables for chatbot
bot = None
bot_available = False

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to every response
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Handle OPTIONS preflight requests
        self.send_response(204)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running"}).encode())
    
    def do_POST(self):
        if self.path == '/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                # Parse the JSON request
                request_json = json.loads(post_data)
                question = request_json.get('text', '')
                
                # Initialize the chatbot if needed
                global bot, bot_available
                if bot is None and not bot_available:
                    try:
                        from chatbot import GameOfThronesBot
                        bot = GameOfThronesBot()
                        bot_available = True
                    except Exception as e:
                        print(f"Failed to initialize chatbot: {str(e)}")
                        bot_available = False
                
                # Generate response using chatbot or fallback
                if bot_available:
                    response_text = bot.ask(question)
                    # Truncate if too long
                    if len(response_text) > 1000:
                        sentences = response_text.split('. ')
                        response_text = '. '.join(sentences[:10]) + '... (Response truncated)'
                else:
                    response_text = "The chatbot is currently unavailable. Please try again later."
                
                # Create response object
                response = {
                    "status": "success",
                    "response": response_text
                }
                
                # Send the response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "error",
                    "response": f"Server error: {str(e)}"
                }).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": "Not found"}).encode())

# Create server
with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
    print(f"Server running at port {PORT}")
    httpd.serve_forever()
