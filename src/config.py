"""Configuration management for the smart home MCP server and agent."""

from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # SmartThings Configuration
    smartthings_pat_token: str = ""
    smartthings_api_url: str = "https://api.smartthings.com"
    smartthings_webhook_url: str = ""

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "ollama"] = "openai"
    llm_model: str = "gpt-4-turbo-preview"

    # OpenAI Configuration
    openai_api_key: str = ""

    # Anthropic Configuration
    anthropic_api_key: str = ""

    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"

    # MCP Server Configuration
    mcp_server_host: str = "127.0.0.1"
    mcp_server_port: int = 8000

    # Agent Configuration
    agent_confirmation_required: bool = True
    agent_log_level: str = "INFO"

    # Enabled Providers
    enabled_providers: str = "smartthings"  # comma-separated

    # Home Assistant Configuration
    home_assistant_base_url: str = ""
    home_assistant_token: str = ""

    # Matter Configuration
    matter_controller_url: str = ""
    matter_admin_pin: str = ""

    # Alexa Configuration
    alexa_client_id: str = ""
    alexa_client_secret: str = ""
    alexa_refresh_token: str = ""

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False

    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names."""
        providers = [p.strip() for p in self.enabled_providers.split(",")]
        return [p for p in providers if p]
