# II-Agent MCP Server Add-On

A Multi-Cloud Provider (MCP) server add-on for II-Agent that integrates multiple AI model providers with automated configuration, secure API key handling, and robust fallback logic.

## Features

- **Multi-Provider Support**: Integrates with Gemini, DeepSeek, and Mistral APIs
- **Automated Configuration**: Discovers available models and configures endpoints automatically
- **Secure API Key Handling**: Encrypts API keys for secure storage
- **Robust Fallback Logic**: Automatically falls back to alternative providers on errors, rate limits, or timeouts
- **Monitoring and Logging**: Tracks request metrics and provides detailed logs
- **II-Agent Integration**: Seamlessly connects with II-Agent as a backend provider

## Installation

### Prerequisites

- Python 3.12+
- pip

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/your-username/ii-agent-mcp-mvp.git
cd ii-agent-mcp-mvp
```

2. Install the package:
```bash
pip install -e .
```

## Setup

### Configure Providers

Run the setup script to configure providers:

```bash
python -m ii_agent_mcp_mvp.setup
```

The setup script will:
1. Prompt for API keys for each provider (Gemini, DeepSeek, Mistral)
2. Validate the API keys with each provider
3. Discover available models
4. Generate an encrypted `providers.yaml` configuration file

### Manual Configuration

If you prefer to configure providers manually, create a `providers.yaml` file with the following structure:

```yaml
providers:
  - name: gemini
    api_key: YOUR_GEMINI_API_KEY
    models:
      - gemini-1.5-pro
      - gemini-1.5-flash
  - name: deepseek
    api_key: YOUR_DEEPSEEK_API_KEY
    models:
      - deepseek-chat
      - deepseek-coder
  - name: mistral
    api_key: YOUR_MISTRAL_API_KEY
    models:
      - mistral-large
      - mistral-medium
      - mistral-small
fallback:
  enabled: true
  max_retries: 2
  timeout: 10
server:
  host: 0.0.0.0
  port: 8000
  log_level: info
```

Then run the setup script with the `--encrypt` flag to encrypt the API keys:

```bash
python -m ii_agent_mcp_mvp.setup --encrypt
```

## Running the Server

Start the MCP server:

```bash
python -m ii_agent_mcp_mvp.main
```

By default, the server runs on `http://localhost:8000`.

## II-Agent Integration

See [II-Agent Integration Guide](ii_agent_integration.md) for detailed instructions on integrating with II-Agent.

## API Reference

### Generate Endpoint

**URL**: `/generate`

**Method**: `POST`

**Request Body**:
```json
{
  "prompt": "Your prompt text here",
  "model": "model-name",
  "provider": "provider-name",  // Optional
  "temperature": 0.7,           // Optional
  "max_tokens": 1024,           // Optional
  "top_p": 0.95,                // Optional
  "top_k": 40                   // Optional
}
```

**Response**:
```json
{
  "text": "Generated text response",
  "model": "model-used",
  "provider": "provider-used",
  "latency": 0.5,
  "fallback_used": false
}
```

### Status Endpoint

**URL**: `/status`

**Method**: `GET`

**Response**:
```json
{
  "status": "ok",
  "uptime": 3600,
  "providers": {
    "gemini": {
      "name": "gemini",
      "models": ["gemini-1.5-pro", "gemini-1.5-flash"],
      "request_count": 10,
      "failure_count": 0,
      "success_rate": 100.0,
      "rate_limit_remaining": 100
    },
    "deepseek": {
      "name": "deepseek",
      "models": ["deepseek-chat", "deepseek-coder"],
      "request_count": 5,
      "failure_count": 0,
      "success_rate": 100.0,
      "rate_limit_remaining": 50
    },
    "mistral": {
      "name": "mistral",
      "models": ["mistral-large", "mistral-medium", "mistral-small"],
      "request_count": 2,
      "failure_count": 0,
      "success_rate": 100.0,
      "rate_limit_remaining": 200
    }
  }
}
```

## Testing

Run the test suite:

```bash
python -m tests.run_tests
```

To test with actual API keys:

```bash
python -m tests.run_tests --gemini-key YOUR_GEMINI_API_KEY --deepseek-key YOUR_DEEPSEEK_API_KEY --mistral-key YOUR_MISTRAL_API_KEY
```

## Security

- API keys are encrypted using Python's cryptography library
- Key files are stored with restricted permissions (600)
- Logs are sanitized to prevent sensitive data exposure
- All provider API interactions use HTTPS

## Future Development

This MVP is the first step toward a universal dynamic connector that will:

1. Auto-discover API configs using Crawl4AI
2. Support installation/configuration of local models
3. Dynamically adjust routing based on user selections
4. Add persistent memory across providers
5. Include a WebUI for configuration and monitoring

## License

Open source under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
