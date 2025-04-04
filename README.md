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

An AI-powered chatbot that lets you explore the Game of Thrones books. Ask questions about characters, events, and locations with answers drawn directly from the text.

## Live Demo

Try it live: [Game of Thrones Knowledge Bot](https://huggingface.co/spaces/willhcurry/gotbot)

## Features
- Retrieval Augmented Generation (RAG) for accurate answers
- Direct evidence from the book series
- Interactive chat interface
- API endpoint for programmatic access
- Memory-efficient implementation

## Tech Stack
- **Backend:**
  - Python with LangChain for RAG implementation
  - Sentence Transformers for embeddings
  - FAISS for vector search
  - Hugging Face models for text generation
  - Gradio for web interface and API

- **Frontend:**
  - Next.js 14
  - Tailwind CSS
  - TypeScript
  - Deployed on Vercel

## How It Works

1. **Book Processing Pipeline**: EPUB books are converted to text, split into semantic chunks, and stored as JSON with metadata.
2. **Vector Embedding**: Text chunks are embedded using Sentence Transformers.
3. **FAISS Vector Search**: When a question is asked, the system finds the most relevant text chunks.
4. **Response Generation**: A language model generates a coherent answer based on the retrieved context.

## API Usage

The knowledge bot can be accessed programmatically:
POST https://willhcurry-gotbot.hf.space/api/predict
{
"data": ["Your question about Game of Thrones"]
}

Response format:
```
{
  "data": [{
    "response": "Detailed answer based on the books..."
  }]
}
```

## Local Development

### Setup

1. Clone the repository:
   ```
   git clone [your-repo-url]
   cd game-of-thrones-rag-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Place EPUB files in the `input` folder

4. Process the books:
   ```
   python backend/convert_books.py
   ```

5. Run the application:
   ```
   python backend/app.py
   ```

6. Frontend setup (optional):
   ```
   cd got-explorer-frontend
   npm install
   npm run dev
   ```

## Deployment

The chatbot is deployed on Hugging Face Spaces with 16GB RAM, which provides sufficient resources for the RAG implementation.

## Note

For educational purposes only. You'll need your own copies of the books in EPUB format.

{
"data": [{
"response": "Detailed answer based on the books..."
}]
}


## Local Development

### Setup

1. Clone the repository:
   ```
   git clone [your-repo-url]
   cd game-of-thrones-rag-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Place EPUB files in the `input` folder

4. Process the books:
   ```
   python backend/convert_books.py
   ```

5. Run the application:
   ```
   python backend/app.py
   ```

6. Frontend setup (optional):
   ```
   cd got-explorer-frontend
   npm install
   npm run dev
   ```

## Deployment

The chatbot is deployed on Hugging Face Spaces with 16GB RAM, which provides sufficient resources for the RAG implementation.

## Note

For educational purposes only. You'll need your own copies of the books in EPUB format.