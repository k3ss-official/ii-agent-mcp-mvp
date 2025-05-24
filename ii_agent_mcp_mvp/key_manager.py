"""
II-Agent MCP Server Add-On - Key Manager
Handles API key management, encryption, and validation
"""
import os
import re
import base64
import json
from typing import Dict, Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class KeyManager:
    """Manages API keys for providers"""
    
    def __init__(self, key_file: str = "api_keys.enc", salt_file: str = "salt.bin"):
        """Initialize the key manager"""
        self.key_file = key_file
        self.salt_file = salt_file
        self.encryption_key = self._load_or_create_encryption_key()
        
    def _load_or_create_encryption_key(self) -> bytes:
        """Load or create encryption key"""
        # Check if salt file exists
        if not os.path.exists(self.salt_file):
            # Generate new salt
            salt = os.urandom(16)
            # Save salt with restricted permissions
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            os.chmod(self.salt_file, 0o600)
        else:
            # Load existing salt
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        
        # Generate password file path
        password_file = "key_password.txt"
        
        # Check if password file exists
        if not os.path.exists(password_file):
            # Generate random password
            password = os.urandom(32)
            # Save password with restricted permissions
            with open(password_file, 'wb') as f:
                f.write(password)
            os.chmod(password_file, 0o600)
        else:
            # Load existing password
            with open(password_file, 'rb') as f:
                password = f.read()
        
        # Derive key from password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        return key
    
    def encrypt_keys(self, keys: Dict[str, str]) -> bytes:
        """Encrypt API keys"""
        # Create Fernet cipher
        cipher = Fernet(self.encryption_key)
        
        # Convert keys to JSON and encrypt
        keys_json = json.dumps(keys).encode()
        encrypted_data = cipher.encrypt(keys_json)
        
        return encrypted_data
    
    def decrypt_keys(self, encrypted_data: bytes) -> Dict[str, str]:
        """Decrypt API keys"""
        try:
            # Create Fernet cipher
            cipher = Fernet(self.encryption_key)
            
            # Decrypt and parse JSON
            decrypted_data = cipher.decrypt(encrypted_data)
            keys = json.loads(decrypted_data.decode())
            
            return keys
        except Exception as e:
            print(f"Error decrypting keys: {e}")
            return {}
    
    def save_keys(self, keys: Dict[str, str]) -> bool:
        """Save encrypted API keys to file"""
        try:
            # Encrypt keys
            encrypted_data = self.encrypt_keys(keys)
            
            # Save to file with restricted permissions
            with open(self.key_file, 'wb') as f:
                f.write(encrypted_data)
            os.chmod(self.key_file, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving keys: {e}")
            return False
    
    def load_keys(self) -> Dict[str, str]:
        """Load encrypted API keys from file"""
        try:
            # Check if file exists
            if not os.path.exists(self.key_file):
                return {}
            
            # Load encrypted data
            with open(self.key_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt keys
            keys = self.decrypt_keys(encrypted_data)
            
            return keys
        except Exception as e:
            print(f"Error loading keys: {e}")
            return {}
    
    def validate_key(self, provider: str, api_key: str) -> bool:
        """Validate API key format based on provider-specific patterns"""
        if not api_key:
            return False
            
        # Provider-specific validation patterns
        patterns = {
            "gemini": r"^AIza[0-9A-Za-z\-_]{35,}$",  # Google API key pattern
            "deepseek": r"^[0-9a-f]{32}$",  # DeepSeek API key pattern (hex)
            "mistral": r"^[A-Za-z0-9]{48}$",  # Mistral API key pattern
        }
        
        if provider.lower() not in patterns:
            return False
            
        return bool(re.match(patterns[provider.lower()], api_key))
    
    def mask_key(self, api_key: str) -> str:
        """Mask API key for logging purposes"""
        if not api_key or len(api_key) < 8:
            return "***"
        
        # Show first 4 and last 4 characters, mask the rest
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
