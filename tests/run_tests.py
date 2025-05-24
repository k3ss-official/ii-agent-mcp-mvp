"""
II-Agent MCP Server Add-On - Test Runner
Runs all tests for the MCP server
"""
import os
import sys
import argparse
import subprocess
from typing import Dict, Any, List

def run_test(test_script: str, args: List[str] = None) -> bool:
    """Run a test script and return success status"""
    cmd = [sys.executable, test_script]
    if args:
        cmd.extend(args)
        
    print(f"\n=== Running {os.path.basename(test_script)} ===")
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description="II-Agent MCP Server Test Runner")
    parser.add_argument("--gemini-key", help="Gemini API key")
    parser.add_argument("--deepseek-key", help="DeepSeek API key")
    parser.add_argument("--mistral-key", help="Mistral API key")
    parser.add_argument("--skip-providers", action="store_true", help="Skip provider tests")
    parser.add_argument("--skip-fallback", action="store_true", help="Skip fallback tests")
    parser.add_argument("--skip-security", action="store_true", help="Skip security tests")
    args = parser.parse_args()
    
    # Get directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Track test results
    results = {}
    
    # Run security tests
    if not args.skip_security:
        security_script = os.path.join(script_dir, "test_security.py")
        results["security"] = run_test(security_script)
    
    # Run fallback tests
    if not args.skip_fallback:
        fallback_script = os.path.join(script_dir, "test_fallback.py")
        results["fallback"] = run_test(fallback_script)
    
    # Run provider tests if API keys provided
    if not args.skip_providers and (args.gemini_key or args.deepseek_key or args.mistral_key):
        provider_script = os.path.join(script_dir, "test_providers.py")
        provider_args = []
        
        if args.gemini_key:
            provider_args.extend(["--gemini-key", args.gemini_key])
        if args.deepseek_key:
            provider_args.extend(["--deepseek-key", args.deepseek_key])
        if args.mistral_key:
            provider_args.extend(["--mistral-key", args.mistral_key])
            
        results["providers"] = run_test(provider_script, provider_args)
    elif not args.skip_providers:
        print("\n=== Skipping provider tests (no API keys provided) ===")
        results["providers"] = None
    
    # Print overall summary
    print("\n=== Overall Test Summary ===")
    all_success = True
    
    for test_name, success in results.items():
        if success is None:
            status = "⚠️ SKIPPED"
        else:
            status = "✅ PASS" if success else "❌ FAIL"
            all_success = all_success and success
        
        print(f"{test_name.title()}: {status}")
    
    print("\nOverall Result:", "✅ PASS" if all_success else "❌ FAIL")
    
    if not all_success:
        sys.exit(1)

if __name__ == "__main__":
    main()
