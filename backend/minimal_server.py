# minimal_server.py
def app(environ, start_response):
    """Simplest possible WSGI application."""
    status = '200 OK'
    headers = [
        ('Content-type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', 'Content-Type'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    ]
    
    # Handle OPTIONS requests
    if environ['REQUEST_METHOD'] == 'OPTIONS':
        start_response('204 No Content', headers)
        return [b'']
    
    # Handle different routes
    path = environ.get('PATH_INFO', '').lstrip('/')
    
    if path == 'health' or path == '':
        response_body = b'{"status":"healthy"}'
    elif path == 'ask' and environ['REQUEST_METHOD'] == 'POST':
        # Get request body
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            
            # Just return a simple response
            response_body = b'{"status":"success","response":"This is a test response while we debug server issues."}'
        except Exception as e:
            response_body = f'{{"status":"error","response":"Error: {str(e)}"}}'.encode('utf-8')
    else:
        response_body = b'{"status":"running"}'
    
    start_response(status, headers)
    return [response_body]

if __name__ == '__main__':
    import os
    from wsgiref.simple_server import make_server
    
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}")
    with make_server('', port, app) as httpd:
        print(f"Serving on port {port}...")
        httpd.serve_forever()