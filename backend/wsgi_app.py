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

def application(environ, start_response):
    """WSGI application with Game of Thrones functionality."""
    status = '200 OK'
    
    # Basic CORS support - allow all origins
    response_headers = [
        ('Content-type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
        ('Access-Control-Allow-Headers', 'Content-Type')
    ]
    
    # Handle preflight OPTIONS request
    if environ.get('REQUEST_METHOD') == 'OPTIONS':
        start_response('204 No Content', response_headers)
        return [b'']
    
    path = environ.get('PATH_INFO', '')
    
    # Handle different endpoints
    if path == '/health':
        response_body = json.dumps({"status": "healthy"})
    elif path == '/ask' and environ.get('REQUEST_METHOD') == 'POST':
        if not bot_available:
            status = '500 Internal Server Error'
            response_body = json.dumps({"status": "error"})
        else:
            try:
                # Get POST data
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                post_data = environ.get('wsgi.input').read(content_length)
                question_data = json.loads(post_data)
                
                # Process the question
                response = bot.ask(question_data.get('text', ''))
                response_body = json.dumps({
                    "response": response,
                    "status": "success"
                })
            except Exception as e:
                status = '500 Internal Server Error'
                response_body = json.dumps({"status": "error"})
    else:
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
