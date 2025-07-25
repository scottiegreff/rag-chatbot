from typing import List, Dict, Any, Optional, AsyncGenerator
from pathlib import Path
import logging
import os
from dotenv import load_dotenv
from datetime import datetime
import time
import threading
import openai

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

class LLMService:
    """Service for interacting with the LLM model using ctransformers or OpenAI"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            logger.info("🆕 Creating new LLMService instance (singleton)")
            cls._instance = super(LLMService, cls).__new__(cls)
        else:
            logger.info("♻️  Reusing existing LLMService instance (singleton)")
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            logger.info("🔄 LLMService already initialized, skipping...")
            return
        logger.info(f"🔧 LLMService initializing with provider: {LLM_PROVIDER}")
        self.provider = LLM_PROVIDER
        if self.provider == "openai":
            if not OPENAI_API_KEY:
                logger.error("OPENAI_API_KEY is not set in .env!")
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider.")
            openai.api_key = OPENAI_API_KEY
            logger.info(f"✅ Using OpenAI model: {OPENAI_MODEL}")
        elif self.provider == "local":
            # Place your local model initialization here if needed
            logger.info("✅ Using local LLM model (not OpenAI)")
        else:
            logger.error(f"Unknown LLM_PROVIDER: {self.provider}")
            raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")
        self._initialized = True

    def generate_response(self, prompt, context=None, **kwargs):
        logger.info(f"[LLMService] Generating response with provider: {self.provider}")
        if self.provider == "openai":
            # Use OpenAI v1.x API (see: https://github.com/openai/openai-python/discussions/742)
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            try:
                response = openai.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=1024,
                )
                return "[OPENAI] " + response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                return f"[OpenAI API error: {e}]"
        elif self.provider == "local":
            # Place your local model inference code here
            return "[Local LLM not implemented in this patch]"
        else:
            logger.error(f"Unknown LLM_PROVIDER: {self.provider}")
            raise ValueError(f"Unknown LLM_PROVIDER: {self.provider}")