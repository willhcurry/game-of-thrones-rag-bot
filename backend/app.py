"""
Game of Thrones Knowledge Bot - Server Application

This module implements a Gradio web interface and API for the Game of Thrones
RAG (Retrieval Augmented Generation) chatbot. It loads pre-processed book 
chunks, creates a vector store for semantic search, and provides both a 
user-friendly chat interface and a programmatic API.

The application is designed to run on Hugging Face Spaces with the following
architecture:
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Vector database: FAISS for efficient similarity search
- Language model: Local transformer-based model for text generation
- Frontend: Gradio for web interface with chat capabilities
- API: Accessible endpoint for frontend integration

Usage:
    Deploy directly to Hugging Face Spaces or run locally with:
    $ python app.py
"""

import gradio as gr
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.llms import HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

print("Loading embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_documents():
    print("Loading documents...")
    documents = []
    rag_dir = "output/rag_chunks"
    if os.path.exists(rag_dir):
        print(f"Found rag_dir: {rag_dir}")
        for filename in os.listdir(rag_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(rag_dir, filename)
                print(f"Processing file: {filepath}")
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    chunks = data.get('chunks', [])
                    for chunk in chunks:
                        content = chunk.get('content', '')
                        metadata = chunk.get('metadata', {})
                        doc = Document(page_content=content, metadata=metadata)
                        documents.append(doc)
    print(f"Loaded {len(documents)} documents")
    return documents

print("Creating vector store...")
documents = load_documents()
vector_store = FAISS.from_documents(documents, embeddings)
print("Vector store created successfully")

# Initialize language model for text generation
# Using a smaller model to ensure it fits within memory constraints
model_name = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512
)
local_llm = HuggingFacePipeline(pipeline=pipe)

# Set up conversation memory and retrieval chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=local_llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
    memory=memory
)

def answer_question(question):
    """Simple question answering function"""
    print(f"Received question: '{question}'")
    
    if not question or question.strip() == "":
        return "I didn't receive a question. Please try again."
    
    # Get relevant documents
    docs = vector_store.similarity_search(question, k=3)
    
    # Format response
    response = f"Here's what I found about '{question}':\n\n"
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get('book_title', 'Game of Thrones')
        chapter = doc.metadata.get('chapter', 'Unknown chapter')
        response += f"From {source} ({chapter}):\n{doc.page_content}\n\n"
    
    return response

# Create Gradio Interface
demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(lines=2, placeholder="Ask about Game of Thrones..."),
    outputs="text",
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about the Game of Thrones books!"
)

# Launch the app
if __name__ == "__main__":
    demo.launch() 