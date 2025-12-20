# Comprehensive Smart Home Control MCP Server & Agent

A production-quality, open-source implementation of a Model Context Protocol (MCP) server and AI agent framework for controlling smart home ecosystems. Built with async-first Python, strong typing, and extensible architecture to support multiple LLM providers and smart home platforms.

## 🚀 Features

- **MCP Server**: Fully compliant Model Context Protocol implementation exposing smart home capabilities as tools and resources
- **Multiple Smart Home Platforms**: 
  - ✅ Samsung SmartThings (fully implemented)
  - 🔄 Home Assistant (stub, ready for implementation)
  - 🔄 Matter (stub, ready for implementation)
  - 🔄 Alexa (stub, ready for implementation)
- **LLM Agnostic**: Seamlessly switch between:
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude)
  - Local LLMs via Ollama
- **AI Agent**: Natural language device control with:
  - Ambiguity resolution
  - Destructive action confirmation
  - Structured logging and monitoring
- **Production Ready**:
  - Full type hints with mypy strict mode
  - Comprehensive error handling
  - Async/await throughout
  - Environment-based configuration
  - Zero hardcoded secrets

## 📋 Table of Contents

- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Adding New Providers](#adding-new-providers)
- [API Reference](#api-reference)
- [Development](#development)
- [License](#license)

## 🏗️ Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent Layer                          │
│  (Natural language → MCP tool calls → Device commands)       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    MCP Server                                │
│  (Tools, Resources, Schemas, Type Safety)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Smart Home Provider Abstraction                 │
│  ┌──────────────┬──────────────┬──────────────┐            │
│  │ SmartThings  │ Home Asst.   │ Matter/Alexa │            │
│  └──────────────┴──────────────┴──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
smartthings-mcp-and-agent/
├── src/
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── logging.py                # Structured logging
│   ├── models/
│   │   ├── __init__.py
│   │   ├── device.py             # Device/capability models
│   │   ├── location.py           # Location/room models
│   │   └── schemas.py            # Pydantic schemas
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract SmartHomeProvider
│   │   ├── smartthings/
│   │   │   ├── __init__.py
│   │   │   ├── client.py         # SmartThings API client
│   │   │   ├── provider.py       # SmartThingsProvider implementation
│   │   │   └── models.py         # SmartThings-specific models
│   │   ├── home_assistant/
│   │   │   ├── __init__.py
│   │   │   └── provider.py       # Home Assistant stub
│   │   ├── matter/
│   │   │   ├── __init__.py
│   │   │   └── provider.py       # Matter stub
│   │   └── alexa/
│   │       ├── __init__.py
│   │       └── provider.py       # Alexa stub
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract LLMClient
│   │   ├── openai_client.py      # OpenAI implementation
│   │   ├── anthropic_client.py   # Anthropic implementation
│   │   └── ollama_client.py      # Local Ollama implementation
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent.py              # AI agent core
│   │   ├── prompts.py            # System prompts
│   │   └── tools.py              # Tool definitions
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py             # MCP server implementation
│       └── tools.py              # MCP tool definitions
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_providers.py
│   ├── test_agent.py
│   ├── test_mcp_server.py
│   └── test_llm_clients.py
├── docs/
│   ├── SETUP.md                  # SmartThings setup guide
│   ├── CONFIGURATION.md          # Configuration reference
│   ├── ADDING_PROVIDERS.md       # Guide for adding new providers
│   └── EXAMPLES.md               # Example commands
├── pyproject.toml
├── .env.example
├── LICENSE
├── README.md
└── .gitignore
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip or uv

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smartthings-mcp-and-agent.git
cd smartthings-mcp-and-agent

# Install in development mode
pip install -e ".[dev,mcp,llm-openai]"

# Copy environment template
cp .env.example .env
```

### Basic Usage

1. **Configure SmartThings credentials** (see [Setup Guide](docs/SETUP.md))
2. **Configure LLM provider** (see [Configuration](docs/CONFIGURATION.md))
3. **Start the MCP server**:

```python
from src.mcp_server.server import MCPServer
from src.config import Settings

settings = Settings()
server = MCPServer(settings)
await server.start()
```

4. **Use the agent for natural language control**:

```python
from src.agent.agent import SmartHomeAgent
from src.config import Settings

settings = Settings()
agent = SmartHomeAgent(settings)

# Natural language command
response = await agent.process_command("Turn on the living room lights")
print(response)
```

## 📦 Installation

### Standard Installation

```bash
# Core dependencies only
pip install smartthings-mcp-and-agent

# With MCP support
pip install smartthings-mcp-and-agent[mcp]

# With OpenAI LLM support
pip install smartthings-mcp-and-agent[llm-openai]

# With all features
pip install smartthings-mcp-and-agent[all]
```

### Development Installation

```bash
git clone https://github.com/yourusername/smartthings-mcp-and-agent.git
cd smartthings-mcp-and-agent
pip install -e ".[dev,all]"
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# SmartThings
SMARTTHINGS_PAT_TOKEN=your_token_here
SMARTTHINGS_API_URL=https://api.smartthings.com

# LLM Provider Selection
LLM_PROVIDER=openai  # or 'anthropic', 'ollama'
LLM_MODEL=gpt-4-turbo-preview

# OpenAI (if using OpenAI)
OPENAI_API_KEY=sk-...

# Anthropic (if using Anthropic)
ANTHROPIC_API_KEY=sk-ant-...

# Ollama (if using local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

See [CONFIGURATION.md](docs/CONFIGURATION.md) for detailed reference.

## 💻 Usage

### As an MCP Server

The server exposes smart home capabilities as MCP tools and resources:

```python
from src.mcp_server.server import MCPServer
from src.config import Settings

async def main():
    settings = Settings()
    server = MCPServer(settings)
    
    # Start server (connects to SmartThings, etc.)
    await server.start()
    
    # Server now exposes:
    # - Tools: list_devices, get_device_state, execute_command
    # - Resources: locations, rooms, devices, capabilities
```

### As an AI Agent

Control devices through natural language:

```python
from src.agent.agent import SmartHomeAgent
from src.config import Settings

async def main():
    settings = Settings()
    agent = SmartHomeAgent(settings)
    
    # Natural language control
    response = await agent.process_command(
        "Turn on the living room lights to 80%"
    )
    print(f"Agent: {response}")
```

### Supported Natural Language Commands

```
"Turn on the living room lights"
"Set bedroom temperature to 72 degrees"
"Turn off all lights in the house"
"Close the kitchen blinds"
"What devices are in the master bedroom?"
"Is the front door locked?"
"Unlock the front door"  # Requires confirmation
```

See [EXAMPLES.md](docs/EXAMPLES.md) for more examples.

## 🔧 Adding New Providers

To add a new smart home platform (e.g., Home Assistant, Matter):

1. **Implement the provider interface**:

```python
from src.providers.base import SmartHomeProvider
from src.models import Location, Device, DeviceState

class MyProviderName(SmartHomeProvider):
    async def authenticate(self) -> bool:
        """Authenticate with the provider"""
        pass
    
    async def list_locations(self) -> list[Location]:
        """List all locations"""
        pass
    
    async def list_rooms(self, location_id: str) -> list[Room]:
        """List rooms in a location"""
        pass
    
    async def list_devices(
        self, 
        location_id: str | None = None
    ) -> list[Device]:
        """List devices"""
        pass
    
    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get current device state"""
        pass
    
    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any]
    ) -> bool:
        """Execute a device command"""
        pass
```

2. **Register the provider in configuration**:

```python
# In src/config.py
PROVIDER_CLASSES = {
    'smartthings': SmartThingsProvider,
    'home_assistant': HomeAssistantProvider,  # Your new provider
}
```

See [ADDING_PROVIDERS.md](docs/ADDING_PROVIDERS.md) for detailed guide.

## 📚 API Reference

### SmartHomeProvider Interface

All providers implement this async interface:

```python
class SmartHomeProvider(ABC):
    """Base class for smart home ecosystem providers."""
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the provider."""
    
    @abstractmethod
    async def list_locations(self) -> list[Location]:
        """List all locations."""
    
    @abstractmethod
    async def list_rooms(self, location_id: str) -> list[Room]:
        """List rooms in a location."""
    
    @abstractmethod
    async def list_devices(
        self, 
        location_id: str | None = None
    ) -> list[Device]:
        """List devices, optionally filtered by location."""
    
    @abstractmethod
    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get the current state of a device."""
    
    @abstractmethod
    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] = {}
    ) -> bool:
        """Execute a command on a device."""
```

### MCP Tools

The MCP server exposes these tools:

- **list_devices**: Discover all devices
- **get_device_state**: Read current device state
- **execute_command**: Send commands to devices
- **list_locations**: Get location hierarchy
- **list_rooms**: Get rooms in a location

### Agent Methods

```python
class SmartHomeAgent:
    async def process_command(self, command: str) -> str:
        """Process a natural language command."""
    
    async def execute_mcp_tool(
        self,
        tool_name: str,
        tool_input: dict[str, Any]
    ) -> Any:
        """Execute an MCP tool directly."""
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_agent.py -v

# With asyncio debugging
pytest -v -s
```

### Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Formatting
black src/ tests/

# All checks
make lint  # (if Makefile available)
```

### Creating a Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in editable mode with all dev dependencies
pip install -e ".[dev,all]"

# Run tests to verify
pytest
```

## 🔐 Security Considerations

- **Never commit `.env` files** containing actual credentials
- **Use environment variables** for all secrets (PAT tokens, API keys)
- **Rotate credentials regularly**, especially for shared systems
- **Review SmartThings permissions** - only grant necessary capabilities
- **Destructive actions require confirmation** (configurable)
- **Use HTTPS** for webhook/API endpoints in production

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass and code is formatted
5. Submit a pull request

## 🐛 Reporting Issues

Found a bug or have a feature request?

- Check [existing issues](https://github.com/yourusername/smartthings-mcp-and-agent/issues)
- Create a detailed issue with:
  - Python version
  - Installed packages (`pip list`)
  - Reproducible steps
  - Error messages/logs

## 📖 Additional Documentation

- [Setup Guide for SmartThings](docs/SETUP.md) - OAuth/PAT configuration
- [Configuration Reference](docs/CONFIGURATION.md) - All environment variables
- [Adding New Providers](docs/ADDING_PROVIDERS.md) - Extend to new platforms
- [Example Commands](docs/EXAMPLES.md) - Natural language examples

---

**Built with ❤️ for the smart home community**
