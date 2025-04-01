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
        
        # For the first few requests, use placeholder responses
        # This allows the app to respond while the chatbot initializes in the background
        if bot is None:
            # Start initialization in a more lightweight way
            try:
                # Return a quick response first
                init_response = {
                    "status": "initializing",
                    "response": f"Initializing knowledge base for your question: '{question}'. Please try again in a moment."
                }
                
                # Try to import without creating the bot yet
                from chatbot import GameOfThronesBot
                print("Successfully imported GameOfThronesBot")
                bot = "importing"  # Mark as in progress
                
                return jsonify(init_response)
                
            except Exception as e:
                print(f"Failed to import chatbot: {str(e)}")
                bot_available = False
                return jsonify({
                    "status": "error",
                    "response": "The knowledge base is currently unavailable."
                })
        
        # If we're in the importing state, try to create the bot
        if bot == "importing":
            try:
                from chatbot import GameOfThronesBot
                bot = GameOfThronesBot()
                bot_available = True
                print("Chatbot fully initialized")
                
                # Return a simple response for this request
                return jsonify({
                    "status": "success",
                    "response": f"I'm ready to answer your question about '{question}'. Please ask again."
                })
                
            except Exception as e:
                print(f"Error creating bot: {str(e)}")
                bot = None
                return jsonify({
                    "status": "error",
                    "response": "There was an error initializing the knowledge base. Please try again later."
                })
        
        # Normal operation once bot is initialized
        if bot_available:
            try:
                # Use a simple timeout protection
                response_text = bot.ask(question)
                
                # Ensure response isn't too long
                if len(response_text) > 800:  # Even shorter limit
                    sentences = response_text.split('. ')
                    response_text = '. '.join(sentences[:5]) + '... (Response truncated)'
                
                # Force garbage collection
                gc.collect()
                
                return jsonify({
                    "status": "success",
                    "response": response_text
                })
                
            except Exception as e:
                print(f"Error in bot.ask: {str(e)}")
                return jsonify({
                    "status": "error", 
                    "response": "Sorry, I encountered an error processing your question."
                })
        else:
            return jsonify({
                "status": "unavailable",
                "response": "The Game of Thrones knowledge base is not available right now."
            })
        
    except Exception as e:
        print(f"General error: {str(e)}")
        return jsonify({"status": "error", "response": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
