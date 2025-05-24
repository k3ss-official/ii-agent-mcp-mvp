"""
II-Agent MCP Server Add-On - Test Provider Integration
Tests the integration with all providers
"""
import os
import sys
import time
import argparse
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ii_agent_mcp_mvp.providers.gemini import GeminiProvider
from ii_agent_mcp_mvp.providers.deepseek import DeepSeekProvider
from ii_agent_mcp_mvp.providers.mistral import MistralProvider
from ii_agent_mcp_mvp.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

class ProviderTester:
    """Tests provider integrations"""
    
    def __init__(self):
        """Initialize the provider tester"""
        self.results = {
            "gemini": {"success": False, "error": None, "models": []},
            "deepseek": {"success": False, "error": None, "models": []},
            "mistral": {"success": False, "error": None, "models": []}
        }
    
    def test_provider(self, provider_name: str, api_key: str):
        """Test a specific provider"""
        print(f"\nTesting {provider_name.capitalize()} provider:")
        
        try:
            # Create provider instance
            if provider_name == "gemini":
                provider = GeminiProvider(api_key)
            elif provider_name == "deepseek":
                provider = DeepSeekProvider(api_key)
            elif provider_name == "mistral":
                provider = MistralProvider(api_key)
            else:
                print(f"Error: Unknown provider {provider_name}")
                self.results[provider_name]["error"] = f"Unknown provider {provider_name}"
                return False
            
            # Test API key validation
            print("Testing API key validation...")
            if not provider.validate_api_key():
                print(f"Error: {provider_name.capitalize()} API key validation failed")
                self.results[provider_name]["error"] = "API key validation failed"
                return False
            
            # Discover models
            print("Discovering models...")
            models = provider.discover_models()
            if not models:
                print(f"Warning: No models discovered for {provider_name.capitalize()}")
                self.results[provider_name]["error"] = "No models discovered"
                return False
            
            print(f"Discovered models: {', '.join(models)}")
            self.results[provider_name]["models"] = models
            
            # Test generation
            print("Testing text generation...")
            model = models[0]  # Use first model
            result = provider.generate(
                prompt="Hello, can you tell me what day it is today?",
                model=model,
                temperature=0.7,
                max_tokens=100
            )
            
            if not result.get("success", False):
                error = result.get("error", "Unknown error")
                print(f"Error: Generation failed - {error}")
                self.results[provider_name]["error"] = f"Generation failed: {error}"
                return False
            
            print(f"Generation successful: {result.get('text', '')[:50]}...")
            self.results[provider_name]["success"] = True
            return True
            
        except Exception as e:
            print(f"Exception during {provider_name} test: {str(e)}")
            self.results[provider_name]["error"] = str(e)
            return False
    
    def print_summary(self):
        """Print a summary of test results"""
        print("\n=== Test Summary ===")
        
        all_success = True
        for provider, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            all_success = all_success and result["success"]
            
            print(f"{provider.capitalize()}: {status}")
            if result["success"]:
                print(f"  Models: {', '.join(result['models'])}")
            else:
                print(f"  Error: {result['error']}")
        
        print("\nOverall Result:", "✅ PASS" if all_success else "❌ FAIL")
        return all_success

def main():
    """Main entry point for provider tester"""
    parser = argparse.ArgumentParser(description="II-Agent MCP Server Provider Tester")
    parser.add_argument("--gemini-key", help="Gemini API key")
    parser.add_argument("--deepseek-key", help="DeepSeek API key")
    parser.add_argument("--mistral-key", help="Mistral API key")
    args = parser.parse_args()
    
    tester = ProviderTester()
    
    # Test each provider if key is provided
    if args.gemini_key:
        tester.test_provider("gemini", args.gemini_key)
    else:
        print("Skipping Gemini test (no API key provided)")
    
    if args.deepseek_key:
        tester.test_provider("deepseek", args.deepseek_key)
    else:
        print("Skipping DeepSeek test (no API key provided)")
    
    if args.mistral_key:
        tester.test_provider("mistral", args.mistral_key)
    else:
        print("Skipping Mistral test (no API key provided)")
    
    # Print summary
    success = tester.print_summary()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
