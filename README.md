---
title: Game of Thrones RAG Bot
emoji: 🐉
colorFrom: indigo
colorTo: gray
sdk: gradio
sdk_version: 3.50.2
app_file: backend/app.py
pinned: false
---

# Game of Thrones Knowledge Bot

A RAG-based chatbot that can answer questions about Game of Thrones.

An AI-powered chatbot that lets you explore and discuss the Game of Thrones books. Ask questions about characters, events, and get answers with direct citations from the source material.

## Features
- EPUB to searchable text conversion
- AI-powered question answering
- Direct citations from the books
- Interactive chat interface
- Vector-based search for accurate responses

## Tech Stack
- Backend:
  - Python 3.8
  - FastAPI
  - LangChain for RAG implementation
  - Sentence Transformers for embeddings
  - ChromaDB for vector storage

- Frontend:
  - Next.js 14
  - Tailwind CSS
  - TypeScript
  - React

## Setup

### Backend Setup

## Create conda environment
conda create -n bookbot python=3.8
conda activate bookbot

## Install dependencies
pip install numpy==1.23.5
pip install sentence-transformers==2.2.2
pip install langchain-huggingface==0.0.3
pip install fastapi uvicorn
pip install "langchain[all]" langchain-community
pip install EbookLib beautifulsoup4 PyMuPDF chromadb

## Frontend Setup
cd got-explorer-frontend
npm install
npm run dev

## Usage

Place EPUB files in the input folder
Run the conversion:

python backend/convert_books.py

Start the backend server:

cd backend
uvicorn api:app --reload

Start the frontend (in another terminal):

cd got-explorer-frontend
npm run dev

Visit http://localhost:3000 to use the chatbot

Coming Soon

Enhanced response formatting
Improved source citations
Advanced conversation memory
Deployment instructions

Note
For educational purposes only. You'll need your own copies of the books in EPUB format.