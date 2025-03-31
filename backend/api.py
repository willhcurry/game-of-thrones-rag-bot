"""
Game of Thrones Explorer API

This module implements a FastAPI server that serves as the backend for the 
Game of Thrones Explorer application. It provides endpoints for querying
information about the Game of Thrones universe from the book series
using a Retrieval Augmented Generation (RAG) approach.

The API exposes endpoints for:
- Health checking
- Question answering against the Game of Thrones knowledge base

The server uses CORS middleware to handle cross-origin requests from the frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot import GameOfThronesBot
import os

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware to allow frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Game of Thrones knowledge bot
# This loads the vector store and prepares the embeddings for question answering
bot = GameOfThronesBot()

class Question(BaseModel):
    """
    Data model for question requests.
    
    Attributes:
        text (str): The question text to be answered about Game of Thrones
    """
    text: str

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    This endpoint can be used by monitoring systems to ensure the service
    is available and operational.
    
    Returns:
        dict: Status indication that the service is healthy
    """
    return {"status": "healthy"}

@app.post("/ask")
async def ask_question(question: Question):
    """
    Processes a question about Game of Thrones and returns relevant information.
    
    This endpoint receives a question from the client, processes it through the
    Game of Thrones knowledge base using vector search, and returns passages
    from the books that are most relevant to the question.
    
    Args:
        question (Question): The question model containing the text to answer
        
    Returns:
        dict: Contains the response text and status of the operation
        
    Raises:
        Various exceptions may be caught and handled internally, returning
        an error message to the client instead of failing the request.
    """
    print(f"Received question: {question.text}")
    try:
        # Query the RAG system for relevant passages from the books
        response = bot.ask(question.text)
        print(f"Generated response: {response}")
        return {
            "response": response,
            "status": "success"
        }
    except Exception as e:
        # Log the error and return a user-friendly message
        print(f"Error: {str(e)}")
        return {
            "response": "Sorry, I encountered an error while processing your question.",
            "status": "error"
        }

if __name__ == "__main__":
    """
    Entry point when running this module directly.
    
    Starts the uvicorn server with the FastAPI application.
    The server runs on all interfaces (0.0.0.0) and uses the PORT 
    environment variable with a default of 8000.
    """
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)