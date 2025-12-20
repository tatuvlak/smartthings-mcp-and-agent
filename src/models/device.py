"""Data models for smart home devices, locations, and capabilities."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeviceType(str, Enum):
    """Supported device types."""

    LIGHT = "light"
    SWITCH = "switch"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    SENSOR = "sensor"
    CAMERA = "camera"
    BLINDS = "blinds"
    PLUG = "plug"
    FAN = "fan"
    OTHER = "other"


class CapabilityType(str, Enum):
    """Standard device capability types."""

    SWITCH = "switch"
    LEVEL = "switchLevel"
    COLOR_CONTROL = "colorControl"
    COLOR_TEMPERATURE = "colorTemperature"
    TEMPERATURE_MEASUREMENT = "temperatureMeasurement"
    HUMIDITY_MEASUREMENT = "humiditMeasurement"
    MOTION_SENSOR = "motionSensor"
    CONTACT_SENSOR = "contactSensor"
    LOCK = "lock"
    BATTERY = "battery"
    POWER_CONSUMPTION = "powerConsumption"
    OTHER = "other"


@dataclass
class Location:
    """Represents a physical location (e.g., home, office)."""

    id: str
    name: str
    country_code: str | None = None
    timezone: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"Location(id={self.id}, name={self.name})"


@dataclass
class Room:
    """Represents a room in a location."""

    id: str
    name: str
    location_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"Room(id={self.id}, name={self.name}, location={self.location_id})"


@dataclass
class Capability:
    """Represents a device capability (e.g., switch, level control)."""

    type: CapabilityType
    commands: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"Capability(type={self.type.value}, commands={self.commands})"


@dataclass
class Device:
    """Represents a smart home device."""

    id: str
    name: str
    device_type: DeviceType
    location_id: str
    room_id: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    capabilities: list[Capability] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"Device(id={self.id}, name={self.name}, type={self.device_type.value})"

    def get_capability(self, capability_type: CapabilityType) -> Capability | None:
        """Get a specific capability by type.
        
        Args:
            capability_type: The capability type to find
            
        Returns:
            The capability if found, None otherwise
        """
        for cap in self.capabilities:
            if cap.type == capability_type:
                return cap
        return None

    def has_capability(self, capability_type: CapabilityType) -> bool:
        """Check if device has a capability.
        
        Args:
            capability_type: The capability type to check
            
        Returns:
            True if device has the capability, False otherwise
        """
        return self.get_capability(capability_type) is not None


@dataclass
class DeviceState:
    """Represents the current state of a device."""

    device_id: str
    timestamp: str
    state: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"DeviceState(device_id={self.device_id}, timestamp={self.timestamp})"

    def get_attribute(self, attribute: str) -> Any:
        """Get a state attribute.
        
        Args:
            attribute: The attribute name
            
        Returns:
            The attribute value, or None if not found
        """
        return self.state.get(attribute)


@dataclass
class CommandResult:
    """Represents the result of executing a device command."""

    device_id: str
    success: bool
    message: str = ""
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        status = "success" if self.success else "failed"
        return f"CommandResult(device={self.device_id}, {status})"
