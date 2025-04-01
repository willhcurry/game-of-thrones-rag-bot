from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import gc

app = Flask(__name__)
CORS(app)  # This handles CORS for all routes

# Global variables
bot = None
bot_available = False

@app.route('/')
def index():
    return jsonify({"status": "running"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/ask', methods=['POST'])
def ask():
    global bot, bot_available
    
    try:
        data = request.json
        question = data.get('text', '')
        
        # Initialize bot if needed
        if bot is None and not bot_available:
            try:
                from chatbot import GameOfThronesBot
                bot = GameOfThronesBot()
                bot_available = True
            except Exception as e:
                print(f"Failed to initialize chatbot: {str(e)}")
                bot_available = False
        
        # Generate response
        if bot_available:
            response_text = bot.ask(question)
            # Truncate if needed
            if len(response_text) > 1000:
                sentences = response_text.split('. ')
                response_text = '. '.join(sentences[:10]) + '... (Response truncated)'
            
            gc.collect()  # Force garbage collection
        else:
            response_text = "The Game of Thrones knowledge base is currently unavailable."
        
        return jsonify({
            "status": "success",
            "response": response_text
        })
        
    except Exception as e:
        return jsonify({"status": "error", "response": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
