"""
II-Agent MCP Server Add-On - Security Module
Handles API key encryption, decryption, and validation
"""
import os
import base64
from pathlib import Path
from typing import Dict, Optional
import re

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    """Manages security operations for the MCP server"""
    
    def __init__(self, key_file: str = ".mcp_key", salt_file: str = ".mcp_salt"):
        """Initialize the security manager with key and salt file paths"""
        self.key_file = Path(key_file)
        self.salt_file = Path(salt_file)
        self.fernet = self._load_or_create_key()
        
    def _load_or_create_key(self) -> Fernet:
        """Load existing key or create a new one if it doesn't exist"""
        if not self.key_file.exists() or not self.salt_file.exists():
            return self._create_new_key()
        
        try:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            
            with open(self.key_file, 'rb') as f:
                password = f.read()
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return Fernet(key)
        except Exception as e:
            print(f"Error loading encryption key: {e}")
            return self._create_new_key()
    
    def _create_new_key(self) -> Fernet:
        """Create a new encryption key and salt"""
        salt = os.urandom(16)
        password = os.urandom(32)
        
        # Save salt and password to files
        with open(self.salt_file, 'wb') as f:
            f.write(salt)
        
        with open(self.key_file, 'wb') as f:
            f.write(password)
        
        # Set file permissions to restrict access
        self.salt_file.chmod(0o600)
        self.key_file.chmod(0o600)
        
        # Generate key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return the encrypted value as a string"""
        if not data:
            return ""
        
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an encrypted string and return the original value"""
        if not encrypted_data:
            return ""
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return ""
    
    def validate_api_key(self, provider: str, api_key: str) -> bool:
        """Validate API key format based on provider-specific patterns"""
        if not api_key:
            return False
            
        # Provider-specific validation patterns
        patterns = {
            "gemini": r"^AIza[0-9A-Za-z\-_]{35,}$",  # Google API key pattern (at least 35 chars)
            "deepseek": r"^[0-9a-f]{32}$",  # DeepSeek API key pattern (hex)
            "mistral": r"^[A-Za-z0-9]{48}$",  # Mistral API key pattern
        }
        
        if provider.lower() not in patterns:
            return False
            
        return bool(re.match(patterns[provider.lower()], api_key))
    
    def mask_api_key(self, api_key: str) -> str:
        """Mask API key for logging purposes"""
        if not api_key or len(api_key) < 8:
            return "***"
            
        return api_key[:4] + "..." + api_key[-4:]
