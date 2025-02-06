from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import json
import os

class GameOfThronesBot:
    def __init__(self):
        self.rag_dir = os.path.join("..", "output", "rag_chunks")
        print("Initializing Game of Thrones Knowledge Base...")
        
        # Load chunks and create vectorstore
        self.chunks = self.load_rag_chunks()
        self.vectorstore = self.create_vectorstore()
    
    def load_rag_chunks(self):
        """Load all RAG chunks"""
        all_chunks = []
        for filename in os.listdir(self.rag_dir):
            if filename.endswith('_rag.json'):
                with open(os.path.join(self.rag_dir, filename), 'r') as f:
                    data = json.load(f)
                    all_chunks.extend(data['chunks'])
                    print(f"Loaded {len(data['chunks'])} chunks from {filename}")
        return all_chunks
    
    def create_vectorstore(self):
        """Create vector store from chunks"""
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        texts = [chunk['content'] for chunk in self.chunks]
        metadatas = [chunk['metadata'] for chunk in self.chunks]
        
        return Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            persist_directory="./vectorstore"
        )
    
    def ask(self, question: str):
        """Ask a question and get a response"""
        docs = self.vectorstore.similarity_search(question, k=3)
        
        if docs:
            response = "Here's what I found:\n\n"
            for i, doc in enumerate(docs, 1):
                response += f"From {doc.metadata['book_title']}:\n{doc.page_content}\n\n"
            return response
        else:
            return "I couldn't find any relevant information about that."