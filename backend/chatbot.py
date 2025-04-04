"""
Game of Thrones Chatbot - Core RAG Implementation

This module implements the core Retrieval Augmented Generation (RAG) system 
for the Game of Thrones knowledge bot. It provides the fundamental components
needed to:
1. Process user queries about Game of Thrones
2. Retrieve relevant context from the book corpus
3. Generate accurate, book-based responses
4. Maintain conversation context

The chatbot uses LangChain components to implement a production-ready RAG system
with vector search capabilities.

Classes:
    GameOfThronesBot: Main chatbot implementation with RAG capabilities

Usage:
    from chatbot import GameOfThronesBot
    
    bot = GameOfThronesBot()
    response = bot.ask("Who is Jon Snow?")
"""

import os
import json
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import HuggingFaceHub
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.text import TextLoader
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from typing import List, Dict, Optional, Any, Union

class GameOfThronesBot:
    """
    A retrieval-augmented chatbot specializing in Game of Thrones knowledge.
    
    This class manages the complete RAG pipeline:
    1. Loading and managing document embeddings
    2. Storing and retrieving vectors efficiently
    3. Maintaining conversation context
    4. Generating contextually relevant responses using an LLM
    
    Attributes:
        embeddings: The embedding model used for text vectorization
        vector_store: FAISS vector database for similarity search
        memory: Conversation memory buffer for context retention
        qa_chain: The retrieval and generation chain
    """
    
    def __init__(
        self, 
        vector_store_path: str = "faiss_index",
        books_dir: str = "input",
        rag_chunks_dir: str = "output/rag_chunks",
        model_name: str = "HuggingFaceH4/zephyr-7b-beta",
    ):
        """
        Initialize the Game of Thrones chatbot.
        
        Args:
            vector_store_path: Path to store/load FAISS index
            books_dir: Directory containing book text files
            rag_chunks_dir: Directory containing pre-processed RAG chunks
            model_name: Name of the HuggingFace model to use
        """
        self.embeddings = HuggingFaceEmbeddings()
        
        # Try to load existing vector store or create a new one
        if os.path.exists(vector_store_path):
            self.vector_store = FAISS.load_local(vector_store_path, self.embeddings)
        else:
            # Try to load from pre-processed chunks first
            documents = self._load_rag_chunks(rag_chunks_dir)
            
            # If no chunks available, process raw book files
            if not documents:
                documents = self._load_book_files(books_dir)
                
            if documents:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                # Save for future use
                self.vector_store.save_local(vector_store_path)
            else:
                raise ValueError("No documents found to create vector store")
        
        # Initialize LLM
        self.llm = HuggingFaceHub(
            repo_id=model_name,
            model_kwargs={"temperature": 0.7, "max_length": 512}
        )
        
        # Set up memory and conversation chain
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
        )
    
    def _load_rag_chunks(self, rag_chunks_dir: str) -> List[Document]:
        """
        Load pre-processed RAG chunks from JSON files.
        
        Args:
            rag_chunks_dir: Directory containing RAG chunk JSON files
            
        Returns:
            List of Document objects ready for vector embedding
        """
        documents = []
        if os.path.exists(rag_chunks_dir):
            for filename in os.listdir(rag_chunks_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(rag_chunks_dir, filename)
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        chunks = data.get('chunks', [])
                        for chunk in chunks:
                            content = chunk.get('content', '')
                            metadata = chunk.get('metadata', {})
                            doc = Document(page_content=content, metadata=metadata)
                            documents.append(doc)
        return documents
    
    def _load_book_files(self, books_dir: str) -> List[Document]:
        """
        Load and process raw book text files.
        
        Args:
            books_dir: Directory containing book text files
            
        Returns:
            List of Document objects ready for vector embedding
        """
        documents = []
        if os.path.exists(books_dir):
            for filename in os.listdir(books_dir):
                if filename.endswith('.txt'):
                    loader = TextLoader(os.path.join(books_dir, filename))
                    documents.extend(loader.load())
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            documents = text_splitter.split_documents(documents)
        return documents
    
    def ask(self, question: str) -> str:
        """
        Process a user question and generate a response using RAG.
        
        This method:
        1. Retrieves relevant context from the vector database
        2. Passes the context and question to the language model
        3. Returns the generated response
        
        Args:
            question: The user's question about Game of Thrones
            
        Returns:
            Generated response based on book knowledge
        """
        if not question or question.strip() == "":
            return "Please ask a question about Game of Thrones."
        
        try:
            # Process through the QA chain
            response = self.qa_chain({"question": question})
            return response["answer"]
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    def reset_conversation(self) -> None:
        """
        Reset the conversation history.
        
        This clears the memory buffer, starting a fresh conversation context.
        """
        self.memory.clear()