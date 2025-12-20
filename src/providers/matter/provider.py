"""Matter provider stub."""

from typing import Any

from src.logging import get_logger
from src.models.device import CommandResult, Device, DeviceState, Location, Room
from src.providers.base import SmartHomeProvider

logger = get_logger(__name__)


class MatterProvider(SmartHomeProvider):
    """Matter protocol provider (stub).
    
    This is a placeholder implementation. To implement:
    1. Integrate with Matter controller library
    2. Discover and pair Matter devices
    3. Map Matter attributes to capabilities
    4. Implement device control via Matter commands
    
    See ADDING_PROVIDERS.md for detailed guide.
    """

    def __init__(self, controller_url: str, admin_pin: str = "") -> None:
        """Initialize Matter provider.
        
        Args:
            controller_url: Matter controller URL
            admin_pin: Optional admin PIN for pairing
        """
        self.controller_url = controller_url
        self.admin_pin = admin_pin
        self._authenticated = False

    async def authenticate(self) -> bool:
        """Authenticate with Matter controller."""
        logger.warning("MatterProvider.authenticate() not yet implemented")
        return False

    async def list_locations(self) -> list[Location]:
        """List locations."""
        logger.warning("MatterProvider.list_locations() not yet implemented")
        return []

    async def list_rooms(self, location_id: str) -> list[Room]:
        """List rooms."""
        logger.warning("MatterProvider.list_rooms() not yet implemented")
        return []

    async def list_devices(self, location_id: str | None = None) -> list[Device]:
        """List devices."""
        logger.warning("MatterProvider.list_devices() not yet implemented")
        return []

    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get device state."""
        logger.warning("MatterProvider.get_device_state() not yet implemented")
        raise NotImplementedError("Not yet implemented")

    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute device command."""
        logger.warning("MatterProvider.execute_command() not yet implemented")
        return CommandResult(
            device_id=device_id,
            success=False,
            message="Not yet implemented",
        )

    async def close(self) -> None:
        """Close connection."""
        logger.info("MatterProvider closed")
