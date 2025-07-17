#!/usr/bin/env python3
"""
Test script to compare different embedding models
"""
import os
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

def test_embedding_model(model_name):
    """Test a specific embedding model"""
    print(f"\n🧪 Testing embedding model: {model_name}")
    print("=" * 50)
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # Load model
        print(f"🔄 Loading {model_name}...")
        start_time = time.time()
        model = SentenceTransformer(model_name, device='cpu')
        load_time = time.time() - start_time
        print(f"✅ Model loaded in {load_time:.2f} seconds")
        
        # Test sentences
        test_sentences = [
            "What are the company policies regarding vacation time?",
            "How do I submit an expense report?",
            "What is the dress code policy?",
            "How do I request time off?",
            "What are the benefits for full-time employees?"
        ]
        
        # Test encoding speed
        print(f"\n🔤 Testing encoding speed with {len(test_sentences)} sentences...")
        encode_start = time.time()
        embeddings = model.encode(test_sentences)
        encode_time = time.time() - encode_start
        avg_time = encode_time / len(test_sentences)
        
        print(f"✅ Encoded {len(test_sentences)} sentences in {encode_time:.2f} seconds")
        print(f"📊 Average time per sentence: {avg_time*1000:.2f}ms")
        print(f"📏 Embedding dimension: {embeddings.shape[1]}")
        
        # Test similarity search
        print(f"\n🔍 Testing similarity search...")
        query = "vacation policy"
        query_embedding = model.encode([query])
        
        # Calculate similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        
        print(f"Query: '{query}'")
        for i, (sentence, similarity) in enumerate(zip(test_sentences, similarities)):
            print(f"  {i+1}. {sentence[:50]}... (similarity: {similarity:.3f})")
        
        return {
            'model': model_name,
            'load_time': load_time,
            'encode_time': encode_time,
            'avg_encode_time': avg_time,
            'embedding_dim': embeddings.shape[1],
            'max_similarity': max(similarities)
        }
        
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Embedding Model Comparison Test")
    print("=" * 60)
    
    # Models to test
    models = [
        "intfloat/e5-small",
        "intfloat/e5-large", 
        "sentence-transformers/all-MiniLM-L6-v2"
    ]
    
    results = []
    
    for model in models:
        result = test_embedding_model(model)
        if result:
            results.append(result)
    
    # Print comparison summary
    print(f"\n📊 COMPARISON SUMMARY")
    print("=" * 60)
    print(f"{'Model':<35} {'Load(s)':<8} {'Encode(ms)':<12} {'Dim':<6} {'Quality':<8}")
    print("-" * 60)
    
    for result in results:
        print(f"{result['model']:<35} {result['load_time']:<8.2f} {result['avg_encode_time']*1000:<12.2f} {result['embedding_dim']:<6} {result['max_similarity']:<8.3f}")
    
    print(f"\n💡 Recommendations:")
    print(f"• intfloat/e5-small: Fast (134MB), good for development")
    print(f"• intfloat/e5-large: Accurate (438MB), best for production")
    print(f"• all-MiniLM-L6-v2: Balanced (80MB), good compromise")
    
    print(f"\n🔧 To switch models, set EMBEDDING_MODEL in your .env file:")
    print(f"   EMBEDDING_MODEL=intfloat/e5-small    # Fast development")
    print(f"   EMBEDDING_MODEL=intfloat/e5-large    # Best quality")
    print(f"   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2  # Balanced")

if __name__ == "__main__":
    main() 