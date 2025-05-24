"""
II-Agent MCP Server Add-On - II-Agent Integration Guide
Provides instructions for integrating the MCP server with II-Agent
"""

# II-Agent Integration

This document outlines the steps to integrate the MCP Server Add-On with II-Agent.

## Prerequisites

- II-Agent installed and configured
- MCP Server Add-On installed and configured with at least one provider

## Integration Steps

### 1. Start the MCP Server

First, ensure the MCP server is running:

```bash
# Activate your Python environment if needed
# cd to the project directory
python -m ii_agent_mcp_mvp.main
```

By default, the server runs on `http://localhost:8000`.

### 2. Configure II-Agent to Use MCP Server

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

### 3. Test the Integration

Run a simple test with II-Agent to verify the integration:

```bash
ii-agent run --provider mcp --model gemini-1.5-pro "What is the current date?"
```

### 4. Verify Fallback Functionality

To test the fallback functionality, you can temporarily disable one provider in the MCP server configuration and verify that II-Agent requests are automatically routed to the next available provider.

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

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the MCP server is running and accessible from II-Agent.

2. **Authentication Errors**: Verify that API keys are correctly configured in the MCP server.

3. **Model Not Found**: Check that the requested model is available in the provider's model list.

4. **Rate Limit Errors**: If you encounter rate limit errors despite fallback logic, consider adding more providers or implementing a delay between requests.

### Logs

Check the MCP server logs (`mcp_logs.log`) for detailed information about requests, errors, and fallback events.
