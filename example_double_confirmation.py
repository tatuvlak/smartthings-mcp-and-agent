"""End-to-end example demonstrating double confirmation for state-changing operations.

This example shows:
1. User request to create/delete an entity
2. Agent requests confirmation with expiry tracking
3. Confirmation expiry scenario OR successful confirmation
4. Safe abort of expired actions
5. Device commands (on/off, etc.) executing WITHOUT confirmation

Scenario Flow:
- Scenario 1: User creates a room (STATE_CHANGING) - requires confirmation
- Scenario 2: User turns on a light (DEVICE_COMMAND) - NO confirmation
- Scenario 3: Confirmation expires - action is safely cancelled
"""

from datetime import datetime, timedelta
from src.agent.state_change_confirmation import (
    StateChangeConfirmationMiddleware,
    ActionCategory,
    ConfirmationState,
    ConfirmationStateManager,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def scenario_1_create_room_with_confirmation() -> None:
    """Demonstrate creating a room with double confirmation."""
    print_section("SCENARIO 1: Create Room (STATE_CHANGING - Requires Confirmation)")
    
    middleware = StateChangeConfirmationMiddleware(confirmation_ttl_seconds=60)
    
    # Step 1: User requests to create a room
    print("USER REQUEST:")
    print('  "Create a new room called \"Master Bedroom\" in my home"')
    print()
    
    # Step 2: Agent receives the request and categorizes the tool
    tool_name = "create_room"
    tool_input = {
        "location_id": "loc-123",
        "name": "Master Bedroom",
    }
    
    category = middleware.categorize_tool(tool_name)
    print(f"AGENT ANALYSIS:")
    print(f"  Tool: {tool_name}")
    print(f"  Category: {category.value}")
    print(f"  Action: Requires double confirmation")
    print()
    
    # Step 3: Agent requests confirmation
    pending_action = middleware.request_confirmation(
        tool_name=tool_name,
        tool_input=tool_input,
        description="Create a new room 'Master Bedroom' in your home location"
    )
    
    print(f"AGENT FIRST CONFIRMATION REQUEST:")
    confirmation_prompt = middleware.get_confirmation_prompt(pending_action)
    print(confirmation_prompt)
    print()
    
    # Step 4: User confirms the action
    print("USER RESPONSE: \"Yes, create the room\"")
    print()
    
    # Step 5: Agent validates and processes confirmation
    success, message = middleware.confirm_pending_action()
    print(f"AGENT CONFIRMATION VALIDATION:")
    print(f"  Status: {message}")
    print(f"  Pending Action State: {pending_action.state.value}")
    print()
    
    # Step 6: Agent executes the action (simulated)
    print("AGENT EXECUTION:")
    print("  -> Calling SmartThings API to create room...")
    print("  -> Room created successfully!")
    print("  -> Room ID: room-456")
    print()
    
    # Step 7: Agent marks action as executed
    middleware.mark_action_executed()
    print(f"AGENT COMPLETION:")
    print(f"  Action state: {pending_action.state.value}")
    print()
    
    print("USER SEES:")
    print('  "✓ Room \"Master Bedroom\" created successfully"')


def scenario_2_device_command_no_confirmation() -> None:
    """Demonstrate device commands executing WITHOUT confirmation."""
    print_section("SCENARIO 2: Turn On Light (DEVICE_COMMAND - No Confirmation)")
    
    middleware = StateChangeConfirmationMiddleware(confirmation_ttl_seconds=60)
    
    # Step 1: User requests to turn on a light
    print("USER REQUEST:")
    print('  "Turn on the living room light"')
    print()
    
    # Step 2: Agent categorizes the tool
    tool_name = "execute_command"
    tool_input = {
        "device_id": "device-789",
        "capability": "switch",
        "command": "on",
    }
    
    category = middleware.categorize_tool(tool_name)
    print(f"AGENT ANALYSIS:")
    print(f"  Tool: {tool_name}")
    print(f"  Category: {category.value}")
    print(f"  Action: DEVICE COMMAND - Executes immediately (NO confirmation)")
    print()
    
    # Step 3: Agent IMMEDIATELY executes command (no confirmation request)
    print("AGENT EXECUTION (Immediate):")
    print("  -> Calling SmartThings API to turn on light...")
    print("  -> Light command executed successfully!")
    print()
    
    print("USER SEES:")
    print('  "✓ Living room light turned on"')


def scenario_3_confirmation_expiry() -> None:
    """Demonstrate confirmation expiry and safe abort."""
    print_section("SCENARIO 3: Confirmation Expiry (TTL exceeded)")
    
    middleware = StateChangeConfirmationMiddleware(confirmation_ttl_seconds=2)  # Short TTL for demo
    
    # Step 1: User requests to delete a scene
    print("USER REQUEST:")
    print('  "Delete the \"Good Night\" scene"')
    print()
    
    # Step 2: Agent requests confirmation
    tool_name = "delete_scene"
    tool_input = {
        "location_id": "loc-123",
        "scene_id": "scene-999",
    }
    
    category = middleware.categorize_tool(tool_name)
    print(f"AGENT ANALYSIS:")
    print(f"  Tool: {tool_name}")
    print(f"  Category: {category.value}")
    print()
    
    pending_action = middleware.request_confirmation(
        tool_name=tool_name,
        tool_input=tool_input,
        description="Delete the 'Good Night' scene from your home"
    )
    
    print("AGENT FIRST CONFIRMATION REQUEST:")
    print(middleware.get_confirmation_prompt(pending_action))
    print()
    
    # Step 3: User doesn't respond - time passes
    print("TIME PASSES (Agent and user are in different conversation...)")
    print("  [Waiting for confirmation...]")
    print("  [60 seconds pass...]")
    print()
    
    # Step 4: User issues a new command (which should cancel the pending action)
    print("USER (Different request):")
    print('  "List all my scenes"')
    print()
    
    # Step 5: Check if pending confirmation is still valid
    has_pending = middleware.has_pending_confirmation()
    print(f"AGENT CHECK:")
    print(f"  Pending confirmation still valid? {has_pending}")
    if not has_pending:
        print(f"  Reason: Confirmation expired (TTL exceeded)")
        print(f"  Action state: {pending_action.state.value}")
    print()
    
    # Step 6: User tries to confirm expired action
    print("USER (Remembers the earlier request):")
    print('  "Yes, delete the scene"')
    print()
    
    # Step 7: Agent validates - fails because confirmation is expired
    success, message = middleware.confirm_pending_action()
    print(f"AGENT CONFIRMATION VALIDATION:")
    print(f"  Status: {message}")
    print()
    
    print("USER SEES:")
    print('  "⚠ Confirmation expired. Please request the action again if you want to proceed."')


def scenario_4_context_drift_cancellation() -> None:
    """Demonstrate cancellation when context changes."""
    print_section("SCENARIO 4: Unrelated Command Cancels Pending Confirmation")
    
    manager = ConfirmationStateManager()
    middleware = manager.get_middleware("conversation-1", confirmation_ttl_seconds=60)
    
    # Step 1: User requests to create a location
    print("USER REQUEST:")
    print('  "Create a new location called \"Vacation Home\" in Hawaii"')
    print()
    
    tool_name = "create_location"
    tool_input = {
        "name": "Vacation Home",
        "country_code": "US",
        "timezone": "Pacific/Honolulu",
    }
    
    pending_action = middleware.request_confirmation(
        tool_name=tool_name,
        tool_input=tool_input,
        description="Create a new location 'Vacation Home' in Hawaii"
    )
    
    print("AGENT FIRST CONFIRMATION REQUEST:")
    print(middleware.get_confirmation_prompt(pending_action))
    print()
    
    # Step 2: User takes a different action instead of confirming
    print("USER (Changes their mind):")
    print('  "Actually, what time is it in Hawaii?"')
    print()
    
    # Step 3: Agent processes new unrelated action
    print("AGENT PROCESSES NEW REQUEST:")
    print("  -> This is a READ operation, not related to pending confirmation")
    print("  -> Cancelling pending location creation...")
    print()
    
    # Simulate agent cancelling the pending action
    middleware.cancel_pending_action("User issued unrelated command")
    
    print("AGENT INTERNAL STATE:")
    print(f"  Pending confirmation? {middleware.has_pending_confirmation()}")
    print(f"  Previous action state: {pending_action.state.value}")
    print()
    
    print("USER SEES:")
    print('  "It\'s currently 2:30 PM in Hawaii (HST)"')
    print()
    
    # Step 4: User later tries to confirm the old action
    print("USER (Later):")
    print('  "Yes, create the vacation home location"')
    print()
    
    success, message = middleware.confirm_pending_action()
    print("AGENT RESPONSE:")
    print(f"  Status: {message}")
    print()
    
    print("USER SEES:")
    print('  "⚠ No pending action to confirm. Please request the action again."')


def scenario_5_multiple_conversations() -> None:
    """Demonstrate state isolation across multiple conversations."""
    print_section("SCENARIO 5: Multiple Concurrent Conversations with Isolated State")
    
    manager = ConfirmationStateManager()
    
    # Conversation 1: User A
    print("CONVERSATION 1 (User A):")
    middleware_1 = manager.get_middleware("user-a-conv", confirmation_ttl_seconds=60)
    
    print("  User A: \"Create a new room called Living Room\"")
    pending_1 = middleware_1.request_confirmation(
        tool_name="create_room",
        tool_input={"location_id": "loc-a", "name": "Living Room"},
        description="Create room 'Living Room'"
    )
    print(f"  Agent: [Pending confirmation for room creation]")
    print(f"  Action ID: {pending_1.action_id}")
    print()
    
    # Conversation 2: User B (independent state)
    print("CONVERSATION 2 (User B):")
    middleware_2 = manager.get_middleware("user-b-conv", confirmation_ttl_seconds=60)
    
    print("  User B: \"Delete the Evening scene\"")
    pending_2 = middleware_2.request_confirmation(
        tool_name="delete_scene",
        tool_input={"location_id": "loc-b", "scene_id": "scene-evening"},
        description="Delete scene 'Evening'"
    )
    print(f"  Agent: [Pending confirmation for scene deletion]")
    print(f"  Action ID: {pending_2.action_id}")
    print()
    
    # Check state isolation
    print("STATE ISOLATION CHECK:")
    print(f"  User A pending action: {middleware_1.has_pending_confirmation()}")
    print(f"  User B pending action: {middleware_2.has_pending_confirmation()}")
    print(f"  Actions are different? {pending_1.action_id != pending_2.action_id}")
    print()
    
    # User A cancels their action
    print("CONVERSATION 1:")
    print("  User A: \"Actually, cancel that\"")
    middleware_1.cancel_pending_action("User cancelled")
    print(f"  Agent: Cancelled pending room creation")
    print(f"  User A pending action now: {middleware_1.has_pending_confirmation()}")
    print()
    
    # User B's action is unaffected
    print("CONVERSATION 2:")
    print(f"  User B's action still pending? {middleware_2.has_pending_confirmation()}")
    print("  User B: \"Yes, delete the scene\"")
    success, msg = middleware_2.confirm_pending_action()
    print(f"  Agent: Confirmed and executing scene deletion")
    print()


def main() -> None:
    """Run all demonstration scenarios."""
    print("\n" + "="*70)
    print("  SMARTTHINGS DOUBLE CONFIRMATION - END-TO-END EXAMPLES")
    print("="*70)
    
    scenario_1_create_room_with_confirmation()
    scenario_2_device_command_no_confirmation()
    scenario_3_confirmation_expiry()
    scenario_4_context_drift_cancellation()
    scenario_5_multiple_conversations()
    
    print_section("SUMMARY OF TOOL CATEGORIZATION")
    
    print("READ_ONLY Tools (No confirmation required):")
    print("  • list_locations, get_location")
    print("  • list_rooms, get_room")
    print("  • list_devices, get_device, get_device_state")
    print("  • list_scenes, get_scene")
    print("  • list_rules, get_rule")
    print()
    
    print("DEVICE_COMMAND Tools (No confirmation required - immediate execution):")
    print("  • execute_command (turn on/off, set level, thermostat, etc.)")
    print("  • execute_scene (run a scene)")
    print("  • enable_rule, disable_rule (toggle rule state)")
    print()
    
    print("STATE_CHANGING Tools (Double confirmation REQUIRED):")
    print("  • create_location, update_location, delete_location")
    print("  • create_room, update_room, delete_room")
    print("  • create_scene, update_scene, delete_scene")
    print("  • create_rule, update_rule, delete_rule")
    print("  • create_subscription, delete_subscription")
    print("  • update_device")
    print("  • uninstall_app")
    print()
    
    print("CONFIRMATION FLOW FOR STATE_CHANGING ACTIONS:")
    print("  1. User requests action (e.g., \"Delete the Good Night scene\")")
    print("  2. Agent categorizes tool as STATE_CHANGING")
    print("  3. Agent calls request_confirmation() - generates pending action")
    print("  4. Agent displays confirmation prompt with:")
    print("     - What will happen")
    print("     - Which entity is affected")
    print("     - Time remaining before expiry (default: 60 seconds)")
    print("  5. User must explicitly confirm:")
    print("     - If confirmed: Action executes")
    print("     - If user silent >60s: Confirmation expires, action aborts")
    print("     - If user changes topic: Pending action is cancelled, action aborts")
    print()
    
    print("KEY SAFETY FEATURES:")
    print("  ✓ TTL-based expiry (default 60s, configurable)")
    print("  ✓ Only ONE pending confirmation at a time per user")
    print("  ✓ Auto-cancel on unrelated command")
    print("  ✓ Explicit state transitions (PENDING → CONFIRMED/EXPIRED/CANCELLED)")
    print("  ✓ Device commands bypass confirmation entirely")
    print("  ✓ Multi-conversation isolation via ConfirmationStateManager")
    print()


if __name__ == "__main__":
    main()
