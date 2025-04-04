import gradio as gr
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

# Print debug info
print("Starting application setup...")
print(f"Current directory: {os.getcwd()}")

# Initialize embeddings
print("Initializing embeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load documents and create vector store
print("Loading documents...")
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

print(f"Loaded {len(documents)} documents")
vector_store = FAISS.from_documents(documents, embeddings)
print("Vector store created")

# Simple answer function that uses vector store but no LLM
def answer_question(question):
    docs = vector_store.similarity_search(question, k=2)
    response = "\n\n".join([doc.page_content for doc in docs])
    return {"response": response}

# Create Gradio interface
demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(label="Question"),
    outputs=gr.Textbox(label="Answer"),
    title="Game of Thrones Knowledge Bot (No LLM)",
    description="Simple retrieval without using an LLM"
)

# Launch
if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch() 