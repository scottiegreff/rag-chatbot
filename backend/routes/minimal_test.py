from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
import logging
import threading
import os
from backend.services.llm_service import LLMService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/minimal", tags=["minimal"])

class MinimalRequest(BaseModel):
    message: str

@router.post("/test-model")
async def test_model_minimal(request: MinimalRequest):
    """Minimal endpoint that only calls the LLM model - no RAG, no DB, no other services"""
    
    start_time = time.time()
    logger.info(f"🚀 [MINIMAL] Starting minimal model test (thread={threading.current_thread().name}, pid={os.getpid()})")
    logger.info(f"[MINIMAL] Environment: CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
    
    try:
        # Get LLM service
        llm_service_start = time.time()
        llm_service = LLMService()
        llm_service_end = time.time()
        llm_service_duration = (llm_service_end - llm_service_start) * 1000
        logger.info(f"🔧 [MINIMAL] LLM service initialization: {llm_service_duration:.2f}ms")
        
        # Check if model is loaded
        if not llm_service.model:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        logger.info(f"✅ [MINIMAL] Model is loaded and ready")
        
        # Generate response using non-streaming method for simplicity
        generation_start = time.time()
        logger.info(f"🤖 [MINIMAL] Starting model generation for: '{request.message}'")
        
        response = await llm_service.generate_response(
            message=request.message,
            history=None,  # No history
            system_instruction=None  # No system instruction
        )
        
        generation_end = time.time()
        generation_duration = (generation_end - generation_start) * 1000
        
        total_time = time.time() - start_time
        total_duration = total_time * 1000
        
        logger.info(f"🎯 [MINIMAL] Model generation completed in {generation_duration:.2f}ms")
        logger.info(f"⏱️ [MINIMAL] Total request time: {total_duration:.2f}ms")
        logger.info(f"📊 [MINIMAL] Response length: {len(response)} characters")
        
        return {
            "message": request.message,
            "response": response,
            "timing": {
                "llm_service_init_ms": llm_service_duration,
                "generation_ms": generation_duration,
                "total_ms": total_duration
            },
            "environment": {
                "ct_metal": os.getenv('CT_METAL'),
                "ct_cuda": os.getenv('CT_CUDA'),
                "gpu_layers": os.getenv('GPU_LAYERS'),
                "thread": threading.current_thread().name,
                "pid": os.getpid()
            }
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        error_duration = error_time * 1000
        logger.error(f"❌ [MINIMAL] Error after {error_duration:.2f}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-model-stream")
async def test_model_minimal_stream(request: MinimalRequest):
    """Minimal streaming endpoint that only calls the LLM model"""
    
    start_time = time.time()
    logger.info(f"🚀 [MINIMAL] Starting minimal streaming test (thread={threading.current_thread().name}, pid={os.getpid()})")
    logger.info(f"[MINIMAL] Environment: CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
    
    try:
        # Get LLM service
        llm_service = LLMService()
        if not llm_service.model:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        logger.info(f"✅ [MINIMAL] Model is loaded and ready for streaming")
        
        # Use streaming response
        async def generate():
            generation_start = time.time()
            logger.info(f"🤖 [MINIMAL] Starting streaming generation for: '{request.message}'")
            
            async for token in llm_service.generate_streaming_response(
                message=request.message,
                history=None,
                system_instruction=None
            ):
                yield f"data: {token}\n"
            
            generation_end = time.time()
            generation_duration = (generation_end - generation_start) * 1000
            total_time = time.time() - start_time
            total_duration = total_time * 1000
            
            logger.info(f"🎯 [MINIMAL] Streaming generation completed in {generation_duration:.2f}ms")
            logger.info(f"⏱️ [MINIMAL] Total streaming time: {total_duration:.2f}ms")
            yield "data: [DONE]\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        error_time = time.time() - start_time
        error_duration = error_time * 1000
        logger.error(f"❌ [MINIMAL] Streaming error after {error_duration:.2f}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-model-with-system")
async def test_model_with_system(request: MinimalRequest):
    """Minimal endpoint with a short system instruction to test if long system instructions cause delays"""
    
    start_time = time.time()
    logger.info(f"🚀 [MINIMAL] Starting minimal model test with system instruction (thread={threading.current_thread().name}, pid={os.getpid()})")
    logger.info(f"[MINIMAL] Environment: CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
    
    try:
        # Get LLM service
        llm_service_start = time.time()
        llm_service = LLMService()
        llm_service_end = time.time()
        llm_service_duration = (llm_service_end - llm_service_start) * 1000
        logger.info(f"🔧 [MINIMAL] LLM service initialization: {llm_service_duration:.2f}ms")
        
        # Check if model is loaded
        if not llm_service.model:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        logger.info(f"✅ [MINIMAL] Model is loaded and ready")
        
        # Generate response with a short system instruction
        generation_start = time.time()
        logger.info(f"🤖 [MINIMAL] Starting model generation with system instruction for: '{request.message}'")
        
        short_system_instruction = "You are a helpful AI assistant. Provide clear and accurate responses."
        
        response = await llm_service.generate_response(
            message=request.message,
            history=None,  # No history
            system_instruction=short_system_instruction
        )
        
        generation_end = time.time()
        generation_duration = (generation_end - generation_start) * 1000
        
        total_time = time.time() - start_time
        total_duration = total_time * 1000
        
        logger.info(f"🎯 [MINIMAL] Model generation with system instruction completed in {generation_duration:.2f}ms")
        logger.info(f"⏱️ [MINIMAL] Total request time: {total_duration:.2f}ms")
        logger.info(f"📊 [MINIMAL] Response length: {len(response)} characters")
        
        return {
            "message": request.message,
            "response": response,
            "system_instruction": short_system_instruction,
            "timing": {
                "llm_service_init_ms": llm_service_duration,
                "generation_ms": generation_duration,
                "total_ms": total_duration
            },
            "environment": {
                "ct_metal": os.getenv('CT_METAL'),
                "ct_cuda": os.getenv('CT_CUDA'),
                "gpu_layers": os.getenv('GPU_LAYERS'),
                "thread": threading.current_thread().name,
                "pid": os.getpid()
            }
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        error_duration = error_time * 1000
        logger.error(f"❌ [MINIMAL] Error after {error_duration:.2f}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-model-with-full-system")
async def test_model_with_full_system(request: MinimalRequest):
    """Minimal endpoint with the full SYSTEM_INSTRUCTION to confirm it causes delays"""
    
    start_time = time.time()
    logger.info(f"🚀 [MINIMAL] Starting minimal model test with FULL system instruction (thread={threading.current_thread().name}, pid={os.getpid()})")
    logger.info(f"[MINIMAL] Environment: CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
    
    try:
        # Get LLM service
        llm_service_start = time.time()
        llm_service = LLMService()
        llm_service_end = time.time()
        llm_service_duration = (llm_service_end - llm_service_start) * 1000
        logger.info(f"🔧 [MINIMAL] LLM service initialization: {llm_service_duration:.2f}ms")
        
        # Check if model is loaded
        if not llm_service.model:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        logger.info(f"✅ [MINIMAL] Model is loaded and ready")
        
        # Generate response with the full system instruction
        generation_start = time.time()
        logger.info(f"🤖 [MINIMAL] Starting model generation with FULL system instruction for: '{request.message}'")
        
        # Import the full system instruction from chat.py
        from backend.routes.chat import SYSTEM_INSTRUCTION
        
        response = await llm_service.generate_response(
            message=request.message,
            history=None,  # No history
            system_instruction=SYSTEM_INSTRUCTION
        )
        
        generation_end = time.time()
        generation_duration = (generation_end - generation_start) * 1000
        
        total_time = time.time() - start_time
        total_duration = total_time * 1000
        
        logger.info(f"🎯 [MINIMAL] Model generation with FULL system instruction completed in {generation_duration:.2f}ms")
        logger.info(f"⏱️ [MINIMAL] Total request time: {total_duration:.2f}ms")
        logger.info(f"📊 [MINIMAL] Response length: {len(response)} characters")
        
        return {
            "message": request.message,
            "response": response,
            "system_instruction_length": len(SYSTEM_INSTRUCTION),
            "timing": {
                "llm_service_init_ms": llm_service_duration,
                "generation_ms": generation_duration,
                "total_ms": total_duration
            },
            "environment": {
                "ct_metal": os.getenv('CT_METAL'),
                "ct_cuda": os.getenv('CT_CUDA'),
                "gpu_layers": os.getenv('GPU_LAYERS'),
                "thread": threading.current_thread().name,
                "pid": os.getpid()
            }
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        error_duration = error_time * 1000
        logger.error(f"❌ [MINIMAL] Error after {error_duration:.2f}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/test-model-with-optimized-system")
async def test_model_with_optimized_system(request: MinimalRequest):
    """Minimal endpoint with the optimized system instruction to test performance improvement"""
    
    start_time = time.time()
    logger.info(f"🚀 [MINIMAL] Starting minimal model test with OPTIMIZED system instruction (thread={threading.current_thread().name}, pid={os.getpid()})")
    logger.info(f"[MINIMAL] Environment: CT_METAL={os.getenv('CT_METAL')}, CT_CUDA={os.getenv('CT_CUDA')}, GPU_LAYERS={os.getenv('GPU_LAYERS')}")
    
    try:
        # Get LLM service
        llm_service_start = time.time()
        llm_service = LLMService()
        llm_service_end = time.time()
        llm_service_duration = (llm_service_end - llm_service_start) * 1000
        logger.info(f"🔧 [MINIMAL] LLM service initialization: {llm_service_duration:.2f}ms")
        
        # Check if model is loaded
        if not llm_service.model:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        logger.info(f"✅ [MINIMAL] Model is loaded and ready")
        
        # Generate response with the optimized system instruction
        generation_start = time.time()
        logger.info(f"🤖 [MINIMAL] Starting model generation with OPTIMIZED system instruction for: '{request.message}'")
        
        # Use the optimized system instruction
        optimized_system_instruction = "You are a helpful AI assistant. Use markdown formatting: **bold**, *italic*, `code`, ```blocks```, lists (- or 1.), ## headings, > quotes. Answer confidently based on your knowledge. For unknown facts, say \"I don't know\"."
        
        response = await llm_service.generate_response(
            message=request.message,
            history=None,  # No history
            system_instruction=optimized_system_instruction
        )
        
        generation_end = time.time()
        generation_duration = (generation_end - generation_start) * 1000
        
        total_time = time.time() - start_time
        total_duration = total_time * 1000
        
        logger.info(f"🎯 [MINIMAL] Model generation with OPTIMIZED system instruction completed in {generation_duration:.2f}ms")
        logger.info(f"⏱️ [MINIMAL] Total request time: {total_duration:.2f}ms")
        logger.info(f"📊 [MINIMAL] Response length: {len(response)} characters")
        
        return {
            "message": request.message,
            "response": response,
            "system_instruction": optimized_system_instruction,
            "system_instruction_length": len(optimized_system_instruction),
            "timing": {
                "llm_service_init_ms": llm_service_duration,
                "generation_ms": generation_duration,
                "total_ms": total_duration
            },
            "environment": {
                "ct_metal": os.getenv('CT_METAL'),
                "ct_cuda": os.getenv('CT_CUDA'),
                "gpu_layers": os.getenv('GPU_LAYERS'),
                "thread": threading.current_thread().name,
                "pid": os.getpid()
            }
        }
        
    except Exception as e:
        error_time = time.time() - start_time
        error_duration = error_time * 1000
        logger.error(f"❌ [MINIMAL] Error after {error_duration:.2f}ms: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") 