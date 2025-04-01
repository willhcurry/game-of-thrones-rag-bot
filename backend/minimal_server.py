# minimal_server.py
def app(environ, start_response):
    """Simplest possible WSGI application with detailed logging."""
    print(f"Received request: {environ['REQUEST_METHOD']} {environ.get('PATH_INFO', '')}")
    
    status = '200 OK'
    headers = [
        ('Content-type', 'application/json'),
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Headers', 'Content-Type'),
        ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    ]
    
    # Handle OPTIONS requests
    if environ['REQUEST_METHOD'] == 'OPTIONS':
        print("Handling OPTIONS request")
        start_response('204 No Content', headers)
        return [b'']
    
    # Handle different routes
    path = environ.get('PATH_INFO', '').lstrip('/')
    print(f"Processing path: '{path}'")
    
    if path == 'health' or path == '':
        response_body = b'{"status":"healthy"}'
    elif path == 'ask' and environ['REQUEST_METHOD'] == 'POST':
        # Get request body
        print("Processing POST to /ask")
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            print(f"Request body size: {request_body_size}")
            
            if request_body_size > 0:
                request_body = environ['wsgi.input'].read(request_body_size)
                print(f"Request body: {request_body}")
            
            # Return a simple response
            response_body = b'{"status":"success","response":"This is a test response."}'
            print(f"Sending response: {response_body}")
        except Exception as e:
            print(f"Error processing request: {str(e)}")
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