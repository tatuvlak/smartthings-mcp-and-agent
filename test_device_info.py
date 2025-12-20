import asyncio
from src.config import Settings
from src.agent.agent import SmartHomeAgent

async def main():
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    try:
        query = "get all info on frient smoke detector"
        print(f"Query: {query}\n")
        resp = await asyncio.wait_for(agent.process_command(query), timeout=15)
        print("---RESPONSE---")
        print(resp)
        print("---END---")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
