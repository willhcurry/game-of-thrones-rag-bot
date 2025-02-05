from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import GameOfThronesBot  # Import our chatbot class
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the chatbot
bot = GameOfThronesBot()

class Question(BaseModel):
    text: str

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/ask")
async def ask_question(question: Question):
    print(f"Received question: {question.text}")
    try:
        response = bot.ask(question.text)
        print(f"Generated response: {response}")
        return {
            "response": response,
            "status": "success"
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "response": "Sorry, I encountered an error while processing your question.",
            "status": "error"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)