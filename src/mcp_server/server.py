"""MCP server implementation for smart home control."""

from typing import Any

from src.config import Settings
from src.logging import get_logger
from src.models.device import Device, DeviceState, Location, Room
from src.providers.base import SmartHomeProvider
from src.providers.smartthings.provider import SmartThingsProvider

logger = get_logger(__name__)


class MCPServer:
    """Model Context Protocol server for smart home control.
    
    Exposes smart home capabilities as MCP tools and resources,
    allowing language models to discover and control devices.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize MCP server.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.providers: dict[str, SmartHomeProvider] = {}
        self._locations: dict[str, Location] = {}
        self._rooms: dict[str, Room] = {}
        self._devices: dict[str, Device] = {}

    async def start(self) -> None:
        """Start the MCP server and initialize providers."""
        try:
            logger.info("Starting MCP server")
            await self._initialize_providers()
            await self._refresh_device_cache()
            logger.info("MCP server started successfully")
        except Exception as e:
            logger.error("Failed to start MCP server", error=str(e))
            raise

    async def stop(self) -> None:
        """Stop the MCP server and close providers."""
        try:
            logger.info("Stopping MCP server")
            for provider_name, provider in self.providers.items():
                await provider.close()
                logger.debug("Closed provider", provider=provider_name)
            self.providers.clear()
            logger.info("MCP server stopped")
        except Exception as e:
            logger.error("Error stopping MCP server", error=str(e))
            raise

    async def _initialize_providers(self) -> None:
        """Initialize enabled providers."""
        enabled = self.settings.get_enabled_providers()
        logger.info("Initializing providers", enabled=enabled)

        for provider_name in enabled:
            provider = self._create_provider(provider_name)
            if provider:
                try:
                    if await provider.authenticate():
                        self.providers[provider_name] = provider
                        logger.info("Provider authenticated", provider=provider_name)
                except Exception as e:
                    logger.warning(
                        "Failed to authenticate provider",
                        provider=provider_name,
                        error=str(e),
                    )

    def _create_provider(self, provider_name: str) -> SmartHomeProvider | None:
        """Create a provider instance by name.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider instance or None if unknown
        """
        if provider_name == "smartthings":
            return SmartThingsProvider(
                pat_token=self.settings.smartthings_pat_token,
                api_url=self.settings.smartthings_api_url,
            )
        # Additional providers can be added here
        logger.warning("Unknown provider", provider=provider_name)
        return None

    async def _refresh_device_cache(self) -> None:
        """Refresh locations, rooms, and devices cache."""
        try:
            self._locations.clear()
            self._rooms.clear()
            self._devices.clear()

            for provider_name, provider in self.providers.items():
                logger.debug("Refreshing cache for provider", provider=provider_name)

                # Get locations
                locations = await provider.list_locations()
                for location in locations:
                    self._locations[location.id] = location

                    # Get rooms for each location
                    rooms = await provider.list_rooms(location.id)
                    for room in rooms:
                        self._rooms[room.id] = room

                # Get devices
                devices = await provider.list_devices()
                for device in devices:
                    self._devices[device.id] = device

            logger.info(
                "Device cache refreshed",
                locations=len(self._locations),
                rooms=len(self._rooms),
                devices=len(self._devices),
            )
        except Exception as e:
            logger.error("Failed to refresh device cache", error=str(e))
            raise

    # MCP Tools

    def get_mcp_tools(self) -> list[dict[str, Any]]:
        """Get list of MCP tools.
        
        Returns:
            List of tool definitions
        """
        return [
            {
                "name": "list_locations",
                "description": "List all smart home locations",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "list_devices",
                "description": "List devices in a location or all devices",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location_id": {
                            "type": "string",
                            "description": "Optional location ID to filter devices",
                        }
                    },
                    "required": [],
                },
            },
            {
                "name": "get_device",
                "description": "Get device description, metadata, and capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device ID"}
                    },
                    "required": ["device_id"],
                },
            },
            {
                "name": "get_device_state",
                "description": "Get current state of a device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device ID"}
                    },
                    "required": ["device_id"],
                },
            },
            {
                "name": "execute_command",
                "description": "Execute a command on a device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {"type": "string", "description": "Device ID"},
                        "capability": {
                            "type": "string",
                            "description": "Capability type",
                        },
                        "command": {"type": "string", "description": "Command name"},
                        "arguments": {
                            "type": "object",
                            "description": "Command arguments",
                        },
                    },
                    "required": ["device_id", "capability", "command"],
                },
            },
            {
                "name": "get_device_activities",
                "description": "Get activity history for a specific device",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID to query",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of activities to return (default: 100, max: 500)",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time for activity range (ISO 8601 format)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time for activity range (ISO 8601 format)",
                        },
                    },
                    "required": ["device_id"],
                },
            },
            {
                "name": "get_location_activities",
                "description": "Get activity history for a specific location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location_id": {
                            "type": "string",
                            "description": "Location ID to query",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of activities to return (default: 100, max: 500)",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Start time for activity range (ISO 8601 format)",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "End time for activity range (ISO 8601 format)",
                        },
                    },
                    "required": ["location_id"],
                },
            },
        ]

    async def call_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        """Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool
            
        Returns:
            Tool result
        """
        if tool_name == "list_locations":
            return await self.list_locations()
        elif tool_name == "list_devices":
            return await self.list_devices(tool_input.get("location_id"))
        elif tool_name == "get_device":
            return await self.get_device(tool_input["device_id"])
        elif tool_name == "get_device_state":
            return await self.get_device_state(tool_input["device_id"])
        elif tool_name == "execute_command":
            return await self.execute_command(
                device_id=tool_input["device_id"],
                capability=tool_input["capability"],
                command=tool_input["command"],
                arguments=tool_input.get("arguments", {}),
            )
        elif tool_name == "get_device_activities":
            return await self.get_device_activities(
                device_id=tool_input["device_id"],
                limit=tool_input.get("limit"),
                start_time=tool_input.get("start_time"),
                end_time=tool_input.get("end_time"),
            )
        elif tool_name == "get_location_activities":
            return await self.get_location_activities(
                location_id=tool_input["location_id"],
                limit=tool_input.get("limit"),
                start_time=tool_input.get("start_time"),
                end_time=tool_input.get("end_time"),
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def list_locations(self) -> list[dict[str, Any]]:
        """List all locations.
        
        Returns:
            List of location dicts
        """
        await self._refresh_device_cache()
        return [
            {
                "id": loc.id,
                "name": loc.name,
                "timezone": loc.timezone,
                "country_code": loc.country_code,
            }
            for loc in self._locations.values()
        ]

    async def list_devices(self, location_id: str | None = None) -> list[dict[str, Any]]:
        """List devices, optionally filtered by location.
        
        Args:
            location_id: Optional location ID
            
        Returns:
            List of device dicts
        """
        await self._refresh_device_cache()
        devices = self._devices.values()

        if location_id:
            devices = [d for d in devices if d.location_id == location_id]

        return [
            {
                "id": device.id,
                "name": device.name,
                "type": device.device_type.value,
                "location_id": device.location_id,
                "room_id": device.room_id,
                "capabilities": [cap.type.value for cap in device.capabilities],
                "state": device.state,
            }
            for device in devices
        ]

    async def get_device(self, device_id: str) -> dict[str, Any]:
        """Get device description.
        
        Args:
            device_id: Device ID
            
        Returns:
            Device description dict
        """
        device_desc = None
        for provider in self.providers.values():
            try:
                device_desc = await provider.get_device(device_id)
                break
            except Exception:
                continue

        if not device_desc:
            raise ValueError(f"Device not found: {device_id}")

        return device_desc

    async def get_device_state(self, device_id: str) -> dict[str, Any]:
        """Get device state.
        
        Args:
            device_id: Device ID
            
        Returns:
            Device state dict
        """
        device_state = None
        for provider in self.providers.values():
            try:
                device_state = await provider.get_device_state(device_id)
                break
            except Exception:
                continue

        if not device_state:
            raise ValueError(f"Device not found: {device_id}")

        return {
            "device_id": device_state.device_id,
            "timestamp": device_state.timestamp,
            "state": device_state.state,
        }

    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a command on a device.
        
        Args:
            device_id: Device ID
            capability: Capability type
            command: Command name
            arguments: Command arguments
            
        Returns:
            Command result dict
        """
        if arguments is None:
            arguments = {}

        result = None
        for provider in self.providers.values():
            try:
                result = await provider.execute_command(
                    device_id=device_id,
                    capability=capability,
                    command=command,
                    arguments=arguments,
                )
                break
            except Exception:
                continue

        if not result:
            raise ValueError(f"Device not found: {device_id}")

        return {
            "device_id": result.device_id,
            "success": result.success,
            "message": result.message,
            "error": result.error,
        }

    async def get_device_activities(
        self,
        device_id: str,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """Get activity history for a device.
        
        Args:
            device_id: Device ID to query
            limit: Optional result limit
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            
        Returns:
            Activity page dict with results
        """
        activity_page = None
        for provider in self.providers.values():
            try:
                activity_page = await provider.get_device_activities(
                    device_id=device_id,
                    limit=limit,
                    start_time=start_time,
                    end_time=end_time,
                )
                break
            except Exception:
                continue

        if not activity_page:
            raise ValueError(f"Device not found: {device_id}")

        return {
            "device_id": device_id,
            "items": [
                {
                    "id": activity.id,
                    "timestamp": activity.timestamp,
                    "type": activity.activity_type.value,
                    "source": activity.source.value,
                    "capability": activity.capability,
                    "command": activity.command,
                    "attribute": activity.attribute,
                    "changes": [
                        {
                            "attribute": change.attribute,
                            "old_value": change.old_value,
                            "new_value": change.new_value,
                        }
                        for change in activity.changes
                    ],
                    "summary": activity.summary(),
                }
                for activity in activity_page.items
            ],
            "total": activity_page.total,
            "has_more": activity_page.has_more,
        }

    async def get_location_activities(
        self,
        location_id: str,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """Get activity history for a location.
        
        Args:
            location_id: Location ID to query
            limit: Optional result limit
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            
        Returns:
            Activity page dict with results
        """
        activity_page = None
        for provider in self.providers.values():
            try:
                activity_page = await provider.get_location_activities(
                    location_id=location_id,
                    limit=limit,
                    start_time=start_time,
                    end_time=end_time,
                )
                break
            except Exception:
                continue

        if not activity_page:
            raise ValueError(f"Location not found: {location_id}")

        return {
            "location_id": location_id,
            "items": [
                {
                    "id": activity.id,
                    "timestamp": activity.timestamp,
                    "type": activity.activity_type.value,
                    "source": activity.source.value,
                    "device_id": activity.device_id,
                    "capability": activity.capability,
                    "command": activity.command,
                    "attribute": activity.attribute,
                    "changes": [
                        {
                            "attribute": change.attribute,
                            "old_value": change.old_value,
                            "new_value": change.new_value,
                        }
                        for change in activity.changes
                    ],
                    "summary": activity.summary(),
                }
                for activity in activity_page.items
            ],
            "total": activity_page.total,
            "has_more": activity_page.has_more,
        }

    # MCP Resources

    def get_mcp_resources(self) -> list[dict[str, Any]]:
        """Get list of available MCP resources.
        
        Returns:
            List of resource definitions
        """
        resources = []

        # Location resources
        for loc_id, location in self._locations.items():
            resources.append(
                {
                    "uri": f"location://{loc_id}",
                    "name": f"Location: {location.name}",
                    "mimeType": "application/json",
                    "description": f"Location {location.name}",
                }
            )

        # Device resources
        for device_id, device in self._devices.items():
            resources.append(
                {
                    "uri": f"device://{device_id}",
                    "name": f"Device: {device.name}",
                    "mimeType": "application/json",
                    "description": f"Smart home device {device.name}",
                }
            )

        return resources

    async def read_resource(self, uri: str) -> str:
        """Read a resource by URI.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content as JSON string
        """
        import json

        if uri.startswith("location://"):
            loc_id = uri.split("://")[1]
            if loc_id in self._locations:
                loc = self._locations[loc_id]
                return json.dumps(
                    {
                        "id": loc.id,
                        "name": loc.name,
                        "timezone": loc.timezone,
                        "country_code": loc.country_code,
                    }
                )
        elif uri.startswith("device://"):
            device_id = uri.split("://")[1]
            if device_id in self._devices:
                device = self._devices[device_id]
                return json.dumps(
                    {
                        "id": device.id,
                        "name": device.name,
                        "type": device.device_type.value,
                        "location_id": device.location_id,
                        "room_id": device.room_id,
                        "capabilities": [cap.type.value for cap in device.capabilities],
                        "state": device.state,
                    }
                )

        raise ValueError(f"Resource not found: {uri}")
