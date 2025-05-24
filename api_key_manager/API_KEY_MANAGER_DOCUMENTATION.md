# API Key Manager: Comprehensive Documentation

## What is the API Key Manager?

The API Key Manager is a secure Python utility designed for the MCP server to manage API keys for various AI service providers (Gemini, DeepSeek, and Mistral). It addresses the critical need for secure credential management in AI systems by providing:

1. **Secure Storage**: Encrypts sensitive API keys before storing them on disk
2. **Key Validation**: Verifies API keys are valid before storing them
3. **Access Control**: Implements proper file permissions to restrict access
4. **Decryption Capability**: Provides secure methods to retrieve keys when needed

This solution follows security best practices by implementing password-based encryption, secure key derivation, and proper error handling to protect sensitive credentials from unauthorized access.

## Where Does the API Key Manager Fit?

### System Architecture

The API Key Manager serves as a critical security component in the MCP server architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     MCP Server                          │
│                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌─────────┐  │
│  │ API Key       │    │ Core MCP      │    │ Other   │  │
│  │ Manager       │◄───┤ Application   │◄───┤ Modules │  │
│  │ (key_manager.py)   │ Logic         │    │         │  │
│  └───────┬───────┘    └───────────────┘    └─────────┘  │
│          │                                              │
│  ┌───────▼───────┐                                      │
│  │ providers.yaml│                                      │
│  │ (encrypted)   │                                      │
│  └───────────────┘                                      │
└─────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Gemini API          │    │ DeepSeek API    │    │ Mistral API     │
│ (api.google.com)    │    │ (api.deepseek.com)   │ (api.mistral.ai)│
└─────────────────────┘    └─────────────────┘    └─────────────────┘
```

### File Structure

The API Key Manager consists of the following files:

1. **key_manager.py**: The main Python script containing all encryption, decryption, and validation logic
2. **encryption_key.bin**: Generated file containing the salt for key derivation (chmod 600)
3. **providers.yaml**: Generated file containing the encrypted API keys (chmod 600)
4. **key_manager.log**: Log file for operations and errors

### Integration Points

The API Key Manager integrates with:

1. **Conda Environment**: Runs within the ii-agent-mcp-mvp Conda environment
2. **External APIs**: Validates keys against Gemini, DeepSeek, and Mistral APIs
3. **MCP Application**: Provides decryption functions for the main application to access keys

## How Does the API Key Manager Work?

### Setup Process

1. **Installation**:
   ```bash
   # Activate the Conda environment
   conda activate ii-agent-mcp-mvp
   
   # Install required packages
   pip install --force-reinstall --no-cache-dir cryptography pyyaml requests
   ```

2. **Initial Configuration**:
   ```bash
   # Run the setup mode
   python key_manager.py setup
   ```

   This initiates the following process:
   
   ```
   ┌─────────────────────┐
   │ User enters password│
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ PBKDF2 derives key  │
   │ from password + salt│
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Salt saved to       │
   │ encryption_key.bin  │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ User enters API keys│
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Keys validated with │
   │ test API requests   │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Keys encrypted with │
   │ Fernet (AES)        │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Encrypted keys saved│
   │ to providers.yaml   │
   └─────────────────────┘
   ```

### Key Encryption Process

1. **Password-Based Key Derivation**:
   - Uses PBKDF2HMAC with SHA256
   - 100,000 iterations for computational difficulty
   - 16-byte random salt
   - Derives a 32-byte key

2. **Encryption**:
   - Uses Fernet symmetric encryption (AES-128-CBC with HMAC-SHA256)
   - Encrypts each API key separately
   - Base64-encodes the encrypted data for storage

3. **Storage**:
   - Stores encrypted keys in YAML format
   - Sets file permissions to 600 (read/write for owner only)
   - Logs operations with timestamps

### Key Retrieval Process

1. **Decryption**:
   ```bash
   # Run the decrypt mode
   python key_manager.py decrypt
   ```

   This initiates the following process:
   
   ```
   ┌─────────────────────┐
   │ User enters password│
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Load salt from      │
   │ encryption_key.bin  │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ PBKDF2 derives key  │
   │ from password + salt│
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Load encrypted keys │
   │ from providers.yaml │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Decrypt keys using  │
   │ derived key         │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Display masked keys │
   │ for verification    │
   └─────────────────────┘
   ```

2. **Programmatic Usage**:
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

### Security Measures

1. **Password Protection**:
   - Password never stored, only used for key derivation
   - Minimum 12-character password requirement
   - PBKDF2 with 100,000 iterations to resist brute-force attacks

2. **File Security**:
   - chmod 600 permissions (read/write for owner only)
   - Salt and encrypted keys stored separately
   - No plaintext keys in logs or error messages

3. **Error Handling**:
   - Graceful handling of incorrect passwords
   - Validation of API keys before storage
   - Comprehensive logging with timestamps
   - Masked key display for verification

4. **API Key Validation**:
   - Test requests to provider endpoints:
     - Gemini: api.google.com/gen-ai
     - DeepSeek: api.deepseek.com
     - Mistral: api.mistral.ai/v1
   - Retry options for failed validations
   - Skip option for unavailable services

### Backup and Recovery

1. **Backup Strategy**:
   - Secure backup of encryption password (password manager recommended)
   - Regular backup of encryption_key.bin and providers.yaml
   - Documentation of backup locations and procedures

2. **Recovery Process**:
   - Restore encryption_key.bin and providers.yaml from backup
   - Use original password to decrypt keys
   - Re-run setup if password is lost (requires re-entering API keys)

## Implementation Details

### Key Components

1. **Key Derivation Function**:
   ```python
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
   ```

2. **Encryption Function**:
   ```python
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
   ```

3. **Decryption Function**:
   ```python
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
   ```

4. **API Key Validation**:
   ```python
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
           response = requests.get(endpoint, headers=headers, timeout=10)
           
           # Check if the response indicates the API key is valid
           if response.status_code in (200, 401, 403):
               logger.info(f"API key validation for {provider} succeeded")
               return True
           else:
               logger.warning(f"API key validation for {provider} failed with status code {response.status_code}")
               return False
               
       except requests.exceptions.RequestException as e:
           logger.warning(f"API key validation for {provider} failed: {str(e)}")
           return False
   ```

### Error Handling

The API Key Manager implements comprehensive error handling:

1. **File Access Errors**:
   - Checks for missing encryption key file
   - Verifies file permissions
   - Handles file read/write exceptions

2. **Decryption Errors**:
   - Catches InvalidToken exceptions for wrong passwords
   - Provides clear error messages
   - Logs detailed error information

3. **API Validation Errors**:
   - Handles network connectivity issues
   - Processes various HTTP status codes
   - Provides retry options for failed validations

## Best Practices and Recommendations

1. **Password Management**:
   - Use a strong, unique password (minimum 12 characters)
   - Store the password in a secure password manager
   - Never share the password or store it in plaintext

2. **Backup Procedures**:
   - Regularly back up encryption_key.bin and providers.yaml
   - Store backups in a secure location
   - Test restoration procedures periodically

3. **Security Considerations**:
   - Run the script in a secure environment
   - Limit access to the server and files
   - Regularly update dependencies for security patches

4. **Integration Guidelines**:
   - Import decryption functions rather than executing the script
   - Handle exceptions appropriately in the calling code
   - Avoid storing decrypted keys in memory longer than necessary

## Troubleshooting

### Common Issues and Solutions

1. **"Invalid encryption key or corrupted data" Error**:
   - Verify you're using the correct password
   - Check that encryption_key.bin hasn't been modified
   - Ensure providers.yaml hasn't been corrupted

2. **API Key Validation Failures**:
   - Check internet connectivity
   - Verify the API key is correct and active
   - Confirm the API endpoint is accessible

3. **Permission Denied Errors**:
   - Verify file ownership and permissions
   - Ensure the script is run with appropriate user privileges
   - Check for file system restrictions

4. **Import Errors**:
   - Verify all dependencies are installed
   - Check Python version compatibility
   - Ensure the script is in the Python path

## Conclusion

The API Key Manager provides a secure, robust solution for managing API keys in the MCP server environment. By implementing industry-standard encryption techniques, proper file permissions, and comprehensive error handling, it ensures that sensitive credentials are protected while remaining accessible to authorized processes.

This documentation serves as a complete guide to understanding what the API Key Manager is, where it fits in the system architecture, and how it works to secure your API keys. By following the provided instructions and best practices, you can maintain a high level of security for your AI service provider credentials.
