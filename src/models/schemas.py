"""Pydantic schemas for API and validation."""

from typing import Any

from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """Schema for location data."""

    id: str
    name: str
    country_code: str | None = None
    timezone: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"json_schema_extra": {"examples": [{"id": "loc-1", "name": "Home"}]}}


class RoomSchema(BaseModel):
    """Schema for room data."""

    id: str
    name: str
    location_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {"examples": [{"id": "room-1", "name": "Living Room", "location_id": "loc-1"}]}
    }


class CapabilitySchema(BaseModel):
    """Schema for device capability."""

    type: str
    commands: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "switch",
                    "commands": ["on", "off"],
                    "attributes": {"state": "on|off"},
                }
            ]
        }
    }


class DeviceSchema(BaseModel):
    """Schema for device data."""

    id: str
    name: str
    device_type: str
    location_id: str
    room_id: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    capabilities: list[CapabilitySchema] = Field(default_factory=list)
    state: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "device-1",
                    "name": "Living Room Light",
                    "device_type": "light",
                    "location_id": "loc-1",
                    "room_id": "room-1",
                    "capabilities": [{"type": "switch", "commands": ["on", "off"]}],
                    "state": {"switch": "on"},
                }
            ]
        }
    }


class DeviceStateSchema(BaseModel):
    """Schema for device state."""

    device_id: str
    timestamp: str
    state: dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "device_id": "device-1",
                    "timestamp": "2025-01-01T12:00:00Z",
                    "state": {"switch": "on", "level": 80},
                }
            ]
        }
    }


class CommandSchema(BaseModel):
    """Schema for device command."""

    device_id: str
    capability: str
    command: str
    arguments: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "device_id": "device-1",
                    "capability": "switch",
                    "command": "on",
                    "arguments": {},
                }
            ]
        }
    }


class CommandResultSchema(BaseModel):
    """Schema for command result."""

    device_id: str
    success: bool
    message: str = ""
    error: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "device_id": "device-1",
                    "success": True,
                    "message": "Command executed successfully",
                }
            ]
        }
    }


class AgentResponseSchema(BaseModel):
    """Schema for agent response."""

    success: bool
    message: str
    devices_affected: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Turned on the living room lights",
                    "devices_affected": ["device-1"],
                }
            ]
        }
    }
