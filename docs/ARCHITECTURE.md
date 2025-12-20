# Architecture Overview

Comprehensive documentation of the smart home MCP server and agent architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  (CLI, Chat, API Clients, Mobile Apps)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              AI Agent Layer (agent.py)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ - Processes natural language commands                │   │
│  │ - Manages multi-turn conversation context            │   │
│  │ - Makes tool/function calls to MCP server            │   │
│  │ - Reports results to user                            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         LLM Provider Abstraction (llm/base.py)               │
│  ┌──────────────┬──────────────┬──────────────────────┐     │
│  │   OpenAI     │ Anthropic    │ Ollama (Local)       │     │
│  │   (GPT-4)    │  (Claude)    │ (Llama2, Mistral)    │     │
│  └──────────────┴──────────────┴──────────────────────┘     │
│  - Consistent interface regardless of provider              │
│  - Tool calling capability                                  │
│  - Conversation management                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│        Model Context Protocol (MCP) Server                   │
│                    (mcp_server/server.py)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Tools:                                               │   │
│  │  - list_devices()                                    │   │
│  │  - get_device_state(device_id)                       │   │
│  │  - execute_command(device, capability, command)      │   │
│  │                                                      │   │
│  │ Resources:                                           │   │
│  │  - location://...                                    │   │
│  │  - device://...                                      │   │
│  │  - room://...                                        │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│     Smart Home Provider Abstraction Layer                    │
│                    (providers/base.py)                       │
│  ┌──────────────┬──────────────┬──────────────────────┐     │
│  │ SmartThings  │ Home Asst.   │ Matter / Alexa       │     │
│  │ (Fully Impl) │ (Stub)       │ (Stubs)              │     │
│  └──────────────┴──────────────┴──────────────────────┘     │
│  - Unified device model                                     │
│  - Consistent command execution                             │
│  - State caching and refresh                                │
│  - Error handling and retries                               │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Third-Party APIs & Ecosystems                        │
│  ┌──────────────┬──────────────┬──────────────────────┐     │
│  │SmartThings   │ Home Asst.   │ Matter, Alexa        │     │
│  │REST API      │ REST API     │ APIs                 │     │
│  └──────────────┴──────────────┴──────────────────────┘     │
│  - Device data                                              │
│  - State changes                                            │
│  - Command execution                                        │
│  - Event streams                                            │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Models (models/)

**Device Model Hierarchy:**

```
Location
  ├── Room
  │   └── Device
  │       └── Capability
  │           ├── Command
  │           └── Attribute
  └── Device (ungrouped)
```

**Core Classes:**
- `Location`: Physical location (home, office)
- `Room`: Room within a location
- `Device`: Smart device (light, thermostat, lock)
- `Capability`: Device capability (switch, brightness control)
- `DeviceState`: Current device state and attributes
- `CommandResult`: Result of executing a device command

**Device Normalization:**
All providers map their native device types to a standard set:
- `DeviceType`: LIGHT, SWITCH, THERMOSTAT, LOCK, SENSOR, CAMERA, BLINDS, PLUG, FAN, OTHER
- `CapabilityType`: SWITCH, LEVEL, COLOR, TEMPERATURE, MOTION, CONTACT, etc.

### 2. Provider Abstraction (providers/)

**Base Interface:**

```python
class SmartHomeProvider(ABC):
    - authenticate() -> bool
    - list_locations() -> List[Location]
    - list_rooms(location_id) -> List[Room]
    - list_devices(location_id=None) -> List[Device]
    - get_device_state(device_id) -> DeviceState
    - execute_command(device_id, capability, command, args) -> CommandResult
    - close() -> None
```

**Provider Implementations:**

1. **SmartThingsProvider** (FULLY IMPLEMENTED)
   - Uses SmartThings REST API
   - Handles device discovery and state reading
   - Maps SmartThings capabilities to standard types
   - Implements command execution via API

2. **HomeAssistantProvider** (STUB)
   - Framework for Home Assistant REST API
   - Would use `/api/states` and `/api/services`
   - Maps entities to devices

3. **MatterProvider** (STUB)
   - Framework for Matter protocol support
   - Would integrate Matter controller library
   - Handles device pairing and control

4. **AlexaProvider** (STUB)
   - Framework for Alexa/Amazon integration
   - Would use OAuth2 and SmartHome API
   - Maps Alexa devices and directives

### 3. LLM Abstraction (llm/)

**Base Interface:**

```python
class LLMClient(ABC):
    - chat(messages, tools, temperature, max_tokens) -> LLMResponse
    - close() -> None

class LLMResponse:
    - content: Optional[str]
    - tool_calls: Optional[List[ToolCall]]
    - stop_reason: str
```

**Implementations:**

1. **OpenAIClient**
   - Supports GPT-4, GPT-4 Turbo, GPT-3.5
   - Handles function calling
   - Token management and streaming

2. **AnthropicClient**
   - Supports Claude 3 models
   - Tool use capabilities
   - Extended context windows

3. **OllamaClient**
   - Runs models locally without external APIs
   - Supports Llama 2, Mistral, etc.
   - Privacy-focused for sensitive operations

### 4. MCP Server (mcp_server/)

**Responsibilities:**
- Aggregates devices from multiple providers
- Maintains device cache for performance
- Provides normalized tool interface
- Handles resource lookup
- Implements tool calling

**Tools Exposed:**
- `list_locations()` - Get all locations
- `list_devices(location_id)` - Get devices
- `get_device_state(device_id)` - Read device state
- `execute_command()` - Send device commands

**Resources Exposed:**
- `location://...` - Location objects
- `device://...` - Device objects
- `room://...` - Room objects (future)

### 5. AI Agent (agent/)

**Workflow:**

```
User Input
    ↓
Agent.process_command()
    ↓
Add to conversation history
    ↓
LLMClient.chat(messages, tools)
    ↓
├─ Tool Calls? → Execute via MCP
│   └─ Execute tools
│   └─ Add results to history
│   └─ Call LLM again if needed
│
└─ Text Response
    └─ Return to user
```

**Key Features:**
- Context-aware conversation
- Multi-turn support
- Tool calling and result handling
- Error handling and recovery
- Device disambiguation
- Confirmation for critical operations

### 6. Configuration (config.py)

**Settings Management:**
- Environment variable loading
- Default values
- Type validation via Pydantic
- Extensible for custom configuration

**Scope:**
- API credentials
- LLM provider selection
- Logging configuration
- Feature toggles

## Data Flow Example: "Turn on living room lights"

```
1. User Input
   "Turn on living room lights"
   
2. Agent receives command
   → Adds to conversation_history
   
3. Agent calls LLM
   messages = [{"role": "user", "content": "Turn on..."}]
   tools = [list_devices, get_device_state, execute_command]
   
4. LLM recognizes need for tool call
   → Returns: tool_calls = [{
       "name": "list_devices",
       "arguments": {"location_id": null}
     }]
   
5. Agent executes tool via MCP server
   → Returns list of devices with "living room" in name
   
6. LLM decides on action
   → Returns: tool_calls = [{
       "name": "execute_command",
       "arguments": {
         "device_id": "device-1",
         "capability": "switch",
         "command": "on",
         "arguments": {}
       }
     }]
   
7. Agent executes command via MCP
   → SmartThings provider sends API request
   → Device turns on
   → Returns success result
   
8. LLM generates final response
   "Turned on the living room lights"
   
9. Response returned to user
```

## Concurrency Model

**Async/Await Throughout:**
- All I/O operations are async
- Multiple device commands can execute in parallel
- No blocking on network calls

**Concurrency Patterns:**

```python
# Execute multiple commands concurrently
results = await asyncio.gather(
    provider.execute_command(...),
    provider.execute_command(...),
    provider.execute_command(...),
)
```

## Error Handling Strategy

**Layered Approach:**

```
LLM Layer
  ↓ (LLMException)
Agent Layer
  ↓ (AgentException)
MCP Server Layer
  ↓ (MCPException)
Provider Layer
  ↓ (ProviderException)
API Layer
  ↓ (HTTPException, NetworkException)
```

**Error Recovery:**
- API timeouts → Retry with exponential backoff
- Invalid tool calls → Re-prompt LLM
- Device offline → Graceful degradation
- Network errors → Log and report to user

## State Management

**Caching Strategy:**

```
MCP Server
  ├── _locations: Dict[str, Location]
  │   └── Refreshed on demand
  ├── _rooms: Dict[str, Room]
  │   └── Refreshed per location
  └── _devices: Dict[str, Device]
      └── Refreshed on tool call
```

**Cache Invalidation:**
- Manual refresh via MCP tools
- Automatic refresh on command execution
- Time-based expiration (future)
- Event-based updates (future)

## Security Considerations

### Credential Management
- All secrets via environment variables
- No hardcoded credentials
- Credentials never logged
- Support for credential rotation

### Rate Limiting
- Respect provider rate limits
- Implement exponential backoff
- Queue concurrent requests
- Log rate limit violations

### Access Control
- Confirmation for destructive actions
- User context preservation
- Audit logging (future)
- Per-user device access (future)

### Data Privacy
- Local option with Ollama
- No device data cached unnecessarily
- Secure HTTP only
- GDPR-compatible logging (future)

## Extensibility Points

### Add New LLM Provider
1. Create class extending `LLMClient`
2. Implement `chat()` method
3. Register in `Settings`
4. Done!

### Add New Smart Home Provider
1. Create class extending `SmartHomeProvider`
2. Implement all abstract methods
3. Map device/capability types
4. Register in MCP server
5. Create client class for API interactions

### Add New Device Types
1. Add to `DeviceType` enum
2. Update provider mappings
3. Add tests
4. Document in EXAMPLES.md

### Add New Capabilities
1. Add to `CapabilityType` enum
2. Update provider capability parsing
3. Add capability-specific commands
4. Document in provider docs

## Performance Optimization

**Current:**
- Device caching at MCP server level
- Efficient model representations
- Async I/O throughout

**Future:**
- Instrument with metrics
- Implement request batching
- Add webhooks for state changes
- Optimize conversation history

## Testing Strategy

**Test Pyramid:**
```
       /\
      /E2E\       Integration tests (slow)
     /─────\
    /Unit  /      Unit tests (fast)
   /───────\
```

**Test Coverage Areas:**
- Models and data validation
- Provider implementations
- MCP server tools
- Agent command processing
- LLM client integrations
- Configuration loading
- Error handling

## Deployment Scenarios

### Development
- Local providers only
- Debug logging
- No confirmation required

### Production
- Real providers
- Info logging
- Confirmation required
- Error tracking
- Rate limiting

### Headless
- MCP server mode
- Scripted commands
- Batch operations

### Interactive
- Chat mode
- Real-time feedback
- Multi-turn conversations

## Future Roadmap

### High Priority
1. Implement Home Assistant provider
2. Add automation/scene support
3. Implement persistence for conversation history
4. Add webhook support for device events

### Medium Priority
1. Matter provider implementation
2. Alexa provider implementation
3. Per-user access control
4. Audit logging and reporting
5. Device grouping and zones

### Low Priority
1. Web UI
2. Mobile app
3. Voice interface integration
4. Complex automation rules
5. Machine learning for patterns

## Monitoring and Debugging

**Structured Logging:**
- Uses structlog for JSON output
- Configurable log levels
- Request tracing
- Performance metrics (future)

**Debugging:**
- Enable DEBUG logging
- Use agent.get_devices_summary()
- Check MCP server state
- Review provider logs

---

For implementation details, see:
- [SmartThings Setup](SETUP.md)
- [Configuration Reference](CONFIGURATION.md)
- [Adding Providers](ADDING_PROVIDERS.md)
- [Example Commands](EXAMPLES.md)
