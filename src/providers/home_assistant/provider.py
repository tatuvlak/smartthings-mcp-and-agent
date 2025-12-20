"""Home Assistant provider stub."""

from typing import Any

from src.logging import get_logger
from src.models.device import CommandResult, Device, DeviceState, Location, Room
from src.providers.base import SmartHomeProvider

logger = get_logger(__name__)


class HomeAssistantProvider(SmartHomeProvider):
    """Home Assistant smart home provider (stub).
    
    This is a placeholder implementation. To implement:
    1. Create HTTP client for Home Assistant API
    2. Map Home Assistant entities to Device objects
    3. Implement state reading and command execution
    
    See ADDING_PROVIDERS.md for detailed guide.
    """

    def __init__(self, base_url: str, token: str) -> None:
        """Initialize Home Assistant provider.
        
        Args:
            base_url: Home Assistant instance URL
            token: Long-lived access token
        """
        self.base_url = base_url
        self.token = token
        self._authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate with Home Assistant."""
        logger.warning("HomeAssistantProvider.authenticate() not yet implemented")
        return False

    async def list_locations(self) -> list[Location]:
        """List locations."""
        logger.warning("HomeAssistantProvider.list_locations() not yet implemented")
        return []

    async def list_rooms(self, location_id: str) -> list[Room]:
        """List rooms."""
        logger.warning("HomeAssistantProvider.list_rooms() not yet implemented")
        return []

    async def list_devices(self, location_id: str | None = None) -> list[Device]:
        """List devices."""
        logger.warning("HomeAssistantProvider.list_devices() not yet implemented")
        return []

    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get device state."""
        logger.warning("HomeAssistantProvider.get_device_state() not yet implemented")
        raise NotImplementedError("Not yet implemented")

    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute device command."""
        logger.warning("HomeAssistantProvider.execute_command() not yet implemented")
        return CommandResult(
            device_id=device_id,
            success=False,
            message="Not yet implemented",
        )

    async def close(self) -> None:
        """Close connection."""
        logger.info("HomeAssistantProvider closed")
