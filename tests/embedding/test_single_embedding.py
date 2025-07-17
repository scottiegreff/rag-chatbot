#!/usr/bin/env python3
"""
Simple test to verify e5-small embedding model works
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_e5_large():
    """Test the e5-large model specifically"""
    print("🧪 Testing intfloat/e5-large embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load the model
        print("🔄 Loading intfloat/e5-large...")
        model = SentenceTransformer('intfloat/e5-large', device='cpu')
        print("✅ Model loaded successfully!")
        
        # Test encoding
        test_text = "What are the company policies regarding vacation time?"
        print(f"🔤 Testing encoding: '{test_text}'")
        
        embedding = model.encode(test_text)
        print(f"✅ Encoding successful! Vector shape: {embedding.shape}")
        print(f"📏 Embedding dimension: {embedding.shape[0]}")
        
        # Test with multiple sentences
        sentences = [
            "How do I submit an expense report?",
            "What is the dress code policy?",
            "How do I request time off?"
        ]
        
        embeddings = model.encode(sentences)
        print(f"✅ Batch encoding successful! Shape: {embeddings.shape}")
        
        print("\n🎉 e5-large model test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing e5-large: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_e5_large() 