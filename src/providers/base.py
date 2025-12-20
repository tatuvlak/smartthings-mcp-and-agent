"""Abstract base classes for smart home providers."""

from abc import ABC, abstractmethod
from typing import Any

from src.models.device import Capability, CommandResult, Device, DeviceState, Location, Room


class SmartHomeProvider(ABC):
    """Abstract base class for smart home ecosystem providers.
    
    All providers must implement this interface to work with the MCP server
    and agent. This allows seamless switching between different ecosystems.
    """

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the provider.
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            Exception: If authentication fails with detailed error
        """
        pass

    @abstractmethod
    async def list_locations(self) -> list[Location]:
        """List all locations available to the user.
        
        Returns:
            List of Location objects
            
        Raises:
            Exception: If unable to retrieve locations
        """
        pass

    @abstractmethod
    async def list_rooms(self, location_id: str) -> list[Room]:
        """List all rooms in a specific location.
        
        Args:
            location_id: The ID of the location
            
        Returns:
            List of Room objects for the location
            
        Raises:
            Exception: If unable to retrieve rooms
        """
        pass

    @abstractmethod
    async def list_devices(self, location_id: str | None = None) -> list[Device]:
        """List devices, optionally filtered by location.
        
        Args:
            location_id: Optional location ID to filter devices
            
        Returns:
            List of Device objects
            
        Raises:
            Exception: If unable to retrieve devices
        """
        pass

    @abstractmethod
    async def get_device_state(self, device_id: str) -> DeviceState:
        """Get the current state of a device.
        
        Args:
            device_id: The ID of the device
            
        Returns:
            DeviceState object with current state information
            
        Raises:
            Exception: If unable to retrieve device state
        """
        pass

    @abstractmethod
    async def execute_command(
        self,
        device_id: str,
        capability: str,
        command: str,
        arguments: dict[str, Any] | None = None,
    ) -> CommandResult:
        """Execute a command on a device.
        
        Args:
            device_id: The ID of the device
            capability: The capability type (e.g., 'switch', 'level')
            command: The command name (e.g., 'on', 'off')
            arguments: Optional arguments for the command
            
        Returns:
            CommandResult indicating success or failure
            
        Raises:
            Exception: If unable to execute command
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections or clean up resources.
        
        This should be called when the provider is no longer needed.
        """
        pass
