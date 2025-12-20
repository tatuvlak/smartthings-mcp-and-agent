"""Abstract LLM client interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    """Represents a message in a conversation."""

    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ToolCall:
    """Represents a function/tool call made by the LLM."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """Response from an LLM."""

    content: str | None = None
    tool_calls: list[ToolCall] | None = None
    stop_reason: str = "end_turn"


class LLMClient(ABC):
    """Abstract base class for LLM providers.
    
    All LLM integrations must implement this interface to work with the agent.
    """

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send messages to the LLM and get a response.
        
        Args:
            messages: List of messages in conversation
            tools: Optional list of tool/function definitions
            temperature: Temperature for response generation (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLMResponse with generated content or tool calls
            
        Raises:
            Exception: If API call fails
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close any open connections."""
        pass
