import gradio as gr
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
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

# Create a QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=local_llm,
    chain_type="stuff",
    retriever=vector_store.as_retriever(search_kwargs={"k": 3})
)
print("QA chain created")

# Answer function that uses the QA chain
def answer_question(question):
    try:
        response = qa_chain.run(question)
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
demo = gr.Interface(
    fn=answer_question,
    inputs=gr.Textbox(label="Question"),
    outputs=gr.Textbox(label="Answer"),
    title="Game of Thrones Knowledge Bot",
    description="Ask me anything about Game of Thrones!"
)

# Launch
if __name__ == "__main__":
    print("Launching Gradio interface...")
    demo.launch() 