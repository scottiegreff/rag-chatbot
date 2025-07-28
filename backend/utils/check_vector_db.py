#!/usr/bin/env python3
"""
Check Vector Database Contents

This script checks what documents are currently in the Weaviate vector store.
"""

import os
from dotenv import load_dotenv
import weaviate
from weaviate.connect import ConnectionParams
import re

load_dotenv()
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
print("WEAVIATE_URL:", WEAVIATE_URL)

# Specify grpc_port as required by v4 client
client = weaviate.WeaviateClient(ConnectionParams.from_url(WEAVIATE_URL, grpc_port=50051))
client.connect()  # Ensure the client is connected
print("Collections:", client.collections.list_all())

def keyword_search(keywords, filename):
    docs = client.collections.get("Documents")
    # Fetch up to 500 objects for this test (should be enough for one document)
    results = docs.query.fetch_objects(limit=500)
    matches = []
    for obj in results.objects:
        props = obj.properties
        content = props.get("content", "")
        file = props.get("filename", "")
        if file == filename:
            for kw in keywords:
                if re.search(kw, content, re.IGNORECASE):
                    matches.append((props.get("chunk_index"), content.strip().replace("\n", " ")))
                    break
    return matches

# One-off search for Flatland keywords
keywords = [r"circle", r"polygon", r"class"]
filename = "Flatland By Edwin A. Abbott.txt"
results = keyword_search(keywords, filename)

if results:
    print(f"\n🔎 Found {len(results)} matching chunks in '{filename}':\n" + "-"*60)
    for idx, (chunk_idx, content) in enumerate(results, 1):
        print(f"\nChunk {chunk_idx}:\n{content[:500]}\n{'-'*40}")
else:
    print(f"\nNo matching chunks found in '{filename}'.")

# --- Cody and Scott keyword search ---
cody_keywords = [r"Cody", r"Scott"]
cody_filename = "Cody-and-Scott-Coding-Adventures-at-FCIAS.txt"
cody_results = keyword_search(cody_keywords, cody_filename)

if cody_results:
    print(f"\n🔎 Found {len(cody_results)} matching chunks in '{cody_filename}':\n" + "-"*60)
    for idx, (chunk_idx, content) in enumerate(cody_results, 1):
        print(f"\nChunk {chunk_idx}:\n{content[:500]}\n{'-'*40}")
else:
    print(f"\nNo matching chunks found in '{cody_filename}'.")

try:
    docs = client.collections.get("Documents")
    results = docs.query.fetch_objects(limit=5)
    if hasattr(results, 'objects') and results.objects:
        print(f"\n📊 Found {len(results.objects)} documents in the vector database:")
        print("-" * 50)
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            print(f"\n📄 Document {i}:")
            for k, v in props.items():
                print(f"   {k}: {v}")
    else:
        print("\n📭 No documents found in the vector database.")
except Exception as e:
    print(f"❌ Error checking vector database: {e}")

# --- Direct vector search for RAG debugging ---
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("intfloat/e5-large")
    query = "Cody and Scott at FCIAS"
    query_embedding = model.encode(query).tolist()
    docs = client.collections.get("Documents")
    # Fetch more results and print scores if available
    results = docs.query.near_vector(near_vector=query_embedding, limit=10, return_metadata=["distance"])
    print(f"\n🔎 Top 10 vector search results for query: '{query}'\n{'-'*60}")
    if hasattr(results, 'objects') and results.objects:
        for i, obj in enumerate(results.objects, 1):
            props = obj.properties
            content = props.get("content", "")
            filename = props.get("filename", "")
            # Try to get distance/score if available
            score = getattr(obj, 'distance', None) or getattr(obj, 'score', None) or getattr(obj, 'similarity', None)
            print(f"Result {i} (filename: {filename}, score: {score}):\n{content[:500]}\n{'-'*40}")
    else:
        print("No results found for direct vector search.")
except Exception as e:
    print(f"[DEBUG] Error running direct vector search: {e}")

# --- Check if vectors are actually stored ---
print(f"\n🔍 Checking if vectors are stored in collection...")
try:
    docs = client.collections.get("Documents")
    # Fetch all objects to see if they have vectors
    all_objects = docs.query.fetch_objects(limit=10)
    if hasattr(all_objects, 'objects') and all_objects.objects:
        print(f"Found {len(all_objects.objects)} objects in collection")
        for i, obj in enumerate(all_objects.objects[:3]):  # Check first 3
            print(f"Object {i}: has vector = {hasattr(obj, 'vector') and obj.vector is not None}")
            if hasattr(obj, 'vector') and obj.vector is not None:
                print(f"  Vector length: {len(obj.vector)}")
            else:
                print(f"  No vector found")
    else:
        print("No objects found in collection")
except Exception as e:
    print(f"Error checking vectors: {e}") 