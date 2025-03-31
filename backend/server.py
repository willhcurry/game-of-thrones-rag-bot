import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

print("Initializing FastAPI application...")

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
async def root():
    return {"message": "Server is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Initialize chatbot only if we can
try:
    from chatbot import GameOfThronesBot
    bot = GameOfThronesBot()
    
    class Question(BaseModel):
        text: str
    
    @app.post("/ask")
    async def ask_question(question: Question):
        try:
            response = bot.ask(question.text)
            return {"response": response, "status": "success"}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                "response": "Sorry, I encountered an error.",
                "status": "error"
            }
except Exception as e:
    print(f"Failed to initialize chatbot: {str(e)}") 