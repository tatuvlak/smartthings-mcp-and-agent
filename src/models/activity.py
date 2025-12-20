"""Data models for SmartThings activity and event history."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ActivityType(str, Enum):
    """Types of activities that can be recorded."""

    DEVICE_COMMAND = "device_command"
    DEVICE_STATE_CHANGE = "device_state_change"
    USER_ACTION = "user_action"
    AUTOMATION_TRIGGER = "automation_trigger"
    APP_INTERACTION = "app_interaction"
    UNKNOWN = "unknown"


class ActivitySource(str, Enum):
    """Source of the activity."""

    DEVICE = "device"
    USER = "user"
    AUTOMATION = "automation"
    SYSTEM = "system"
    UNKNOWN = "unknown"


@dataclass
class ActivityChange:
    """Represents a change in device state (old value -> new value)."""

    attribute: str
    old_value: Any = None
    new_value: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"Change({self.attribute}: {self.old_value} -> {self.new_value})"


@dataclass
class Activity:
    """Represents a single activity/event in SmartThings history.
    
    This model normalizes SmartThings activity records into a consistent format.
    """

    id: str
    timestamp: str  # ISO 8601 format
    activity_type: ActivityType
    source: ActivitySource
    device_id: str | None = None
    location_id: str | None = None
    user_id: str | None = None
    capability: str | None = None
    command: str | None = None
    attribute: str | None = None
    changes: list[ActivityChange] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        location = f", location={self.location_id}" if self.location_id else ""
        device = f", device={self.device_id}" if self.device_id else ""
        return f"Activity(id={self.id}, type={self.activity_type.value}, timestamp={self.timestamp}{location}{device})"

    def has_value_change(self) -> bool:
        """Check if this activity represents a value change."""
        return len(self.changes) > 0

    def get_change(self, attribute: str) -> ActivityChange | None:
        """Get a specific change by attribute name.
        
        Args:
            attribute: The attribute name to find
            
        Returns:
            The ActivityChange if found, None otherwise
        """
        for change in self.changes:
            if change.attribute == attribute:
                return change
        return None

    def summary(self) -> str:
        """Get a human-readable summary of the activity.
        
        Returns:
            A string description of what happened
        """
        # If we have the raw API text summary, use it (most detailed)
        if self.metadata.get("text"):
            return self.metadata.get("text")
        
        # Otherwise, build a summary from available fields
        device_name = self.metadata.get("deviceName", self.device_id or "Unknown device")
        
        if self.activity_type == ActivityType.DEVICE_COMMAND:
            return f"{device_name} executed command {self.command}"
        elif self.activity_type == ActivityType.DEVICE_STATE_CHANGE:
            if self.changes:
                # Format: "Device turned on", "Brightness set to 75%", etc.
                if len(self.changes) == 1:
                    change = self.changes[0]
                    return f"{device_name} {self.capability or self.attribute or 'state'} changed to {change.new_value}"
                else:
                    changes_str = ", ".join(
                        f"{c.attribute}={c.new_value}" for c in self.changes
                    )
                    return f"{device_name} updated: {changes_str}"
            return f"{device_name} state changed"
        elif self.activity_type == ActivityType.USER_ACTION:
            return f"User {self.user_id} performed action"
        elif self.activity_type == ActivityType.AUTOMATION_TRIGGER:
            return "Automation was triggered"
        else:
            return f"Activity: {self.activity_type.value}"


@dataclass
class ActivityPage:
    """Represents a page of activity results with pagination info."""

    items: list[Activity]
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    has_more: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        return f"ActivityPage(items={len(self.items)}, total={self.total}, has_more={self.has_more})"
