import http.server
import socketserver
import os
import sys
import traceback
import json
import gc  # For garbage collection

# Print detailed environment info
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT: {os.environ.get('PORT')}")
print(f"Files in current dir: {os.listdir('.')}")

# Initialize bot as None first
bot = None
bot_available = False

class Handler(http.server.SimpleHTTPRequestHandler):
    def _send_cors_headers(self):
        """Helper method to consistently send CORS headers"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Credentials", "true")

    def do_OPTIONS(self):
        try:
            print(f"Handling OPTIONS request to {self.path}")
            self.send_response(204)
            self._send_cors_headers()
            self.end_headers()
            print("OPTIONS request handled successfully")
        except Exception as e:
            print(f"Error in do_OPTIONS: {str(e)}")
            traceback.print_exc()
        
    def do_GET(self):
        try:
            print(f"Handling GET request to {self.path}")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            
            if self.path == "/health":
                self.wfile.write(b'{"status": "healthy"}')
            else:
                self.wfile.write(b'{"status": "running"}')
            print("GET request handled successfully")
        except Exception as e:
            print(f"Error in do_GET: {str(e)}")
            traceback.print_exc()
                
    def do_POST(self):
        global bot, bot_available
        
        try:
            print(f"Handling POST request to {self.path}")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data_str = post_data.decode('utf-8')
            print(f"Received POST data: {post_data_str}")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            
            if self.path == "/ask":
                # Lazy load the bot only when needed
                if bot is None and not bot_available:
                    try:
                        print("Attempting to initialize bot...")
                        from chatbot import GameOfThronesBot
                        bot = GameOfThronesBot()
                        bot_available = True
                        print("Bot initialized successfully")
                    except Exception as e:
                        print(f"Failed to initialize bot: {str(e)}")
                        traceback.print_exc()
                
                if bot_available:
                    try:
                        question_data = json.loads(post_data_str)
                        question_text = question_data.get('text', '')
                        print(f"Processing question: {question_text}")
                        
                        response = bot.ask(question_text)
                        print(f"Generated response length: {len(response)} characters")
                        
                        # Truncate extremely long responses
                        if len(response) > 1000:
                            print("Response too long, truncating...")
                            sentences = response.split('. ')
                            truncated_response = '. '.join(sentences[:10]) + '... (Response truncated for better readability)'
                            response = truncated_response
                        
                        response_json = json.dumps({
                            "response": response,
                            "status": "success"
                        })
                        self.wfile.write(response_json.encode('utf-8'))
                        
                        # Force garbage collection after response
                        gc.collect()
                        
                    except Exception as e:
                        print(f"Error processing question: {str(e)}")
                        traceback.print_exc()
                        self.send_response(500)
                        self.send_header("Content-type", "application/json")
                        self._send_cors_headers()
                        self.end_headers()
                        response_json = json.dumps({
                            "response": "Sorry, I encountered an error processing your question.",
                            "status": "error"
                        })
                        self.wfile.write(response_json.encode('utf-8'))
                else:
                    print("Bot not available, sending placeholder response")
                    response_json = json.dumps({
                        "response": "The Game of Thrones chatbot is currently initializing. Please try again later.",
                        "status": "success"
                    })
                    self.wfile.write(response_json.encode('utf-8'))
            else:
                self.wfile.write(b'{"status":"unknown endpoint"}')
            
            print("POST request handled successfully")
        except Exception as e:
            print(f"Error in do_POST: {str(e)}")
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self._send_cors_headers()
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
