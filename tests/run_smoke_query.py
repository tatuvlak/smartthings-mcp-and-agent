import asyncio
from src.config import Settings
from src.agent.agent import SmartHomeAgent

async def main():
    settings = Settings()
    print(f"Settings: SmartThings set={bool(settings.smartthings_pat_token)}, LLM={settings.llm_provider}")

    agent = SmartHomeAgent(settings)
    await agent.start()
    try:
        query = "what is the status of frien smoke detector device"
        print(f"Query: {query}\n")
        try:
            resp = await asyncio.wait_for(agent.process_command(query), timeout=60)
        except asyncio.TimeoutError:
            print('ERROR: Agent response timed out')
            return
        print('\n---AGENT RESPONSE START---')
        print(resp)
        print('---AGENT RESPONSE END---\n')
    finally:
        await agent.stop()

if __name__ == '__main__':
    asyncio.run(main())
