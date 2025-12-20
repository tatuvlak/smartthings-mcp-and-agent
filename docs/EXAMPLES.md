# Example Commands and Usage

This document provides examples of natural language commands and how the system processes them.

## Basic Light Control

### Turn On Lights

```
User: "Turn on the living room lights"
Agent: Identifies "living room" location, finds light device(s) there, 
       sends ON command, reports: "Turned on the living room lights"
```

### Brightness Control

```
User: "Set the bedroom lights to 50%"
Agent: Finds bedroom lights, sends setLevel command with value 50,
       reports: "Set bedroom lights to 50% brightness"
```

### Turn Off All Lights

```
User: "Turn off all the lights"
Agent: Lists all light devices, sends OFF command to each,
       reports: "Turned off 8 lights across the house"
```

### Color Control

```
User: "Make the living room light blue"
Agent: Finds living room light with color capability,
       sends setColor command with blue RGB value,
       reports: "Set living room light to blue"
```

## Thermostat Control

### Set Temperature

```
User: "Set the thermostat to 72 degrees"
Agent: Finds thermostat device, sends setHeatingSetpoint (or mode-appropriate command),
       reports: "Set thermostat to 72°F"
```

### Change Mode

```
User: "Put the thermostat in cooling mode"
Agent: Sends setThermostatMode command with "cooling" value,
       reports: "Switched thermostat to cooling mode"
```

### Check Current Temperature

```
User: "What's the current temperature?"
Agent: Reads temperature from sensor/thermostat,
       reports: "Current temperature is 68°F"
```

## Lock Control

### Secure Lock

```
User: "Lock the front door"
Agent: Identifies front door lock device,
       sends lock command,
       reports: "Locked the front door"
```

### Unlock (with confirmation)

```
User: "Unlock the garage door"
Agent: Recognizes safety-critical action, asks: "Are you sure you want to unlock the garage door?"
User: "Yes"
Agent: Sends unlock command,
       reports: "Unlocked the garage door"
```

## Window Blinds/Shades

### Open Blinds

```
User: "Open the living room blinds"
Agent: Finds blind device in living room,
       sends open/setPosition command,
       reports: "Opened the living room blinds"
```

### Set Position

```
User: "Close the bedroom blinds halfway"
Agent: Sends setPosition command with value 50,
       reports: "Set bedroom blinds to 50% closed"
```

## Sensor Readings

### Read Multiple Sensors

```
User: "What's the humidity in the bedroom?"
Agent: Finds humidity sensor in bedroom,
       reads current value,
       reports: "Bedroom humidity is 45%"
```

### Motion Detection

```
User: "Is there motion in the hallway?"
Agent: Reads motion sensor state,
       reports: "Motion detected in hallway" or "No motion in hallway"
```

### Door/Contact Status

```
User: "Is the back door open?"
Agent: Reads contact sensor for back door,
       reports: "Back door is open" or "Back door is closed"
```

## Complex Scenarios

### Multi-Device Command

```
User: "Turn off everything in the kitchen"
Agent: Identifies all devices in kitchen location,
       sends OFF/close/disable commands as appropriate,
       reports: "Turned off kitchen lights, ceiling fan, and coffee maker"
```

### Scene Control

```
User: "I'm leaving the house"
Agent: (Could implement scene logic)
       - Lock all doors
       - Turn off all lights
       - Set thermostat to away mode
       - Close all blinds
       Reports: "House is locked and secured"
```

### Conditional Logic

```
User: "If the front door is unlocked, lock it"
Agent: Checks door lock state,
       if unlocked: sends lock command, reports action
       if already locked: reports "Front door is already locked"
```

## Device Discovery

### List Devices in Location

```
User: "What devices are in the living room?"
Agent: Filters devices by location,
       reports: "Living room has:
                 - Living Room Light
                 - Living Room TV
                 - Living Room Fan
                 - Temperature Sensor"
```

### List Devices by Type

```
User: "Show me all the lights"
Agent: Filters devices by type,
       reports: "Found 12 light devices:
                 - Living Room Light
                 - Bedroom Light
                 - Kitchen Light
                 - Bathroom Light
                 - Hallway Light
                 [and 7 more...]"
```

### Check Device Status

```
User: "Give me a status report"
Agent: Queries all devices,
       reports: "Smart Home Status:
                 - 8 Lights: 3 on, 5 off
                 - Thermostat: 72°F (heating)
                 - Locks: All locked
                 - Sensors: Normal
                 - Cameras: Recording"
```

## Ambiguity Resolution

### Multiple Matches

```
User: "Turn on the light"
Agent: (Multiple lights found)
       Asks: "Which light would you like to turn on? 
             - Living Room Light
             - Bedroom Light
             - Kitchen Light"
User: "Living room"
Agent: Turns on living room light,
       reports: "Turned on the living room light"
```

### Room vs Device Name

```
User: "Turn on kitchen"
Agent: (Unclear if they mean room or device named "kitchen")
       Asks: "Did you mean:
             - All lights in the kitchen?
             - The device called 'kitchen light'?
             - The kitchen fan?"
User: "The fan"
Agent: Turns on kitchen fan,
       reports: "Turned on the kitchen fan"
```

## Multi-Turn Conversations

```
User: "Turn on the living room lights"
Agent: "Turned on the living room lights"

User: "Make them brighter"
Agent: (Remembers context - "living room lights")
       Sets brightness to 80%,
       reports: "Set living room lights to 80% brightness"

User: "Change the color to blue"
Agent: (Still remembers - "living room lights")
       Sets color to blue,
       reports: "Set living room lights to blue"
```

## Natural Language Variations

The agent handles various phrasings for the same command:

```
Turn on the living room light
=
Turn on living room lights
=
Lights on in living room
=
Living room lights on
=
Make the living room bright
```

All should produce the same result.

## Error Handling

### Device Not Found

```
User: "Turn on the patio lights"
Agent: (No device found matching "patio lights")
       Reports: "I couldn't find any device called 'patio lights'. 
                 Available lights are:
                 - Living Room Light
                 - Bedroom Light
                 - Kitchen Light
                 Did you mean one of these?"
```

### Device Offline

```
User: "Set the garage light to 50%"
Agent: (Device found but offline)
       Reports: "The garage light is currently offline and can't be controlled.
                 Please check if it's connected and powered on."
```

### Unsupported Command

```
User: "Record video on the garage light"
Agent: (Light doesn't have camera capability)
       Reports: "The garage light doesn't support video recording.
                 Your cameras are: Front Door Camera, Driveway Camera"
```

## API Tool Calls (Behind the Scenes)

When processing "Turn on the living room lights":

```json
[
  {
    "tool": "list_devices",
    "arguments": {
      "location_id": null
    },
    "result": [
      {
        "id": "light-123",
        "name": "Living Room Light",
        "type": "light",
        "location_id": "loc-1",
        "capabilities": ["switch", "level"]
      },
      ...
    ]
  },
  {
    "tool": "execute_command",
    "arguments": {
      "device_id": "light-123",
      "capability": "switch",
      "command": "on",
      "arguments": {}
    },
    "result": {
      "device_id": "light-123",
      "success": true,
      "message": "Command executed successfully"
    }
  }
]
```

## Best Practices for Users

1. **Be specific**: "Living room lights" not just "lights"
2. **Use natural language**: The system understands context
3. **Use device names**: As they appear in SmartThings app
4. **Confirm critical actions**: System will ask for confirmation on risky commands
5. **Ask for status**: Get current state before sending commands

## Testing Your Setup

Run these commands to verify the agent is working:

```python
import asyncio
from src.agent.agent import SmartHomeAgent
from src.config import Settings

async def test_agent():
    settings = Settings()
    agent = SmartHomeAgent(settings)
    
    await agent.start()
    
    # Test command
    response = await agent.process_command("List all devices")
    print(f"Agent: {response}")
    
    # Get device summary
    print(agent.get_devices_summary())
    
    await agent.stop()

asyncio.run(test_agent())
```

## Limitations and Caveats

- **No historical data**: System doesn't track command history or state changes
- **No automation rules**: Can't create "if-then" routines (yet)
- **No scheduling**: Can't schedule commands for later
- **Context window**: Long conversations may lose context (model dependent)
- **Hallucination**: LLM may invent devices/capabilities that don't exist
  - Mitigated by: Always checking against real device list before executing

## Advanced Examples

### Building Sequences

```
User: "I'm going to bed"
Agent: (Could implement bedtime scene)
       - Turn off all lights except bedroom
       - Set thermostat to night mode
       - Lock all doors
       - Close all blinds
       - Arm security system (if implemented)
       Reports: "House set for bedtime"
```

### Conditional Queries

```
User: "If the front door is unlocked, tell me"
Agent: Checks current state,
       - If unlocked: "Front door is currently unlocked!"
       - If locked: "Front door is already locked"
```

### Power Management

```
User: "Which devices are using the most power?"
Agent: (If power sensors available)
       Queries power consumption,
       Reports: "Devices by power consumption:
                 1. Oven: 2400W (on)
                 2. Clothes Dryer: 3000W (off)
                 3. AC Unit: 1500W (running)
                 4. Water Heater: 800W (idle)"
```

## Questions?

For more details, see the API reference and configuration guide.
