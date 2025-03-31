from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

print("Starting server initialization...")
print(f"PORT={os.environ.get('PORT')}")
print(f"Current directory: {os.getcwd()}")

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://game-of-thrones-rag-fkhj2xvjg-willhcurrys-projects.vercel.app",
        "https://game-of-thrones-rag-d2ywuwzrk-willhcurrys-projects.vercel.app",
        "https://game-of-thrones-rag.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Game of Thrones Explorer API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Initialize chatbot
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