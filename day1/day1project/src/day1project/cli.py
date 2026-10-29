
"""import argparse
    import json
    import sys
    from pathlib import Path

    import asyncio

    from extractor.pipeline import extract_job_posting  # your existing function


    def main():
        parser = argparse.ArgumentParser(description="Concurrent web fetcher")




  parser.add_argument("file", type=Path, help="Path to the input file containing job postings.")
    parser.add_argument("-o", "--output", type=Path, help="Path to the output JSON file.")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: File {args.file} does not exist.", file=sys.stderr)
        sys.exit(1)

    job_postings = extract_job_posting(args.file)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(job_postings, f, indent=4)
    else:
        print(json.dumps(job_postings, indent=4))

        if __name__ == "__main__":
    main()



import time


def count():
    print("One")
    time.sleep(4)
    print("Two")
    time.sleep(2)

def main():
    for _ in range(3):
        count()

if __name__ == "__main__":
    start = time.perf_counter()
    main()
    elapsed = time.perf_counter() - start
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")




import asyncio

async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")
    await asyncio.sleep(1)

async def main():
    await asyncio.gather(count())

if __name__ == "__main__":
    import time

    start = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - start
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")



import asyncio
import random

COLORS = (
    "\033[0m",  # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)

async def main():
    return await asyncio.gather(
        makerandom(1, 9),
        makerandom(2, 8),
        makerandom(3, 8),
    )

async def makerandom(delay, threshold=6):
    color = COLORS[delay]
    print(f"{color}Initiated makerandom({delay}).")
    while (number := random.randint(0, 10)) <= threshold:
        print(f"{color}makerandom({delay}) == {number} too low; retrying.")
        await asyncio.sleep(delay)
    print(f"{color}---> Finished: makerandom({delay}) == {number}" + COLORS[0])
    return number

if __name__ == "__main__":
    random.seed(444)
    r1, r2, r3 = asyncio.run(main())
    print()
    print(f"r1: {r1}, r2: {r2}, r3: {r3}")
"""






import argparse
from email import parser

import aiohttp # type: ignore
import asyncio

import json
import aiofiles

from day1project.validate_jobs import validate_jobs




def save_json_async(filepath: str, data: dict):
    # 1. Serialize the dictionary to a JSON string (fast, synchronous)
    with open(filepath, "w", encoding="utf-8") as f:
        json_string = json.dumps(data, indent=4)
        f.write(json_string)
    print(f"Saved {len(data)} results to {filepath}")

    # 2. Write the string to the file asynchronously
    #async with aiofiles.open(filepath, mode='w', encoding='utf-8') as f:
    #    await f.write(json_string)

async def check(session, sem, url, retries=3): # type: ignore
    #async with aiohttp.ClientSession() as session:
    for attempt in range(1, retries + 1):
        try:
            async with sem:
                async with session.get(url) as response:
                    print(f"{url}: status -> {response.status}") 
                    print(f"{url}: attempt -> {attempt}")
                    if response.status in (429, 503) and attempt < retries: 
                        should_retry = True
                        #await asyncio.sleep(1)  # Wait a bit before retrying
                        #await asyncio.sleep(2 ** (attempt - 1))
                        #continue
                    res=None
                    if response.status == 200: # Only process the response if the status is 200 OK otherwise you get contentTypeerrors even if the response is valid JSON
                        res = await response.json()
                    return {"attempts":attempt, "url": url, "status": response.status, "data": res, "error": None}
                
                 
        except asyncio.TimeoutError as e:
            #print(f"ur{url}:  {e!r}")
            #print(f"{url}: error -> {type(e).__name__}")
            if attempt == retries:
                return {"attempts":attempt, "url": url, "status": None, "data": None, "error": type(e).__name__}
        except aiohttp.ClientError as e:
            #print(f"{url}: error -> {type(e).__name__}")
            if attempt == retries:
                return {"attempts":attempt, "url": url, "status": None, "data": None, "error": type(e).__name__}
        await asyncio.sleep(2 ** (attempt - 1))

    # The retry logic is handled inside the for loop, so the following code is redundant and can be removed.
 
   


"""Option B: save the response to a file

resp in the docs example is the same object as your response. The file-writing block goes inside the async with session.get(...) block, because the stream only exists while the connection is open:

python
async with session.get(url) as response:
    print(f"{url}: status -> {response.status}")
    if response.status == 200:
        filename = ...   # you need a different name per URL
        with open(filename, 'wb') as fd:
            async for chunk in response.content.iter_chunked(1024):
                fd.write(chunk)
"""
def read_urls(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f if line.strip()]


async def fetch_all(urls: list[str], retries: int, timeout: float, concurrency: int) -> list[dict]:
    # your current async main logic: session, gather, return results
    timeout = aiohttp.ClientTimeout(total=2)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        sem = asyncio.Semaphore(concurrency)
        results = await asyncio.gather(*(check(session, sem, url, retries) for url in urls))
        return results



def main() -> None:


    parser = argparse.ArgumentParser(description="Concurrently fetch URLs with retries and save JSON.")
    parser.add_argument("input", help="Text file with one URL per line")
    parser.add_argument("-o", "--output", default="results.json", help="Where to save results")
    # add --retries (int, default 3), --timeout (float, default 10), --concurrency (int, default 5)
    parser.add_argument("--retries", type=int, default=3, help="Number of retries for each URL")
    parser.add_argument("--timeout", type=float, default=10, help="Timeout for each request in seconds")
    parser.add_argument("--concurrency", type=int, default=5, help="Maximum number of concurrent requests")
    args = parser.parse_args()


    #await asyncio.gather(*(check(url) for url in websites))
    timeout = aiohttp.ClientTimeout(total=args.timeout)

    websites = read_urls(args.input)

    results = asyncio.run(fetch_all(websites, retries=args.retries, timeout=args.timeout, concurrency=args.concurrency))

    save_json_async(args.output, results)

    for r in results:
        print(r)

    raw_jobs: list[dict] = []
    for r in results:
        data = r.get("data")
        if isinstance(data, list):
            raw_jobs.extend(data)
        elif isinstance(data, dict):
            raw_jobs.append(data)

    clean, errors = validate_jobs(raw_jobs)

    print(f"\n{len(clean)} valid jobs, {len(errors)} errors out of {len(raw_jobs)} fetched records")

    with open("clean.json", "w", encoding="utf-8") as f:
        json.dump([job.model_dump(mode="json") for job in clean], f, indent=4)

    with open("rejected.txt", "w", encoding="utf-8") as f:
        for err in errors:
            f.write(err + "\n")

    #asyncio.run(main())
    

if __name__ == "__main__":
    #asyncio.run(main())
    main()