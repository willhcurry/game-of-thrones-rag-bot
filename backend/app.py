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

# Debug logging
print("Starting application...")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir()}")

# Load a minimal fallback dataset directly in code
FALLBACK_DATA = [
    {"content": "Jon Snow is the bastard son of Eddard Stark, Lord of Winterfell.",
     "metadata": {"book_title": "A Game of Thrones", "chapter": "Chapter 1"}},
    {"content": "House Stark rules the North from their castle at Winterfell.",
     "metadata": {"book_title": "A Game of Thrones", "chapter": "Chapter 2"}},
    {"content": "The Red Wedding was a massacre of Stark forces orchestrated by Walder Frey and Roose Bolton.",
     "metadata": {"book_title": "A Storm of Swords", "chapter": "Chapter 51"}}
]

def load_documents():
    """Load documents with extensive error checking"""
    documents = []
    rag_dir = "output/rag_chunks"
    
    # Check if directory exists
    if not os.path.exists(rag_dir):
        print(f"WARNING: Directory {rag_dir} not found!")
        print(f"Creating directory: {rag_dir}")
        os.makedirs(rag_dir, exist_ok=True)
        
        # Use fallback data
        print("Using fallback data since no documents were found")
        for item in FALLBACK_DATA:
            doc = Document(page_content=item["content"], metadata=item["metadata"])
            documents.append(doc)
        return documents
    
    # Try to load documents from files
    try:
        file_count = 0
        for filename in os.listdir(rag_dir):
            if filename.endswith('.json'):
                file_count += 1
                filepath = os.path.join(rag_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        chunks = data.get('chunks', [])
                        for chunk in chunks:
                            content = chunk.get('content', '')
                            metadata = chunk.get('metadata', {})
                            doc = Document(page_content=content, metadata=metadata)
                            documents.append(doc)
                except Exception as e:
                    print(f"Error loading file {filepath}: {str(e)}")
        
        print(f"Processed {file_count} files, loaded {len(documents)} documents")
        
        # If no documents were loaded, use fallback data
        if not documents:
            print("No documents were loaded from files, using fallback data")
            for item in FALLBACK_DATA:
                doc = Document(page_content=item["content"], metadata=item["metadata"])
                documents.append(doc)
    except Exception as e:
        print(f"Error loading documents: {str(e)}")
        # Use fallback data
        print("Using fallback data due to error")
        for item in FALLBACK_DATA:
            doc = Document(page_content=item["content"], metadata=item["metadata"])
            documents.append(doc)
    
    return documents

print("Loading embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("Loading documents...")
documents = load_documents()
print(f"Loaded {len(documents)} documents")

print("Creating vector store...")
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
    """Simple question answering function with detailed logging"""
    print(f"Received question: '{question}'")
    
    if not question or question.strip() == "":
        return "I didn't receive a question. Please try again."
    
    try:
        # Get relevant documents
        print(f"Searching for: '{question}'")
        docs = vector_store.similarity_search(question, k=2)
        print(f"Found {len(docs)} relevant documents")
        
        if not docs:
            return "I couldn't find any information about that in the Game of Thrones books."
        
        # Format response
        response = f"Here's what I found about '{question}':\n\n"
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('book_title', 'Game of Thrones')
            chapter = doc.metadata.get('chapter', 'Unknown chapter')
            content = doc.page_content
            print(f"Doc {i}: {source}, {chapter}, content length: {len(content)}")
            response += f"From {source} ({chapter}):\n{content}\n\n"
        
        return response
    except Exception as e:
        print(f"Error answering question: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

# Create Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# Game of Thrones Knowledge Bot")
    
    with gr.Tab("Chat"):
        question_input = gr.Textbox(lines=2, placeholder="Ask about Game of Thrones...")
        answer_output = gr.Textbox(lines=10)
        submit_btn = gr.Button("Ask")
        submit_btn.click(answer_question, inputs=question_input, outputs=answer_output)
    
    with gr.Tab("API"):
        gr.Markdown("""
        ## API Usage
        
        Send POST requests to: `https://willhcurry-gotbot.hf.space/api/predict`
        
        Format:
        ```json
        {
          "data": ["Your question here"]
        }
        ```
        """)

# Launch the app
if __name__ == "__main__":
    demo.launch() 