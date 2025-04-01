from flask import Flask, request, jsonify
import os
import gc

app = Flask(__name__)

# EXPLICIT CORS configuration - don't rely on flask-cors
@app.after_request
def add_cors_headers(response):
    # Add CORS headers to EVERY response
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Handle OPTIONS requests explicitly
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
        data = request.json
        question = data.get('text', '')
        
        # Simple response for now
        response = {
            "status": "success",
            "response": f"You asked: {question}\n\nThis is a test response with explicit CORS handling."
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"status": "error", "response": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
