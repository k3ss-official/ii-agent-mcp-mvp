# II-Agent MCP Server Add-On Architecture

## Overview
The II-Agent MCP (Multi-Cloud Provider) Server Add-On is designed as a modular, secure middleware that connects II-Agent to multiple AI model providers. The MVP focuses on integrating three providers (Gemini, DeepSeek, Mistral) with automated configuration, secure API key handling, and robust fallback logic.

## Core Components

### 1. Provider Interface
- Abstract base class defining standard methods for all providers
- Each provider implements specific API interactions while maintaining consistent interface
- Supports model discovery, validation, and generation requests

### 2. Security Layer
- Encrypted storage of API keys in providers.yaml
- Key validation before routing requests
- Sanitized logging to prevent sensitive data exposure

### 3. FastAPI Server
- Main entry point with /generate and /status endpoints
- Request validation and sanitization
- Response formatting and error handling

### 4. Fallback Logic
- Provider cycling based on error conditions
- Rate limit detection and management
- Timeout handling with configurable thresholds

### 5. Logging and Monitoring
- Structured logging of API interactions
- In-memory metrics for request tracking
- Status endpoint for monitoring

## Security Design

### API Key Management
1. **Collection**: Setup script prompts for API keys on first run
2. **Validation**: Keys are validated against provider-specific patterns and test calls
3. **Storage**: Keys are encrypted using Python's cryptography library
4. **Usage**: Keys are decrypted only when needed for API calls
5. **Protection**: Keys are never exposed in logs or responses

### Request/Response Security
1. **HTTPS Only**: All provider API interactions use HTTPS
2. **Input Sanitization**: All user inputs are validated and sanitized
3. **Output Filtering**: Sensitive data is filtered from logs and responses
4. **Error Handling**: Errors are logged without exposing sensitive details

## Data Flow

1. II-Agent sends generation request to MCP Server
2. MCP Server validates request and selects primary provider
3. Request is sent to primary provider with appropriate authentication
4. If successful, response is returned to II-Agent
5. If unsuccessful, fallback logic activates and tries alternative providers
6. All interactions are logged with appropriate detail level

## Fallback Logic

### Trigger Conditions
- HTTP status codes 400-499 (client errors)
- HTTP status codes 500-599 (server errors)
- Rate limit headers indicating limits reached
- Timeouts exceeding 10 seconds

### Fallback Process
1. Detect failure condition from primary provider
2. Log failure with appropriate context
3. Select next provider in sequence
4. Retry request with new provider
5. Maximum 2 retries per provider before failing
6. Return final result or comprehensive error

## Logging Strategy

### Log Levels
- INFO: Standard API calls, provider selection, successful responses
- WARNING: Rate limit approaches, slow responses, minor issues
- ERROR: API failures, authentication issues, fallback triggers
- DEBUG: Detailed request/response data (sanitized)

### Log Storage
- File-based logging to mcp_logs.log
- Rotation policy to prevent excessive file growth
- Sanitization to prevent sensitive data exposure

## Monitoring

### In-Memory Metrics
- Total requests per provider
- Success/failure counts
- Average response times
- Rate limit tracking

### Status Endpoint
- Current provider status
- Request counts and success rates
- System health indicators

## Future Extensibility
The architecture is designed to support future expansion toward the universal connector vision:
- Provider interface allows easy addition of new providers
- Modular design supports integration with Crawl4AI
- Configuration system can be extended for local model support
- Logging and monitoring can scale to support more complex deployments
