"""Samsung SmartThings provider implementation."""

from datetime import datetime
from typing import Any
from src.utils.parsers import parse_device_raw

from src.logging import get_logger
from src.models.activity import Activity, ActivityChange, ActivityPage, ActivitySource, ActivityType
from src.models.device import (
    Capability,
    CapabilityType,
    CommandResult,
    Device,
    DeviceState,
    DeviceType,
    Location,
    Room,
)
from src.providers.base import SmartHomeProvider
from src.providers.smartthings.client import SmartThingsAPIClient

logger = get_logger(__name__)


class SmartThingsProvider(SmartHomeProvider):
    """Samsung SmartThings smart home provider implementation.
    
    Integrates with the SmartThings REST API to provide device discovery,
    state reading, and command execution.
    """

    def __init__(self, pat_token: str, api_url: str = "https://api.smartthings.com") -> None:
        """Initialize SmartThings provider.
        
        Args:
            pat_token: Personal Access Token for SmartThings API
            api_url: Base URL for SmartThings API
        """
        self.client = SmartThingsAPIClient(pat_token, api_url)
        self._authenticated = False
        self._locations_cache: dict[str, Location] = {}
        self._devices_cache: dict[str, Device] = {}

    async def authenticate(self) -> bool:
        """Authenticate with SmartThings API.
        
        Returns:
            True if authentication successful
            
        Raises:
            Exception: If authentication fails
        """
        try:
            await self.client.connect()
            # Test connection by fetching locations
            locations = await self.client.get_locations()
            self._authenticated = True
            logger.info("SmartThings authentication successful", locations_count=len(locations))
            return True
        except Exception as e:
            logger.error("SmartThings authentication failed", error=str(e))
            raise

    async def list_locations(self) -> list[Location]:
        """List all locations in SmartThings account.
        
        Returns:
            List of Location objects
        """
        try:
            if not self._authenticated:
                await self.authenticate()

            locations_data = await self.client.get_locations()
            locations = []

            for loc_data in locations_data:
                location = Location(
                    id=loc_data.get("locationId", ""),
                    name=loc_data.get("name", "Unknown"),
                    country_code=loc_data.get("countryCode"),
                    timezone=loc_data.get("timeZone"),
                    metadata={"raw": loc_data},
                )
                self._locations_cache[location.id] = location
                locations.append(location)

            logger.info("Listed locations", count=len(locations))
            return locations
        except Exception as e:
            logger.error("Failed to list locations", error=str(e))
            raise

    async def list_rooms(self, location_id: str) -> list[Room]:
        """List rooms in a location.
        
        Args:
            location_id: The location ID
            
        Returns:
            List of Room objects
        """
        try:
            rooms_data = await self.client.get_rooms(location_id)
            rooms = []

            for room_data in rooms_data:
                room = Room(
                    id=room_data.get("roomId", ""),
                    name=room_data.get("name", "Unknown"),
                    location_id=location_id,
                    metadata={"raw": room_data},
                )
                rooms.append(room)

            logger.info("Listed rooms", location_id=location_id, count=len(rooms))
            return rooms
        except Exception as e:
            logger.error("Failed to list rooms", error=str(e), location_id=location_id)
            raise

    async def list_devices(self, location_id: str | None = None) -> list[Device]:
        """List devices, optionally filtered by location.
        
        Note: This method always uses the account-wide /devices endpoint,
        which is more reliable than /locations/{id}/devices. If a location_id
        is provided, results are filtered to that location.
        
        Args:
            location_id: Optional location ID for filtering results
            
        Returns:
            List of Device objects
        """
        try:
            # Always use account-wide devices endpoint for reliability
            # (location-based endpoint may return 404 on some accounts)
            devices_data = await self.client.get_devices(location_id=None)
            devices = []

            for device_data in devices_data:
                device = self._parse_device(device_data)
                
                # Filter by location if specified
                if location_id and device.location_id != location_id:
                    continue
                
                self._devices_cache[device.id] = device
                devices.append(device)

            logger.info(
                "Listed devices",
                location_id=location_id,
                count=len(devices),
            )
            return devices
        except Exception as e:
            logger.error(
                "Failed to list devices",
                error=str(e),
                location_id=location_id,
            )
            raise

    async def get_device(self, device_id: str) -> dict[str, Any]:
        """Get device description and metadata.
        
        Args:
            device_id: The device ID
            
        Returns:
            Device object with description, capabilities, and metadata
        """
        try:
            device_data = await self.client.get_device(device_id)
            logger.debug("Got device description", device_id=device_id)
            return device_data
        except Exception as e:
            logger.error("Failed to get device", error=str(e), device_id=device_id)
            raise

    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get current state of a device.
        
        Args:
            device_id: The device ID
            
        Returns:
            DeviceState object
        """
        try:
            # Get device status from the /status endpoint (has real component state)
            status_data = await self.client.get_device_status(device_id)
            state_dict = self._extract_component_state(status_data)

            device_state = DeviceState(
                device_id=device_id,
                timestamp=datetime.now().isoformat(),
                state=state_dict,
                metadata={"raw": status_data},
            )

            logger.debug("Got device state", device_id=device_id)
            return device_state
        except Exception as e:
            logger.error("Failed to get device state", error=str(e), device_id=device_id)
            raise

    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute a command on a device.
        
        Args:
            device_id: The device ID
            capability: The capability ID
            command: The command name
            arguments: Optional command arguments
            
        Returns:
            CommandResult indicating success or failure
        """
        try:
            # Convert arguments dict to list format expected by SmartThings API
            args_list = []
            if arguments:
                args_list = [arguments.get("value")] if "value" in arguments else []

            result = await self.client.execute_device_command(
                device_id=device_id,
                capability=capability,
                command=command,
                arguments=args_list,
            )

            success = "commands" in result
            message = "Command executed successfully" if success else "Command execution failed"

            logger.info(
                "Executed device command",
                device_id=device_id,
                capability=capability,
                command=command,
                success=success,
            )

            return CommandResult(
                device_id=device_id,
                success=success,
                message=message,
                metadata={"raw": result},
            )
        except Exception as e:
            logger.error(
                "Failed to execute command",
                error=str(e),
                device_id=device_id,
                capability=capability,
                command=command,
            )
            return CommandResult(
                device_id=device_id,
                success=False,
                message="Command execution failed",
                error=str(e),
            )

    async def close(self) -> None:
        """Close connection to SmartThings API."""
        await self.client.close()
        self._authenticated = False
        logger.info("SmartThings provider closed")

    def _parse_device(self, device_data: dict[str, Any]) -> Device:
        """Parse device data from API response.
        
        Args:
            device_data: Raw device data from API
            
        Returns:
            Parsed Device object
        """
        # Use shared parser to get a normalized representation
        parsed = parse_device_raw(device_data)

        # Parse capabilities using existing logic (capability type mapping preserved)
        capabilities = []
        for component in device_data.get("components", []):
            if component.get("id") != "main":
                continue
            for cap_data in component.get("capabilities", []):
                cap_type_str = cap_data.get("id", "")
                try:
                    cap_type = CapabilityType(cap_type_str)
                except ValueError:
                    cap_type = CapabilityType.OTHER

                commands = cap_data.get("commands", [])
                command_names = [cmd.get("name", "") for cmd in commands]

                capability = Capability(
                    type=cap_type,
                    commands=command_names,
                    metadata={"raw": cap_data},
                )
                capabilities.append(capability)

        device = Device(
            id=parsed.get("id") or "",
            name=parsed.get("name") or "Unknown",
            device_type=self._map_device_type(parsed.get("device_type_name", "")),
            location_id=parsed.get("location_id") or "",
            room_id=parsed.get("room_id"),
            manufacturer=parsed.get("manufacturer"),
            model=parsed.get("model"),
            capabilities=capabilities,
            state=parsed.get("state", {}),
            metadata={"raw": device_data},
        )

        return device

    @staticmethod
    def _extract_device_state(device_data: dict[str, Any]) -> dict[str, Any]:
        """Extract state attributes from device data.
        
        Args:
            device_data: Raw device data
            
        Returns:
            Dictionary of state attributes
        """
        state: dict[str, Any] = {}
        components = device_data.get("components", [])

        for component in components:
            if component.get("id") == "main":
                for cap_data in component.get("capabilities", []):
                    for status in cap_data.get("status", []):
                        attr_name = status.get("name", "")
                        attr_value = status.get("value")
                        if attr_name and attr_value is not None:
                            state[attr_name] = attr_value

        return state

    @staticmethod
    def _extract_component_state(status_data: dict[str, Any]) -> dict[str, Any]:
        """Extract meaningful state from the /status endpoint response.
        
        The status endpoint returns components with capabilities and their current values.
        This extracts the most useful information in a human-readable format.
        
        Example input:
        {
            "components": {
                "main": {
                    "smokeDetector": {"smoke": {"value": "clear", "timestamp": "..."}},
                    "battery": {"battery": {"value": 71, "unit": "%"}},
                    ...
                }
            }
        }
        
        Args:
            status_data: Raw status data from /devices/{id}/status
            
        Returns:
            Flattened dictionary of useful state attributes
        """
        state: dict[str, Any] = {}
        components = status_data.get("components", {})

        # Process each component (usually "main")
        for comp_name, comp_data in components.items():
            if not isinstance(comp_data, dict):
                continue

            # Process each capability in the component
            for cap_name, cap_data in comp_data.items():
                if not isinstance(cap_data, dict):
                    continue

                # For each attribute in the capability
                for attr_name, attr_info in cap_data.items():
                    if isinstance(attr_info, dict) and "value" in attr_info:
                        value = attr_info.get("value")
                        unit = attr_info.get("unit", "")
                        
                        # Build a descriptive key
                        key = f"{cap_name}.{attr_name}"
                        
                        # Format value with unit if present
                        if unit and value is not None:
                            state[key] = f"{value} {unit}"
                        else:
                            state[key] = value
                    elif attr_name not in ("timestamp", "lastUpdateTime"):
                        # If it's a simple value, include it
                        state[f"{cap_name}.{attr_name}"] = attr_info

        return state

    async def get_device_activities(
        self,
        device_id: str,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> ActivityPage:
        """Get activity history for a device.
        
        Args:
            device_id: Device ID to query
            limit: Optional result limit (default 100, max 500)
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            
        Returns:
            ActivityPage with activity records
            
        Raises:
            Exception: If API request fails
        """
        try:
            response = await self.client.get_device_activities(
                device_id=device_id,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
            )
            
            activities = self._parse_activities_response(response)
            logger.debug("Got device activities", device_id=device_id, count=len(activities))
            
            return ActivityPage(
                items=activities,
                total=response.get("_links", {}).get("self", {}).get("href", "").count("limit"),
                metadata={"raw": response},
            )
        except Exception as e:
            logger.error("Failed to get device activities", device_id=device_id, error=str(e))
            raise

    async def get_location_activities(
        self,
        location_id: str,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> ActivityPage:
        """Get activity history for a location.
        
        Args:
            location_id: Location ID to query
            limit: Optional result limit (default 100, max 500)
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            
        Returns:
            ActivityPage with activity records
            
        Raises:
            Exception: If API request fails
        """
        try:
            response = await self.client.get_location_activities(
                location_id=location_id,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
            )
            
            activities = self._parse_activities_response(response)
            logger.debug("Got location activities", location_id=location_id, count=len(activities))
            
            return ActivityPage(
                items=activities,
                total=response.get("_links", {}).get("self", {}).get("href", "").count("limit"),
                metadata={"raw": response},
            )
        except Exception as e:
            logger.error("Failed to get location activities", location_id=location_id, error=str(e))
            raise

    def _parse_activities_response(self, response: dict[str, Any]) -> list[Activity]:
        """Parse SmartThings activities response into Activity models.
        
        Args:
            response: Raw API response
            
        Returns:
            List of Activity objects
        """
        activities = []
        items = response.get("items", [])
        
        for item in items:
            try:
                activity = self._parse_activity(item)
                if activity:
                    activities.append(activity)
            except Exception as e:
                logger.warning("Failed to parse activity item", error=str(e), item=item)
                continue
        
        return activities

    def _parse_activity(self, item: dict[str, Any]) -> Activity | None:
        """Parse a single activity item from SmartThings API.
        
        Args:
            item: Raw activity item from API
            
        Returns:
            Activity object or None if parsing fails
        """
        try:
            # Extract core fields from SmartThings activity response
            activity_id = item.get("hash", item.get("activityId", ""))  # hash is unique per item
            timestamp = item.get("timestamp", "")
            capability = item.get("capability", "")
            attribute_name = item.get("attributeName", "")
            attribute_value = item.get("attributeValue", "")
            text_summary = item.get("text", "")  # Human-readable summary from API
            
            # Determine activity type based on the API data
            # Most SmartThings activities are state changes (device attribute changes)
            activity_type = ActivityType.DEVICE_STATE_CHANGE
            
            # Determine source - SmartThings doesn't explicitly provide this,
            # so we infer from available fields
            source = ActivitySource.UNKNOWN
            if item.get("userId"):
                source = ActivitySource.USER
            elif item.get("automationId"):
                source = ActivitySource.AUTOMATION
            else:
                # Default to system/device if no explicit source
                source = ActivitySource.SYSTEM
            
            # Extract state change information
            changes = []
            if attribute_name and attribute_value is not None:
                # SmartThings API provides the new value in attributeValue
                # We don't always have the old value in the response,
                # so we create a change record with what we have
                changes.append(
                    ActivityChange(
                        attribute=attribute_name,
                        old_value=None,  # Not provided by SmartThings API
                        new_value=attribute_value,
                        metadata={
                            "unit": item.get("unit", ""),
                            "component": item.get("component", "main"),
                        }
                    )
                )
            
            activity = Activity(
                id=activity_id,
                timestamp=timestamp,
                activity_type=activity_type,
                source=source,
                device_id=item.get("deviceId"),
                location_id=item.get("locationId"),
                user_id=item.get("userId"),
                capability=capability,
                command=None,  # Not provided in SmartThings activity API
                attribute=attribute_name,
                changes=changes,
                metadata={
                    "raw": item,
                    "text": text_summary,  # Store the human-readable summary
                    "deviceName": item.get("deviceName"),
                    "roomId": item.get("roomId"),
                    "roomName": item.get("roomName"),
                    "component": item.get("component"),
                    "componentLabel": item.get("componentLabel"),
                },
            )
            
            return activity
        except Exception as e:
            logger.warning("Error parsing activity", error=str(e), item=item)
            return None

    @staticmethod
    def _map_device_type(smartthings_type: str) -> DeviceType:
        """Map SmartThings device type to internal type.
        
        Args:
            smartthings_type: SmartThings device type name
            
        Returns:
            Internal DeviceType
        """
        type_map = {
            "Light": DeviceType.LIGHT,
            "Switch": DeviceType.SWITCH,
            "Dimmer": DeviceType.LIGHT,
            "Color Light": DeviceType.LIGHT,
            "Color Dimmer": DeviceType.LIGHT,
            "Thermostat": DeviceType.THERMOSTAT,
            "Lock": DeviceType.LOCK,
            "Sensor": DeviceType.SENSOR,
            "Motion": DeviceType.SENSOR,
            "Contact": DeviceType.SENSOR,
            "Temperature": DeviceType.SENSOR,
            "Humidity": DeviceType.SENSOR,
            "Camera": DeviceType.CAMERA,
            "Blind": DeviceType.BLINDS,
            "Shade": DeviceType.BLINDS,
            "Outlet": DeviceType.PLUG,
            "Plug": DeviceType.PLUG,
            "Fan": DeviceType.FAN,
        }
        return type_map.get(smartthings_type, DeviceType.OTHER)
