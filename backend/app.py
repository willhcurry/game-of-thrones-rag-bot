import gradio as gr
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Print debug info
import os
import sys
print(f"Starting application setup...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Initialize LLM
llm = HuggingFaceHub(repo_id="HuggingFaceH4/zephyr-7b-beta", model_kwargs={"temperature": 0.7})
memory = ConversationBufferMemory()

# Simple conversation chain
chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

def respond(message, history):
    response = chain.predict(input=message)
    return response

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!"
)

if __name__ == "__main__":
    demo.launch() 