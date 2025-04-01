from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # This will handle CORS for all routes

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
        
        # Simple static response for now
        response = {
            "status": "success",
            "response": f"You asked: {question}\n\nThis is a test response from Flask."
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"status": "error", "response": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
