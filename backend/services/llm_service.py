from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import threading
import multiprocessing

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Global singleton instance
_llm_service_instance = None

class LLMService:
    """Service for interacting with the LLM model using ctransformers"""
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance to force fresh initialization"""
        global _llm_service_instance
        if _llm_service_instance and hasattr(_llm_service_instance, 'model'):
            logger.info("🔄 Resetting LLMService singleton instance")
            _llm_service_instance.model = None
        _llm_service_instance = None
        logger.info("✅ LLMService singleton instance reset")
    
    def __new__(cls):
        global _llm_service_instance
        if _llm_service_instance is None:
            logger.info("🆕 Creating new LLMService instance (singleton)")
            _llm_service_instance = super(LLMService, cls).__new__(cls)
        else:
            logger.info("♻️  Reusing existing LLMService instance (singleton)")
        return _llm_service_instance
    
    def __init__(self):
        # Only initialize if not already initialized
        if hasattr(self, 'model'):
            logger.info("🔄 LLMService already initialized, skipping...")
            return
            
        self.model = None
        # Model configuration
        self.model_type = os.getenv("MODEL_TYPE", "llama")
        self.gpu_layers = int(os.getenv("GPU_LAYERS", "50"))
        self.context_length = int(os.getenv("CONTEXT_LENGTH", "4096"))
        self.model_path = os.getenv("MODEL_PATH", "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
        
        # Generation parameters
        self.max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "512"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.top_p = float(os.getenv("TOP_P", "0.85"))
        self.repetition_penalty = float(os.getenv("REPETITION_PENALTY", "1.1"))
        
        logger.info(
            f"LLMService initialized with model_type={self.model_type}, "
            f"gpu_layers={self.gpu_layers}, context_length={self.context_length}, "
            f"max_new_tokens={self.max_new_tokens}, temperature={self.temperature}, "
            f"top_p={self.top_p}, repetition_penalty={self.repetition_penalty}"
        )
        self._load_model()
    
    def _load_model(self):
        """Load the language model using llama-cpp-python"""
        try:
            from llama_cpp import Llama
            
            logger.info("🔄 Loading language model... (this might take a minute)")
            load_start_time = time.time()
            
            # Project root directory
            project_root = Path(__file__).parent.parent.parent
            logger.info(f"📁 Project root: {project_root}")
            
            # Get model configuration from environment variables
            model_path = project_root / self.model_path
            logger.info(f"🔍 Looking for model at: {model_path}")
            
            # Check if model exists
            if not model_path.exists():
                logger.error(f"❌ Model not found at {model_path}. Please download a model first.")
                return
            
            logger.info("✅ Model file found, attempting to load...")
            
            # Initialize the model with llama-cpp-python
            model_init_start_time = time.time()
            self.model = Llama(
                model_path=str(model_path),
                n_ctx=self.context_length,
                n_gpu_layers=self.gpu_layers,
                verbose=False
            )
            model_init_end_time = time.time()
            model_init_duration = (model_init_end_time - model_init_start_time) * 1000
            logger.info(f"🤖 [TIMING] Model initialization completed in {model_init_duration:.2f}ms")
            
            load_end_time = time.time()
            load_duration = (load_end_time - load_start_time) * 1000
            logger.info(f"🎉 [TIMING] Model loaded successfully in {load_duration:.2f}ms!")
            logger.info(f"📊 Model type: {self.model_type}, GPU layers: {self.gpu_layers}, Context length: {self.context_length}")
            logger.info(f"[DIAGNOSTIC] CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={self.gpu_layers}")
            logger.info("[DIAGNOSTIC] Note: This does not guarantee GPU/Metal is actually being used inside Docker on Mac.")
            
        except Exception as e:
            load_end_time = time.time()
            load_duration = (load_end_time - load_start_time) * 1000
            logger.error(f"❌ [TIMING] Model loading failed after {load_duration:.2f}ms: {e}")
            import traceback
            logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
    
    def _prepare_prompt(self, message: str, history: Optional[List[Dict[str, str]]] = None, system_instruction: Optional[str] = None) -> str:
        """Prepare the prompt for the model with conversation history and system instruction"""
        prompt_start_time = time.time()
        
        # Check if Chain of Thought reasoning should be used
        cot_check_start_time = time.time()
        use_cot = self._should_use_chain_of_thought(message)
        cot_check_end_time = time.time()
        cot_check_duration = (cot_check_end_time - cot_check_start_time) * 1000
        logger.info(f"🧠 [TIMING] Chain of Thought check completed in {cot_check_duration:.2f}ms")
        
        if use_cot:
            logger.info("🧠 Chain of Thought reasoning detected - enhancing prompt")
            cot_enhance_start_time = time.time()
            message = self._add_chain_of_thought_prompt(message)
            cot_enhance_end_time = time.time()
            cot_enhance_duration = (cot_enhance_end_time - cot_enhance_start_time) * 1000
            logger.info(f"🧠 [TIMING] Chain of Thought enhancement completed in {cot_enhance_duration:.2f}ms")
        
        # For Mistral 7B Instruct, use the [INST] format
        format_start_time = time.time()
        if self.model_path and "mistral" in str(self.model_path).lower():
            # Mistral 7B Instruct format
            if system_instruction:
                prompt = f"<s>[INST] {system_instruction}\n\n{message} [/INST]"
            else:
                prompt = f"<s>[INST] {message} [/INST]"
        else:
            # Default format for other models (like TinyLlama)
            if system_instruction:
                prompt = f"{system_instruction}\n\n"
            else:
                prompt = ""
            prompt += f"User: {message}\nAssistant:"
        
        format_end_time = time.time()
        format_duration = (format_end_time - format_start_time) * 1000
        logger.info(f"📝 [TIMING] Prompt formatting completed in {format_duration:.2f}ms")
        
        prompt_end_time = time.time()
        prompt_duration = (prompt_end_time - prompt_start_time) * 1000
        logger.info(f"📝 [TIMING] Total prompt preparation completed in {prompt_duration:.2f}ms")
        
        return prompt

    async def generate_streaming_response(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the model"""
        generation_start_time = time.time()
        logger.info(f"🤖 [TIMING] Starting streaming response generation (thread={threading.current_thread().name}, pid={os.getpid()})")
        logger.info(f"[ENV] CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
        
        try:
            if not self.model:
                raise RuntimeError("Model not loaded. Please load the model first.")
            
            # Time prompt preparation
            prompt_start_time = time.time()
            prompt = self._prepare_prompt(message, history, system_instruction)
            prompt_end_time = time.time()
            prompt_duration = (prompt_end_time - prompt_start_time) * 1000
            logger.info(f"📄 [TIMING] Prompt preparation completed in {prompt_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
            logger.info(f"📄 Prompt length: {len(prompt)} characters")
            logger.info(f"📄 Prompt being sent to model:\n{prompt}")
            logger.info("Generating streaming response...")
            
            # Time token generation
            token_gen_start_time = time.time()
            token_count = 0
            first_token_time = None
            logger.info(f"[TIMING] Model call about to start (thread={threading.current_thread().name}, pid={os.getpid()})")
            
            # Generate response with error handling
            try:
                model_call_start_time = time.time()
                response = self.model.create_completion(
                    prompt,
                    max_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    repeat_penalty=self.repetition_penalty,
                    stop=["[INST]", "</s>", "<|endoftext|>", "User:", "Assistant:", "\n\nUser:", "\n\nAssistant:", "Implementing this functionality", "This functionality", "This will help", "This improves", "User: Do you", "User: Can you", "User: What", "User: How", "User: When", "User: Where", "User: Why", "User: Which"],
                    stream=True
                )
                model_call_end_time = time.time()
                model_call_duration = (model_call_end_time - model_call_start_time) * 1000
                logger.info(f"🤖 [TIMING] Model call returned response generator in {model_call_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                
                for chunk in response:
                    chunk_time = time.time()
                    if isinstance(chunk, dict) and 'choices' in chunk and chunk['choices']:
                        token = chunk['choices'][0]['text']
                        if token:
                            if first_token_time is None:
                                first_token_time = chunk_time
                                first_token_duration = (first_token_time - token_gen_start_time) * 1000
                                logger.info(f"🎯 [TIMING] First token received in {first_token_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                            token_count += 1
                            logger.debug(f"[TOKEN] {token_count}: {token[:30]}...")
                            yield token
                    elif chunk and hasattr(chunk, 'choices') and chunk.choices:
                        token = chunk.choices[0].text
                        if token:
                            if first_token_time is None:
                                first_token_time = chunk_time
                                first_token_duration = (first_token_time - token_gen_start_time) * 1000
                                logger.info(f"🎯 [TIMING] First token received in {first_token_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                            token_count += 1
                            logger.debug(f"[TOKEN] {token_count}: {token[:30]}...")
                            yield token
                
                token_gen_end_time = time.time()
                token_gen_duration = (token_gen_end_time - token_gen_start_time) * 1000
                tokens_per_second = token_count / (token_gen_duration / 1000) if token_gen_duration > 0 else 0
                
                logger.info(f"🤖 [TIMING] Token generation completed in {token_gen_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                logger.info(f"📊 Generated {token_count} tokens at {tokens_per_second:.2f} tokens/second")
                
                generation_end_time = time.time()
                total_generation_duration = (generation_end_time - generation_start_time) * 1000
                logger.info(f"🤖 [TIMING] Total streaming response generation completed in {total_generation_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                
            except Exception as e:
                error_end_time = time.time()
                error_duration = (error_end_time - generation_start_time) * 1000
                logger.error(f"❌ [TIMING] Model generation failed after {error_duration:.2f}ms: {str(e)}", exc_info=True)
                yield f"\n\nError: {str(e)}"
                return
            
        except Exception as e:
            error_end_time = time.time()
            error_duration = (error_end_time - generation_start_time) * 1000
            logger.error(f"❌ [TIMING] Streaming response generation failed after {error_duration:.2f}ms: {str(e)}", exc_info=True)
            yield f"\n\nError: {str(e)}"
            return

    async def generate_response(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """Generate a non-streaming response from the model"""
        try:
            if not self.model:
                raise RuntimeError("Model not loaded. Please load the model first.")
            logger.info(f"🤖 [TIMING] Starting non-streaming response generation (thread={threading.current_thread().name}, pid={os.getpid()})")
            logger.info(f"[ENV] CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
            
            # Time prompt preparation
            prompt_start_time = datetime.utcnow()
            prompt = self._prepare_prompt(message, history, system_instruction)
            prompt_end_time = datetime.utcnow()
            prompt_duration = (prompt_end_time - prompt_start_time).total_seconds() * 1000
            logger.info(f"📝 Prompt preparation completed in {prompt_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
            logger.info(f"📄 Prompt length: {len(prompt)} characters")
            
            logger.info(f"📄 Prompt being sent to model:\n{prompt}")
            logger.info("Generating response...")
            
            # Time token generation
            generation_start_time = datetime.utcnow()
            
            # Generate response with error handling
            try:
                logger.info(f"[TIMING] Model call about to start (thread={threading.current_thread().name}, pid={os.getpid()})")
                model_call_start_time = datetime.utcnow()
                response = self.model.create_completion(
                    prompt,
                    max_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    repeat_penalty=self.repetition_penalty,
                    stop=["[INST]", "</s>", "<|endoftext|>", "User:", "Assistant:", "\n\nUser:", "\n\nAssistant:", "Implementing this functionality", "This functionality", "This will help", "This improves", "User: Do you", "User: Can you", "User: What", "User: How", "User: When", "User: Where", "User: Why", "User: Which"]
                )
                model_call_end_time = datetime.utcnow()
                model_call_duration = (model_call_end_time - model_call_start_time).total_seconds() * 1000
                logger.info(f"🤖 [TIMING] Model call returned in {model_call_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                
                # Extract the response text from the completion object
                extract_start_time = datetime.utcnow()
                logger.info(f"🔍 Response object type: {type(response)}")
                logger.info(f"🔍 Response object: {str(response)[:200]}...")
                if isinstance(response, dict) and 'choices' in response and response['choices']:
                    response_text = response['choices'][0]['text']
                    logger.info(f"🔍 Extracted text from choices: {response_text[:100]}...")
                elif hasattr(response, 'choices') and response.choices:
                    response_text = response.choices[0].text
                    logger.info(f"🔍 Extracted text from choices: {response_text[:100]}...")
                else:
                    response_text = str(response) if response else ""
                    logger.info(f"🔍 Using string representation: {response_text[:100]}...")
                extract_end_time = datetime.utcnow()
                extract_duration = (extract_end_time - extract_start_time).total_seconds() * 1000
                logger.info(f"🔍 [TIMING] Response extraction completed in {extract_duration:.2f}ms (thread={threading.current_thread().name}, pid={os.getpid()})")
                
                # Clean up the response - remove any unwanted text that might have been generated
                if "Implementing this functionality" in response_text:
                    response_text = response_text.split("Implementing this functionality")[0].strip()
                if "This functionality" in response_text and "Implementing" not in response_text:
                    response_text = response_text.split("This functionality")[0].strip()
                if "This will help" in response_text:
                    response_text = response_text.split("This will help")[0].strip()
                if "This improves" in response_text:
                    response_text = response_text.split("This improves")[0].strip()
                
                # Clean up fake conversations - remove any text that looks like the model is pretending to be a user
                if "User:" in response_text:
                    response_text = response_text.split("User:")[0].strip()
                if "User: Do you" in response_text:
                    response_text = response_text.split("User: Do you")[0].strip()
                if "User: Can you" in response_text:
                    response_text = response_text.split("User: Can you")[0].strip()
                if "User: What" in response_text:
                    response_text = response_text.split("User: What")[0].strip()
                if "User: How" in response_text:
                    response_text = response_text.split("User: How")[0].strip()
                if "User: When" in response_text:
                    response_text = response_text.split("User: When")[0].strip()
                if "User: Where" in response_text:
                    response_text = response_text.split("User: Where")[0].strip()
                if "User: Why" in response_text:
                    response_text = response_text.split("User: Why")[0].strip()
                if "User: Which" in response_text:
                    response_text = response_text.split("User: Which")[0].strip()
                
                # Remove any trailing "Assistant:" that might have been generated
                if response_text.endswith("Assistant:"):
                    response_text = response_text[:-11].strip()
                
                generation_end_time = datetime.utcnow()
                generation_duration = (generation_end_time - generation_start_time).total_seconds() * 1000
                
                logger.info(f"🤖 Response generation completed in {generation_duration:.2f}ms")
                logger.info(f"📊 Response length: {len(response_text)} characters")
                
                return response_text
                
            except Exception as e:
                logger.error(f"Error during model generation: {str(e)}", exc_info=True)
                return f"Error: {str(e)}"
            
        except Exception as e:
            logger.error(f"Error in generate_response: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"

    def _should_use_chain_of_thought(self, message: str) -> bool:
        """
        Determine if Chain of Thought reasoning would be beneficial for this query.
        
        Args:
            message: User's message
            
        Returns:
            True if CoT should be used, False otherwise
        """
        message_lower = message.lower()
        
        # Mathematical problems
        math_indicators = [
            'calculate', 'solve', 'compute', 'find', 'determine',
            'what is', 'how much', 'total', 'sum', 'average', 'percentage',
            'if', 'then', 'equals', 'plus', 'minus', 'times', 'divided by'
        ]
        
        # Logical reasoning problems
        logic_indicators = [
            'if all', 'can we conclude', 'logical', 'reasoning',
            'sequence', 'pattern', 'next in', 'follows', 'therefore',
            'because', 'since', 'implies', 'contradicts'
        ]
        
        # Programming problems
        programming_indicators = [
            'write a function', 'create a program', 'algorithm',
            'debug', 'optimize', 'implement', 'design', 'architecture'
        ]
        
        # Complex multi-step problems
        complexity_indicators = [
            'step by step', 'explain how', 'show your work',
            'break down', 'analyze', 'compare', 'evaluate'
        ]
        
        # Check if any indicators are present
        has_math = any(indicator in message_lower for indicator in math_indicators)
        has_logic = any(indicator in message_lower for indicator in logic_indicators)
        has_programming = any(indicator in message_lower for indicator in programming_indicators)
        has_complexity = any(indicator in message_lower for indicator in complexity_indicators)
        
        return has_math or has_logic or has_programming or has_complexity

    def _add_chain_of_thought_prompt(self, message: str) -> str:
        """
        Add Chain of Thought reasoning instructions to the prompt.
        
        Args:
            message: Original user message
            
        Returns:
            Enhanced message with CoT instructions
        """
        cot_instruction = """
IMPORTANT: For this question, please use Chain of Thought reasoning. Think through the problem step-by-step:

1. First, understand what is being asked
2. Break down the problem into smaller parts
3. Work through each part logically
4. Show your reasoning process
5. Arrive at a conclusion

Let me think through this step by step:

"""
        
        return cot_instruction + message