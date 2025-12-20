# Configuration Reference

Complete reference for all environment variables and configuration options.

## Environment Variables

### SmartThings Configuration

```env
# Personal Access Token for SmartThings API
SMARTTHINGS_PAT_TOKEN=your_token_here

# SmartThings API base URL (usually default)
SMARTTHINGS_API_URL=https://api.smartthings.com

# Webhook URL for receiving device events (optional)
SMARTTHINGS_WEBHOOK_URL=https://your-domain.com/webhook
```

### LLM Provider Selection

```env
# Which LLM provider to use
# Options: openai, anthropic, ollama
LLM_PROVIDER=openai

# Model name for the selected provider
# OpenAI: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
# Anthropic: claude-3-sonnet-20240229, claude-3-opus-20240229
# Ollama: llama2, mistral, etc (local models)
LLM_MODEL=gpt-4-turbo-preview
```

### OpenAI Configuration

```env
# OpenAI API key
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-...

# Optional: Override model for OpenAI
# OPENAI_MODEL=gpt-4-turbo-preview
```

### Anthropic Configuration

```env
# Anthropic API key
# Get from: https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Override model for Anthropic
# ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

### Ollama Configuration (Local LLM)

```env
# URL where Ollama is running
OLLAMA_BASE_URL=http://localhost:11434

# Model name to use
# Popular options: llama2, mistral, neural-chat, dolphin-phi
OLLAMA_MODEL=llama2
```

### MCP Server Configuration

```env
# Host to bind MCP server to
MCP_SERVER_HOST=127.0.0.1

# Port to run MCP server on
MCP_SERVER_PORT=8000
```

### Agent Configuration

```env
# Whether to require confirmation for destructive actions
AGENT_CONFIRMATION_REQUIRED=true

# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
AGENT_LOG_LEVEL=INFO
```

### Multiple Providers

```env
# Comma-separated list of enabled providers
# Currently supported: smartthings
# Future: home_assistant, matter, alexa
ENABLED_PROVIDERS=smartthings
```

### Home Assistant Configuration (Stub)

```env
# Home Assistant instance URL
HOME_ASSISTANT_BASE_URL=http://localhost:8123

# Long-lived access token
# Create in Home Assistant Settings > Devices & Services > Tokens
HOME_ASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Matter Configuration (Stub)

```env
# Matter controller URL
MATTER_CONTROLLER_URL=http://localhost:5580

# Matter admin PIN for device pairing
MATTER_ADMIN_PIN=12345
```

### Alexa Configuration (Stub)

```env
# Amazon Alexa OAuth credentials
ALEXA_CLIENT_ID=your_client_id
ALEXA_CLIENT_SECRET=your_client_secret
ALEXA_REFRESH_TOKEN=your_refresh_token
```

## Python Configuration

You can also configure settings programmatically:

```python
from src.config import Settings

# Load from environment
settings = Settings()

# Or create with explicit values
settings = Settings(
    smartthings_pat_token="your_token",
    llm_provider="openai",
    openai_api_key="sk-...",
)

# Access settings
print(settings.llm_model)
print(settings.get_enabled_providers())
```

## LLM Configuration Details

### OpenAI

Recommended models:
- `gpt-4-turbo-preview` - Most capable (recommended)
- `gpt-4` - Stable GPT-4 version
- `gpt-3.5-turbo` - Faster, more economical

Cost: See [OpenAI Pricing](https://openai.com/pricing)

### Anthropic

Recommended models:
- `claude-3-opus-20240229` - Most capable
- `claude-3-sonnet-20240229` - Balanced (recommended)
- `claude-3-haiku-20240307` - Fastest

Cost: See [Anthropic Pricing](https://www.anthropic.com/pricing)

### Ollama (Local)

Free, runs locally. Popular models:
- `llama2` - General purpose (6B, 7B, 13B, 70B variants)
- `mistral` - Fast and capable
- `neural-chat` - Optimized for chat
- `orca-mini` - Smaller model for resource-constrained systems

Requirements:
- Ollama installed (https://ollama.ai)
- Sufficient disk space for model (varies, 4-40GB+)
- GPU optional but recommended

## Configuration Loading Order

Settings are loaded in this order (later overrides earlier):
1. Default values from `Settings` class
2. Environment variables from system
3. Variables from `.env` file
4. Explicit Python instantiation

## Validation

The application validates configuration on startup:

```python
from src.config import Settings

try:
    settings = Settings()
    # Check if required fields are set
    if not settings.smartthings_pat_token:
        raise ValueError("SMARTTHINGS_PAT_TOKEN not configured")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Example Configurations

### Local Development (with OpenAI)

```env
SMARTTHINGS_PAT_TOKEN=your_token
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
AGENT_LOG_LEVEL=DEBUG
```

### Production (with Anthropic)

```env
SMARTTHINGS_PAT_TOKEN=your_token
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
AGENT_LOG_LEVEL=INFO
AGENT_CONFIRMATION_REQUIRED=true
```

### Offline (Local Ollama)

```env
SMARTTHINGS_PAT_TOKEN=your_token
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### Multi-Provider Setup

```env
SMARTTHINGS_PAT_TOKEN=your_token
HOME_ASSISTANT_BASE_URL=http://localhost:8123
HOME_ASSISTANT_TOKEN=eyJhbGciOiJIUzI1NiIs...
ENABLED_PROVIDERS=smartthings,home_assistant
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

## Troubleshooting

### Settings not loading
- Verify `.env` file exists and is readable
- Check environment variable names are correct (case-insensitive)
- Restart Python process after changing `.env`

### API key errors
- Ensure keys have correct format for provider
- Verify keys haven't expired
- Check API key permissions/scopes

### Connection errors
- Verify URLs are correct and reachable
- Check firewall/proxy settings
- Ensure API keys have network access

## Security Notes

- **Never commit `.env` to version control** - Add to `.gitignore`
- **Rotate API keys regularly** - Generate new keys periodically
- **Use separate keys for environments** - Dev, staging, production
- **Monitor API usage** - Check provider dashboards for unusual activity
- **Log sensitive data carefully** - API keys should not appear in logs

## Advanced Configuration

For complex deployments, you can extend Settings:

```python
from src.config import Settings
from pydantic_settings import SettingsConfigDict

class CustomSettings(Settings):
    # Add custom fields
    custom_field: str = "default"
    
    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
    )
```
