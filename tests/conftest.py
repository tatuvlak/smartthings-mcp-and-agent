"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_location():
    """Fixture providing a sample location."""
    from src.models.device import Location

    return Location(
        id="loc-1",
        name="Home",
        timezone="America/New_York",
        country_code="US",
    )


@pytest.fixture
def sample_device():
    """Fixture providing a sample device."""
    from src.models.device import Device, DeviceType, Capability, CapabilityType

    return Device(
        id="device-1",
        name="Living Room Light",
        device_type=DeviceType.LIGHT,
        location_id="loc-1",
        room_id="room-1",
        capabilities=[
            Capability(type=CapabilityType.SWITCH, commands=["on", "off"]),
            Capability(type=CapabilityType.LEVEL, commands=["setLevel"]),
        ],
        state={"switch": "on", "level": 80},
    )


@pytest.fixture
def settings():
    """Fixture providing test settings."""
    from src.config import Settings

    return Settings(
        smartthings_pat_token="test_token",
        llm_provider="ollama",
        enabled_providers="",  # No providers for unit tests
    )
