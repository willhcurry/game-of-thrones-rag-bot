import json
import os

# Try to initialize the chatbot
try:
    from chatbot import GameOfThronesBot
    bot = GameOfThronesBot()
    print("Successfully initialized GameOfThronesBot")
    bot_available = True
except Exception as e:
    print(f"Failed to initialize chatbot: {str(e)}")
    bot_available = False

# CORS allowed origins
ALLOWED_ORIGINS = [
    "https://game-of-thrones-rag-fkhj2xvjg-willhcurrys-projects.vercel.app",
    "https://game-of-thrones-rag-d2ywuwzrk-willhcurrys-projects.vercel.app",
    "https://game-of-thrones-rag.vercel.app",
    "http://localhost:3000"
]

def application(environ, start_response):
    """WSGI application with Game of Thrones functionality and CORS support."""
    # Get request origin
    origin = environ.get('HTTP_ORIGIN', '')
    method = environ.get('REQUEST_METHOD', '')
    
    # Set up response headers with CORS if origin is allowed
    response_headers = [('Content-type', 'application/json')]
    if origin in ALLOWED_ORIGINS:
        response_headers.extend([
            ('Access-Control-Allow-Origin', origin),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type'),
            ('Access-Control-Allow-Credentials', 'true')
        ])
    
    # Handle preflight OPTIONS request
    if method == 'OPTIONS':
        start_response('204 No Content', response_headers)
        return [b'']
    
    path = environ.get('PATH_INFO', '')
    
    # Handle different endpoints
    if path == '/health':
        status = '200 OK'
        response_body = json.dumps({"status": "healthy"})
    elif path == '/ask' and environ.get('REQUEST_METHOD') == 'POST':
        if not bot_available:
            status = '500 Internal Server Error'
            response_body = json.dumps({
                "response": "Chatbot initialization failed",
                "status": "error"
            })
        else:
            try:
                # Get POST data
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                post_data = environ.get('wsgi.input').read(content_length)
                question_data = json.loads(post_data)
                
                # Process the question
                response = bot.ask(question_data.get('text', ''))
                status = '200 OK'
                response_body = json.dumps({
                    "response": response,
                    "status": "success"
                })
            except Exception as e:
                status = '500 Internal Server Error'
                response_body = json.dumps({
                    "response": f"Error: {str(e)}",
                    "status": "error"
                })
    else:
        status = '200 OK'
        response_body = json.dumps({"status": "Game of Thrones API is running"})
    
    start_response(status, response_headers)
    return [response_body.encode('utf-8')]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting WSGI server on port {port}")
    with make_server('', port, application) as httpd:
        print(f"Serving on port {port}...")
        httpd.serve_forever()
