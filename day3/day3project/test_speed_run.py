import asyncio
import time

import my_fake_webpage as fake_web
from speed_run import fetch_one, fetch_all, fetch_all_limited, fetch_all_safe

URLS = [f"http://site{i}.com" for i in range(20)]


def reset() -> None:
       global running, max_running
       running = max_running = 0


def expected_length(url: str) -> int:
    return len(f"<html><body>Fake content from {url}</body></html>")

def test_fetch_one_returns_url_and_length():
    fake_web.reset()
    url = URLS[0]
    result = asyncio.run(fetch_one(url))
    assert result == (url, expected_length(url))



def test_fetch_all_is_concurrent_and_keeps_order():
    fake_web.reset()

    start = time.perf_counter()
    results = asyncio.run(fetch_all(URLS))
    elapsed = time.perf_counter() - start

    # Correct values, in the same order as URLS
    assert results == [(url, expected_length(url)) for url in URLS]
    # Fast: together ≈ 0.2s, one-by-one would be ≈ 4s
    assert elapsed < 0.5, f"took {elapsed:.2f}s, looks like one at a time"
    # All 20 ran at the same time
    assert fake_web.max_running == 20

def test_fetch_all_limited_never_exceeds_limit():
    fake_web.reset()

    start = time.perf_counter()
    results = asyncio.run(fetch_all_limited(URLS, limit=3))
    elapsed = time.perf_counter() - start

    assert results == [(url, expected_length(url)) for url in URLS]
    # Never more than 3 at once...
    assert fake_web.max_running <= 3
    # ...but really 3, not secretly one at a time
    assert fake_web.max_running == 3
    # 20 pages / 3 at a time ≈ 7 rounds × 0.2s ≈ 1.4s, and one-by-one would be 4s
    assert elapsed < 2.0, f"took {elapsed:.2f}s"


def test_fetch_all_safe_gives_up_on_slow_pages():
    fake_web.reset()
    urls = ["http://site0.com", "http://slow.example.com", "http://site2.com"]

    start = time.perf_counter()
    results = asyncio.run(fetch_all_safe(urls, timeout=0.5))
    elapsed = time.perf_counter() - start

    # Normal pages come back with their length
    assert results[0] == ("http://site0.com", expected_length("http://site0.com"))
    assert results[2] == ("http://site2.com", expected_length("http://site2.com"))
    # The slow page gives up and returns None
    assert results[1] == ("http://slow.example.com", None)
    # Nobody waited the full 5 seconds
    assert elapsed < 1.5, f"took {elapsed:.2f}s, the slow page held everyone up"

  
