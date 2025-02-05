from langchain_community.embeddings import HuggingFaceEmbeddings
import os

def test_embeddings():
    print("Testing embedding model loading...")
    try:
        # Initialize the embedding model
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Test it with a simple sentence
        test_text = "This is a test sentence."
        vector = embeddings.embed_query(test_text)
        
        print("✓ Successfully loaded embedding model")
        print(f"✓ Generated embedding vector of length: {len(vector)}")
        return True
    except Exception as e:
        print(f"Error loading embeddings: {str(e)}")
        return False

if __name__ == "__main__":
    print("Starting component tests...")
    test_embeddings()