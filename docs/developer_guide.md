# Developer Guide

## II-Agent MCP Server Add-On

This guide provides detailed information for developers who want to understand, modify, or extend the II-Agent MCP Server Add-On.

## Project Structure

```
ii-agent-mcp-mvp/
├── ii_agent_mcp_mvp/
│   ├── __init__.py
│   ├── main.py                 # FastAPI server entry point
│   ├── config.py               # Configuration handling
│   ├── security.py             # API key encryption/decryption
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base provider class
│   │   ├── gemini.py           # Gemini provider implementation
│   │   ├── deepseek.py         # DeepSeek provider implementation
│   │   ├── mistral.py          # Mistral provider implementation
│   │   └── factory.py          # Provider factory
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py          # Logging utilities
│   └── fallback/
│       ├── __init__.py
│       └── handler.py          # Fallback logic implementation
├── setup.py                    # Package installation
├── requirements.txt            # Dependencies
├── docs/                       # Documentation
│   ├── what_why_how.md         # Project overview and rationale
│   └── technical_design.md     # Technical architecture and design
└── tests/                      # Unit and integration tests
    ├── test_providers.py
    ├── test_fallback.py
    └── test_security.py
```

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/k3ss-official/ii-agent-mcp-mvp.git
cd ii-agent-mcp-mvp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

4. Run tests:
```bash
python -m tests.run_tests
```

## Adding a New Provider

To add a new provider to the MCP Server:

1. Create a new provider class in `ii_agent_mcp_mvp/providers/`:

```python
# ii_agent_mcp_mvp/providers/new_provider.py
from typing import Dict, Any, List, Optional
from .base import AbstractProvider

class NewProvider(AbstractProvider):
    """Provider implementation for New API"""
    
    BASE_URL = "https://api.newprovider.com/v1"
    
    def __init__(self, api_key: str, models: Optional[List[str]] = None):
        """Initialize the provider with API key and optional model list"""
        super().__init__(api_key, models)
        if not models:
            self.models = self.discover_models()
    
    def validate_api_key(self) -> bool:
        """Validate the API key with provider API"""
        # Implementation here
        pass
    
    def discover_models(self) -> List[str]:
        """Discover available models from provider API"""
        # Implementation here
        pass
    
    def generate(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """Generate text using provider API"""
        # Implementation here
        pass
```

2. Update the provider factory in `ii_agent_mcp_mvp/providers/factory.py`:

```python
# Add import
from .new_provider import NewProvider

# Update provider_classes dictionary in ProviderFactory.__init__
self.provider_classes = {
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
    "mistral": MistralProvider,
    "newprovider": NewProvider  # Add new provider
}
```

3. Update the security manager in `ii_agent_mcp_mvp/security.py` to add validation for the new provider's API key format:

```python
# Update patterns dictionary in SecurityManager.validate_api_key
patterns = {
    "gemini": r"^AIza[0-9A-Za-z\-_]{35,}$",
    "deepseek": r"^[0-9a-f]{32}$",
    "mistral": r"^[A-Za-z0-9]{48}$",
    "newprovider": r"^your-regex-pattern$"  # Add new pattern
}
```

4. Add tests for the new provider in `tests/test_providers.py`

## Modifying Fallback Logic

The fallback logic is implemented in `ii_agent_mcp_mvp/fallback/handler.py`. To modify the fallback behavior:

1. Update the `process_request` method in `FallbackHandler` class
2. Modify the conditions that trigger fallback
3. Adjust the retry mechanism as needed
4. Update the error handling and logging

Example: Changing the maximum number of retries:

```python
def __init__(self, provider_factory: ProviderFactory, max_retries: int = 3):  # Changed from 2 to 3
    """Initialize the fallback handler"""
    self.provider_factory = provider_factory
    self.max_retries = max_retries
```

## Enhancing Security

The security implementation is in `ii_agent_mcp_mvp/security.py`. To enhance security:

1. Update the encryption method in `SecurityManager` class
2. Modify the key derivation parameters
3. Improve the API key validation patterns
4. Enhance the masking of sensitive data

Example: Increasing the PBKDF2 iterations:

```python
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=200000,  # Increased from 100000
)
```

## API Reference

### FastAPI Server

The FastAPI server is defined in `ii_agent_mcp_mvp/main.py`. It exposes two endpoints:

1. `/generate` (POST): Generates text from a specified model
   - Request body: `GenerateRequest` model
   - Response: `GenerateResponse` model

2. `/status` (GET): Returns server status
   - Response: `StatusResponse` model

### Configuration Manager

The configuration manager is defined in `ii_agent_mcp_mvp/config.py`. It provides methods for:

1. Loading configuration from `providers.yaml`
2. Saving configuration with encrypted API keys
3. Getting provider-specific configuration
4. Adding or updating providers

### Provider Interface

The provider interface is defined in `ii_agent_mcp_mvp/providers/base.py`. It requires implementing:

1. `validate_api_key()`: Validates the API key with the provider
2. `discover_models()`: Discovers available models from the provider
3. `generate()`: Generates text from the specified model

## Troubleshooting

### Common Issues

1. **API Key Validation Failures**
   - Check that the API key format matches the expected pattern
   - Verify that the API key is valid with the provider
   - Ensure the provider's API is accessible

2. **Provider Discovery Failures**
   - Check network connectivity to the provider's API
   - Verify that the API key has permissions to list models
   - Check for changes in the provider's API response format

3. **Fallback Not Working**
   - Ensure multiple providers are configured
   - Check that the fallback conditions are being triggered
   - Verify that the fallback order is correctly specified

### Debugging

1. Enable debug logging by setting the log level in `providers.yaml`:
```yaml
server:
  log_level: debug
```

2. Check the logs in `mcp_logs.log` for detailed information

3. Use the `/status` endpoint to check provider status and request metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite to ensure all tests pass
6. Submit a pull request

## Code Style

This project follows these coding conventions:

1. PEP 8 for Python code style
2. Type hints for all function parameters and return values
3. Docstrings for all classes and methods
4. Comprehensive error handling and logging
5. Test coverage for all new functionality
