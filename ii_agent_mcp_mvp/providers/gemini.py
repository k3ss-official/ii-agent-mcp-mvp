"""
II-Agent MCP Server Add-On - Gemini Provider
Implements the Gemini API provider
"""
import time
import requests
from typing import Dict, Any, List, Optional

from .base import AbstractProvider


class GeminiProvider(AbstractProvider):
    """Provider implementation for Google's Gemini API"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: str, models: Optional[List[str]] = None):
        """Initialize the Gemini provider with API key and optional model list"""
        super().__init__(api_key, models)
        if not models:
            self.models = self.discover_models()
    
    def validate_api_key(self) -> bool:
        """Validate the API key with Gemini API"""
        try:
            url = f"{self.BASE_URL}/models?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return True
            return False
        except Exception:
            return False
    
    def discover_models(self) -> List[str]:
        """Discover available models from Gemini API"""
        try:
            url = f"{self.BASE_URL}/models?key={self.api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            models = []
            
            for model in data.get("models", []):
                name = model.get("name", "")
                if name and "gemini" in name.lower():
                    # Extract model name from path (models/gemini-1.5-pro)
                    model_name = name.split("/")[-1]
                    models.append(model_name)
            
            return models
        except Exception as e:
            print(f"Error discovering Gemini models: {e}")
            return []
    
    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate text using Gemini API"""
        start_time = time.time()
        
        try:
            # Ensure model name is properly formatted
            if not model.startswith("gemini-"):
                model = f"gemini-{model}"
            
            url = f"{self.BASE_URL}/models/{model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "topP": kwargs.get("top_p", 0.95),
                    "topK": kwargs.get("top_k", 40),
                    "maxOutputTokens": kwargs.get("max_tokens", 1024)
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
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
            if "candidates" in data and data["candidates"]:
                for part in data["candidates"][0].get("content", {}).get("parts", []):
                    if "text" in part:
                        generated_text += part["text"]
            
            self._update_metrics(True)
            return {
                "success": True,
                "text": generated_text,
                "model": model,
                "provider": "gemini",
                "latency": time.time() - start_time
            }
            
        except Exception as e:
            self._update_metrics(False)
            return {
                "success": False,
                "error": f"Exception: {str(e)}",
                "latency": time.time() - start_time
            }
