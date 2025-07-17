# Model Optimization Guide

## Current Model Size Issues
- TinyLlama 1.1B: ~668MB (already optimized)
- Sentence Transformers: ~438MB (can be reduced)

## Optimization Strategies

### 1. Use Smaller Sentence Transformer Model
Replace `all-mpnet-base-v2` with smaller alternatives:
- `all-MiniLM-L6-v2` (80MB vs 438MB) - 82% smaller
- `paraphrase-MiniLM-L3-v2` (61MB) - 86% smaller

### 2. Model Quantization
- Convert models to INT8 or INT4 quantization
- Potential 50-75% size reduction

### 3. Model Caching Strategy
- Cache models in volume instead of image
- Download on first run, persist in volume

### 4. Lazy Loading
- Load models only when needed
- Unload unused models

## Implementation
```python
# In backend/services/rag_service.py
# Replace:
# self.embedding_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# With:
self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

## Expected Results
- Current: ~21GB
- After optimizations: ~4-6GB
- After model optimization: ~2-3GB 