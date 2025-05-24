# User Guide

## II-Agent MCP Server Add-On

This guide provides instructions for setting up and using the II-Agent MCP Server Add-On.

## Installation

### Prerequisites

- Python 3.12+
- pip
- II-Agent installed and configured

### Install from GitHub

1. Clone the repository:
```bash
git clone https://github.com/k3ss-official/ii-agent-mcp-mvp.git
cd ii-agent-mcp-mvp
```

2. Install the package:
```bash
pip install -e .
```

## Configuration

### Initial Setup

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

### Configuration

Edit your II-Agent configuration to point to the MCP server:

```yaml
# II-Agent config.yaml
providers:
  mcp:
    type: api
    url: http://localhost:8000/generate
    models:
      - name: gemini-1.5-pro
        provider: gemini
      - name: deepseek-chat
        provider: deepseek
      - name: mistral-large
        provider: mistral
```

### Usage

Run II-Agent with the MCP provider:

```bash
ii-agent run --provider mcp --model gemini-1.5-pro "What is the current date?"
```

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

## Monitoring and Logging

### Log Files

Logs are written to `mcp_logs.log` in the project directory. The log level can be configured in `providers.yaml`.

### Status Monitoring

You can monitor the status of the MCP server and its providers by accessing the `/status` endpoint:

```bash
curl http://localhost:8000/status
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the MCP server is running
   - Check that the host and port are correctly configured

2. **Authentication Errors**
   - Verify that API keys are correctly configured
   - Check that the API keys are valid with their respective providers

3. **Model Not Found**
   - Ensure the requested model is available in the provider's model list
   - Check the spelling of the model name

4. **Rate Limit Errors**
   - If you encounter rate limit errors despite fallback logic, consider adding more providers or implementing a delay between requests

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs in `mcp_logs.log` for detailed error information
2. Review the [Technical Design Document](technical_design.md) for insights into the system architecture
3. Consult the [Developer Guide](developer_guide.md) for more advanced troubleshooting

## Security Considerations

### API Key Protection

- API keys are encrypted in the `providers.yaml` file
- The encryption key is stored in a separate file with restricted permissions
- Logs are sanitized to prevent API key exposure

### Best Practices

- Regularly rotate your API keys
- Use a dedicated API key for the MCP server
- Restrict access to the MCP server to trusted networks
- Monitor the logs for suspicious activity

## Advanced Configuration

### Custom Provider Order

You can specify the order of providers for fallback in the `providers.yaml` file. The server will try providers in the order they are listed.

### Rate Limit Handling

The MCP server automatically detects rate limits and falls back to alternative providers. You can adjust the fallback behavior in the `providers.yaml` file:

```yaml
fallback:
  enabled: true
  max_retries: 2  # Number of retries per provider
  timeout: 10     # Timeout in seconds
```

### Logging Configuration

You can adjust the log level in the `providers.yaml` file:

```yaml
server:
  log_level: debug  # Options: debug, info, warning, error, critical
```
