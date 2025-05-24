"""
II-Agent MCP Server Add-On - Provider Factory
Creates and manages provider instances
"""
from typing import Dict, List, Optional, Any

from .base import AbstractProvider
from .gemini import GeminiProvider
from .deepseek import DeepSeekProvider
from .mistral import MistralProvider


class ProviderFactory:
    """Factory for creating and managing provider instances"""
    
    def __init__(self):
        """Initialize the provider factory"""
        self.providers = {}
        self.provider_classes = {
            "gemini": GeminiProvider,
            "deepseek": DeepSeekProvider,
            "mistral": MistralProvider
        }
    
    def create_provider(self, provider_name: str, api_key: str, models: Optional[List[str]] = None) -> Optional[AbstractProvider]:
        """Create a provider instance"""
        provider_name = provider_name.lower()
        
        if provider_name not in self.provider_classes:
            return None
        
        provider_class = self.provider_classes[provider_name]
        provider = provider_class(api_key, models)
        
        # Store the provider instance
        self.providers[provider_name] = provider
        
        return provider
    
    def get_provider(self, provider_name: str) -> Optional[AbstractProvider]:
        """Get an existing provider instance"""
        return self.providers.get(provider_name.lower())
    
    def get_all_providers(self) -> List[AbstractProvider]:
        """Get all provider instances"""
        return list(self.providers.values())
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            status[name] = provider.get_status()
        return status
