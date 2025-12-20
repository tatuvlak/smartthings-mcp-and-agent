"""SmartThings API client for REST API interaction."""

from datetime import datetime
from typing import Any
from urllib.parse import urlencode
from src.utils.parsers import parse_device_raw

import httpx

from src.logging import get_logger

logger = get_logger(__name__)


class SmartThingsAPIClient:
    """Client for Samsung SmartThings REST API.
    
    Handles all HTTP communication with the SmartThings API.
    """

    def __init__(self, pat_token: str, base_url: str = "https://api.smartthings.com") -> None:
        """Initialize the SmartThings API client.
        
        Args:
            pat_token: Personal Access Token for authentication
            base_url: Base URL for the SmartThings API
        """
        self.pat_token = pat_token
        self.base_url = base_url
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "SmartThingsAPIClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Create HTTP client connection."""
        headers = {
            "Authorization": f"Bearer {self.pat_token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            headers=headers,
            base_url=self.base_url,
            timeout=30.0,
        )
        logger.info("SmartThings API client connected")

    async def close(self) -> None:
        """Close HTTP client connection."""
        if self.client:
            await self.client.aclose()
            logger.info("SmartThings API client closed")

    async def get(self, endpoint: str) -> dict[str, Any]:
        """Make a GET request to the API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Response JSON as dict
            
        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        logger.debug("GET request", endpoint=endpoint)
        response = await self.client.get(endpoint)
        response.raise_for_status()
        return response.json()

    async def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make a POST request to the API.
        
        Args:
            endpoint: API endpoint path
            data: Request body as dict
            
        Returns:
            Response JSON as dict
            
        Raises:
            httpx.HTTPError: If request fails
        """
        if not self.client:
            raise RuntimeError("Client not connected. Call connect() first.")

        logger.debug("POST request", endpoint=endpoint, data=data)
        response = await self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

    async def get_locations(self) -> list[dict[str, Any]]:
        """Get all locations.
        
        Returns:
            List of location objects
        """
        result = await self.get("/locations")
        return result.get("items", [])

    async def get_rooms(self, location_id: str) -> list[dict[str, Any]]:
        """Get rooms in a location.
        
        Args:
            location_id: The location ID
            
        Returns:
            List of room objects
        """
        result = await self.get(f"/locations/{location_id}/rooms")
        return result.get("items", [])

    async def get_devices(self, location_id: str | None = None) -> list[dict[str, Any]]:
        """Get devices, optionally filtered by location.
        
        Important: This method always uses the /devices endpoint (not /locations/{id}/devices)
        because the location-based endpoint is not reliably available on all SmartThings accounts.
        The location_id parameter is kept for API compatibility but is not used in the request.
        
        To filter by location, use the returned data and filter by the locationId field:
        
            devices = await client.get_devices()
            location_devices = [d for d in devices if d['locationId'] == location_id]
        
        Args:
            location_id: Deprecated. Kept for backward compatibility but not used.
                        Filter results using the locationId field instead.
            
        Returns:
            List of device objects
        """
        # Always use account-wide endpoint regardless of location_id parameter
        # The location-based endpoint (/locations/{id}/devices) may return 404
        result = await self.get("/devices")
        return result.get("items", [])

    async def get_device(self, device_id: str) -> dict[str, Any]:
        """Get a specific device's details and state.
        
        Args:
            device_id: The device ID
            
        Returns:
            Device object with current state
        """
        return await self.get(f"/devices/{device_id}")

    async def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Get a device's current component status.
        
        This endpoint returns the actual state of device components,
        including capabilities like smokeDetector, battery, switch, etc.
        
        Args:
            device_id: The device ID
            
        Returns:
            Device status object with components and their states
        """
        return await self.get(f"/devices/{device_id}/status")

    async def execute_device_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a command on a device.
        
        Args:
            device_id: The device ID
            capability: The capability ID
            command: The command name
            arguments: Optional command arguments
            
        Returns:
            Response from API
        """
        data = {
            "commands": [
                {
                    "component": "main",
                    "capability": capability,
                    "command": command,
                    "arguments": arguments or [],
                }
            ]
        }
        return await self.post(f"/devices/{device_id}/commands", data)

    def _parse_device_response(self, device_data: dict[str, Any]) -> dict[str, Any]:
        """Parse device response to extract key information.
        
        Args:
            device_data: Raw device data from API
            
        Returns:
            Normalized device data
        """
        parsed = parse_device_raw(device_data)
        # Map device type string to client's internal string representation
        return {
            "id": parsed.get("id"),
            "name": parsed.get("name"),
            "device_type": self._map_device_type(parsed.get("device_type_name", "")),
            "location_id": parsed.get("location_id"),
            "room_id": parsed.get("room_id"),
            "manufacturer": parsed.get("manufacturer"),
            "model": parsed.get("model"),
            "state": parsed.get("state", {}),
        }

    @staticmethod
    def _map_device_type(smartthings_type: str) -> str:
        """Map SmartThings device type to internal type.
        
        Args:
            smartthings_type: SmartThings device type name
            
        Returns:
            Internal device type
        """
        type_map = {
            "Light": "light",
            "Switch": "switch",
            "Dimmer": "light",
            "Thermostat": "thermostat",
            "Lock": "lock",
            "Sensor": "sensor",
            "Motion": "sensor",
            "Contact": "sensor",
            "Camera": "camera",
            "Blind": "blinds",
            "Shade": "blinds",
            "Outlet": "plug",
        }
        return type_map.get(smartthings_type, "other")

    async def get_activities(
        self,
        device_id: str | None = None,
        location_id: str | None = None,
        capability: str | None = None,
        attribute: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Get activity history for a device or location.
        
        Args:
            device_id: Optional device ID to filter activities
            location_id: Optional location ID to filter activities
            capability: Optional capability to filter by
            attribute: Optional attribute to filter by
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            limit: Optional result limit (default 100, max 500)
            
        Returns:
            Activity results from SmartThings API
            
        Raises:
            ValueError: If both device_id and location_id are provided, or neither
            httpx.HTTPError: If request fails
        """
        if device_id and location_id:
            raise ValueError("Cannot specify both device_id and location_id")
        
        if not device_id and not location_id:
            raise ValueError("Must specify either device_id or location_id")

        params: dict[str, str | int] = {}
        
        if device_id:
            params["device"] = device_id
        if location_id:
            params["location"] = location_id
        if capability:
            params["capability"] = capability
        if attribute:
            params["attribute"] = attribute
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        if limit:
            params["limit"] = limit

        query_string = urlencode(params)
        endpoint = f"/activities?{query_string}" if query_string else "/activities"
        
        logger.debug(
            "Querying activities",
            device_id=device_id,
            location_id=location_id,
            capability=capability,
            attribute=attribute,
        )
        
        return await self.get(endpoint)

    async def get_device_activities(
        self,
        device_id: str,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """Get activity history for a specific device.
        
        Args:
            device_id: Device ID to query
            limit: Optional result limit
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            
        Returns:
            Activity results from SmartThings API
            
        Raises:
            httpx.HTTPError: If request fails
        """
        return await self.get_activities(
            device_id=device_id,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )

    async def get_location_activities(
        self,
        location_id: str,
        limit: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> dict[str, Any]:
        """Get activity history for a specific location.
        
        Args:
            location_id: Location ID to query
            limit: Optional result limit
            start_time: Optional start time (ISO 8601 format)
            end_time: Optional end time (ISO 8601 format)
            
        Returns:
            Activity results from SmartThings API
            
        Raises:
            httpx.HTTPError: If request fails
        """
        return await self.get_activities(
            location_id=location_id,
            limit=limit,
            start_time=start_time,
            end_time=end_time,
        )

