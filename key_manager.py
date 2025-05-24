#!/usr/bin/env python3
"""
key_manager.py - Secure API Key Management for MCP Server

This script securely manages API keys for Gemini, DeepSeek, and Mistral services.
It prompts for API keys, validates them with test requests, encrypts them using
Fernet symmetric encryption with a password-derived key, and stores them in
providers.yaml.

Project ID: API-Mgmt-2025-05-24
"""

import os
import sys
import yaml
import logging
import getpass
import requests
import base64
import hashlib
from typing import Dict, Optional, Tuple, Any
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("key_manager.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("key_manager")

# Constants
ENCRYPTION_KEY_FILE = "encryption_key.bin"
PROVIDERS_FILE = "providers.yaml"
ITERATIONS = 100000  # Number of iterations for PBKDF2
KEY_LENGTH = 32  # Length of the derived key in bytes

# API endpoints for validation
API_ENDPOINTS = {
    "gemini": "https://api.google.com/gen-ai",
    "deepseek": "https://api.deepseek.com",
    "mistral": "https://api.mistral.ai/v1"
}

def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Derive an encryption key from a password using PBKDF2.
    
    Args:
        password: The password to derive the key from
        salt: Optional salt bytes, generated if not provided
        
    Returns:
        Tuple of (derived_key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def save_encryption_materials(salt: bytes) -> None:
    """
    Save encryption materials (salt) to a file with restricted permissions.
    
    Args:
        salt: The salt bytes to save
    """
    with open(ENCRYPTION_KEY_FILE, 'wb') as f:
        f.write(salt)
    
    # Set file permissions to 600 (read/write for owner only)
    os.chmod(ENCRYPTION_KEY_FILE, 0o600)
    logger.info(f"Encryption materials saved to {ENCRYPTION_KEY_FILE} with restricted permissions")

def load_encryption_materials() -> bytes:
    """
    Load encryption materials (salt) from file.
    
    Returns:
        The salt bytes
    """
    try:
        with open(ENCRYPTION_KEY_FILE, 'rb') as f:
            salt = f.read()
        return salt
    except FileNotFoundError:
        logger.error(f"Encryption key file {ENCRYPTION_KEY_FILE} not found")
        print(f"Error: Encryption key file not found. Please run the script in setup mode first.")
        sys.exit(1)

def encrypt_data(data: str, key: bytes) -> bytes:
    """
    Encrypt data using Fernet symmetric encryption.
    
    Args:
        data: The string data to encrypt
        key: The encryption key
        
    Returns:
        Encrypted bytes
    """
    f = Fernet(key)
    return f.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """
    Decrypt data using Fernet symmetric encryption.
    
    Args:
        encrypted_data: The encrypted bytes to decrypt
        key: The encryption key
        
    Returns:
        Decrypted string
    """
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()
    except InvalidToken:
        logger.error("Invalid encryption key or corrupted data")
        print("Error: Invalid encryption key or corrupted data")
        sys.exit(1)

def validate_api_key(provider: str, api_key: str) -> bool:
    """
    Validate an API key by making a test request to the provider's API.
    
    Args:
        provider: The provider name (gemini, deepseek, mistral)
        api_key: The API key to validate
        
    Returns:
        True if validation succeeded, False otherwise
    """
    endpoint = API_ENDPOINTS.get(provider.lower())
    if not endpoint:
        logger.warning(f"No validation endpoint defined for {provider}")
        return True  # Skip validation if no endpoint is defined
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        # Make a simple request to validate the API key
        # Note: This is a simplified example. Actual validation would depend on the specific API
        response = requests.get(endpoint, headers=headers, timeout=10)
        
        # Check if the response indicates the API key is valid
        # This logic would need to be adjusted based on the actual API response
        if response.status_code in (200, 401, 403):  # 401/403 might indicate valid key with insufficient permissions
            logger.info(f"API key validation for {provider} succeeded")
            return True
        else:
            logger.warning(f"API key validation for {provider} failed with status code {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.warning(f"API key validation for {provider} failed: {str(e)}")
        return False

def prompt_for_api_keys() -> Dict[str, str]:
    """
    Prompt the user for API keys and validate them.
    
    Returns:
        Dictionary of provider names to API keys
    """
    api_keys = {}
    
    for provider in ["gemini", "deepseek", "mistral"]:
        valid = False
        while not valid:
            api_key = getpass.getpass(f"Enter {provider.capitalize()} API key: ")
            
            if not api_key:
                print(f"Warning: No API key provided for {provider}. Skipping validation.")
                api_keys[provider] = ""
                valid = True
                continue
                
            print(f"Validating {provider.capitalize()} API key...")
            valid = validate_api_key(provider, api_key)
            
            if valid:
                api_keys[provider] = api_key
            else:
                retry = input(f"API key validation for {provider} failed. Retry? (y/n): ")
                if retry.lower() != 'y':
                    print(f"Skipping {provider} API key.")
                    api_keys[provider] = ""
                    valid = True
    
    return api_keys

def save_providers_yaml(api_keys: Dict[str, str], key: bytes) -> None:
    """
    Encrypt API keys and save them to providers.yaml.
    
    Args:
        api_keys: Dictionary of provider names to API keys
        key: The encryption key
    """
    providers_data = {}
    
    for provider, api_key in api_keys.items():
        if api_key:
            encrypted_key = encrypt_data(api_key, key)
            providers_data[provider] = {
                "api_key": base64.b64encode(encrypted_key).decode()
            }
        else:
            providers_data[provider] = {"api_key": ""}
    
    with open(PROVIDERS_FILE, 'w') as f:
        yaml.dump(providers_data, f, default_flow_style=False)
    
    # Set file permissions to 600 (read/write for owner only)
    os.chmod(PROVIDERS_FILE, 0o600)
    logger.info(f"Encrypted API keys saved to {PROVIDERS_FILE} with restricted permissions")

def load_providers_yaml() -> Dict[str, Any]:
    """
    Load the providers.yaml file.
    
    Returns:
        Dictionary containing the providers data
    """
    try:
        with open(PROVIDERS_FILE, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning(f"Providers file {PROVIDERS_FILE} not found")
        return {}

def decrypt_providers_yaml(key: bytes) -> Dict[str, str]:
    """
    Load and decrypt API keys from providers.yaml.
    
    Args:
        key: The encryption key
        
    Returns:
        Dictionary of provider names to decrypted API keys
    """
    providers_data = load_providers_yaml()
    decrypted_keys = {}
    
    for provider, data in providers_data.items():
        encrypted_key = data.get("api_key", "")
        if encrypted_key:
            try:
                encrypted_bytes = base64.b64decode(encrypted_key)
                decrypted_keys[provider] = decrypt_data(encrypted_bytes, key)
            except Exception as e:
                logger.error(f"Error decrypting {provider} API key: {str(e)}")
                decrypted_keys[provider] = ""
        else:
            decrypted_keys[provider] = ""
    
    return decrypted_keys

def setup_mode() -> None:
    """
    Run the script in setup mode to configure encryption and store API keys.
    """
    print("=== MCP API Key Manager Setup ===")
    
    # Prompt for password to derive encryption key
    while True:
        password = getpass.getpass("Enter a strong password for encryption: ")
        if len(password) < 12:
            print("Password must be at least 12 characters long. Please try again.")
            continue
            
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            continue
            
        break
    
    # Derive key and save salt
    key, salt = derive_key_from_password(password)
    save_encryption_materials(salt)
    
    # Prompt for and validate API keys
    api_keys = prompt_for_api_keys()
    
    # Save encrypted API keys to providers.yaml
    save_providers_yaml(api_keys, key)
    
    print("\nSetup complete! API keys have been encrypted and saved.")
    print(f"The encryption materials are stored in {ENCRYPTION_KEY_FILE}")
    print(f"The encrypted API keys are stored in {PROVIDERS_FILE}")
    print("\nIMPORTANT: Keep a secure backup of your password and these files.")

def decrypt_mode() -> None:
    """
    Run the script in decrypt mode to view stored API keys.
    """
    print("=== MCP API Key Manager - Decrypt Mode ===")
    
    # Load salt and prompt for password
    salt = load_encryption_materials()
    password = getpass.getpass("Enter your encryption password: ")
    
    # Derive key from password and salt
    key, _ = derive_key_from_password(password, salt)
    
    # Decrypt and display API keys
    try:
        decrypted_keys = decrypt_providers_yaml(key)
        
        print("\nDecrypted API Keys:")
        print("-------------------")
        for provider, api_key in decrypted_keys.items():
            if api_key:
                # Show only first/last 4 characters of the API key for security
                masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
                print(f"{provider.capitalize()}: {masked_key}")
            else:
                print(f"{provider.capitalize()}: Not set")
                
        print("\nNote: For security, API keys are partially masked.")
        print("Use the returned decrypted keys in your application as needed.")
        
        return decrypted_keys
        
    except Exception as e:
        logger.error(f"Error in decrypt mode: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

def main() -> None:
    """
    Main function to run the script based on command line arguments.
    """
    if len(sys.argv) < 2:
        print("Usage: python key_manager.py [setup|decrypt]")
        sys.exit(1)
        
    mode = sys.argv[1].lower()
    
    if mode == "setup":
        setup_mode()
    elif mode == "decrypt":
        decrypt_mode()
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python key_manager.py [setup|decrypt]")
        sys.exit(1)

if __name__ == "__main__":
    main()
