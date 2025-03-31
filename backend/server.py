import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Print environment information
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT environment variable: {os.environ.get('PORT')}")

# Create a FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you'd list specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Game of Thrones Explorer API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Add chatbot functionality
try:
    from chatbot import GameOfThronesBot
    bot = GameOfThronesBot()
    print("Chatbot initialized successfully")
    
    class Question(BaseModel):
        text: str
    
    @app.post("/ask")
    async def ask_question(question: Question):
        print(f"Received question: {question.text}")
        try:
            response = bot.ask(question.text)
            return {
                "response": response,
                "status": "success"
            }
        except Exception as e:
            print(f"Error in ask: {str(e)}")
            return {
                "response": "Sorry, I encountered an error processing your question.",
                "status": "error"
            }
except Exception as e:
    print(f"Error initializing chatbot: {str(e)}")

# The port binding code needs to stay at the bottom of the file
port = int(os.environ.get("PORT", 8000))
print(f"ATTEMPTING TO BIND TO PORT {port}")

if __name__ == "__main__":
    print("Running server directly")
    uvicorn.run(app, host="0.0.0.0", port=port)
else:
    print("Imported as module - for use with Uvicorn command") 