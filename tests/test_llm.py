import asyncio
from backend.services.llm_service import LLMService

async def test():
    print("Initializing LLM Service...")
    service = LLMService()
    
    if not service.model:
        print("Model failed to load. Check the error messages above.")
        return
    
    print("\nTesting with some example prompts...")
    
    test_prompts = [
        "What is artificial intelligence?",
        "Write a short poem about the ocean.",
        "Explain quantum computing in simple terms."
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        print("Generating response...")
        response = await service.generate_response(prompt)
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test()) 