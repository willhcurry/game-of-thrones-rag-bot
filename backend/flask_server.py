from flask import Flask, request, jsonify
import os
import gc
import json

app = Flask(__name__)

# CORS configuration - added to every response
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Handle OPTIONS requests explicitly
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return jsonify({}), 200

# Global variables with lazy initialization
bot = None
bot_available = False
bot_initialized = False

@app.route('/')
def index():
    return jsonify({"status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ask', methods=['POST'])
def ask():
    global bot, bot_available, bot_initialized
    
    try:
        data = request.json
        question = data.get('text', '')
        print(f"Received question: {question}")
        
        # First request - initialize bot in background
        if not bot_initialized:
            try:
                print("Starting bot initialization...")
                bot_initialized = True  # Mark initialization attempted
                
                # Try to import the minimal version
                from memory_optimized_chatbot import GameOfThronesBot
                bot = GameOfThronesBot()
                bot_available = True
                print("Bot initialized successfully")
                
            except Exception as e:
                print(f"Failed to initialize bot: {str(e)}")
                bot_available = False
                
                # Return quick response for first question
                return jsonify({
                    "status": "initializing",
                    "response": f"I'm searching for information about '{question}'. Please try asking again in a moment."
                })
        
        # If bot is available, use it
        if bot_available:
            try:
                # Process the question
                response_text = bot.ask(question)
                
                # Truncate long responses
                if len(response_text) > 800:
                    sentences = response_text.split('. ')
                    response_text = '. '.join(sentences[:8]) + '... (Response truncated for readability)'
                
                # Force garbage collection to free memory
                gc.collect()
                
                return jsonify({
                    "status": "success",
                    "response": response_text
                })
                
            except Exception as e:
                print(f"Error processing question: {str(e)}")
                return jsonify({
                    "status": "error",
                    "response": "I encountered an error while searching for information."
                })
        else:
            # Fallback response if bot initialization failed
            return jsonify({
                "status": "unavailable",
                "response": "I'm having trouble accessing my knowledge base right now. Please try again later."
            })
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({
            "status": "error",
            "response": "An unexpected error occurred."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)
