import os
from typing import Dict, Any
from app.orchestrator.llm.base import LLMClient

class OpenAIClient(LLMClient):
    """OpenAI LLM client"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI API"""
        try:
            import openai
            openai.api_key = self.api_key
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except ImportError:
            return '{"content": "OpenAI client not available - install openai package"}'
        except Exception as e:
            return f'{{"error": "OpenAI API error: {str(e)}"}}'
