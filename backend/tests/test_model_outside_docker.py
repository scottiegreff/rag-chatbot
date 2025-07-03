#!/usr/bin/env python3
"""
Test script to run TinyLlama model outside Docker to check performance
"""
import time
import os
from pathlib import Path

def test_model_performance():
    print("🧪 Testing TinyLlama model outside Docker...")
    
    # Check if model exists
    model_path = Path("./models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    if not model_path.exists():
        print(f"❌ Model not found at {model_path}")
        return
    
    print(f"✅ Model found: {model_path}")
    print(f"📁 Model size: {model_path.stat().st_size / (1024*1024):.1f} MB")
    
    try:
        from llama_cpp import Llama
        print("✅ llama-cpp-python imported successfully")
    except ImportError:
        print("❌ llama-cpp-python not installed. Installing...")
        os.system("pip install llama-cpp-python")
        from llama_cpp import Llama
    
    # Test model loading
    print("\n🔄 Loading model...")
    load_start = time.time()
    
    model = Llama(
        model_path=str(model_path),
        n_ctx=4096,
        n_gpu_layers=0,  # CPU only
        verbose=False
    )
    
    load_end = time.time()
    load_duration = (load_end - load_start) * 1000
    print(f"✅ Model loaded in {load_duration:.2f}ms")
    
    # Test simple inference
    print("\n🤖 Testing simple inference...")
    
    # Simple prompt
    prompt = "User: Hello\nAssistant:"
    
    print(f"📝 Prompt: {prompt}")
    print("🔄 Generating response...")
    
    gen_start = time.time()
    
    response = model.create_completion(
        prompt,
        max_tokens=50,
        temperature=0.7,
        top_p=0.85,
        repeat_penalty=1.1,
        stop=["User:", "Assistant:"],
        stream=False
    )
    
    gen_end = time.time()
    gen_duration = (gen_end - gen_start) * 1000
    
    print(f"✅ Response generated in {gen_duration:.2f}ms")
    print(f"📄 Response: {response['choices'][0]['text']}")
    
    # Test streaming inference
    print("\n🌊 Testing streaming inference...")
    
    stream_start = time.time()
    first_token_time = None
    
    stream_response = model.create_completion(
        prompt,
        max_tokens=50,
        temperature=0.7,
        top_p=0.85,
        repeat_penalty=1.1,
        stop=["User:", "Assistant:"],
        stream=True
    )
    
    token_count = 0
    full_response = ""
    
    for chunk in stream_response:
        if isinstance(chunk, dict) and 'choices' in chunk and chunk['choices']:
            token = chunk['choices'][0]['text']
            if token:
                if first_token_time is None:
                    first_token_time = time.time()
                    first_token_duration = (first_token_time - stream_start) * 1000
                    print(f"🎯 First token received in {first_token_duration:.2f}ms")
                
                token_count += 1
                full_response += token
                print(f"Token {token_count}: '{token}'")
    
    stream_end = time.time()
    stream_duration = (stream_end - stream_start) * 1000
    
    print(f"✅ Streaming completed in {stream_duration:.2f}ms")
    print(f"📊 Total tokens generated: {token_count}")
    print(f"📄 Full response: {full_response}")
    
    # Performance summary
    print("\n📈 PERFORMANCE SUMMARY:")
    print(f"  • Model loading: {load_duration:.2f}ms")
    print(f"  • First token latency: {first_token_duration:.2f}ms" if first_token_time else "  • First token latency: N/A")
    print(f"  • Total generation time: {stream_duration:.2f}ms")
    print(f"  • Tokens per second: {token_count / (stream_duration / 1000):.2f}")
    
    # Compare with Docker performance
    print("\n🔍 COMPARISON WITH DOCKER:")
    print("  • Docker model loading: ~333ms")
    print("  • Docker first token: ~80,000ms")
    print("  • Docker total time: ~82,000ms")
    
    if first_token_time and first_token_duration < 5000:  # Less than 5 seconds
        print("✅ HOST PERFORMANCE IS MUCH BETTER - Docker is the issue!")
    elif first_token_time and first_token_duration > 30000:  # More than 30 seconds
        print("❌ HOST PERFORMANCE IS ALSO SLOW - Model/configuration issue")
    else:
        print("⚠️  HOST PERFORMANCE IS MODERATE - May be model size issue")

if __name__ == "__main__":
    test_model_performance() 