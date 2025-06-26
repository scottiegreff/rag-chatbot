import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.services.rag_service import RAGService

def test_healthcare_query():
    """Test healthcare document retrieval with multiple queries"""
    rag_service = RAGService()
    
    # Test multiple queries
    test_queries = [
        "Who is the best doctor in Vancouver?",
        "Dr. Narvis",
        "best doctor Vancouver",
        "Vancouver healthcare",
        "doctor in Vancouver",
        "physician Vancouver",
        "healthcare Vancouver"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing query: {query}")
        print(f"{'='*50}")
        
        results = rag_service.query_documents(query, n_results=5, include_scores=True)
        
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]
        scores = results.get('distances', [[]])[0] if 'distances' in results else [None]*len(docs)

        if docs:
            for i, (doc, metadata, score) in enumerate(zip(docs, metas, scores)):
                print(f"{i+1}. {doc}")
                print(f"   Source: {metadata.get('source')}")
                print(f"   Category: {metadata.get('category')}")
                if score is not None:
                    print(f"   Similarity score: {score}")
                print()
        else:
            print("No results found")

if __name__ == "__main__":
    test_healthcare_query() 