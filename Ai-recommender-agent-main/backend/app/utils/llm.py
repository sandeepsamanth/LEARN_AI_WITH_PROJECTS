"""
LLM Utility using Euron AI
"""
from typing import Optional
from euriai import EuriaiClient
from app.core.config import settings


class LLMService:
    """Service for interacting with Euron AI LLM"""
    
    def __init__(self):
        self.client = EuriaiClient(
            api_key=settings.EURON_API_KEY,
            model=settings.EURON_MODEL
        )
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using the Euron AI LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        try:
            # Combine system prompt and user prompt if system_prompt is provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.client.generate_completion(
                prompt=full_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Handle OpenAI-compatible response format
            if isinstance(response, dict):
                # Extract content from OpenAI-compatible format
                if "choices" in response and len(response["choices"]) > 0:
                    message = response["choices"][0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        return content
                # Fallback to other common keys
                return response.get("text", response.get("content", response.get("response", str(response))))
            elif isinstance(response, str):
                return response
            else:
                return str(response)
        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")


# Global instance
llm_service = LLMService()





