# DocChat MCP Server - Installation Guide

This guide provides detailed installation instructions for DocChat MCP Server across different platforms.

## 📋 Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: 3.10 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space (for models and documents)
- **Claude Desktop**: Latest version

### Required Software

1. **Python 3.10+**
   - Windows: Download from [python.org](https://python.org)
   - macOS: `brew install python@3.10` or download from python.org
   - Linux: `sudo apt install python3.10 python3.10-venv` (Ubuntu/Debian)

2. **Git**
   - Windows: Download from [git-scm.com](https://git-scm.com)
   - macOS: `brew install git` or Xcode Command Line Tools
   - Linux: `sudo apt install git` (Ubuntu/Debian)

3. **Claude Desktop**
   - Download from [claude.ai/download](https://claude.ai/download)

## 🚀 Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/Enkidu-png/docchat-mcp-server.git
cd docchat-mcp-server

# Create and activate virtual environment
python -m venv docchat_env

# Windows
docchat_env\Scripts\activate

# macOS/Linux
source docchat_env/bin/activate

# Install the package
pip install -e .
```

### Method 2: Development Install

```bash
# Clone the repository
git clone https://github.com/Enkidu-png/docchat-mcp-server.git
cd docchat-mcp-server

# Create and activate virtual environment
python -m venv docchat_env
source docchat_env/bin/activate  # or docchat_env\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements-dev.txt
pip install -e .
```

### Method 3: From PyPI (When Available)

```bash
pip install docchat-mcp-server
```

## ⚙️ Configuration

### Claude Desktop Configuration

1. **Open Claude Desktop Settings**
   - Launch Claude Desktop
   - Click the gear icon (⚙️) in the bottom left
   - Select "Developer" tab
   - Click "Edit Config"

2. **Add DocChat Configuration**

   **Windows Configuration:**
   ```json
   {
     "mcpServers": {
       "docchat": {
         "command": "python",
         "args": [
           "-m",
           "src.mcp_server_official"
         ],
         "cwd": "C:\\path\\to\\docchat-mcp-server",
         "env": {
           "PYTHONPATH": "C:\\path\\to\\docchat-mcp-server"
         }
       }
     }
   }
   ```

   **macOS/Linux Configuration:**
   ```json
   {
     "mcpServers": {
       "docchat": {
         "command": "python",
         "args": [
           "-m",
           "src.mcp_server_official"
         ],
         "cwd": "/path/to/docchat-mcp-server",
         "env": {
           "PYTHONPATH": "/path/to/docchat-mcp-server"
         }
       }
     }
   }
   ```

3. **Save and Restart**
   - Save the configuration
   - Restart Claude Desktop completely

### Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR)
DOCCHAT_LOG_LEVEL=INFO

# OpenAI API integration (optional)
# OPENAI_API_KEY=your-api-key-here
# EMBEDDING_USE_OPENAI=true

# Custom model path (optional)
# EMBEDDING_MODEL_PATH=/path/to/custom/model
```

## 🧪 Testing Installation

### 1. Test Python Module

```bash
# Activate virtual environment
source docchat_env/bin/activate  # or docchat_env\Scripts\activate on Windows

# Test module import
python -c "import src.mcp_server_official; print('✅ Module loads correctly')"
```

### 2. Test MCP Server

```bash
# Run a quick test (if available)
python -m src.mcp_server_official --test
```

### 3. Test Claude Integration

1. Start a new conversation in Claude Desktop
2. Type: `What document tools do you have available?`
3. You should see DocChat tools listed

### 4. Test Document Processing

```
What documents are in my Documents folder?
```

## Platform-Specific Instructions

### Windows

1. **Install Python from Microsoft Store** (alternative)
   ```bash
   winget install Python.Python.3.11
   ```

2. **Use PowerShell** (recommended over Command Prompt)
   ```powershell
   # Enable script execution if needed
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Virtual Environment Activation**
   ```cmd
   # Command Prompt
   docchat_env\Scripts\activate.bat

   # PowerShell
   docchat_env\Scripts\Activate.ps1
   ```

### macOS

1. **Install with Homebrew**
   ```bash
   brew install python@3.11
   brew install git
   ```

2. **Xcode Command Line Tools** (if needed)
   ```bash
   xcode-select --install
   ```

### Linux (Ubuntu/Debian)

1. **Install system dependencies**
   ```bash
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev
   sudo apt install git build-essential
   ```

2. **Install pip** (if not included)
   ```bash
   sudo apt install python3-pip
   ```

## 🔧 Troubleshooting

### Common Issues

#### "Module not found" errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'src'
```

**Solutions:**
1. Ensure virtual environment is activated
2. Check PYTHONPATH in Claude Desktop config
3. Verify installation with `pip list | grep docchat`

#### Claude Desktop connection issues

**Symptoms:**
- "No result received from client-side tool execution"
- Tools not appearing in Claude

**Solutions:**
1. Check Claude Desktop logs:
   - Windows: `%APPDATA%\Claude\logs`
   - macOS: `~/Library/Application Support/Claude/logs`
2. Verify JSON configuration syntax
3. Ensure file paths use correct separators
4. Restart Claude Desktop completely

#### Python version conflicts

**Symptoms:**
```
This package requires Python 3.10+
```

**Solutions:**
1. Check Python version: `python --version`
2. Use specific Python version: `python3.11 -m venv docchat_env`
3. Update PATH to use correct Python

#### Permission errors

**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. Run terminal as administrator (Windows)
2. Check folder permissions
3. Use `--user` flag: `pip install --user -e .`

### Advanced Troubleshooting

#### Enable Debug Logging

1. Set environment variable:
   ```bash
   export DOCCHAT_LOG_LEVEL=DEBUG  # Linux/macOS
   set DOCCHAT_LOG_LEVEL=DEBUG     # Windows
   ```

2. Check logs in Claude Desktop logs directory

#### Clean Installation

```bash
# Remove virtual environment
rm -rf docchat_env  # Linux/macOS
rmdir /s docchat_env  # Windows

# Clear pip cache
pip cache purge

# Reinstall
python -m venv docchat_env
source docchat_env/bin/activate
pip install -e .
```

#### Network Issues

If model downloads fail:

```bash
# Set custom cache directory
export TRANSFORMERS_CACHE=/path/to/custom/cache

# Use offline mode (if model already downloaded)
export TRANSFORMERS_OFFLINE=1
```

## 📊 Performance Optimization

### Memory Management

For systems with limited RAM:

```python
# In src/config/settings.py, adjust:
max_memory_mb = 256  # Reduce from default 500MB
chunk_size = 500     # Reduce from default 1000
batch_size = 8       # Reduce from default 16
```

### Model Caching

First run downloads ~90MB model. To preload:

```bash
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model cached successfully')
"
```

## 🔄 Updates

### Update to Latest Version

```bash
# Activate virtual environment
source docchat_env/bin/activate

# Update from Git
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Reinstall package
pip install -e . --force-reinstall
```

### Migration Notes

Check `CHANGELOG.md` for version-specific migration instructions.

## 📞 Support

If installation fails:

1. **Check Prerequisites**: Verify all requirements are met
2. **Review Logs**: Check both terminal output and Claude Desktop logs
3. **Search Issues**: Look for similar problems on GitHub
4. **Create Issue**: Provide detailed error information

### Information to Include in Support Requests

- Operating system and version
- Python version (`python --version`)
- Claude Desktop version
- Complete error messages
- Installation method used
- Virtual environment details (`pip list`)

---

**Installation complete!** You should now be able to use DocChat with Claude Desktop. 🚀