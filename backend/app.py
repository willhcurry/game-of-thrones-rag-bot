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

# Initialize a local model (distilgpt2 is small enough to fit in memory)
print("Loading local model...")
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
print("Local model loaded")

# Set up memory and QA chain
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=local_llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
    memory=memory
)

# Define API function
def api_ask(question):
    try:
        response = qa_chain({"question": question})
        return {"response": response["answer"]}
    except Exception as e:
        return {"error": str(e)}

# Create chat interface
def chat_interface(message, history):
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
    print("Launching Gradio interface...")
    demo.launch() 