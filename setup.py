"""
II-Agent MCP Server Add-On - Package Setup
Handles package installation
"""
from setuptools import setup, find_packages

setup(
    name="ii-agent-mcp-mvp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "requests>=2.31.0",
        "pydantic>=2.4.2",
        "pyyaml>=6.0.1",
        "cryptography>=41.0.4",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "mcp-setup=ii_agent_mcp_mvp.setup:main",
            "mcp-server=ii_agent_mcp_mvp.main:main",
        ],
    },
    author="II-Agent Team",
    description="Multi-Cloud Provider server add-on for II-Agent",
    keywords="ai, api, mcp, ii-agent",
    python_requires=">=3.12",
)
