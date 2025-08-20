import os
from typing import Dict, Any
from app.orchestrator.llm.base import LLMClient

class AnthropicClient(LLMClient):
    """Anthropic LLM client"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Anthropic API"""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except ImportError:
            return '{"content": "Anthropic client not available - install anthropic package"}'
        except Exception as e:
            return f'{{"error": "Anthropic API error: {str(e)}"}}'
