"""
II-Agent MCP Server Add-On - DeepSeek Provider
Implements the DeepSeek API provider
"""
import time
import requests
from typing import Dict, Any, List, Optional

from .base import AbstractProvider


class DeepSeekProvider(AbstractProvider):
    """Provider implementation for DeepSeek API"""
    
    BASE_URL = "https://api.deepseek.com/v1"
    
    def __init__(self, api_key: str, models: Optional[List[str]] = None):
        """Initialize the DeepSeek provider with API key and optional model list"""
        super().__init__(api_key, models)
        if not models:
            self.models = self.discover_models()
    
    def validate_api_key(self) -> bool:
        """Validate the API key with DeepSeek API"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.BASE_URL}/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False
    
    def discover_models(self) -> List[str]:
        """Discover available models from DeepSeek API"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.BASE_URL}/models", headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            models = []
            
            for model in data.get("data", []):
                model_id = model.get("id", "")
                if model_id and "deepseek" in model_id.lower():
                    models.append(model_id)
            
            # If no models found, add default models
            if not models:
                models = ["deepseek-chat", "deepseek-coder"]
                
            return models
        except Exception as e:
            print(f"Error discovering DeepSeek models: {e}")
            # Return default models on error
            return ["deepseek-chat", "deepseek-coder"]
    
    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate text using DeepSeek API"""
        start_time = time.time()
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            # Ensure model name is properly formatted
            if not model.startswith("deepseek-") and model not in self.models:
                model = "deepseek-chat"
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "max_tokens": kwargs.get("max_tokens", 1024)
            }
            
            response = requests.post(
                f"{self.BASE_URL}/chat/completions", 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            # Check for rate limiting headers
            if "x-ratelimit-remaining" in response.headers:
                self.rate_limit_remaining = int(response.headers["x-ratelimit-remaining"])
            
            if response.status_code != 200:
                self._update_metrics(False)
                return {
                    "success": False,
                    "error": f"API Error: {response.status_code}",
                    "response": response.text,
                    "latency": time.time() - start_time
                }
            
            data = response.json()
            
            # Extract the generated text from the response
            generated_text = ""
            if "choices" in data and data["choices"]:
                message = data["choices"][0].get("message", {})
                if "content" in message:
                    generated_text = message["content"]
            
            self._update_metrics(True)
            return {
                "success": True,
                "text": generated_text,
                "model": model,
                "provider": "deepseek",
                "latency": time.time() - start_time
            }
            
        except Exception as e:
            self._update_metrics(False)
            return {
                "success": False,
                "error": f"Exception: {str(e)}",
                "latency": time.time() - start_time
            }
