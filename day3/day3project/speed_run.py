"""Day 3 · The speed run

20 pages, 0.2 seconds each. One by one that's 4 seconds. Together it's about 0.2.
Use fake_web.fetch(url) for every request.

Run `python quest.py 3` after each TODO.
"""
import asyncio  # noqa: F401

import my_fake_webpage as fake_web


async def fetch_one(url: str) -> tuple[str, int]:
    """TODO 3.1 · Fetch one page with `await fake_web.fetch(url)` and return (url, length of the page)."""
    content = await fake_web.fetch(url)
    return url, len(content)


async def fetch_all(urls: list[str]) -> list[tuple[str, int]]:
    """TODO 3.2 · Fetch every url AT THE SAME TIME (hint: asyncio.gather) and return results in the same order."""
    tasks = [fetch_one(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


async def fetch_all_limited(urls: list[str], limit: int = 3) -> list[tuple[str, int]]:
    """TODO 3.3 · Same as fetch_all, but never more than `limit` fetches at once (hint: asyncio.Semaphore)."""
    semaphore = asyncio.Semaphore(limit)

    async def fetch_limited(url: str) -> tuple[str, int]:
        async with semaphore:
            return await fetch_one(url)

    tasks = [fetch_limited(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results


async def fetch_all_safe(urls: list[str], timeout: float = 0.5) -> list[tuple[str, int | None]]:
    """TODO 3.4 · Same as fetch_all, but a page that takes longer than `timeout` seconds
    gives (url, None) instead of making everyone wait (hint: asyncio.wait_for and TimeoutError)."""
    async def fetch_safe(url: str) -> tuple[str, int | None]:
        try:
            return await asyncio.wait_for(fetch_one(url), timeout=timeout)
        except asyncio.TimeoutError:
            return url, None

    tasks = [fetch_safe(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

