"""ReAct-enforced state tracking for smart home agent.

This module provides middleware-level enforcement of the ReAct (Reasoning + Acting) pattern,
ensuring that device commands are only executed after proper state observations.

MANDATORY PRE-ACTION CHECKS:
1. Device metadata must be retrieved FIRST (GET /devices/{id})
2. Device status must be retrieved SECOND (GET /devices/{id}/status)
3. Only then can commands be executed

These checks are enforced at the middleware level, not just prompted.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Any

from src.logging import get_logger

logger = get_logger(__name__)


class ActionType(Enum):
    """Types of actions the agent can take."""
    QUERY_METADATA = "query_metadata"       # GET /devices/{id}
    QUERY_STATUS = "query_status"           # GET /devices/{id}/status
    QUERY_DEVICE = "query_device"           # list_devices, resolve_device
    OBSERVE_STATE = "observe_state"         # get_device_state
    EXECUTE_COMMAND = "execute_command"     # execute_command
    LIST_LOCATIONS = "list_locations"       # list_locations
    CLARIFY = "clarify"                     # ask user for clarification


class ObservationType(Enum):
    """Types of observations from tool execution."""
    DEVICE_LIST = "device_list"             # Result from list_devices
    DEVICE_RESOLVED = "device_resolved"     # Result from resolve_device
    DEVICE_STATE = "device_state"           # Result from get_device_state
    LOCATION_LIST = "location_list"         # Result from list_locations
    ERROR = "error"                         # Tool execution error
    NONE = "none"                           # No observation yet


@dataclass
class DeviceObservation:
    """Captures a device state observation for ReAct reasoning."""
    
    device_id: str
    device_name: str
    observation_type: ObservationType
    timestamp: datetime
    
    # Device state details
    capabilities: list[str] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    is_offline: bool = False
    location_id: Optional[str] = None
    
    def is_stale(self, max_age_seconds: int = 60) -> bool:
        """Check if observation is stale."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > max_age_seconds
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if device has a specific capability."""
        return capability_name.lower() in [c.lower() for c in self.capabilities]


@dataclass
class DeviceMetadata:
    """Captures device metadata from GET /devices/{id}."""
    
    device_id: str
    device_name: str
    timestamp: datetime
    
    # Metadata fields
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    device_type: Optional[str] = None
    capabilities: list[str] = field(default_factory=list)
    location_id: Optional[str] = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)
    
    def is_stale(self, max_age_seconds: int = 60) -> bool:
        """Check if metadata is stale."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > max_age_seconds
    
    def has_capability(self, capability_name: str) -> bool:
        """Check if device has a specific capability."""
        return capability_name.lower() in [c.lower() for c in self.capabilities]


@dataclass
class DeviceStatus:
    """Captures device status from GET /devices/{id}/status."""
    
    device_id: str
    device_name: str
    timestamp: datetime
    
    # Status fields
    status: dict[str, Any] = field(default_factory=dict)
    is_online: bool = True
    raw_status: dict[str, Any] = field(default_factory=dict)
    
    def is_stale(self, max_age_seconds: int = 60) -> bool:
        """Check if status is stale."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > max_age_seconds


@dataclass
class ReActState:
    """Tracks ReAct reasoning state for the current conversation."""
    
    # Latest action taken
    last_action_type: ActionType = ActionType.QUERY_DEVICE
    last_action_time: Optional[datetime] = None
    
    # Latest observation
    last_observation_type: ObservationType = ObservationType.NONE
    last_observation_time: Optional[datetime] = None
    last_device_observed: Optional[DeviceObservation] = None
    
    # Device observation history (keyed by device_id)
    device_observations: dict[str, DeviceObservation] = field(default_factory=dict)
    
    # PRE-ACTION CHECK TRACKING: Metadata and Status (NEW)
    device_metadata: dict[str, DeviceMetadata] = field(default_factory=dict)
    device_status: dict[str, DeviceStatus] = field(default_factory=dict)
    
    # Conversation context
    conversation_id: str = ""
    current_user_intent: str = ""
    
    def reset_for_new_intent(self) -> None:
        """Reset state for a new user intent."""
        self.last_action_type = ActionType.QUERY_DEVICE
        self.last_action_time = None
        self.last_observation_type = ObservationType.NONE
        self.last_observation_time = None
        self.last_device_observed = None
        # Keep device_observations for context, but mark as potentially stale
    
    def record_action(self, action_type: ActionType) -> None:
        """Record that an action was taken."""
        self.last_action_type = action_type
        self.last_action_time = datetime.utcnow()
        logger.debug(f"ReAct action recorded: {action_type.value}")
    
    def record_observation(self, obs: DeviceObservation) -> None:
        """Record a device state observation."""
        self.last_observation_type = obs.observation_type
        self.last_observation_time = datetime.utcnow()
        self.last_device_observed = obs
        self.device_observations[obs.device_id] = obs
        logger.debug(
            f"ReAct observation recorded: device={obs.device_name}, type={obs.observation_type.value}"
        )
    
    def record_metadata(self, metadata: DeviceMetadata) -> None:
        """Record device metadata from GET /devices/{id}."""
        self.device_metadata[metadata.device_id] = metadata
        logger.debug(
            f"ReAct metadata recorded: device={metadata.device_name}, "
            f"capabilities={','.join(metadata.capabilities)}"
        )
    
    def record_status(self, status: DeviceStatus) -> None:
        """Record device status from GET /devices/{id}/status."""
        self.device_status[status.device_id] = status
        logger.debug(
            f"ReAct status recorded: device={status.device_name}, online={status.is_online}"
        )
    
    def get_device_observation(self, device_id: str) -> Optional[DeviceObservation]:
        """Get the most recent observation for a device."""
        return self.device_observations.get(device_id)
    
    def get_device_metadata(self, device_id: str) -> Optional[DeviceMetadata]:
        """Get the most recent metadata for a device."""
        return self.device_metadata.get(device_id)
    
    def get_device_status(self, device_id: str) -> Optional[DeviceStatus]:
        """Get the most recent status for a device."""
        return self.device_status.get(device_id)


class ReActEnforcer:
    """Enforces ReAct pattern adherence at the middleware level.
    
    MANDATORY PRE-ACTION CHECKS:
    Before ANY device command, the following MUST be true:
    1. Device metadata has been retrieved (GET /devices/{id})
    2. Device status has been retrieved (GET /devices/{id}/status)
    3. Both must be fresh (< max_observation_age_seconds old)
    4. Device must have the requested capability
    5. Device must be online
    6. Device must not be read-only (sensor-only)
    """
    
    def __init__(self, max_observation_age_seconds: int = 60):
        """Initialize the enforcer.
        
        Args:
            max_observation_age_seconds: How long metadata/status is valid before being stale
        """
        self.state = ReActState()
        self.max_observation_age = max_observation_age_seconds
        self.safety_critical_commands = {
            "unlock", "lock", "disarm", "arm", "delete", "clear",
            "shutdown", "restart", "factory_reset", "drain"
        }
    
    # ========== NEW: PRE-ACTION CHECK VALIDATION ==========
    
    def has_metadata_retrieved(self, device_id: str) -> tuple[bool, str]:
        """Check if device metadata has been retrieved.
        
        Returns:
            (has_metadata: bool, reason: str)
        """
        metadata = self.state.get_device_metadata(device_id)
        if metadata is None:
            return (
                False,
                f"Device metadata not yet retrieved. "
                f"First call: GET /devices/{device_id} to retrieve device metadata (name, capabilities, etc.)"
            )
        
        if metadata.is_stale(self.max_observation_age):
            return (
                False,
                f"Device metadata is stale (> {self.max_observation_age}s). "
                f"Refresh metadata with: GET /devices/{device_id}"
            )
        
        return (True, "Metadata retrieved and fresh")
    
    def has_status_retrieved(self, device_id: str) -> tuple[bool, str]:
        """Check if device status has been retrieved.
        
        Returns:
            (has_status: bool, reason: str)
        """
        status = self.state.get_device_status(device_id)
        if status is None:
            return (
                False,
                f"Device status not yet retrieved. "
                f"Second call: GET /devices/{device_id}/status to retrieve device state and connectivity"
            )
        
        if status.is_stale(self.max_observation_age):
            return (
                False,
                f"Device status is stale (> {self.max_observation_age}s). "
                f"Refresh status with: GET /devices/{device_id}/status"
            )
        
        return (True, "Status retrieved and fresh")
    
    def validate_prerequisites(self, device_id: str) -> tuple[bool, str]:
        """Validate that BOTH metadata and status have been retrieved.
        
        MUST BE CALLED before any command execution.
        
        Returns:
            (prerequisites_met: bool, reason: str)
        """
        # Check metadata first
        has_meta, meta_reason = self.has_metadata_retrieved(device_id)
        if not has_meta:
            return (False, meta_reason)
        
        # Check status second
        has_status, status_reason = self.has_status_retrieved(device_id)
        if not has_status:
            return (False, status_reason)
        
        return (True, "All prerequisites met: metadata and status retrieved")
    
    # ========== EXISTING: COMMAND EXECUTION GUARDS ==========
    
    def can_execute_command(
        self,
        device_id: str,
        command_name: str,
        capability_name: str,
    ) -> tuple[bool, str]:
        """Check if a command can be executed given current ReAct state.
        
        ENFORCES MANDATORY PRE-ACTION CHECKS:
        1. Metadata must be retrieved
        2. Status must be retrieved
        3. Observation must be fresh
        4. Device must have capability
        5. Device must be online
        6. Device must not be read-only
        
        Returns:
            (allowed: bool, reason: str)
        """
        # NEW: Check prerequisites (metadata and status)
        has_prereqs, prereq_reason = self.validate_prerequisites(device_id)
        if not has_prereqs:
            return (False, prereq_reason)
        
        # Rule 1: Must have prior device state observation
        device_obs = self.state.get_device_observation(device_id)
        if device_obs is None:
            return (
                False,
                f"Cannot execute command: No prior state observation for device {device_id}. "
                f"Query device status first with get_device_state."
            )
        
        # Rule 2: Observation must be fresh
        if device_obs.is_stale(self.max_observation_age):
            return (
                False,
                f"Cannot execute command: Device observation is stale (> {self.max_observation_age}s). "
                f"Refresh device status before executing command."
            )
        
        # Rule 3: Device must have the capability
        if not device_obs.has_capability(capability_name):
            available = ", ".join(device_obs.capabilities) if device_obs.capabilities else "none"
            return (
                False,
                f"Cannot execute command: Device '{device_obs.device_name}' does not have "
                f"capability '{capability_name}'. Available: {available}"
            )
        
        # Rule 4: Device must be online
        if device_obs.is_offline:
            return (
                False,
                f"Cannot execute command: Device '{device_obs.device_name}' is offline. "
                f"Cannot send commands to offline devices."
            )
        
        # Rule 5: Read-only devices (sensors) cannot receive commands
        read_only_types = {"motionSensor", "temperatureSensor", "humiditySensor", "battery"}
        if device_obs.capabilities and all(
            cap in read_only_types for cap in device_obs.capabilities
        ):
            return (
                False,
                f"Cannot execute command: Device '{device_obs.device_name}' is read-only (sensor). "
                f"Cannot send commands to sensor-only devices."
            )
        
        return (True, "Command execution allowed by ReAct guards")
    
    def requires_confirmation(self, device_id: str, command_name: str) -> bool:
        """Check if a command requires user confirmation."""
        command_lower = command_name.lower()
        return any(critical in command_lower for critical in self.safety_critical_commands)
    
    def validate_command_for_device(
        self,
        device_id: str,
        command_name: str,
        capability_name: str,
    ) -> tuple[bool, str, bool]:
        """Full validation of command execution.
        
        Returns:
            (allowed: bool, reason: str, requires_confirmation: bool)
        """
        allowed, reason = self.can_execute_command(device_id, command_name, capability_name)
        requires_conf = self.requires_confirmation(device_id, command_name) if allowed else False
        return (allowed, reason, requires_conf)
