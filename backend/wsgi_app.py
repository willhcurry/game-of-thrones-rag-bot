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
    """Simplest possible WSGI application."""
    status = '200 OK'
    response_headers = [
        ('Content-type', 'application/json'),
        ('Access-Control-Allow-Origin', '*')
    ]
    start_response(status, response_headers)
    
    path = environ.get('PATH_INFO', '')
    if path == '/health':
        return [b'{"status": "healthy"}']
    return [b'{"status": "Game of Thrones API is running"}']

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting WSGI server on port {port}")
    with make_server('', port, application) as httpd:
        print(f"Serving on port {port}...")
        httpd.serve_forever()
