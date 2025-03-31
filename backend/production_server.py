from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys

# Print debug info for troubleshooting
print(f"Starting server with PORT={os.environ.get('PORT')}")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Game of Thrones API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Try to initialize the chatbot if possible
try:
    from chatbot import GameOfThronesBot
    bot = GameOfThronesBot()
    print("Successfully initialized GameOfThronesBot")

    class Question(BaseModel):
        text: str

    @app.post("/ask")
    async def ask_question(question: Question):
        try:
            response = bot.ask(question.text)
            return {"response": response, "status": "success"}
        except Exception as e:
            print(f"Error processing question: {str(e)}")
            return {
                "response": "Sorry, I encountered an error processing your question.",
                "status": "error"
            }
except Exception as e:
    print(f"Failed to initialize chatbot: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    # Use the simplest approach
    uvicorn.run(app, host="0.0.0.0", port=port)
