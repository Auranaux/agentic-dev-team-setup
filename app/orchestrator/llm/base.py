from abc import ABC, abstractmethod
from typing import Dict, Any
import json

class LLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """Generate a text response"""
        pass
    
    async def generate_json_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a JSON response with retry logic for invalid JSON"""
        json_prompt = f"{prompt}\n\nReturn your response as valid JSON matching this schema: {json.dumps(schema)}"
        
        try:
            response = await self.generate_response(json_prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        retry_prompt = f"{json_prompt}\n\nIMPORTANT: Return ONLY valid JSON, no other text or formatting."
        try:
            response = await self.generate_response(retry_prompt)
            return json.loads(response)
        except json.JSONDecodeError:
            response_lines = response.strip().split('\n')
            for line in response_lines:
                try:
                    return json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
            
            if schema.get("type") == "object":
                return {}
            return {"error": "Failed to generate valid JSON response"}
