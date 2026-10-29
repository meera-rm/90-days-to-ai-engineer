
import asyncio
import time


running =0
max_running=0


def reset() -> None:
    global running, max_running
    running = max_running = 0

async def fetch(url):
    global running, max_running
    running += 1
    if not url.startswith("http"):
            raise ValueError("Invalid URL")
    #if the URL is not valid, raise an error
    if running > max_running:
        max_running = running
    
    try:
        if "slow" in url:
            await asyncio.sleep(5)
        else:
            await asyncio.sleep(0.2)  # Simulate fetching a webpage
        return f"<html><body>Fake content from {url}</body></html>"
    finally:
        running -= 1

"""
   
async def main():
    global running, max_running
    start = time.perf_counter()
    url = "http://example.com"
    content = await fetch_fake_webpage(url)
    print(content)
    print(f"took {time.perf_counter() - start:.2f}s")

    start = time.perf_counter()
    url = "http://slow.example.com"
    content = await fetch_fake_webpage(url)
    print(content)
    print(f"took {time.perf_counter() - start:.2f}s")

    max_running = 0
    await asyncio.gather(*(fetch_fake_webpage(f"http://site{i}.com") for i in range(5)))
    print("gather max_running:", max_running)      # expect 5
    
    max_running = 0
    for _ in range(5):
        await fetch_fake_webpage(f"http://site{_}.com")
    print("loop max_running:", max_running)        # expect 1

if __name__ == "__main__":
    
    asyncio.run(main()) 

    """