#### Coroutines for LLM
LLM API SDK
API SDKs—Google GenAI, OpenAI, Claude, and others— provide coroutine functions. You can easily leverage coroutines for AI like this:

# Synchronous inference function of OpenAI SDK
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": prompt}],
)

# Coroutine function of OpenAI SDK
client = AsyncOpenAI()
response = await client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": prompt}],
)
# Synchronous inference function of Google GenAI SDK
client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash", contents=prompt
)

# Coroutine function of Google GenAI SDK
client = genai.Client()
response = await client.aio.models.generate_content(
    model="gemini-2.5-flash", contents=prompt
)
For the OpenAI SDK, there’s a specific client for async. For Google GenAI, you should add aio after client. Other SDKs, such as Claude and Ollama, also support coroutine functions.

Example comparing async and sync functions
Input

import asyncio
import time
import os
import logging
from dotenv import load_dotenv
from google import genai
from openai import OpenAI, AsyncOpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

load_dotenv()

# --- Sync Functions ---

def sync_chat_google(prompt: str):
    logger.info("Starting Sync Google GenAI request...")
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        logger.info("Finished Sync Google GenAI request.")
        return f"Google (Sync): {response.text[:50]}..."
    except Exception as e:
        logger.error(f"Sync Google Error: {e}")
        return f"Google (Sync) Error: {e}"

def sync_chat_openai(prompt: str):
    logger.info("Starting Sync OpenAI request...")
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort="low"
        )
        logger.info("Finished Sync OpenAI request.")
        return f"OpenAI (Sync): {response.choices[0].message.content[:50]}..."
    except Exception as e:
        logger.error(f"Sync OpenAI Error: {e}")
        return f"OpenAI (Sync) Error: {e}"

def run_sync():
    logger.info("--- Starting Sync Execution ---")
    start_time = time.time()

    prompt = "Explain asyncio in one sentence."
    res_google = sync_chat_google(prompt)
    res_openai = sync_chat_openai(prompt)

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n[Sync Results]")
    print(res_google)
    print(res_openai)
    print(f"Total Sync Time: {total_time:.2f} seconds\n")
    return total_time

# --- Async Functions ---

async def async_chat_google(prompt: str):
    logger.info("Starting Async Google GenAI request...")
    try:
        client = genai.Client()
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        logger.info("Finished Async Google GenAI request.")
        return f"Google (Async): {response.text[:50]}..."
    except Exception as e:
        logger.error(f"Async Google Error: {e}")
        return f"Google (Async) Error: {e}"

async def async_chat_openai(prompt: str):
    logger.info("Starting Async OpenAI request...")
    try:
        client = AsyncOpenAI()
        response = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort="low"
        )
        logger.info("Finished Async OpenAI request.")
        return f"OpenAI (Async): {response.choices[0].message.content[:50]}..."
    except Exception as e:
        logger.error(f"Async OpenAI Error: {e}")
        return f"OpenAI (Async) Error: {e}"

async def run_async():
    logger.info("--- Starting Async Execution ---")
    start_time = time.time()

    prompt = "Explain asyncio in one sentence."
    # Schedule both calls concurrently
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(async_chat_google(prompt))
        task2 = tg.create_task(async_chat_openai(prompt))

    results = [task1.result(), task2.result()]

    end_time = time.time()
    total_time = end_time - start_time

    print(f"\n[Async Results]")
    for res in results:
        print(res)
    print(f"Total Async Time: {total_time:.2f} seconds\n")
    return total_time

async def main():
    logger.info("Starting Comparison...")

    sync_time = run_sync()
    async_time = await run_async()

    print("-" * 30)
    print(f"Sync Time:  {sync_time:.2f}s")
    print(f"Async Time: {async_time:.2f}s")
    if async_time < sync_time:
        print(f"Conclusion: Async was {sync_time / async_time:.2f}x faster!")
    else:
        print("Conclusion: Async was not faster (overhead or network variance).")

if __name__ == "__main__":
    asyncio.run(main())