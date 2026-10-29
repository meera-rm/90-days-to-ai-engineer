import asyncio, httpx

async def fetch(client, url, limit):
    async with limit:
        r = await client.get(url, timeout=10)
        return url, r.status_code

async def main(urls):
    limit = asyncio.Semaphore(5)
    async with httpx.AsyncClient() as client:
        return await asyncio.gather(*(fetch(client, u, limit) for u in urls))