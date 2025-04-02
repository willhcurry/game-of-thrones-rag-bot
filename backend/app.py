import gradio as gr
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import sys

# Print debug info immediately
print(f"Starting application setup...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT env var: {os.environ.get('PORT')}")

# Import your chatbot
from chatbot import GameOfThronesBot

# Add your RAG implementation - either directly here or import from your files
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.text import TextLoader
from langchain.memory import ConversationBufferMemory

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the chatbot
bot = GameOfThronesBot()

# Initialize your chatbot
embeddings = HuggingFaceEmbeddings()
books_dir = "books" # Make sure to upload your books directory

# Load vector store if it exists, otherwise create it
vector_store_path = "faiss_index"
if os.path.exists(vector_store_path):
    vector_store = FAISS.load_local(vector_store_path, embeddings)
else:
    # Load and process your books
    documents = []
    for filename in os.listdir(books_dir):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(books_dir, filename))
            documents.extend(loader.load())
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    # Create vector store
    vector_store = FAISS.from_documents(texts, embeddings)
    vector_store.save_local(vector_store_path)

# Initialize LLM and chat chain
llm = HuggingFaceHub(repo_id="HuggingFaceH4/zephyr-7b-beta", model_kwargs={"temperature": 0.7})
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(),
    memory=memory,
)

def respond(message, history):
    response = qa_chain({"question": message})
    return response["answer"]

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!",
)

# FastAPI endpoint for frontend integration
@app.post("/ask")
async def ask_endpoint(request: Request):
    data = await request.json()
    question = data.get("text", "")
    response = bot.ask(question)
    return {"response": response, "status": "success"}

# Gradio interface (for testing directly on Hugging Face)
def answer_question(question):
    return bot.ask(question)

# Mount FastAPI app
gr.mount_gradio_app(app, demo, path="/")

# Start the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

@app.get("/")
async def root():
    return {"status": "alive"}

@app.get("/health")
async def health():
    return {"status": "healthy"} 