"""Main entry point for the smart home MCP server and agent."""

import asyncio
import sys
from typing import Optional

from src.agent.agent import SmartHomeAgent
from src.config import Settings
from src.logging import configure_logging, get_logger
from src.mcp_server.server import MCPServer

logger = get_logger(__name__)


async def run_mcp_server() -> None:
    """Run the MCP server standalone."""
    logger.info("Starting MCP server...")
    settings = Settings()
    
    server = MCPServer(settings)
    await server.start()
    
    logger.info(
        "MCP server running",
        host=settings.mcp_server_host,
        port=settings.mcp_server_port,
    )
    
    try:
        # Keep server running
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop()


async def run_agent_demo() -> None:
    """Run the agent in demo mode for testing."""
    logger.info("Starting agent demo...")
    settings = Settings()
    
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    print("\n=== Smart Home Agent Demo ===")
    print("Enter commands to control your smart home.")
    print("Type 'quit' to exit.\n")
    
    try:
        while True:
            try:
                command = input("You: ").strip()
                if command.lower() == "quit":
                    break
                if not command:
                    continue
                
                response = await agent.process_command(command)
                print(f"Agent: {response}\n")
            except KeyboardInterrupt:
                print()
                break
    finally:
        await agent.stop()


async def run_interactive_chat() -> None:
    """Run the agent in interactive chat mode."""
    logger.info("Starting interactive chat...")
    settings = Settings()
    
    # Check LLM API key before starting
    if settings.llm_provider == "openai" and not settings.openai_api_key:
        print("\n[ERROR] OpenAI API key not configured!")
        print("\nTo use the chat interface:")
        print("  1. Get your API key from https://platform.openai.com/account/api-keys")
        print("  2. Add to .env: OPENAI_API_KEY=your_key_here")
        print("  3. Or set environment variable: set OPENAI_API_KEY=your_key_here")
        print("\nAlternatively, switch to Ollama for local LLM:")
        print("  1. Set LLM_PROVIDER=ollama in .env")
        print("  2. Install Ollama from https://ollama.ai")
        print("  3. Run: ollama pull llama2")
        print("  4. Run agent again")
        sys.exit(1)
    
    if settings.llm_provider == "anthropic" and not settings.anthropic_api_key:
        print("\n[ERROR] Anthropic API key not configured!")
        print("\nTo use the chat interface:")
        print("  1. Get your API key from https://console.anthropic.com/")
        print("  2. Add to .env: ANTHROPIC_API_KEY=your_key_here")
        print("  3. Or set environment variable: set ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)
    
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    print("\n=== Smart Home Control Chat ===")
    print("Chat with the agent to control your devices.")
    print("Commands are context-aware across the conversation.")
    print("Type 'devices' to see available devices.")
    print("Type 'quit' to exit.\n")
    
    try:
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == "quit":
                    break
                if user_input.lower() == "devices":
                    print(agent.get_devices_summary())
                    continue
                if not user_input:
                    continue
                
                response = await agent.process_command(user_input)
                print(f"Agent: {response}\n")
            except KeyboardInterrupt:
                print()
                break
    finally:
        await agent.stop()


async def main() -> None:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Smart Home MCP Server and Agent"
    )
    parser.add_argument(
        "mode",
        choices=["server", "agent", "chat"],
        help="Mode to run in",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(args.log_level)
    
    logger.info("Starting smart home system", mode=args.mode)
    
    try:
        if args.mode == "server":
            await run_mcp_server()
        elif args.mode == "agent":
            await run_agent_demo()
        elif args.mode == "chat":
            await run_interactive_chat()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
