import asyncio
from src.config import Settings
from src.agent.agent import SmartHomeAgent

async def main():
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    try:
        # Test ambiguous query
        queries = [
            "what is the status of tv",  # Ambiguous - could match TV and Smart Monitor
            "check the status of samsung tv",  # More specific
        ]
        
        for query in queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print('='*60)
            resp = await asyncio.wait_for(agent.process_command(query), timeout=20)
            print(resp)
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
