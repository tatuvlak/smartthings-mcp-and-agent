"""OpenAI LLM client implementation."""

from typing import Any

from src.llm.base import LLMClient, LLMResponse, Message, ToolCall
from src.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient(LLMClient):
    """OpenAI API client for GPT models.
    
    Supports GPT-4, GPT-4 Turbo, GPT-3.5, and other OpenAI models.
    """

    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview") -> None:
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., 'gpt-4-turbo-preview', 'gpt-3.5-turbo')
        """
        self.api_key = api_key
        self.model = model
        self.client: Any = None  # Will be initialized with openai.AsyncOpenAI
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the OpenAI async client."""
        try:
            from openai import AsyncOpenAI
            
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized", model=self.model)
        except ImportError:
            logger.error(
                "OpenAI library not installed. "
                "Install with: pip install smartthings-mcp-and-agent[llm-openai]"
            )
            raise

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send messages to OpenAI and get response.
        
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
                kwargs["tools"] = [{"type": "function", "function": tool} for tool in tools]

            # Call OpenAI API
            response = await self.client.chat.completions.create(**kwargs)

            # Parse response
            choice = response.choices[0]

            # Check for tool calls
            tool_calls: list[ToolCall] | None = None
            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=self._parse_function_args(tc.function.arguments),
                    )
                    for tc in choice.message.tool_calls
                ]

            content = choice.message.content
            stop_reason = choice.finish_reason or "end_turn"

            logger.debug(
                "OpenAI response",
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
            logger.error("OpenAI API call failed", error=str(e))
            raise

    @staticmethod
    def _parse_function_args(args_str: str) -> dict[str, Any]:
        """Parse function arguments from JSON string.
        
        Args:
            args_str: JSON string of arguments
            
        Returns:
            Parsed arguments dict
        """
        import json
        
        try:
            return json.loads(args_str)
        except json.JSONDecodeError:
            return {}

    async def close(self) -> None:
        """Close the OpenAI client."""
        if self.client:
            await self.client.close()
            logger.info("OpenAI client closed")
