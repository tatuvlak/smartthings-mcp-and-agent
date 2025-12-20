# Adding New Smart Home Providers

This guide explains how to add support for new smart home ecosystems (Home Assistant, Matter, Alexa, etc).

## Architecture Overview

The system uses a **plugin-based provider architecture** where each smart home platform is wrapped in a provider class that implements the `SmartHomeProvider` interface.

```
┌─────────────────────────────────┐
│   SmartHomeProvider (Abstract)   │
│  - authenticate()                │
│  - list_locations()              │
│  - list_rooms()                  │
│  - list_devices()                │
│  - get_device_state()            │
│  - execute_command()             │
└─────────────────────────────────┘
         △         △         △
         │         │         │
    ┌────┴──┐  ┌───┴────┐  ┌─┴────────┐
    │        │  │        │  │          │
SmartThings  HA  Matter Alexa
```

## Step 1: Create Provider Package

Create a directory for your provider:

```bash
mkdir -p src/providers/your_provider_name
touch src/providers/your_provider_name/__init__.py
touch src/providers/your_provider_name/provider.py
```

## Step 2: Implement the Provider Class

Here's a complete example for a new provider:

```python
# src/providers/your_provider_name/provider.py

from typing import Any
from src.providers.base import SmartHomeProvider
from src.models.device import (
    Location, Room, Device, DeviceState, 
    CommandResult, Capability, CapabilityType
)
from src.logging import get_logger

logger = get_logger(__name__)

class YourProviderNameProvider(SmartHomeProvider):
    """Your smart home provider implementation."""

    def __init__(self, api_url: str, access_token: str) -> None:
        """Initialize provider with credentials."""
        self.api_url = api_url
        self.access_token = access_token
        self._authenticated = False
        # Initialize any HTTP clients, state caches, etc.

    async def authenticate(self) -> bool:
        """Authenticate with the provider.
        
        This should verify credentials and establish any required connections.
        Raise an exception if authentication fails.
        """
        try:
            # TODO: Implement authentication
            # Example: Check API connectivity, validate token, etc.
            self._authenticated = True
            logger.info("Provider authenticated")
            return True
        except Exception as e:
            logger.error("Authentication failed", error=str(e))
            raise

    async def list_locations(self) -> list[Location]:
        """Return list of locations/homes."""
        if not self._authenticated:
            await self.authenticate()
        
        # TODO: Fetch locations from API
        locations = []
        
        # Example: Parse API response and create Location objects
        # location = Location(
        #     id="location-1",
        #     name="Home",
        #     timezone="America/New_York",
        # )
        # locations.append(location)
        
        logger.info("Listed locations", count=len(locations))
        return locations

    async def list_rooms(self, location_id: str) -> list[Room]:
        """Return list of rooms in a location."""
        # TODO: Fetch rooms for the location
        rooms = []
        
        # Example:
        # room = Room(
        #     id="room-1",
        #     name="Living Room",
        #     location_id=location_id,
        # )
        # rooms.append(room)
        
        logger.info("Listed rooms", location_id=location_id, count=len(rooms))
        return rooms

    async def list_devices(self, location_id: str | None = None) -> list[Device]:
        """Return list of devices, optionally filtered by location."""
        # TODO: Fetch devices from API
        devices = []
        
        # Example: Create Device objects from API response
        # device = Device(
        #     id="device-1",
        #     name="Living Room Light",
        #     device_type=DeviceType.LIGHT,
        #     location_id=location_id,
        #     capabilities=[
        #         Capability(
        #             type=CapabilityType.SWITCH,
        #             commands=["on", "off"],
        #         ),
        #         Capability(
        #             type=CapabilityType.LEVEL,
        #             commands=["setLevel"],
        #         ),
        #     ],
        # )
        # devices.append(device)
        
        return devices

    async def get_device_state(self, device_id: str) -> DeviceState:
        """Return current state of a device."""
        # TODO: Fetch current state from API
        
        # Example:
        # state = {
        #     "power": "on",
        #     "brightness": 80,
        # }
        # return DeviceState(
        #     device_id=device_id,
        #     timestamp=datetime.now().isoformat(),
        #     state=state,
        # )
        
        raise NotImplementedError()

    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute a command on a device."""
        if arguments is None:
            arguments = {}
        
        try:
            # TODO: Send command to device via API
            
            # Example:
            # await self._api_call(
            #     method="POST",
            #     endpoint=f"/devices/{device_id}/commands",
            #     data={
            #         "capability": capability,
            #         "command": command,
            #         "arguments": arguments,
            #     },
            # )
            
            return CommandResult(
                device_id=device_id,
                success=True,
                message="Command executed",
            )
        except Exception as e:
            return CommandResult(
                device_id=device_id,
                success=False,
                message="Command failed",
                error=str(e),
            )

    async def close(self) -> None:
        """Close any open connections."""
        logger.info("Provider closed")
```

## Step 3: Create API Client (Optional)

For complex providers, create a separate API client class:

```python
# src/providers/your_provider_name/client.py

import httpx
from src.logging import get_logger

logger = get_logger(__name__)

class YourProviderAPIClient:
    """Client for your provider's REST API."""

    def __init__(self, api_url: str, access_token: str) -> None:
        self.api_url = api_url
        self.access_token = access_token
        self.client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        """Establish connection."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            headers=headers,
            base_url=self.api_url,
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close connection."""
        if self.client:
            await self.client.aclose()

    async def get(self, endpoint: str) -> dict:
        """Make GET request."""
        if not self.client:
            raise RuntimeError("Not connected")
        response = await self.client.get(endpoint)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, data: dict) -> dict:
        """Make POST request."""
        if not self.client:
            raise RuntimeError("Not connected")
        response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
```

## Step 4: Register the Provider

Add the provider to the providers init file:

```python
# src/providers/__init__.py

from src.providers.your_provider_name.provider import YourProviderNameProvider

__all__ = [
    # ... existing exports ...
    "YourProviderNameProvider",
]
```

## Step 5: Update Configuration

Add configuration fields in `src/config.py`:

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # Your provider configuration
    your_provider_api_url: str = ""
    your_provider_token: str = ""
```

Add environment variables to `.env.example`:

```env
# Your Provider Configuration
YOUR_PROVIDER_API_URL=https://api.yourprovider.com
YOUR_PROVIDER_TOKEN=your_token_here
```

## Step 6: Enable in MCP Server

Update `src/mcp_server/server.py` to instantiate your provider:

```python
def _create_provider(self, provider_name: str) -> SmartHomeProvider | None:
    """Create a provider instance by name."""
    if provider_name == "smartthings":
        return SmartThingsProvider(...)
    elif provider_name == "your_provider_name":
        return YourProviderNameProvider(
            api_url=self.settings.your_provider_api_url,
            access_token=self.settings.your_provider_token,
        )
    # ... more providers ...
```

## Step 7: Add Tests

Create comprehensive tests:

```python
# tests/test_your_provider.py

import pytest
from src.providers.your_provider_name.provider import YourProviderNameProvider

@pytest.fixture
async def provider():
    p = YourProviderNameProvider(
        api_url="http://test-url",
        access_token="test-token",
    )
    yield p
    await p.close()

@pytest.mark.asyncio
async def test_authenticate(provider):
    # Mock the API calls
    result = await provider.authenticate()
    assert result is True

@pytest.mark.asyncio
async def test_list_devices(provider):
    devices = await provider.list_devices()
    assert isinstance(devices, list)
```

## Mapping Guide

### Device Type Mapping

Map your provider's device types to internal types:

```python
@staticmethod
def _map_device_type(provider_type: str) -> DeviceType:
    mapping = {
        "light": DeviceType.LIGHT,
        "dimmer": DeviceType.LIGHT,
        "switch": DeviceType.SWITCH,
        "thermostat": DeviceType.THERMOSTAT,
        "lock": DeviceType.LOCK,
        "sensor": DeviceType.SENSOR,
        "motion": DeviceType.SENSOR,
        # Add more mappings
    }
    return mapping.get(provider_type, DeviceType.OTHER)
```

### Capability Mapping

Map capabilities to standard types:

```python
@staticmethod
def _map_capability(provider_capability: str) -> CapabilityType:
    mapping = {
        "power": CapabilityType.SWITCH,
        "brightness": CapabilityType.LEVEL,
        "color": CapabilityType.COLOR_CONTROL,
        "temperature": CapabilityType.TEMPERATURE_MEASUREMENT,
        # Add more mappings
    }
    return mapping.get(provider_capability, CapabilityType.OTHER)
```

## Best Practices

1. **Error Handling**: Wrap API calls in try-except, log errors
2. **Caching**: Cache device lists to reduce API calls
3. **Rate Limiting**: Implement backoff for rate-limited APIs
4. **Async Throughout**: Use async/await consistently
5. **Logging**: Use structured logging for debugging
6. **Type Hints**: Use full type hints for IDE support
7. **Documentation**: Document device type/capability mappings
8. **Testing**: Write unit and integration tests

## Example: Home Assistant Implementation

Here's a sketch of how Home Assistant provider would look:

```python
class HomeAssistantProvider(SmartHomeProvider):
    """Home Assistant smart home provider."""

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url  # e.g., http://localhost:8123
        self.token = token
        self.client = None

    async def authenticate(self) -> bool:
        # Test connection to /api/
        # Verify token is valid
        pass

    async def list_locations(self) -> list[Location]:
        # HA doesn't have locations, return single "Home"
        pass

    async def list_devices(self) -> list[Device]:
        # GET /api/states to list all entities
        # Parse entity_id and convert to Device
        # Extract attributes as capabilities
        pass

    async def execute_command(self, device_id: str, ...) -> CommandResult:
        # POST /api/services/{domain}/{service}
        # Map internal commands to HA services
        pass
```

## Troubleshooting

**Issue**: API calls timeout
- Solution: Increase timeout in `httpx.AsyncClient`

**Issue**: Device state is stale
- Solution: Clear cache after commands, implement polling

**Issue**: Capability not recognized
- Solution: Add mapping in `_map_capability`, use UNKNOWN type as fallback

**Issue**: Authentication fails silently
- Solution: Log detailed error messages, check credentials

## Contributing New Providers

To contribute a new provider:

1. Follow this guide exactly
2. Write comprehensive tests (aim for >80% coverage)
3. Add documentation for setup
4. Update README with provider info
5. Submit pull request with examples

## Questions?

See `docs/` folder for more examples and architecture details.
