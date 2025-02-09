import asyncio
import os
from dialogllm.core.client import LLMClient

async def main():
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379") # Default Redis URL
    client = LLMClient(redis_url=redis_url)
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())