import asyncio
from src.config import Settings
from src.agent.agent import SmartHomeAgent

async def main():
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    try:
        # Test the status endpoint directly
        query = "check the status of frient smoke detector"
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        resp = await asyncio.wait_for(agent.process_command(query), timeout=20)
        print("\nAgent Response:")
        print(resp)
        print('='*60)
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
