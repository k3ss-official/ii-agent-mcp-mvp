# Technical Design Document

## II-Agent MCP Server Add-On

### System Architecture

#### Overview

The II-Agent MCP Server Add-On is designed as a middleware layer that sits between II-Agent and multiple AI model providers. It presents a unified API to II-Agent while managing the complexities of interacting with different provider APIs behind the scenes.

```
┌─────────┐     ┌───────────────────────┐     ┌─────────────┐
│         │     │                       │     │ Gemini API  │
│ II-Agent├─────┤  MCP Server Add-On    ├─────┤             │
│         │     │                       │     └─────────────┘
└─────────┘     │  ┌─────────────────┐  │     ┌─────────────┐
                │  │ Provider Factory │  │     │ DeepSeek API│
                │  └─────────────────┘  ├─────┤             │
                │  ┌─────────────────┐  │     └─────────────┘
                │  │ Fallback Handler │  │     ┌─────────────┐
                │  └─────────────────┘  │     │ Mistral API  │
                │  ┌─────────────────┐  ├─────┤             │
                │  │ Security Manager │  │     └─────────────┘
                │  └─────────────────┘  │
                └───────────────────────┘
```

#### Component Breakdown

1. **FastAPI Server**
   - Entry point for all requests
   - Handles request validation and routing
   - Exposes /generate and /status endpoints
   - Manages response formatting

2. **Provider Factory**
   - Creates and manages provider instances
   - Maintains provider registry
   - Provides access to provider status

3. **Provider Modules**
   - Abstract base class defines common interface
   - Provider-specific implementations handle API differences
   - Each provider handles its own authentication and API calls

4. **Fallback Handler**
   - Implements retry and fallback logic
   - Detects errors, rate limits, and timeouts
   - Manages provider cycling based on configuration

5. **Security Manager**
   - Handles API key encryption and decryption
   - Validates API key formats
   - Manages secure storage of sensitive information

6. **Configuration Manager**
   - Loads and parses providers.yaml
   - Handles configuration updates
   - Provides configuration access to other components

7. **Logging Utilities**
   - Configures structured logging
   - Implements log sanitization
   - Manages log rotation and storage

### Data Flow

#### Request Processing

1. II-Agent sends a request to the `/generate` endpoint
2. FastAPI server validates the request
3. Server selects the primary provider based on request or configuration
4. Request is forwarded to the fallback handler
5. Fallback handler attempts the request with the primary provider
6. If successful, response is returned to II-Agent
7. If unsuccessful, fallback logic activates and tries alternative providers
8. All interactions are logged with appropriate detail level

#### Configuration Flow

1. Setup script prompts for API keys
2. Keys are validated against provider APIs
3. Provider APIs are queried for available models
4. Configuration is encrypted and saved to providers.yaml
5. On server startup, configuration is loaded and decrypted
6. Providers are initialized with their respective configurations

### Security Architecture

#### API Key Management

1. **Collection**
   - Setup script prompts for API keys
   - Keys are validated against provider-specific patterns
   - Test calls verify key functionality

2. **Storage**
   - Keys are encrypted using Fernet symmetric encryption
   - Encryption key is derived using PBKDF2HMAC with a random salt
   - Salt and password are stored in restricted files
   - Encrypted keys are stored in providers.yaml

3. **Usage**
   - Keys are decrypted only when needed for API calls
   - Keys are never logged or exposed in responses
   - Keys are masked in debug output

#### Request/Response Security

1. All provider API interactions use HTTPS
2. Input validation prevents injection attacks
3. Error responses are sanitized to prevent information leakage
4. Logging is configured to mask sensitive information

### Fallback Mechanism

#### Trigger Conditions

1. **HTTP Errors**
   - 400-499: Client errors (e.g., 401 Unauthorized, 429 Too Many Requests)
   - 500-599: Server errors

2. **Rate Limits**
   - Detection via rate limit headers (e.g., x-rate-limit-remaining)
   - Detection via 429 Too Many Requests responses
   - Proactive avoidance when approaching limits

3. **Timeouts**
   - Requests exceeding 10 seconds

#### Fallback Process

1. Error is detected and logged
2. Current provider is marked as failed for this request
3. Next provider in sequence is selected
4. Request is retried with new provider
5. Process repeats until success or all providers are exhausted
6. Maximum 2 retries per provider

### Monitoring and Logging

#### Metrics Tracked

1. **Per Provider**
   - Request count
   - Success/failure count
   - Success rate
   - Average response time
   - Rate limit status

2. **System-wide**
   - Uptime
   - Total requests
   - Fallback frequency
   - Error distribution

#### Log Levels

- **DEBUG**: Detailed request/response data (sanitized)
- **INFO**: Standard API calls, provider selection
- **WARNING**: Rate limit approaches, slow responses
- **ERROR**: API failures, authentication issues
- **CRITICAL**: System-level failures

### Extensibility Points

1. **New Providers**
   - Implement AbstractProvider interface
   - Register in provider factory
   - Add to configuration

2. **Enhanced Fallback Logic**
   - Modify FallbackHandler class
   - Update fallback configuration

3. **Additional Endpoints**
   - Add new routes to FastAPI app
   - Implement handler functions

4. **Custom Logging**
   - Extend logging utilities
   - Add new log handlers or formatters

### Future Expansion

1. **Crawl4AI Integration**
   - New module for API documentation scraping
   - Configuration generator based on scraped data
   - Automatic updates when APIs change

2. **Local Model Support**
   - Model installation and management module
   - Interface adapters for local inference
   - Resource monitoring and optimization

3. **WebUI**
   - Dashboard for configuration and monitoring
   - Real-time metrics visualization
   - Provider performance comparison

4. **Persistent Memory**
   - Cross-provider context storage
   - Memory optimization and pruning
   - Integration with II-Agent task context
