# MCP API Key Manager

A secure Python utility for managing API keys for the MCP server. This tool securely encrypts and stores API keys for Gemini, DeepSeek, and Mistral services.

## Features

- Password-based encryption using PBKDF2 key derivation
- Fernet symmetric encryption for API keys
- API key validation with test requests
- Secure storage with proper file permissions
- Decryption functionality for retrieving keys

## Requirements

- Python 3.6+
- Required packages:
  - cryptography
  - pyyaml
  - requests

## Installation

1. Ensure you're in the correct Conda environment:
   ```bash
   conda activate ii-agent-mcp-mvp
   ```

2. Install required packages:
   ```bash
   pip install --force-reinstall --no-cache-dir cryptography pyyaml requests
   ```

3. Clone the repository (if not already done):
   ```bash
   git clone https://github.com/your-username/ii-agent-mcp-mvp.git
   cd ii-agent-mcp-mvp
   ```

## Usage

### Setting Up API Keys

To set up and encrypt your API keys:

```bash
python key_manager.py setup
```

This will:
1. Prompt you for a strong password (minimum 12 characters)
2. Derive an encryption key using PBKDF2
3. Store the salt in `encryption_key.bin` with restricted permissions (600)
4. Prompt for Gemini, DeepSeek, and Mistral API keys
5. Validate each API key with a test request
6. Encrypt and store the keys in `providers.yaml` with restricted permissions (600)

### Retrieving API Keys

To decrypt and view your stored API keys:

```bash
python key_manager.py decrypt
```

This will:
1. Prompt for your encryption password
2. Decrypt the stored API keys
3. Display the keys with partial masking for security

### Using in Your Application

To use the decryption function in your application:

```python
from key_manager import derive_key_from_password, load_encryption_materials, decrypt_providers_yaml

# Load encryption materials and derive key
salt = load_encryption_materials()
password = getpass.getpass("Enter your encryption password: ")
key, _ = derive_key_from_password(password, salt)

# Decrypt API keys
api_keys = decrypt_providers_yaml(key)

# Use the API keys in your application
gemini_key = api_keys.get("gemini", "")
deepseek_key = api_keys.get("deepseek", "")
mistral_key = api_keys.get("mistral", "")
```

## Security Notes

- The encryption password is never stored and must be provided by the user when decrypting
- API keys are encrypted using Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256)
- The encryption key is derived using PBKDF2 with 100,000 iterations
- Files containing sensitive information have restricted permissions (600)
- API keys are validated before storage to ensure they are functional

## Backup Recommendations

It is crucial to maintain secure backups of:

1. Your encryption password (store in a password manager)
2. The `encryption_key.bin` file (contains the salt for key derivation)
3. The `providers.yaml` file (contains the encrypted API keys)

**IMPORTANT**: If you lose your encryption password or the `encryption_key.bin` file, you will not be able to recover your stored API keys.

## File Locations

- `key_manager.py`: The main script
- `encryption_key.bin`: Contains the salt for key derivation (created during setup)
- `providers.yaml`: Contains the encrypted API keys (created during setup)
- `key_manager.log`: Log file for operations and errors

## Troubleshooting

If you encounter issues:

1. Check the `key_manager.log` file for error messages
2. Ensure you're using the correct password
3. Verify that the `encryption_key.bin` and `providers.yaml` files exist and have not been corrupted
4. If API validation fails, check your internet connection and the validity of your API keys

## License

[Specify license information here]

## Contributing

[Specify contribution guidelines here]
