"""
II-Agent MCP Server Add-On - Setup Script
Automates provider configuration and generates providers.yaml
"""
import os
import sys
import argparse
from typing import Dict, Any, List, Optional
import yaml

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ii_agent_mcp_mvp.config import ConfigManager
from ii_agent_mcp_mvp.security import SecurityManager
from ii_agent_mcp_mvp.providers.gemini import GeminiProvider
from ii_agent_mcp_mvp.providers.deepseek import DeepSeekProvider
from ii_agent_mcp_mvp.providers.mistral import MistralProvider
from ii_agent_mcp_mvp.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

class SetupManager:
    """Manages the setup process for the MCP server"""
    
    def __init__(self):
        """Initialize the setup manager"""
        self.config_manager = ConfigManager()
        self.security = SecurityManager()
        
    def run_setup(self, interactive: bool = True):
        """Run the setup process"""
        print("II-Agent MCP Server Add-On Setup")
        print("================================")
        
        # Initialize configuration
        config = {
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
        
        # Configure providers
        providers = ["gemini", "deepseek", "mistral"]
        for provider_name in providers:
            print(f"\nConfiguring {provider_name.capitalize()} provider:")
            
            if interactive:
                api_key = input(f"Enter {provider_name.capitalize()} API key (leave empty to skip): ").strip()
                if not api_key:
                    print(f"Skipping {provider_name.capitalize()} provider")
                    continue
            else:
                # Non-interactive mode (for testing)
                api_key = os.environ.get(f"{provider_name.upper()}_API_KEY", "")
                if not api_key:
                    print(f"No API key found for {provider_name.capitalize()}, skipping")
                    continue
            
            # Validate API key format
            if not self.security.validate_api_key(provider_name, api_key):
                print(f"Warning: {provider_name.capitalize()} API key format appears invalid")
                if interactive:
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
            
            # Test API key with provider
            print(f"Testing {provider_name.capitalize()} API key...")
            provider_class = self._get_provider_class(provider_name)
            if not provider_class:
                print(f"Error: Provider class not found for {provider_name}")
                continue
                
            provider = provider_class(api_key)
            if not provider.validate_api_key():
                print(f"Error: {provider_name.capitalize()} API key validation failed")
                if interactive:
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
            
            # Discover models
            print(f"Discovering {provider_name.capitalize()} models...")
            models = provider.discover_models()
            if not models:
                print(f"Warning: No models discovered for {provider_name.capitalize()}")
                if interactive:
                    confirm = input("Continue anyway? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
            else:
                print(f"Discovered models: {', '.join(models)}")
            
            # Add provider to configuration
            config["providers"].append({
                "name": provider_name,
                "api_key": api_key,
                "models": models
            })
        
        # Save configuration
        if not config["providers"]:
            print("\nError: No providers configured")
            return False
        
        print("\nSaving configuration...")
        if self.config_manager.save_config(config):
            print("Configuration saved successfully")
            return True
        else:
            print("Error: Failed to save configuration")
            return False
    
    def _get_provider_class(self, provider_name: str):
        """Get the provider class for a given provider name"""
        provider_classes = {
            "gemini": GeminiProvider,
            "deepseek": DeepSeekProvider,
            "mistral": MistralProvider
        }
        return provider_classes.get(provider_name.lower())

def main():
    """Main entry point for setup script"""
    parser = argparse.ArgumentParser(description="II-Agent MCP Server Add-On Setup")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    args = parser.parse_args()
    
    setup_manager = SetupManager()
    success = setup_manager.run_setup(not args.non_interactive)
    
    if success:
        print("\nSetup completed successfully")
        print("You can now start the MCP server with: python -m ii_agent_mcp_mvp.main")
    else:
        print("\nSetup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
