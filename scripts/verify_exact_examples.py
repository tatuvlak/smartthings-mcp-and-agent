#!/usr/bin/env python
"""Verify the exact examples from the user request."""

import asyncio
from src.agent.agent import SmartHomeAgent
from src.config import Settings


async def main():
    print("\n" + "="*80)
    print("VERIFICATION: Testing User's Specific Examples")
    print("="*80)
    
    settings = Settings()
    agent = SmartHomeAgent(settings)
    await agent.start()
    
    # The exact user examples
    queries = [
        "what is current cycle type in pralka",
        "what is current washer mode in pralka",
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"User Query: {query}")
        print(f"{'-'*80}")
        
        response = await agent.process_command(query)
        
        print(f"\nAgent Response:")
        print(response)
        
        # Check for full state dump (should NOT see this)
        if "Status:" in response and "demandResponseLoadControl" in response:
            print("\n[WARNING] Response contains full device state!")
        else:
            print("\n[GOOD] Response is filtered and concise")
        
        # Check line count
        lines = response.split('\n')
        print(f"Response length: {len(lines)} lines")
        if len(lines) > 30:
            print("  [WARNING] Response is very long")
        else:
            print("  [GOOD] Response is concise")
    
    await agent.stop()
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
