"""
II-Agent MCP Server Add-On - Test Security
Tests the security module functionality
"""
import os
import sys
import unittest
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ii_agent_mcp_mvp.security import SecurityManager
from ii_agent_mcp_mvp.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

class SecurityTester(unittest.TestCase):
    """Tests security module functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.key_file = os.path.join(self.temp_dir.name, ".mcp_key")
        self.salt_file = os.path.join(self.temp_dir.name, ".mcp_salt")
        
        # Create security manager
        self.security = SecurityManager(self.key_file, self.salt_file)
    
    def tearDown(self):
        """Clean up test environment"""
        self.temp_dir.cleanup()
    
    def test_key_generation(self):
        """Test key generation"""
        # Check that key files were created
        self.assertTrue(os.path.exists(self.key_file))
        self.assertTrue(os.path.exists(self.salt_file))
        
        # Check file permissions
        key_perms = oct(os.stat(self.key_file).st_mode)[-3:]
        salt_perms = oct(os.stat(self.salt_file).st_mode)[-3:]
        self.assertEqual(key_perms, "600")
        self.assertEqual(salt_perms, "600")
    
    def test_encryption_decryption(self):
        """Test encryption and decryption"""
        # Test with various strings
        test_strings = [
            "test",
            "This is a longer test string with spaces",
            "Special characters: !@#$%^&*()",
            "API key: sk-1234567890abcdef",
            ""  # Empty string
        ]
        
        for test_str in test_strings:
            encrypted = self.security.encrypt(test_str)
            decrypted = self.security.decrypt(encrypted)
            self.assertEqual(decrypted, test_str)
    
    def test_api_key_validation(self):
        """Test API key validation"""
        # Valid keys
        self.assertTrue(self.security.validate_api_key("gemini", "AIzaAbCdEfGhIjKlMnOpQrStUvWxYz1234567890-_123"))  # Added extra chars to match updated regex
        self.assertTrue(self.security.validate_api_key("deepseek", "abcdef1234567890abcdef1234567890"))
        self.assertTrue(self.security.validate_api_key("mistral", "ABCDEFGHIJKLMNOPQRSTUVWX0123456789abcdefghijklmn"))  # Exactly 48 chars
        
        # Invalid keys
        self.assertFalse(self.security.validate_api_key("gemini", "invalid-key"))
        self.assertFalse(self.security.validate_api_key("deepseek", "too-short"))
        self.assertFalse(self.security.validate_api_key("mistral", "invalid!@#"))
        self.assertFalse(self.security.validate_api_key("unknown", "any-key"))
    
    def test_key_masking(self):
        """Test API key masking"""
        # Test with various keys
        test_keys = [
            "AIzaAbCdEfGhIjKlMnOpQrStUvWxYz1234567890-_",
            "abcdef1234567890abcdef1234567890",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123",
            "short"
        ]
        
        for key in test_keys:
            masked = self.security.mask_api_key(key)
            # Check that masked key is not the original
            self.assertNotEqual(masked, key)
            # Check that masked key contains "..."
            if len(key) >= 8:
                self.assertIn("...", masked)
                # Check that masked key starts with first 4 chars
                self.assertTrue(masked.startswith(key[:4]))
                # Check that masked key ends with last 4 chars
                self.assertTrue(masked.endswith(key[-4:]))
            else:
                self.assertEqual(masked, "***")

def main():
    """Main entry point for security tester"""
    unittest.main()

if __name__ == "__main__":
    main()
