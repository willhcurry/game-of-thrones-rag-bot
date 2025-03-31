"""
Game of Thrones Knowledge Bot

This module implements a Retrieval Augmented Generation (RAG) system for
answering questions about the Game of Thrones book series. It uses:
- Vector-based similarity search with HuggingFace embeddings
- Chroma vector database for storing and querying content
- Pre-processed text chunks from the books with metadata

The bot connects the frontend interface to the knowledge base,
providing contextually relevant passages from the books in response
to user questions without requiring a generative AI model.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import json
import os

class GameOfThronesBot:
    """
    A retrieval-based question answering system for Game of Thrones content.
    
    This class loads pre-processed book chunks, creates embeddings, and 
    performs similarity searches to answer questions about the Game of Thrones
    universe based on content from the original books.
    
    Attributes:
        rag_dir (str): Directory containing RAG chunks in JSON format
        chunks (list): Loaded content chunks with metadata
        vectorstore (Chroma): Vector database containing embedded chunks
    """
    
    def __init__(self):
        """
        Initialize the Game of Thrones knowledge base.
        
        This constructor:
        1. Sets up the path to pre-processed RAG chunks
        2. Loads the chunks into memory
        3. Creates and initializes the vector store with embeddings
        """
        self.rag_dir = os.path.join("..", "output", "rag_chunks")
        print("Initializing Game of Thrones Knowledge Base...")
        
        # Load chunks and create vectorstore
        self.chunks = self.load_rag_chunks()
        self.vectorstore = self.create_vectorstore()
    
    def load_rag_chunks(self):
        """
        Load pre-processed text chunks from RAG JSON files with memory optimization.
        
        This method scans the RAG directory for JSON files containing
        pre-processed book chunks, but limits the number loaded to stay
        within memory constraints for cloud deployment.
        
        Returns:
            list: A memory-optimized list of content chunks with metadata
        """
        all_chunks = []
        total_chunks = 0
        max_chunks = 200  # Limit total chunks for memory efficiency
        chunks_per_book = 40  # Take an equal amount from each book
        
        for filename in os.listdir(self.rag_dir):
            if filename.endswith('_rag.json'):
                with open(os.path.join(self.rag_dir, filename), 'r') as f:
                    data = json.load(f)
                    # Load limited chunks from each book
                    book_chunks = data['chunks'][:chunks_per_book]
                    all_chunks.extend(book_chunks)
                    total_chunks += len(book_chunks)
                    print(f"Loaded {len(book_chunks)} chunks from {filename}")
                    
                    # Stop if we exceed the maximum chunk limit
                    if total_chunks >= max_chunks:
                        print(f"Reached memory-safe limit of {max_chunks} chunks")
                        break
        
        print(f"Total chunks loaded: {len(all_chunks)}")
        return all_chunks
    
    def create_vectorstore(self):
        """
        Create a vector store using a memory-efficient embedding model.
        
        This method:
        1. Initializes a smaller, more memory-efficient HuggingFace model
        2. Extracts text and metadata from chunks
        3. Creates vector embeddings with reduced batch size
        4. Stores these in a Chroma vector database
        
        Returns:
            Chroma: A populated vector store with embedded content
        """
        # Using a smaller model to reduce memory usage by ~60%
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-MiniLM-L3-v2",  # Memory-efficient model
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'batch_size': 4}  # Reduced batch size for memory savings
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
        """
        Answer a question about Game of Thrones using RAG retrieval.
        
        This method:
        1. Performs a similarity search between the question and embedded chunks
        2. Retrieves the most relevant passages from the books
        3. Formats the response with source attribution
        4. Optionally adds contextual information for certain topics
        
        Args:
            question (str): The user's question about Game of Thrones
            
        Returns:
            str: A formatted response containing relevant passages from the books
        """
        # Find the most relevant chunks using semantic similarity
        docs = self.vectorstore.similarity_search(question, k=2)
        
        if docs:
            # Extract metadata for better formatting
            sources = set()
            content = []
            
            for doc in docs:
                snippet = doc.page_content
                source = f"{doc.metadata['book_title']}"
                sources.add(source)
                content.append({"source": source, "content": snippet})
            
            # Build a nicely formatted response with source attribution
            response = f"Here's what I found:\n\n"
            for item in content:
                response += f"From {item['source']}:\n{item['content']}\n\n"
            
            # Add extra context based on entity recognition
            # This enhances responses with additional background information
            if "stark" in question.lower() or "jon" in question.lower():
                response += "\nHouse Stark is one of the Great Houses of Westeros, ruling over the vast region known as the North."
            
            return response
        else:
            return "I couldn't find any relevant information about that."