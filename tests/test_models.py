"""Unit tests for data models."""

import pytest

from src.models.device import (
    CapabilityType,
    Device,
    DeviceState,
    DeviceType,
    Location,
    Room,
)


def test_location_creation():
    """Test creating a location."""
    loc = Location(id="loc-1", name="Home")
    assert loc.id == "loc-1"
    assert loc.name == "Home"
    assert "loc-1" in str(loc)


def test_room_creation(sample_location):
    """Test creating a room."""
    room = Room(
        id="room-1",
        name="Living Room",
        location_id=sample_location.id,
    )
    assert room.id == "room-1"
    assert room.name == "Living Room"
    assert room.location_id == sample_location.id


def test_device_creation(sample_device):
    """Test creating a device."""
    assert sample_device.id == "device-1"
    assert sample_device.name == "Living Room Light"
    assert sample_device.device_type == DeviceType.LIGHT
    assert len(sample_device.capabilities) == 2


def test_device_get_capability(sample_device):
    """Test getting capability by type."""
    cap = sample_device.get_capability(CapabilityType.SWITCH)
    assert cap is not None
    assert cap.type == CapabilityType.SWITCH
    assert "on" in cap.commands


def test_device_has_capability(sample_device):
    """Test checking if device has capability."""
    assert sample_device.has_capability(CapabilityType.SWITCH)
    assert sample_device.has_capability(CapabilityType.LEVEL)
    assert not sample_device.has_capability(CapabilityType.LOCK)


def test_device_state_creation():
    """Test creating device state."""
    state = DeviceState(
        device_id="device-1",
        timestamp="2025-01-01T12:00:00Z",
        state={"power": "on", "brightness": 80},
    )
    assert state.device_id == "device-1"
    assert state.get_attribute("power") == "on"
    assert state.get_attribute("brightness") == 80
    assert state.get_attribute("nonexistent") is None


def test_device_type_enum():
    """Test device type enum."""
    assert DeviceType.LIGHT.value == "light"
    assert DeviceType.SWITCH.value == "switch"
    assert DeviceType.THERMOSTAT.value == "thermostat"


def test_capability_type_enum():
    """Test capability type enum."""
    assert CapabilityType.SWITCH.value == "switch"
    assert CapabilityType.LEVEL.value == "switchLevel"
