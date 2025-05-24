# II-Agent MCP Server Add-On

A Multi-Cloud Provider (MCP) server add-on for II-Agent, providing a unified interface to multiple AI model providers (Gemini, DeepSeek, Mistral) with automated configuration and fallback logic.

## Overview

This project creates an AI-centric "universal connector" that bridges multiple API providers to II-Agent. It handles rate limits, provides fallback mechanisms, and offers a consistent interface regardless of the underlying AI provider.

## Features

- **Multi-Provider Support**: Seamlessly integrates with Gemini, DeepSeek, and Mistral APIs
- **Automated Configuration**: Discovers available models and configures endpoints automatically
- **Robust Fallback Logic**: Automatically falls back to alternative providers on errors, rate limits, or timeouts
- **Monitoring and Logging**: Tracks request metrics and provides detailed logs
- **Secure API Key Handling**: Uses the included [API Key Manager](./api_key_manager/README.md) for secure credential storage

## Repository Structure

```
ii_agent_mcp_mvp/
├── main.py                # Main FastAPI server implementation
├── config.py              # Configuration handling
├── security.py            # Security utilities
├── setup.py               # Package setup script
├── requirements.txt       # Dependencies
├── providers.yaml         # Sample provider configuration
├── ii_agent_integration.md # II-Agent integration guide
├── api_key_manager/       # Secure API key management utility
│   ├── key_manager.py     # API key encryption/decryption tool
│   ├── README.md          # API Key Manager documentation
│   └── ...
├── providers/             # Provider implementations
│   ├── base.py            # Base provider class
│   ├── gemini.py          # Gemini provider
│   ├── deepseek.py        # DeepSeek provider
│   ├── mistral.py         # Mistral provider
│   └── factory.py         # Provider factory
├── fallback/              # Fallback logic
│   └── handler.py         # Fallback handler
├── utils/                 # Utility functions
│   └── logging.py         # Logging utilities
├── tests/                 # Test suite
│   ├── test_providers.py  # Provider tests
│   ├── test_fallback.py   # Fallback tests
│   └── ...
└── docs/                  # Documentation
    ├── technical_design.md # Technical design document
    ├── developer_guide.md # Developer guide
    └── user_guide.md      # User guide
```

## Installation

1. Ensure you're in the correct Conda environment:
   ```bash
   conda activate ii_agent_mcp_mvp
   ```

2. Install the package:
   ```bash
   pip install --force-reinstall --no-cache-dir -e .
   ```

## Configuration

1. Set up API keys using the API Key Manager:
   ```bash
   cd api_key_manager
   python key_manager.py setup
   ```

2. Start the MCP server:
   ```bash
   python main.py
   ```

## API Endpoints

- **POST /generate**: Generate text from a prompt using available providers
- **GET /status**: Get server status and request metrics

## II-Agent Integration

See [II-Agent Integration Guide](ii_agent_integration.md) for detailed instructions on integrating with II-Agent.

## API Key Management

This repository includes a secure API Key Manager utility for handling provider credentials. See the [API Key Manager README](./api_key_manager/README.md) for details.

## Documentation

- [Technical Design Document](./docs/technical_design.md)
- [Developer Guide](./docs/developer_guide.md)
- [User Guide](./docs/user_guide.md)

## License

MIT License
