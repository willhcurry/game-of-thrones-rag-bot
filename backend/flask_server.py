from flask import Flask, request, jsonify
import os
import traceback

app = Flask(__name__)

# CORS configuration
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return jsonify({}), 200

@app.route('/')
def index():
    return jsonify({"status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ask', methods=['POST'])
def ask():
    try:
        # Get question from request
        data = request.json
        question = data.get('text', '')
        print(f"Processing question: {question}")
        
        # Generate a simple static response for testing
        # Don't try to use the ML models yet until we confirm basic processing works
        response_text = f"You asked about '{question}'. This is a static test response while we debug the server issues."
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
        
    except Exception as e:
        # Log the full error with traceback
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error", 
            "response": f"Server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, threaded=False)  # Disable threading for stability
