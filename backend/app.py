import gradio as gr
import os
import sys
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# Print debug info
print(f"Starting application setup...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Try to use a pre-built vector store first
vector_store_path = "output/faiss_index"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")  # Smaller model

# Load vector store if it exists
if os.path.exists(vector_store_path):
    print(f"Loading existing vector store from {vector_store_path}")
    vector_store = FAISS.load_local(vector_store_path, embeddings)
    print("Vector store loaded successfully")
else:
    print(f"Vector store not found at {vector_store_path}, using mock data")
    # Create a simple mock store with a few entries
    from langchain.docstore.document import Document
    texts = [
        "Jon Snow is the son of Lyanna Stark and Rhaegar Targaryen.",
        "Daenerys Targaryen is the Mother of Dragons and breaker of chains.",
        "The Stark family includes Ned, Catelyn, Robb, Sansa, Arya, Bran, and Rickon.",
        "House Lannister's words are 'Hear Me Roar', but they're better known for 'A Lannister always pays his debts'."
    ]
    docs = [Document(page_content=t) for t in texts]
    vector_store = FAISS.from_documents(docs, embeddings)
    
# Initialize LLM - use a smaller model
llm = HuggingFaceHub(
    repo_id="google/flan-t5-small",  # Smaller model to start with
    model_kwargs={"temperature": 0.7, "max_length": 512}
)

# Set up memory and QA chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    memory=memory,
    verbose=True
)

def respond(message, history):
    try:
        print(f"Received question: {message}")
        response = qa_chain({"question": message})
        print(f"Generated response: {response}")
        return response["answer"]
    except Exception as e:
        print(f"Error in respond: {str(e)}")
        return f"I encountered an error: {str(e)}"

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!",
)

if __name__ == "__main__":
    demo.launch() 