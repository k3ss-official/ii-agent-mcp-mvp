# II-Agent MCP Server Add-On Project Structure

## Directory Structure
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
│   │   ├── logging.py          # Logging utilities
│   │   └── validation.py       # Input validation utilities
│   └── fallback/
│       ├── __init__.py
│       └── handler.py          # Fallback logic implementation
├── setup.py                    # Package installation
├── requirements.txt            # Dependencies
├── providers.yaml.template     # Template for provider configuration
├── README.md                   # Setup and integration guide
└── tests/                      # Unit and integration tests
    ├── __init__.py
    ├── test_providers.py
    ├── test_fallback.py
    └── test_security.py
```

## Key Components

### 1. FastAPI Server (main.py)
- Implements the FastAPI application with /generate and /status endpoints
- Handles request validation and response formatting
- Integrates with provider factory and fallback handler

### 2. Configuration (config.py)
- Loads and parses providers.yaml
- Manages environment variables and defaults
- Provides configuration access to other components

### 3. Security (security.py)
- Implements API key encryption and decryption
- Provides key validation utilities
- Manages secure storage of sensitive information

### 4. Provider Interface (providers/base.py)
- Defines AbstractProvider base class
- Standardizes methods for all provider implementations
- Ensures consistent behavior across providers

### 5. Provider Implementations
- Gemini (providers/gemini.py)
- DeepSeek (providers/deepseek.py)
- Mistral (providers/mistral.py)
- Each implements provider-specific API interactions

### 6. Provider Factory (providers/factory.py)
- Creates provider instances based on configuration
- Manages provider lifecycle and selection
- Supports dynamic provider loading

### 7. Fallback Handler (fallback/handler.py)
- Implements fallback logic based on error conditions
- Manages provider cycling and retry attempts
- Tracks rate limits and timeouts

### 8. Logging Utilities (utils/logging.py)
- Configures structured logging
- Implements log sanitization
- Manages log rotation and storage

### 9. Setup Script
- Prompts for API keys on first run
- Validates keys against provider APIs
- Generates encrypted providers.yaml file
