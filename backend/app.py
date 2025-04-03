import gradio as gr
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
import os
import json

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load RAG chunks and create vector store
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

def respond(message, history):
    response = qa_chain({"question": message})
    return response["answer"]

# Create Gradio interface
demo = gr.ChatInterface(
    respond,
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!"
)

if __name__ == "__main__":
    demo.launch() 