"""Anthropic LLM client implementation."""

from typing import Any

from src.llm.base import LLMClient, LLMResponse, Message, ToolCall
from src.logging import get_logger

logger = get_logger(__name__)


class AnthropicClient(LLMClient):
    """Anthropic API client for Claude models.
    
    Supports Claude 3 and other Anthropic models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
    ) -> None:
        """Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key
            model: Model name (e.g., 'claude-3-sonnet-20240229')
        """
        self.api_key = api_key
        self.model = model
        self.client: Any = None  # Will be initialized with anthropic.AsyncAnthropic
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Anthropic async client."""
        try:
            from anthropic import AsyncAnthropic
            
            self.client = AsyncAnthropic(api_key=self.api_key)
            logger.info("Anthropic client initialized", model=self.model)
        except ImportError:
            logger.error(
                "Anthropic library not installed. "
                "Install with: pip install smartthings-mcp-and-agent[llm-anthropic]"
            )
            raise

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send messages to Anthropic and get response.
        
        Args:
            messages: List of Message objects
            tools: Optional list of tool definitions
            temperature: Response temperature
            max_tokens: Maximum response tokens
            
        Returns:
            LLMResponse with content and/or tool calls
        """
        try:
            # Convert Message objects to dict format for API
            api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Prepare API call
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": api_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if tools:
                kwargs["tools"] = tools

            # Call Anthropic API
            response = await self.client.messages.create(**kwargs)

            # Parse response content
            content = None
            tool_calls: list[ToolCall] | None = None

            for block in response.content:
                if hasattr(block, "text"):
                    content = block.text
                elif hasattr(block, "type") and block.type == "tool_use":
                    if tool_calls is None:
                        tool_calls = []
                    tool_calls.append(
                        ToolCall(
                            id=block.id,
                            name=block.name,
                            arguments=block.input,
                        )
                    )

            stop_reason = response.stop_reason or "end_turn"

            logger.debug(
                "Anthropic response",
                model=self.model,
                has_content=bool(content),
                tool_calls_count=len(tool_calls) if tool_calls else 0,
            )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason=stop_reason,
            )
        except Exception as e:
            logger.error("Anthropic API call failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close the Anthropic client."""
        if self.client:
            await self.client.close()
            logger.info("Anthropic client closed")
