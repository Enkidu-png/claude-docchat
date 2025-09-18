#!/usr/bin/env python3
"""
Setup script for DocChat MCP Server.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="docchat-mcp-server",
    version="1.0.0",
    author="Enkidu-png",
    author_email="jansachse@outlook.com",
    description="Semantic Document Search and Q&A System for Claude Desktop via MCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Enkidu-png/docchat-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastmcp>=0.2.0",
        "mcp>=1.0.0",
        "sentence-transformers>=2.2.0",
        "PyMuPDF>=1.23.0",
        "python-docx>=0.8.11",
        "watchdog>=3.0.0",
        "psutil>=5.9.0",
        "chardet>=5.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "docchat-mcp=src.mcp_server_official:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["config/*.py", "models/*.py", "services/*.py", "utils/*.py"],
    },
    keywords=[
        "mcp",
        "model-context-protocol",
        "claude",
        "document-search",
        "semantic-search",
        "pdf",
        "docx",
        "nlp",
        "embeddings",
        "ai",
        "chatbot",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Enkidu-png/docchat-mcp-server/issues",
        "Source": "https://github.com/Enkidu-png/docchat-mcp-server",
        "Documentation": "https://github.com/Enkidu-png/docchat-mcp-server#readme",
    },
)