"""
II-Agent MCP Server Add-On - Fallback Handler
Implements fallback logic for provider failures
"""
import time
from typing import Dict, Any, List, Optional

from ..providers.factory import ProviderFactory
from ..utils.logging import get_logger

logger = get_logger(__name__)

class FallbackHandler:
    """Handles fallback logic when providers fail"""
    
    def __init__(self, provider_factory: ProviderFactory, max_retries: int = 2):
        """Initialize the fallback handler"""
        self.provider_factory = provider_factory
        self.max_retries = max_retries
        
    def process_request(self, prompt: str, model: str, provider_order: List[str], **kwargs) -> Dict[str, Any]:
        """Process a generation request with fallback logic"""
        attempts = 0
        errors = []
        
        # Try each provider in order
        for provider_name in provider_order:
            provider = self.provider_factory.get_provider(provider_name)
            if not provider:
                logger.warning(f"Provider {provider_name} not found, skipping")
                continue
                
            # Try the current provider up to max_retries times
            for retry in range(self.max_retries):
                attempts += 1
                
                # Check if we're approaching rate limits
                try:
                    if provider.rate_limit_remaining is not None and provider.rate_limit_remaining < 5:
                        logger.warning(f"Provider {provider_name} approaching rate limit ({provider.rate_limit_remaining} remaining), trying next provider")
                        break
                except (TypeError, AttributeError):
                    # Handle case where rate_limit_remaining is a mock or not comparable
                    logger.debug(f"Could not check rate limit for {provider_name}, continuing")
                    pass
                
                logger.info(f"Attempting generation with {provider_name} (attempt {attempts}, retry {retry})")
                start_time = time.time()
                
                try:
                    result = provider.generate(prompt, model, **kwargs)
                    
                    # If successful, return the result
                    if result.get("success", False):
                        logger.info(f"Generation successful with {provider_name} after {attempts} attempts")
                        result["attempts"] = attempts
                        result["fallback_used"] = attempts > 1
                        return result
                    
                    # If failed, log the error and try again or move to next provider
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"Generation failed with {provider_name}: {error_msg}")
                    errors.append(f"{provider_name}: {error_msg}")
                    
                    # Check for specific error conditions that should trigger immediate fallback
                    response_text = result.get("response", "").lower()
                    if "rate limit" in response_text or "429" in response_text:
                        logger.warning(f"Rate limit detected for {provider_name}, moving to next provider")
                        break
                        
                except Exception as e:
                    logger.error(f"Exception during generation with {provider_name}: {str(e)}")
                    errors.append(f"{provider_name}: {str(e)}")
                
                # Check for timeout
                elapsed = time.time() - start_time
                if elapsed >= 10:
                    logger.warning(f"Timeout detected for {provider_name} ({elapsed:.2f}s), moving to next provider")
                    break
        
        # If all providers failed, return error
        logger.error(f"All providers failed after {attempts} attempts")
        return {
            "success": False,
            "error": "All providers failed",
            "details": errors,
            "attempts": attempts,
            "fallback_used": attempts > 1
        }
