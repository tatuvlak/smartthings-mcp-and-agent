"""Amazon Alexa provider stub."""

from typing import Any

from src.logging import get_logger
from src.models.device import CommandResult, Device, DeviceState, Location, Room
from src.providers.base import SmartHomeProvider

logger = get_logger(__name__)


class AlexaProvider(SmartHomeProvider):
    """Amazon Alexa smart home provider (stub).
    
    This is a placeholder implementation. To implement:
    1. Set up OAuth2 flow with Alexa API
    2. Fetch customer devices and their states
    3. Map Alexa capabilities to internal model
    4. Send directives to control devices
    
    See ADDING_PROVIDERS.md for detailed guide.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> None:
        """Initialize Alexa provider.
        
        Args:
            client_id: Alexa OAuth client ID
            client_secret: Alexa OAuth client secret
            refresh_token: Stored refresh token
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._authenticated = False
        self._access_token = ""

    async def authenticate(self) -> bool:
        """Authenticate with Alexa API."""
        logger.warning("AlexaProvider.authenticate() not yet implemented")
        return False

    async def list_locations(self) -> list[Location]:
        """List locations."""
        logger.warning("AlexaProvider.list_locations() not yet implemented")
        return []

    async def list_rooms(self, location_id: str) -> list[Room]:
        """List rooms."""
        logger.warning("AlexaProvider.list_rooms() not yet implemented")
        return []

    async def list_devices(self, location_id: str | None = None) -> list[Device]:
        """List devices."""
        logger.warning("AlexaProvider.list_devices() not yet implemented")
        return []

    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get device state."""
        logger.warning("AlexaProvider.get_device_state() not yet implemented")
        raise NotImplementedError("Not yet implemented")

    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute device command."""
        logger.warning("AlexaProvider.execute_command() not yet implemented")
        return CommandResult(
            device_id=device_id,
            success=False,
            message="Not yet implemented",
        )

    async def close(self) -> None:
        """Close connection."""
        logger.info("AlexaProvider closed")
