"""
Game of Thrones Knowledge Bot - Memory Optimized Version
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import json
import os
import gc

class GameOfThronesBot:
    def __init__(self):
        """Initialize with minimal memory footprint"""
        print("Initializing Game of Thrones Knowledge Base (memory-optimized)...")
        self.rag_dir = os.path.join("..", "output", "rag_chunks")
        self.chunks = None
        self.vectorstore = None
        self.embeddings = None
        # Don't load anything in constructor - lazy load on first query
    
    def _ensure_initialized(self):
        """Lazy initialization of resources when needed"""
        if self.vectorstore is None:
            self.chunks = self.load_rag_chunks()
            self.vectorstore = self.create_vectorstore()
    
    def load_rag_chunks(self):
        """Load minimal chunks to stay within memory constraints"""
        all_chunks = []
        max_chunks = 100  # Reduced from 200 to 100
        chunks_per_book = 20  # Reduced from 40 to 20
        
        # Create output/rag_chunks directory if it doesn't exist (for development)
        os.makedirs(os.path.join("..", "output", "rag_chunks"), exist_ok=True)
        
        try:
            # List the directory contents
            files = os.listdir(self.rag_dir)
            if not files:
                # Fallback data if no files available
                return [
                    {"content": "House Stark rules the North from their seat at Winterfell.", 
                     "metadata": {"book_title": "A Game of Thrones"}}
                ]
                
            for filename in files:
                if filename.endswith('_rag.json'):
                    with open(os.path.join(self.rag_dir, filename), 'r') as f:
                        data = json.load(f)
                        # Load smaller number of chunks
                        book_chunks = data['chunks'][:chunks_per_book]
                        all_chunks.extend(book_chunks)
                        
                        if len(all_chunks) >= max_chunks:
                            break
            
            print(f"Loaded {len(all_chunks)} chunks (memory-optimized)")
            return all_chunks
        except Exception as e:
            print(f"Error loading chunks: {str(e)}")
            # Return minimal fallback data
            return [
                {"content": "House Stark rules the North from their seat at Winterfell.", 
                 "metadata": {"book_title": "A Game of Thrones"}}
            ]
    
    def create_vectorstore(self):
        """Create vector store with minimal memory usage"""
        try:
            # Initialize the embedding model only when needed
            self.embeddings = HuggingFaceEmbeddings(
                model_name="paraphrase-MiniLM-L3-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'batch_size': 2}  # Reduced batch size further
            )
            
            texts = [chunk['content'] for chunk in self.chunks]
            metadatas = [chunk['metadata'] for chunk in self.chunks]
            
            # Create vectorstore with smaller collection name
            vectorstore = Chroma.from_texts(
                texts=texts,
                embedding=self.embeddings,
                metadatas=metadatas,
                persist_directory="./vectorstore"
            )
            
            # Force garbage collection after creating vector store
            gc.collect()
            
            return vectorstore
        except Exception as e:
            print(f"Error creating vectorstore: {str(e)}")
            return None
    
    def ask(self, question: str):
        """Process question with memory optimization"""
        try:
            # Ensure resources are initialized
            self._ensure_initialized()
            
            if self.vectorstore is None:
                return "I'm having trouble accessing my knowledge base at the moment."
            
            # Reduce k from 2 to 1 to get fewer results
            docs = self.vectorstore.similarity_search(question, k=1)
            
            if docs:
                sources = set()
                content = []
                
                for doc in docs:
                    snippet = doc.page_content
                    source = f"{doc.metadata['book_title']}"
                    sources.add(source)
                    content.append({"source": source, "content": snippet})
                
                # Build a more concise response
                response = "Here's what I found:\n\n"
                for item in content:
                    response += f"From {item['source']}:\n{item['content']}\n\n"
                
                # Force garbage collection after query
                gc.collect()
                
                return response
            else:
                return "I couldn't find any relevant information about that."
        except Exception as e:
            print(f"Error in ask: {str(e)}")
            return "I encountered an error while searching for information."
