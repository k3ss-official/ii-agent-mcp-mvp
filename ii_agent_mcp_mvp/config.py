"""
II-Agent MCP Server Add-On - Configuration Module
Handles loading and saving configuration
"""
import os
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path

from .security import SecurityManager
from .utils.logging import get_logger

logger = get_logger(__name__)

class ConfigManager:
    """Manages configuration for the MCP server"""
    
    def __init__(self, config_file: str = "providers.yaml"):
        """Initialize the configuration manager"""
        self.config_file = Path(config_file)
        self.security = SecurityManager()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            logger.warning(f"Configuration file {self.config_file} not found, using defaults")
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Decrypt API keys
            if "providers" in config:
                for provider in config["providers"]:
                    if "api_key" in provider:
                        encrypted_key = provider["api_key"]
                        provider["api_key"] = self.security.decrypt(encrypted_key)
            
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "providers": [],
            "fallback": {
                "enabled": True,
                "max_retries": 2,
                "timeout": 10
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "log_level": "info"
            }
        }
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            # Create a deep copy to avoid modifying the original
            config_to_save = {
                "providers": [],
                "fallback": config.get("fallback", {}),
                "server": config.get("server", {})
            }
            
            # Encrypt API keys
            if "providers" in config:
                for provider in config["providers"]:
                    provider_copy = provider.copy()
                    if "api_key" in provider_copy:
                        api_key = provider_copy["api_key"]
                        provider_copy["api_key"] = self.security.encrypt(api_key)
                    config_to_save["providers"].append(provider_copy)
            
            # Save to file
            with open(self.config_file, 'w') as f:
                yaml.dump(config_to_save, f, default_flow_style=False)
            
            # Set file permissions to restrict access
            self.config_file.chmod(0o600)
            
            # Update internal config
            self.config = config
            
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific provider"""
        if "providers" not in self.config:
            return None
        
        for provider in self.config["providers"]:
            if provider.get("name", "").lower() == provider_name.lower():
                return provider
        
        return None
    
    def get_provider_order(self) -> List[str]:
        """Get the order of providers for fallback"""
        if "providers" not in self.config:
            return []
        
        return [p.get("name", "").lower() for p in self.config["providers"]]
    
    def add_provider(self, name: str, api_key: str, models: Optional[List[str]] = None) -> bool:
        """Add or update a provider in the configuration"""
        if "providers" not in self.config:
            self.config["providers"] = []
        
        # Check if provider already exists
        for provider in self.config["providers"]:
            if provider.get("name", "").lower() == name.lower():
                provider["api_key"] = api_key
                if models:
                    provider["models"] = models
                return self.save_config(self.config)
        
        # Add new provider
        self.config["providers"].append({
            "name": name.lower(),
            "api_key": api_key,
            "models": models or []
        })
        
        return self.save_config(self.config)
