import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.dependencies import get_agent_service


async def main() -> None:
    agent = get_agent_service()
    query = "weather in Moscow and usd to rub"
    async for event in agent.run_stream(query):
        print(event)


if __name__ == "__main__":
    asyncio.run(main())
