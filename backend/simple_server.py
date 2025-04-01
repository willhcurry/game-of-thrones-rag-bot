import http.server
import socketserver
import os
import sys
import traceback
import json

# Print detailed environment info
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT: {os.environ.get('PORT')}")
print(f"Files in current dir: {os.listdir('.')}")

# Try to initialize the chatbot with robust error handling
try:
    print("Attempting to import GameOfThronesBot...")
    from chatbot import GameOfThronesBot
    bot = GameOfThronesBot()
    print("Successfully initialized GameOfThronesBot")
    bot_available = True
except Exception as e:
    print(f"Failed to initialize chatbot: {str(e)}")
    traceback.print_exc()
    bot_available = False
    print("Will continue without chatbot functionality")

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
                post_data_str = post_data.decode('utf-8')
                print(f"Received POST data: {post_data_str}")
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                
                if self.path == "/ask":
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
                        except Exception as e:
                            print(f"Error processing question: {str(e)}")
                            traceback.print_exc()
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
                try:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(b'{"status":"error","message":"Internal server error"}')
                except:
                    print("Failed to send error response")

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
