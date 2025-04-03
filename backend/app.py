import gradio as gr
import os
import sys
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Print verbose debug info
print(f"Starting application setup...")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")
if os.path.exists("output"):
    print(f"Output directory contents: {os.listdir('output')}")
    if os.path.exists("output/rag_chunks"):
        print(f"RAG chunks directory contents: {os.listdir('output/rag_chunks')}")

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load RAG chunks from JSON files with extra error handling
def load_json_chunks():
    documents = []
    rag_dir = "output/rag_chunks"
    
    if not os.path.exists(rag_dir):
        print(f"Directory not found: {rag_dir}")
        print(f"Available directories: {os.listdir('.')}")
        # Try alternate location
        rag_dir = "rag_chunks"
        if not os.path.exists(rag_dir):
            return documents
    
    print(f"Reading from {rag_dir}")
    
    for filename in os.listdir(rag_dir):
        if filename.endswith('.json'):
            try:
                filepath = os.path.join(rag_dir, filename)
                print(f"Loading {filepath}")
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    book_title = data.get('book_title', 'Unknown')
                    chunks = data.get('chunks', [])
                    
                    for chunk in chunks:
                        content = chunk.get('content', '')
                        metadata = chunk.get('metadata', {})
                        doc = Document(page_content=content, metadata=metadata)
                        documents.append(doc)
                    
                    print(f"Loaded {len(chunks)} chunks from {book_title}")
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
    
    print(f"Total documents loaded: {len(documents)}")
    return documents

# Create vector store
print("Loading documents from JSON files...")
documents = load_json_chunks()

if documents:
    print(f"Creating vector store with {len(documents)} documents...")
    vector_store = FAISS.from_documents(documents, embeddings)
    print("Vector store created successfully")
else:
    print("No documents loaded, creating mock vector store with SPECIFIC Red Wedding info")
    mock_texts = [
        "The Red Wedding was a massacre that took place during the War of the Five Kings. During the wedding feast of Edmure Tully and Roslin Frey at the Twins, the Lord of the Crossing, Walder Frey, violated guest right by slaughtering many of the attendees, including Robb Stark, his mother Catelyn, and many of their bannermen. This was done as revenge against Robb for breaking his vow to marry one of Frey's daughters.",
        "Jon Snow is the bastard son of Ned Stark who joins the Night's Watch.",
        "House Lannister is one of the Great Houses of Westeros, with Tywin Lannister as its head.",
        "Daenerys Targaryen is the daughter of King Aerys II Targaryen."
    ]
    mock_docs = [Document(page_content=t) for t in mock_texts]
    vector_store = FAISS.from_documents(mock_docs, embeddings)

# Initialize LLM
llm = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    model_kwargs={"temperature": 0.7, "max_length": 512}
)

# Set up memory and QA chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
    memory=memory,
    verbose=True
)

# Define both GET and POST endpoints for /ask
@app.get("/ask")
async def ask_get():
    return {"response": "API is working, please use POST method with JSON body"}

@app.post("/ask")
async def ask_endpoint(request: Request):
    try:
        data = await request.json()
        question = data.get("text", "")
        print(f"Received question via API: {question}")
        response = qa_chain({"question": question})
        print(f"API response: {response}")
        return {"response": response["answer"]}
    except Exception as e:
        print(f"API error: {str(e)}")
        return {"response": f"I encountered an error: {str(e)}"}

# Gradio interface
def respond(message, history):
    try:
        response = qa_chain({"question": message})
        return response["answer"]
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!"
)

# THIS IS CRITICAL: Mount Gradio app as a subpath
app = gr.mount_gradio_app(app, demo, path="/gradio")

# Start the server - THIS MUST BE THE ENTRY POINT
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860) 