import gradio as gr
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from transformers import pipeline

# Print debug info
print("Starting application setup...")
print(f"Current directory: {os.getcwd()}")
print(f"Directory listing: {os.listdir('.')}")

# Initialize a local model
print("Initializing local model...")
model = pipeline(
    "text-generation",
    model="distilgpt2",
    max_length=512
)

# Define a simple question answering function
def answer_question(question):
    # For debugging during startup
    print(f"Received question: {question}")
    
    # Return mock response while testing
    return {
        "response": f"You asked: {question}. This is a simplified response while we fix the model loading issues."
    }

# Create a Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Game of Thrones Knowledge Bot")
    gr.Markdown("Ask me anything about Game of Thrones!")
    
    # Chat interface
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your question")
    clear = gr.Button("Clear")
    
    def respond(message, chat_history):
        response = answer_question(message)["response"]
        chat_history.append((message, response))
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)

# Launch the app
if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch() 