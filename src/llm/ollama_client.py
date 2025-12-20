"""Ollama LLM client implementation for local LLMs."""

from typing import Any

from src.llm.base import LLMClient, LLMResponse, Message, ToolCall
from src.logging import get_logger

logger = get_logger(__name__)


class OllamaClient(LLMClient):
    """Local Ollama client for running LLMs locally.
    
    Supports any model available in Ollama (Llama 2, Mistral, etc).
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
    ) -> None:
        """Initialize Ollama client.
        
        Args:
            base_url: Base URL of Ollama server
            model: Model name (e.g., 'llama2', 'mistral')
        """
        self.base_url = base_url
        self.model = model
        self.client: Any = None  # Will be initialized with ollama library
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Ollama async client."""
        try:
            import ollama
            
            # Ollama client is not async-first but we'll handle it gracefully
            self.ollama = ollama
            logger.info("Ollama client initialized", model=self.model, base_url=self.base_url)
        except ImportError:
            logger.error(
                "Ollama library not installed. "
                "Install with: pip install smartthings-mcp-and-agent[llm-ollama] "
                "or download from https://ollama.ai"
            )
            raise

    async def chat(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send messages to Ollama and get response.
        
        Args:
            messages: List of Message objects
            tools: Optional list of tool definitions (not supported by Ollama)
            temperature: Response temperature
            max_tokens: Maximum response tokens
            
        Returns:
            LLMResponse with content
            
        Note:
            Ollama doesn't support function calling like cloud APIs.
            Tool definitions are ignored, but tool calls can be parsed from
            the text response if the model outputs structured JSON.
        """
        try:
            # Convert Message objects to dict format for API
            api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Note: The ollama Python package is not async
            # For production, consider using httpx directly or integrate with async wrapper
            response = self.ollama.chat(
                model=self.model,
                messages=api_messages,
                stream=False,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            )

            content = response.get("message", {}).get("content", "")

            # Note: Ollama doesn't support function calling, but we can attempt
            # to parse tool calls from structured JSON in the response
            tool_calls = self._parse_tool_calls_from_text(content)

            logger.debug(
                "Ollama response",
                model=self.model,
                content_length=len(content),
                tool_calls_count=len(tool_calls) if tool_calls else 0,
            )

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason="end_turn",
            )
        except Exception as e:
            logger.error("Ollama call failed", error=str(e))
            raise

    @staticmethod
    def _parse_tool_calls_from_text(content: str) -> list[ToolCall] | None:
        """Attempt to parse tool calls from model output.
        
        This is a best-effort attempt to extract function calls from plain text.
        It looks for JSON patterns that resemble tool calls.
        
        Args:
            content: The model's text response
            
        Returns:
            List of ToolCall objects if found, None otherwise
        """
        import json
        import re
        
        try:
            # Look for JSON blocks in the response
            json_pattern = r"```json\n(.*?)\n```"
            matches = re.findall(json_pattern, content, re.DOTALL)
            
            if not matches:
                return None
            
            tool_calls = []
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and "name" in data and "arguments" in data:
                        tool_calls.append(
                            ToolCall(
                                id=data.get("id", "ollama-tool"),
                                name=data["name"],
                                arguments=data.get("arguments", {}),
                            )
                        )
                except json.JSONDecodeError:
                    continue
            
            return tool_calls if tool_calls else None
        except Exception:
            return None

    async def close(self) -> None:
        """Close the Ollama client."""
        logger.info("Ollama client closed")
