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
import sys

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware with wildcard for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Print debug info about environment
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir()}")
print(f"Environment variables: PORT={os.environ.get('PORT', 'Not set')}")

try:
    # Initialize the chatbot
    bot = GameOfThronesBot()

    class Question(BaseModel):
        """
        Data model for question requests.
        
        Attributes:
            text (str): The question text to be answered about Game of Thrones
        """
        text: str

    @app.get("/")
    async def root():
        return {"message": "Game of Thrones Explorer API is running"}

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

except Exception as e:
    print(f"Error during initialization: {str(e)}")
    # Add fallback route so the server can still start
    @app.get("/")
    async def error_root():
        return {"status": "error", "message": "Service is initializing or encountered an error"}

# This is critical for Render - must be outside the if __name__ block
import uvicorn

# Get port from environment variable with fallback to 8000
port = int(os.environ.get("PORT", 8000))
print(f"Starting server on 0.0.0.0:{port}")

# Define the config first
config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
server = uvicorn.Server(config)

if __name__ == "__main__":
    # Start server
    server.run()
else:
    # When imported by gunicorn or other ASGI servers
    # This makes the app variable available for them to use
    pass