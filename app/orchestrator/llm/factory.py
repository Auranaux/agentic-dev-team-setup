import os
from app.orchestrator.llm.base import LLMClient
from app.orchestrator.llm.openai_client import OpenAIClient
from app.orchestrator.llm.anthropic_client import AnthropicClient

def get_llm_client() -> LLMClient:
    """Factory function to get the appropriate LLM client based on environment"""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
