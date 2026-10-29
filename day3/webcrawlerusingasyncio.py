
"""
Async fast for API calls, not number crunching:

Async (asyncio) runs on a single thread with one event loop. It gets speed from not blocking
 — when a coroutine hits await on I/O (network call, disk read, sleep), 
 it hands control back to the event loop, which runs other coroutines while waiting for the OS to 
 signal "data's ready." Dozens of API calls can be "in flight" concurrently because the CPU 
 isn't doing anything during the wait — it's just idle, waiting on the network.

Number crunching (e.g. a tight loop computing primes) uses the CPU the whole time — 
there's no "waiting" to yield during. If you await a CPU-bound function, nothing is released back 
to the event loop at the right moments; the one thread just grinds through it, 
blocking every other coroutine. You get zero parallelism — it runs exactly as fast 
as sequential code,maybe slower from async overhead. For CPU-bound work you need actual parallelism: 
multiprocessing (separate processes, real parallel cores) or 
sometimes threads if the work releases the GIL (e.g. numpy/C extensions).

Rule of thumb: async helps when the bottleneck is waiting; it does nothing when the bottleneck is 
computing.

What a Semaphore protects you from:

A Semaphore(n) caps how many coroutines can be inside a critical section at once — 
it holds a counter starting at n; acquire() decrements it (blocking if it hits 0), 
release() increments it back.

It protects you from overwhelming a limited resource when you fire off many concurrent tasks — 
e.g. your crawler's workers=5 pattern does this implicitly via a fixed task count, 
but a semaphore does it more directly: wrap asyncio.Semaphore(10) around your client.get() calls 
and even if you spin up 1000 coroutines, only 10 actual HTTP requests run at a time. 
Without it you'd slam a server with hundreds of simultaneous requests, get rate-limited/banned, 
exhaust file descriptors, or blow past a DB's connection pool limit.

So: a lock (asyncio.Lock) protects shared state from concurrent mutation (only 1 at a time); 
a semaphore protects a shared resource's capacity from being exceeded (only N at a time).



"""


import asyncio
import html.parser
import pathlib
import urllib.parse
import time
from typing import Callable, Iterable
from unittest import result

import httpx  # https://github.com/encode/httpx

"""
async def do_work(item):
    await asyncio.sleep(1)  # Simulate some work
    print(f"Finished processing item {item}")

async def demo_main():
    print("Start of main coroutine")

    start= time.perf_counter()
    print(f"Start time: {start}")

    todo = ["dolaundry", "clean kitchen", "read a book"]  # Example list of items to process

    tasks = [asyncio.create_task(do_work(item)) for item in todo]
    done,pending =await asyncio.wait(tasks)

    for task in done:
       result=  task.result()  # Retrieve the result of the completed task


    #or
    coros = [asyncio.create_task(do_work(item)) for item in todo]
    results =await asyncio.gather(*coros, return_exceptions=True)

    #or
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(do_work(item)) for item in todo]
        for task in tasks:
            result = await task 

    end= time.perf_counter()
    print(f"End time: {end}")
    print(f"Elapsed time: {end - start}")


asyncio.run(demo_main())

"""

#WEBCRAWLER


class UrlFilterer:
    def __init__(
            self,
            allowed_domains: set[str] | None = None,
            allowed_schemes: set[str] | None = None,
            allowed_filetypes: set[str] | None = None,
    ):
        self.allowed_domains = allowed_domains
        self.allowed_schemes = allowed_schemes
        self.allowed_filetypes = allowed_filetypes

    def filter_url(self, base: str, url: str) -> str | None:
        url = urllib.parse.urljoin(base, url)
        url, _frag = urllib.parse.urldefrag(url)
        parsed = urllib.parse.urlparse(url)
        if (self.allowed_schemes is not None
                and parsed.scheme not in self.allowed_schemes):
            return None
        if (self.allowed_domains is not None
                and parsed.netloc not in self.allowed_domains):
            return None
        ext = pathlib.Path(parsed.path).suffix
        if (self.allowed_filetypes is not None
                and ext not in self.allowed_filetypes):
            return None
        return url


class UrlParser(html.parser.HTMLParser):
    def __init__(self, base: str, filter_url: Callable[[str,str],str | None]):
        super().__init__()
        self.base = base
        self.filter_url = filter_url
        self.found_links = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag != 'a':
            return

        for attr, url in attrs:
            if attr == "href" and url is not None:
                filtered_url = self.filter_url(self.base, url)
                if filtered_url is not None:
                    self.found_links.add(filtered_url)

class Crawler:
    def __init__(self, 
                 client: httpx.AsyncClient,
                 urls:Iterable[str],
                 filter_url: Callable[[str,str],str | None],
                 workers:int =10,
                 limit:int =25):
        self.client = client
        self.todo=asyncio.Queue()
        self.seen = set()
        self.done = set()
        self.start_urls = set(urls)
        self.filter_url = filter_url
        self.num_workers = workers
        self.limit = limit
        self.total = 0

    async def fetch(self, url):
        await asyncio.sleep(1)  # Simulate fetching a URL
        return f"Content from {url}"

    async def crawl(self):
        tasks = [asyncio.create_task(self.fetch(url)) for url in self.start_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def run(self):
        await self.on_found_links(self.start_urls) #prime the queue with initial URLs
        workers=[
            asyncio.create_task(self.worker()) for _ in range(self.num_workers)
        ]

        await self.todo.join()  # Wait for all tasks to be processed
        for worker in workers:
            worker.cancel()
    
    async def worker(self):
        while True:
            try:
                await self.process_one()  # Get the next URL to process from the queue
            except asyncio.CancelledError:
                return
            
    async def process_one(self):
        url = await self.todo.get()
        try:
            await self.crawl(url)
            self.total += 1
        except Exception as e:#retry  
            pass
            #await asyncio.sleep(1)  # Wait a bit before retrying
            #print(f"Error processing {url}: {e}")
            #await self.todo.put(url)  # Requeue the URL for retry
        finally:
            self.todo.task_done()

    async def crawl(self, url):
        #rate teh limit
        await asyncio.sleep(.1)  # Simulate fetching a URL
        response =await self.client.get(url,follow_redirects=True)

        found_links = await self.parsse_links(base=str(response.url), text=response.text)

        await self.on_found_links(found_links)
        self.done.add(url)

    async def parsse_links(self, base: str, text: str) -> set[str]:
        # Implement your link parsing logic here
        # For example, you could use BeautifulSoup or regex to extract links
        # Return a set of found links
        parser = UrlParser(base, self.filter_url)
        parser.feed(text)
        return parser.found_links
    
    async def on_found_links(self, urls: set[str]):
       new =urls - self.seen
       self.seen.update(new)


     #await save to data base or file here

       for url in new:
           await self.todo.put(url)

    async def put_todo(self, url: str):
        if self.total >= self.limit:
            return
        await self.todo.put(url)
        self.total += 1


async def main():
    filterer = UrlFilterer(
        allowed_domains={"mcoding.io"},
        allowed_schemes={"http", "https"},
        allowed_filetypes={".html", ".php", ""},
    )

    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        crawler = Crawler(
            client=client,
            urls=["https://mcoding.io/"],
            filter_url=filterer.filter_url,
            workers=5,
            limit=30,
        )
        await crawler.run()
    end = time.perf_counter()

    seen = sorted(crawler.seen)
    print("Results:")
    for url in seen:
        print(url)
    print(f"Crawled: {len(crawler.done)} URLs")
    print(f"Found: {len(seen)} URLs")
    print(f"Done in {end - start:.2f}s")


if __name__ == '__main__':
    asyncio.run(main(), debug=True)


    