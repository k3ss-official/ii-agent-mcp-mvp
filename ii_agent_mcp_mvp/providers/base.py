"""
II-Agent MCP Server Add-On - Provider Base Module
Defines the abstract base class for all providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class AbstractProvider(ABC):
    """Abstract base class for all model providers"""
    
    def __init__(self, api_key: str, models: Optional[List[str]] = None):
        """Initialize the provider with API key and optional model list"""
        self.api_key = api_key
        self.models = models or []
        self.name = self.__class__.__name__.lower().replace('provider', '')
        self.request_count = 0
        self.failure_count = 0
        self.rate_limit_remaining = None
        
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key with the provider"""
        pass
    
    @abstractmethod
    def discover_models(self) -> List[str]:
        """Discover available models from the provider"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate text from the specified model"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the provider"""
        return {
            "name": self.name,
            "models": self.models,
            "request_count": self.request_count,
            "failure_count": self.failure_count,
            "success_rate": self._calculate_success_rate(),
            "rate_limit_remaining": self.rate_limit_remaining
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate the success rate of requests"""
        if self.request_count == 0:
            return 0.0
        return (self.request_count - self.failure_count) / self.request_count * 100
    
    def _update_metrics(self, success: bool) -> None:
        """Update request metrics"""
        self.request_count += 1
        if not success:
            self.failure_count += 1
