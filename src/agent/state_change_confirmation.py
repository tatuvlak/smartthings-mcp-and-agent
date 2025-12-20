"""State-changing action confirmation middleware.

This module implements the confirmation and expiry logic for state-changing
SmartThings API operations (create, update, delete operations on entities).

Device commands (e.g., turn on/off) do NOT require confirmation and bypass this layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from src.logging import get_logger

logger = get_logger(__name__)


class ActionCategory(Enum):
    """Categorization of MCP tool actions."""
    READ_ONLY = "read_only"               # list_*, get_* (no changes)
    DEVICE_COMMAND = "device_command"     # execute_command (allowed without confirmation)
    STATE_CHANGING = "state_changing"     # create_*, update_*, delete_* (requires confirmation)


class ConfirmationState(Enum):
    """Lifecycle states of a pending confirmation."""
    PENDING = "pending"                   # Waiting for user confirmation
    CONFIRMED = "confirmed"               # User explicitly confirmed
    EXPIRED = "expired"                   # Confirmation window closed
    CANCELLED = "cancelled"               # User cancelled or took different action
    EXECUTED = "executed"                 # Action has been executed


@dataclass
class PendingAction:
    """Represents a state-changing action awaiting user confirmation."""
    
    action_id: str                          # Unique ID for tracking
    action_type: str                        # e.g., "create_room", "delete_scene"
    category: ActionCategory                # READ_ONLY, DEVICE_COMMAND, or STATE_CHANGING
    entity_type: str                        # e.g., "room", "scene", "rule", "location"
    entity_id: Optional[str] = None         # ID of entity being modified (None for create)
    entity_name: Optional[str] = None       # Human-readable name
    parameters: dict[str, Any] = field(default_factory=dict)  # Action parameters
    timestamp_requested: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: int = 60                   # How long confirmation is valid
    state: ConfirmationState = ConfirmationState.PENDING
    
    def is_expired(self) -> bool:
        """Check if confirmation has expired."""
        age = (datetime.utcnow() - self.timestamp_requested).total_seconds()
        return age > self.ttl_seconds
    
    def time_remaining(self) -> int:
        """Get seconds remaining before expiration."""
        age = (datetime.utcnow() - self.timestamp_requested).total_seconds()
        remaining = max(0, int(self.ttl_seconds - age))
        return remaining


class StateChangeConfirmationMiddleware:
    """Middleware that enforces double confirmation for state-changing actions.
    
    Design:
    - Tracks pending confirmations in a conversation-scoped state
    - Enforces automatic expiry of old confirmations
    - Blocks execution of state-changing actions without confirmation
    - Device commands bypass this layer entirely
    - Only ONE pending confirmation allowed at a time
    """
    
    def __init__(self, confirmation_ttl_seconds: int = 60):
        """Initialize the confirmation middleware.
        
        Args:
            confirmation_ttl_seconds: How long a pending confirmation stays valid (30-120s typical)
        """
        self.confirmation_ttl_seconds = confirmation_ttl_seconds
        self.pending_action: Optional[PendingAction] = None
        self._action_counter = 0
    
    def _generate_action_id(self) -> str:
        """Generate a unique action ID."""
        self._action_counter += 1
        return f"action_{self._action_counter}_{int(datetime.utcnow().timestamp() * 1000)}"
    
    def categorize_tool(self, tool_name: str) -> ActionCategory:
        """Determine the category of a tool.
        
        Returns:
            READ_ONLY, DEVICE_COMMAND, or STATE_CHANGING
        """
        # Device commands - exempt from confirmation
        if tool_name == "execute_command":
            return ActionCategory.DEVICE_COMMAND
        
        # Read-only tools
        if tool_name.startswith("list_") or tool_name.startswith("get_"):
            return ActionCategory.READ_ONLY
        
        # State-changing tools
        if tool_name.startswith("create_") or \
           tool_name.startswith("update_") or \
           tool_name.startswith("delete_"):
            return ActionCategory.STATE_CHANGING
        
        # Default to read-only for unknown tools
        logger.warning(f"Unknown tool category for {tool_name}, treating as read-only")
        return ActionCategory.READ_ONLY
    
    def extract_entity_info(self, tool_name: str, tool_input: dict[str, Any]) -> tuple[str, Optional[str], Optional[str]]:
        """Extract entity type, ID, and name from tool call.
        
        Returns:
            (entity_type, entity_id, entity_name)
        """
        # Extract from tool name: create_room → room, delete_scene → scene
        parts = tool_name.split("_")
        entity_type = "_".join(parts[1:]) if len(parts) > 1 else "entity"
        
        # Extract ID - look for common ID field names
        entity_id = tool_input.get("id") or \
                   tool_input.get("room_id") or \
                   tool_input.get("scene_id") or \
                   tool_input.get("rule_id") or \
                   tool_input.get("location_id") or \
                   tool_input.get("device_id") or \
                   None
        
        # Extract name
        entity_name = tool_input.get("name") or \
                     tool_input.get("room_name") or \
                     tool_input.get("scene_name") or \
                     None
        
        return (entity_type, entity_id, entity_name)
    
    def request_confirmation(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        description: str = ""
    ) -> PendingAction:
        """Register a state-changing action and request user confirmation.
        
        Args:
            tool_name: Name of the MCP tool
            tool_input: Input parameters
            description: Human-readable description of the action
            
        Returns:
            PendingAction object with confirmation request
            
        Raises:
            ValueError: If attempting to register while another confirmation is pending
        """
        # Cancel any existing pending action
        if self.pending_action and self.pending_action.state == ConfirmationState.PENDING:
            logger.warning(
                "Cancelling existing pending action to register new one",
                previous_action=self.pending_action.action_id,
                new_action_type=tool_name
            )
            self.pending_action.state = ConfirmationState.CANCELLED
        
        # Extract entity information
        entity_type, entity_id, entity_name = self.extract_entity_info(tool_name, tool_input)
        
        # Create pending action
        action_id = self._generate_action_id()
        pending_action = PendingAction(
            action_id=action_id,
            action_type=tool_name,
            category=ActionCategory.STATE_CHANGING,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            parameters=tool_input,
            ttl_seconds=self.confirmation_ttl_seconds,
        )
        
        self.pending_action = pending_action
        
        logger.info(
            "State-changing action registered for confirmation",
            action_id=action_id,
            action_type=tool_name,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        
        return pending_action
    
    def has_pending_confirmation(self) -> bool:
        """Check if there's an active pending confirmation."""
        if self.pending_action is None:
            return False
        
        if self.pending_action.state != ConfirmationState.PENDING:
            return False
        
        if self.pending_action.is_expired():
            logger.warning(
                "Pending confirmation expired",
                action_id=self.pending_action.action_id,
                time_remaining=self.pending_action.time_remaining()
            )
            self.pending_action.state = ConfirmationState.EXPIRED
            return False
        
        return True
    
    def get_pending_action(self) -> Optional[PendingAction]:
        """Get the current pending action, if any and if still valid.
        
        Returns:
            PendingAction if one is pending and not expired, None otherwise
        """
        if not self.has_pending_confirmation():
            return None
        
        return self.pending_action
    
    def confirm_pending_action(self) -> tuple[bool, str]:
        """Confirm the pending action and allow execution.
        
        Returns:
            (success: bool, message: str)
        """
        if not self.has_pending_confirmation():
            return (False, "No pending confirmation to confirm")
        
        if self.pending_action.is_expired():
            self.pending_action.state = ConfirmationState.EXPIRED
            return (False, f"Confirmation expired. It was valid for {self.pending_action.ttl_seconds}s.")
        
        self.pending_action.state = ConfirmationState.CONFIRMED
        logger.info(
            "Pending action confirmed by user",
            action_id=self.pending_action.action_id,
            action_type=self.pending_action.action_type
        )
        return (True, "Confirmation accepted. Proceeding with action execution.")
    
    def cancel_pending_action(self, reason: str = "User cancelled") -> None:
        """Cancel the pending action (called if user takes different action).
        
        Args:
            reason: Why the action was cancelled
        """
        if self.pending_action:
            self.pending_action.state = ConfirmationState.CANCELLED
            logger.info(
                "Pending action cancelled",
                action_id=self.pending_action.action_id,
                reason=reason
            )
    
    def mark_action_executed(self) -> None:
        """Mark the confirmed action as executed."""
        if self.pending_action:
            self.pending_action.state = ConfirmationState.EXECUTED
            logger.info(
                "Action executed",
                action_id=self.pending_action.action_id,
                action_type=self.pending_action.action_type
            )
    
    def get_confirmation_prompt(self, pending_action: PendingAction) -> str:
        """Generate a user-friendly confirmation prompt.
        
        Args:
            pending_action: The action to confirm
            
        Returns:
            Human-readable confirmation message
        """
        entity_desc = f"'{pending_action.entity_name}' ({pending_action.entity_type})" \
                     if pending_action.entity_name else f"{pending_action.entity_type}"
        
        if pending_action.entity_id:
            entity_desc += f" [ID: {pending_action.entity_id}]"
        
        action_verb = "Create"
        if "update" in pending_action.action_type:
            action_verb = "Update"
        elif "delete" in pending_action.action_type:
            action_verb = "Delete"
        
        prompt = f"""
CONFIRMATION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Action: {action_verb} {entity_desc}

Details:
{chr(10).join(f"  • {k}: {v}" for k, v in pending_action.parameters.items() if k not in ['id', 'name'])}

Time remaining: {pending_action.time_remaining()} seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To proceed, please EXPLICITLY confirm:
  "Yes, confirm this action" or "I confirm"

To cancel, say anything else (e.g., "Never mind", "Cancel", etc.)
"""
        return prompt.strip()


class ConfirmationStateManager:
    """Manages confirmation state across potentially multiple conversations."""
    
    def __init__(self):
        """Initialize the state manager."""
        self.conversation_middleware: dict[str, StateChangeConfirmationMiddleware] = {}
    
    def get_middleware(self, conversation_id: str, confirmation_ttl_seconds: int = 60) -> StateChangeConfirmationMiddleware:
        """Get or create middleware for a conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            confirmation_ttl_seconds: TTL for confirmations in this conversation
            
        Returns:
            StateChangeConfirmationMiddleware for the conversation
        """
        if conversation_id not in self.conversation_middleware:
            self.conversation_middleware[conversation_id] = StateChangeConfirmationMiddleware(
                confirmation_ttl_seconds=confirmation_ttl_seconds
            )
        return self.conversation_middleware[conversation_id]
    
    def cleanup_conversation(self, conversation_id: str) -> None:
        """Clean up state for a conversation that's ending.
        
        Args:
            conversation_id: Conversation to clean up
        """
        if conversation_id in self.conversation_middleware:
            middleware = self.conversation_middleware[conversation_id]
            if middleware.pending_action and middleware.pending_action.state == ConfirmationState.PENDING:
                middleware.cancel_pending_action("Conversation ended")
            del self.conversation_middleware[conversation_id]
            logger.info("Cleaned up confirmation state", conversation_id=conversation_id)
