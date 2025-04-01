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
        # Use wildcard to allow all origins or specify your Vercel domains
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")  # 24 hours

    def do_OPTIONS(self):
        # This method needs to be implemented correctly for preflight requests
        print(f"Handling OPTIONS request to {self.path}")
        # Send 204 No Content for OPTIONS
        self.send_response(204)
        self.send_header("Content-Length", "0")
        self._send_cors_headers()
        self.end_headers()
        print("OPTIONS request completed")
        
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
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data_str = post_data.decode('utf-8')
            print(f"Received POST request to {self.path} with data length: {len(post_data_str)}")
            
            # Prepare response
            response_dict = {"status": "error", "response": "Unknown endpoint"}
            
            if self.path == "/ask":
                try:
                    question_data = json.loads(post_data_str)
                    question_text = question_data.get('text', '')
                    print(f"Processing question: {question_text}")
                    
                    # Simple placeholder response for testing
                    response_dict = {
                        "status": "success",
                        "response": "This is a test response to your question about Game of Thrones."
                    }
                    
                    # Don't try to use the bot yet - just test JSON response first
                    # Once we confirm basic JSON works, we can add bot functionality back
                    
                except Exception as e:
                    print(f"Error processing POST data: {str(e)}")
                    response_dict = {
                        "status": "error",
                        "response": "Error processing your request"
                    }
            
            # Convert response dict to JSON and ensure it's properly encoded
            response_json = json.dumps(response_dict)
            response_bytes = response_json.encode('utf-8')
            
            # Send response with proper headers
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-Length", str(len(response_bytes)))
            self._send_cors_headers()
            self.end_headers()
            
            # Log response for debugging
            print(f"Sending response: {response_json}")
            
            # Write response
            self.wfile.write(response_bytes)
            
        except Exception as e:
            print(f"Critical error in do_POST: {str(e)}")
            try:
                # Send a minimal error response
                error_response = json.dumps({"status": "error", "response": "Server error"})
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", str(len(error_response.encode('utf-8'))))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(error_response.encode('utf-8'))
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
