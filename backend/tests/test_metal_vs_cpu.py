#!/usr/bin/env python3
"""
Test script to compare Metal vs CPU performance for TinyLlama
"""
import time
import os
from pathlib import Path

def test_metal_vs_cpu():
    print("🧪 Testing Metal vs CPU performance...")
    
    model_path = Path("./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    # Test 1: CPU-only mode
    print("\n🔧 Testing CPU-only mode...")
    os.environ['CT_METAL'] = '0'
    os.environ['CT_CUDA'] = '0'
    os.environ['GPU_LAYERS'] = '0'
    
    try:
        from llama_cpp import Llama
        
        # Test CPU performance
        start_time = time.time()
        llm = Llama(
            model_path=str(model_path),
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False
        )
        load_time = time.time() - start_time
        print(f"✅ CPU Model loaded in {load_time:.2f}s")
        
        # Test CPU inference
        start_time = time.time()
        response = llm("Hello", max_tokens=50, temperature=0.7)
        inference_time = time.time() - start_time
        print(f"✅ CPU Inference: {inference_time:.2f}s")
        print(f"✅ CPU Response: {response['choices'][0]['text'][:100]}...")
        
        del llm
        
    except Exception as e:
        print(f"❌ CPU test failed: {e}")
    
    # Test 2: Try Metal mode (if available)
    print("\n⚡ Testing Metal mode...")
    os.environ['CT_METAL'] = '1'
    os.environ['GPU_LAYERS'] = '4'
    
    try:
        from llama_cpp import Llama
        
        # Test Metal performance
        start_time = time.time()
        llm = Llama(
            model_path=str(model_path),
            n_ctx=2048,
            n_threads=4,
            n_gpu_layers=4,
            verbose=False
        )
        load_time = time.time() - start_time
        print(f"✅ Metal Model loaded in {load_time:.2f}s")
        
        # Test Metal inference
        start_time = time.time()
        response = llm("Hello", max_tokens=50, temperature=0.7)
        inference_time = time.time() - start_time
        print(f"✅ Metal Inference: {inference_time:.2f}s")
        print(f"✅ Metal Response: {response['choices'][0]['text'][:100]}...")
        
        del llm
        
    except Exception as e:
        print(f"❌ Metal test failed: {e}")
        print("💡 This confirms Metal is not available in this environment")

if __name__ == "__main__":
    test_metal_vs_cpu() 