"""
II-Agent MCP Server Add-On - Main FastAPI Server
Implements the FastAPI server with /generate and /status endpoints
"""
import os
import time
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import ConfigManager
from .providers.factory import ProviderFactory
from .fallback.handler import FallbackHandler
from .utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize application
app = FastAPI(
    title="II-Agent MCP Server",
    description="Multi-Cloud Provider server for II-Agent",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize configuration, provider factory, and fallback handler
config_manager = ConfigManager()
provider_factory = ProviderFactory()
fallback_handler = None

# Request and response models
class GenerateRequest(BaseModel):
    """Model for generation request"""
    prompt: str = Field(..., description="The prompt to generate from")
    model: str = Field("default", description="The model to use for generation")
    provider: Optional[str] = Field(None, description="The provider to use (optional)")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: int = Field(1024, description="Maximum tokens to generate")
    top_p: float = Field(0.95, description="Top-p sampling parameter")
    top_k: int = Field(40, description="Top-k sampling parameter")

class GenerateResponse(BaseModel):
    """Model for generation response"""
    text: str = Field(..., description="Generated text")
    model: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider used for generation")
    latency: float = Field(..., description="Generation latency in seconds")
    fallback_used: bool = Field(False, description="Whether fallback was used")

class StatusResponse(BaseModel):
    """Model for status response"""
    status: str = Field("ok", description="Server status")
    uptime: float = Field(..., description="Server uptime in seconds")
    providers: Dict[str, Any] = Field(..., description="Provider status")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize providers on startup"""
    global fallback_handler
    
    # Load configuration
    config = config_manager.config
    
    # Initialize providers
    if "providers" in config:
        for provider_config in config["providers"]:
            name = provider_config.get("name")
            api_key = provider_config.get("api_key")
            models = provider_config.get("models")
            
            if name and api_key:
                logger.info(f"Initializing provider: {name}")
                provider_factory.create_provider(name, api_key, models)
    
    # Initialize fallback handler
    fallback_config = config.get("fallback", {})
    max_retries = fallback_config.get("max_retries", 2)
    fallback_handler = FallbackHandler(provider_factory, max_retries)
    
    logger.info("MCP Server initialized successfully")

# Generate endpoint
@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    """Generate text from the specified model"""
    start_time = time.time()
    
    # Log the request (sanitized)
    logger.info(f"Generation request: model={request.model}, length={len(request.prompt)}")
    
    # Check if providers are available
    providers = provider_factory.get_all_providers()
    if not providers:
        logger.error("No providers available")
        raise HTTPException(status_code=503, detail="No providers available")
    
    # Determine provider order
    if request.provider:
        # If specific provider requested, use it first
        provider_order = [request.provider.lower()]
        # Add other providers for fallback
        for p in config_manager.get_provider_order():
            if p.lower() != request.provider.lower():
                provider_order.append(p.lower())
    else:
        # Use default provider order from config
        provider_order = config_manager.get_provider_order()
    
    # Process the request with fallback logic
    result = fallback_handler.process_request(
        prompt=request.prompt,
        model=request.model,
        provider_order=provider_order,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        top_p=request.top_p,
        top_k=request.top_k
    )
    
    # Check for success
    if not result.get("success", False):
        error_msg = result.get("error", "Unknown error")
        details = result.get("details", [])
        logger.error(f"Generation failed: {error_msg}, details: {details}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {error_msg}")
    
    # Log success
    logger.info(f"Generation successful: provider={result['provider']}, model={result['model']}, latency={result['latency']:.2f}s")
    
    # Return response
    return {
        "text": result["text"],
        "model": result["model"],
        "provider": result["provider"],
        "latency": result["latency"],
        "fallback_used": result.get("fallback_used", False)
    }

# Status endpoint
@app.get("/status", response_model=StatusResponse)
async def status():
    """Get server status"""
    # Calculate uptime
    uptime = time.time() - startup_time
    
    # Get provider status
    provider_status = provider_factory.get_provider_status()
    
    return {
        "status": "ok",
        "uptime": uptime,
        "providers": provider_status
    }

# Store startup time
startup_time = time.time()

def main():
    """Run the FastAPI server"""
    import uvicorn
    
    # Load configuration
    config = config_manager.config
    server_config = config.get("server", {})
    
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8000)
    log_level = server_config.get("log_level", "info")
    
    # Run server
    uvicorn.run("ii_agent_mcp_mvp.main:app", host=host, port=port, log_level=log_level, reload=True)

if __name__ == "__main__":
    main()
