import gradio as gr
import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document

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

# Create vector store and QA chain
vector_store = FAISS.from_documents(documents, embeddings)
llm = HuggingFaceHub(
    repo_id="google/flan-t5-small",
    task="text-generation",
    model_kwargs={"temperature": 0.7, "max_length": 512}
)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vector_store.as_retriever(),
    memory=memory
)

# Create a direct API function
def ask_question(question):
    print(f"Received question: {question}")
    response = qa_chain({"question": question})
    print(f"Generated response: {response}")
    return {"response": response["answer"]}

# Gradio interface with the API function
with gr.Blocks() as demo:
    gr.Markdown("# Game of Thrones Knowledge Bot")
    gr.Markdown("Ask me anything about Game of Thrones!")
    
    # Chat interface
    chatbot = gr.Chatbot()
    msg = gr.Textbox(label="Your question")
    clear = gr.Button("Clear")
    
    def respond(message, chat_history):
        answer = qa_chain({"question": message})["answer"]
        chat_history.append((message, answer))
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: None, None, chatbot, queue=False)
    
    # Direct API endpoint
    gr.Interface(
        fn=ask_question,
        inputs=gr.Textbox(label="Question"),
        outputs=gr.JSON(),
        title="API Endpoint",
        description="Send POST requests to this endpoint",
        allow_flagging="never"
    )

# Launch the app
if __name__ == "__main__":
    demo.launch() 