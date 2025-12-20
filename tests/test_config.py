"""Unit tests for configuration."""

import pytest

from src.config import Settings


def test_default_settings():
    """Test settings with defaults."""
    settings = Settings(smartthings_pat_token="test_token")
    assert settings.smartthings_pat_token == "test_token"
    assert settings.llm_provider == "openai"
    assert settings.agent_confirmation_required is True


def test_get_enabled_providers():
    """Test getting enabled providers."""
    settings = Settings(
        smartthings_pat_token="test",
        enabled_providers="smartthings, home_assistant",
    )
    providers = settings.get_enabled_providers()
    assert "smartthings" in providers
    assert "home_assistant" in providers
    assert len(providers) == 2


def test_empty_providers():
    """Test with no enabled providers."""
    settings = Settings(
        smartthings_pat_token="test",
        enabled_providers="",
    )
    providers = settings.get_enabled_providers()
    assert len(providers) == 0


def test_settings_from_dict():
    """Test creating settings from dict."""
    config = {
        "smartthings_pat_token": "token123",
        "llm_provider": "anthropic",
        "anthropic_api_key": "sk-ant-123",
    }
    settings = Settings(**config)
    assert settings.smartthings_pat_token == "token123"
    assert settings.llm_provider == "anthropic"
    assert settings.anthropic_api_key == "sk-ant-123"
