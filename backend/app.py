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

# Initialize embeddings model for document vectorization
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_documents():
    """
    Load pre-processed Game of Thrones book chunks from JSON files.
    
    Each chunk contains content from the books along with metadata about
    its source, chapter, and other contextual information.
    
    Returns:
        list: A list of Document objects ready for vector embedding
    """
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
    return documents

# Load document chunks and create vector store for similarity search
documents = load_documents()
vector_store = FAISS.from_documents(documents, embeddings)

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

def api_ask(question):
    """
    Process a question through the RAG system and return a formatted response.
    
    This function is exposed through the API endpoint and handles error
    cases gracefully.
    
    Args:
        question (str): The user's question about Game of Thrones
        
    Returns:
        dict: Formatted response with answer or error message
    """
    try:
        if not question or question is None:
            return {"response": "I didn't receive a question. Please try again."}
        
        # Safer approach: Get documents directly first
        try:
            docs = vector_store.similarity_search(question, k=4)
            
            # If no documents found, return a graceful message
            if not docs:
                return {"response": "I couldn't find any information about that in the Game of Thrones books."}
                
            # Format a simple response from the retrieved documents
            response_text = f"Here's what I found about '{question}':\n\n"
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('book_title', 'Game of Thrones')
                chapter = doc.metadata.get('chapter', 'Unknown chapter')
                response_text += f"From {source} ({chapter}):\n{doc.page_content}\n\n"
                
            return {"response": response_text}
            
        except Exception as e:
            # Fallback to the QA chain, with error handling
            response = qa_chain({"question": question})
            return {"response": response["answer"]}
            
    except Exception as e:
        return {"error": str(e)}

def chat_interface(message, history):
    """
    Process a message from the chat interface.
    
    This function is used by the Gradio chat interface to handle
    user messages and generate responses.
    
    Args:
        message (str): The user's message
        history (list): The conversation history
        
    Returns:
        str: The generated response
    """
    response = qa_chain({"question": message})
    return response["answer"]

# Set up Gradio app with both chat interface and API
with gr.Blocks() as demo:
    # Chat interface tab
    with gr.Tab("Chat"):
        gr.ChatInterface(
            chat_interface,
            title="Game of Thrones Knowledge Bot",
            description="Ask me anything about Game of Thrones!"
        )
    
    # API tab for documentation and testing
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

# Launch the app when run directly
if __name__ == "__main__":
    # Start the Gradio interface on default port 7860
    demo.launch() 