from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Print debug info immediately
print(f"Starting application setup...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT env var: {os.environ.get('PORT')}")

app = FastAPI()

# Update CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://game-of-thrones-rag-fkhj2xvjg-willhcurrys-projects.vercel.app",
        "https://game-of-thrones-rag-d2ywuwzrk-willhcurrys-projects.vercel.app",  # Your Vercel preview URL
        "https://game-of-thrones-rag.vercel.app",  # Your main Vercel URL (if different)
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Now add back the chatbot functionality
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

@app.get("/")
async def root():
    return {"status": "alive"}

@app.get("/health")
async def health():
    return {"status": "healthy"} 