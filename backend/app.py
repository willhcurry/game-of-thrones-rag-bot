import gradio as gr
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG components
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load documents from JSON files
documents = []
rag_dir = "output/rag_chunks"
if os.path.exists(rag_dir):
    for filename in os.listdir(rag_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(rag_dir, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                chunks = data.get('chunks', [])
                for chunk in chunks:
                    content = chunk.get('content', '')
                    metadata = chunk.get('metadata', {})
                    doc = Document(page_content=content, metadata=metadata)
                    documents.append(doc)

# Create vector store
vector_store = FAISS.from_documents(documents, embeddings)

# Initialize LLM
llm = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    model_kwargs={"temperature": 0.7, "max_length": 512}
)

# Set up memory and QA chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(),
    memory=memory
)

# Define the FastAPI endpoint
@app.post("/ask")
async def ask_endpoint(request: Request):
    data = await request.json()
    question = data.get("text", "")
    print(f"Received question: {question}")
    response = qa_chain({"question": question})
    print(f"Generated response: {response}")
    return {"response": response["answer"]}

# Gradio interface 
def respond(message, history):
    response = qa_chain({"question": message})
    return response["answer"]

demo = gr.ChatInterface(
    respond,
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!"
)

# Mount Gradio to FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

# Start server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860) 