import aiohttp
import asyncio
import time

SERVER_ADDR = f"localhost:8080"


async def make_requests(client):
    start = time.perf_counter()
    async with client.get(f"http://{SERVER_ADDR}/") as resp:
        r = await resp.text()
    return time.perf_counter() - start


async def main():
    CLIENTS = 100
    async with aiohttp.ClientSession() as client:
        res = await asyncio.gather(
            *[make_requests(client) for _ in range(CLIENTS)])
    print(res)


if __name__ == "__main__":
    asyncio.run(main())
