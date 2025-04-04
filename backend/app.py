import gradio as gr
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load documents and create vector store
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

vector_store = FAISS.from_documents(documents, embeddings)

# Simple retrieval function without LLM
def retrieve_answer(question):
    try:
        # Get relevant documents
        docs = vector_store.similarity_search(question, k=3)
        
        # Format a response
        response = f"Here's what I found about '{question}':\n\n"
        for i, doc in enumerate(docs, 1):
            response += f"Source {i}: {doc.page_content}\n\n"
            
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

# Chat interface function
def chat_interface(message, history):
    result = retrieve_answer(message)
    return result.get("response", f"Error: {result.get('error', 'Unknown error')}")

# API function - formatted for Gradio
def api_ask(question):
    result = retrieve_answer(question)
    return result

# Set up Gradio app
with gr.Blocks() as demo:
    # Chat interface tab
    with gr.Tab("Chat"):
        gr.ChatInterface(
            chat_interface,
            title="Game of Thrones Knowledge Bot",
            description="Ask me anything about Game of Thrones!"
        )
    
    # API tab for documentation
    with gr.Tab("API"):
        gr.Markdown("""
        ## API Endpoint
        
        You can access this bot programmatically using the following endpoint:
        
        ```
        POST https://willhcurry-gotbot.hf.space/api/predict
        
        {
          "data": ["Your question here"]
        }
        ```
        
        The response will be in this format:
        ```
        {
          "data": [{"response": "Answer to your question"}]
        }
        ```
        """)
        
        gr.Interface(
            fn=api_ask,
            inputs=gr.Textbox(label="Test question"),
            outputs=gr.JSON(label="Response"),
            title="API Tester",
            description="Test the API directly"
        )

# Launch the app
if __name__ == "__main__":
    demo.launch() 