### THREADS

for parallel tasks that share data with minimal cpu use

#### ASYNCIO
for managing many waiting tasks


#### PROCESSES
for maximing performance on cpu intensive tasks


#### COROUTINE
In Python, a coroutine is an object representing a computation that can be paused and resumed. Coroutines can be entered, exited, and resumed at many different points. It’s the object you get when you call a coroutine function.

To execute the code in a coroutine, you need to await it or run it in an event loop.


a coroutine function is a specialized function defined using the async def syntax that serves as the foundation for asynchronous programming and cooperative multitasking.
Unlike a regular Python function (subroutine) that runs from start to finish without interruption, a coroutine function can pause its execution to let other tasks run, and later resume right where it left off. This makes them incredibly efficient for handling I/O-bound operations like web requests, database queries, or file reading.

#### The Two Halves of a Coroutine

When working with coroutines, it is important to distinguish between the function itself and what it produces:
1. Coroutine Function: The actual recipe or blueprint defined using async def.
2. Coroutine Object: What you get when you call a coroutine function. Calling the function does not run the code inside it. Instead, it returns a "lazy" coroutine object (essentially a promise or recipe) that hasn't executed yet.

Concept	What it is	Python Syntax Example
Coroutine Function	The asynchronous function blueprint	async def fetch_data():
Coroutine Object	The paused task created by calling the function	task = fetch_data()
await Keyword	The trigger that actually runs the object and extracts the result


python
import asyncio

# 1. This is a coroutine function
async def fetch_user_data(user_id):
    print(f"Starting data fetch for user {user_id}...")
    
    # The 'await' keyword pauses this function, allowing the CPU to 
    # work on other tasks while waiting 2 seconds for the "network".
    await asyncio.sleep(2) 
    
    print(f"Data received for user {user_id}!")
    return {"user_id": user_id, "name": "Alex"}

async def main():
    # Calling the function returns a coroutine object; it doesn't print yet.
    coro_object = fetch_user_data(42) 
    
    # Awaiting the coroutine object executes it and retrieves the return value.
    user = await coro_object
    print(f"Result: {user}")

# Kick off the event loop to run the top-level main() coroutine
asyncio.run(main())


#### EXAMPLE WITHOUT THE USE OF COUROUTINES

import time

def brew_coffee(n: int) -> None:
    print(f"Start brewing coffee #{n}...")
    # This blocks the entire thread. Nothing else can happen.
    time.sleep(5)
    print(f"Coffee #{n} is ready!")

def main() -> None:
    start = time.time()

    # Sequential execution
    for i in range(3):
        brew_coffee(i + 1)

    end = time.time()
    print(f"Total time: {end - start:.2f} seconds")

if __name__ == "__main__":
    main()


#### Coroutine functions
In Python, a standard block of code starting with def is simply called a function. But if you add async in front of it like async def, it becomes a coroutine function. This tells Python that the function is intended to run asynchronously. ‘Asynchronous’ means that tasks can be handled independently rather than waiting for one to finish before starting the next.



import asyncio
import time
from typing import List, Coroutine, Any

## 1. Define a coroutine using 'async def' BU THTIS IS CONCURRENT BUT IT HAS BLOCKING I/O 
async def brew_coffee(n: int) -> None:
    print(f"Start brewing coffee #{n}...")

    # 2. 'await' hands control back to the Event Loop
    # This is non-blocking sleep.
    #await asyncio.sleep(5)

    print(f"Coffee #{n} is ready!")

async def main() -> None:
    start = time.time()

    # 3. Create a list of coroutine objects (they haven't run yet!)
    tasks: List[Coroutine[Any, Any, None]] = [brew_coffee(i + 1) for i in range(3)]

    # 4. Schedule them concurrently and wait for all to finish
    await asyncio.gather(*tasks)

    end = time.time()
    print("Coffee ready!")
    print(f"Total time: {end - start:.2f} seconds")

if __name__ == "__main__":
    # 5. The entry point for the async world
    asyncio.run(main())
Output

Start brewing coffee #1...
Start brewing coffee #2...
Start brewing coffee #3...
Coffee #1 is ready!
Coffee #2 is ready!
Coffee #3 is ready!
Coffee ready!
Total time: 5.00 seconds
Now you can make three cups of coffee in just five seconds. You didn’t hire more workers, you didn’t move faster, and you didn’t buy extra equipment. You just took advantage of the idle time you previously wasted.

So, what exactly are coroutines, asyncio, await, and gather? Let’s dive into them one by one.


Yes, this is not a coroutine. Why? Because time.sleep(5) is a blocking I/O operation. If you use blocking functions (like time.sleep, requests.get, or standard file reading) inside a coroutine, you effectively stop the entire "Traffic Controller" from working. For a coroutine to be effective, you must use non-blocking equivalents that know how to await.



##### Coroutine functions
I briefly introduced simple coroutine functions such as async, await, gather, create_task. There are more functions in the asyncio library and you can do so many things with these powerful tools.

###### gather and TaskGroup
I demonstrated how to use gather but I didn’t explain much about it. After you make some coroutine functions, you have to make them coordinate well. Often, several coroutine functions should be executed asynchronously. In that case, you can utilize the functions called gather or TaskGroup in asyncio. But are they exactly the same?

Actually, they have a very crucial difference. When one of the tasks in gather fails, the other tasks keep running. On the other hand, TaskGroup cancels the remaining tasks immediately. Look at this example.

import asyncio
import time

async def example_task(name, delay, should_fail=False):
    print(f"Task {name} starting (delay={delay}s)")
    await asyncio.sleep(delay)
    if should_fail:
        print(f"Task {name} failing")
        raise ValueError(f"Task {name} failed")
    print(f"Task {name} finished")
    return f"Result {name}"

async def demonstrate_gather():
    print("\n--- Demonstrating asyncio.gather ---")
    start_time = time.time()

    # Create tasks: B will fail
    tasks = [
        example_task("A", 1),
        example_task("B", 2, should_fail=True),
        example_task("C", 3)
    ]

    # asyncio.gather without return_exceptions=True raises the first exception immediately
    # BUT it does NOT cancel the other tasks. They keep running in the background.
    print("Starting gather with a failing task...")
    try:
        results = await asyncio.gather(*tasks)
    except Exception as e:
        print(f"Gather caught exception: {e}")

    await asyncio.sleep(2)
    print(f"Gather finished (after waiting). Note if other tasks continued printing above.")
    print(f"Gather took: {time.time() - start_time:.2f}s")

async def demonstrate_task_group():
    print("\n--- Demonstrating asyncio.TaskGroup ---")
    start_time = time.time()

    # TaskGroup cancels all other tasks immediately when one fails
    print("Starting TaskGroup with a failing task...")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(example_task("X", 1))
            tg.create_task(example_task("Y", 2, should_fail=True))
            tg.create_task(example_task("Z", 3))

    except Exception as e:
        print(f"TaskGroup caught exception: {type(e).__name__}: {e}")

    print(f"TaskGroup finished. Other tasks should have been cancelled (no 'finished' print for Z).")
    print(f"TaskGroup took: {time.time() - start_time:.2f}s")

async def main():
    await demonstrate_gather()
    await demonstrate_task_group()

if __name__ == "__main__":
    asyncio.run(main())
Output

--- Demonstrating asyncio.gather ---
Starting gather with a failing task...
Task A starting (delay=1s)
Task B starting (delay=2s)
Task C starting (delay=3s)
Task A finished
Task B failing
Gather caught exception: Task B failed
Task C finished
Gather finished (after waiting). Note if other tasks continued printing above.
Gather took: 4.00s

--- Demonstrating asyncio.TaskGroup ---
Starting TaskGroup with a failing task...
Task X starting (delay=1s)
Task Y starting (delay=2s)
Task Z starting (delay=3s)
Task X finished
Task Y failing
TaskGroup caught exception: ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
TaskGroup finished. Other tasks should have been cancelled (no 'finished' print for Z).
TaskGroup took: 1.99s
As you can see, gather keeps running even if one of the tasks fails while TaskGroup raises an exception and cancels the remaining tasks immediately.

#### Differences: TaskGroup vs. gather
Cancellation: In asyncio.gather(), if one task fails, the others continue running (unless explicitly cancelled). TaskGroup cancels siblings immediately upon the first failure, conserving resources.

#### Error Reporting: gather() returns a list of results or raises the first exception. TaskGroup raises an ExceptionGroup containing all exceptions that occurred, providing a complete picture of the failure state.

#### Why is TaskGroup favored over gather?
TaskGroup enforces a "parent-child" relationship where the parent cannot exit until all children are finished. This eliminates "orphaned tasks"—background processes that silently keep running (and consuming resources) after your main function has finished or crashed. That is why modern high-reliability Python architecture favors Structured Concurrency(asyncio.TaskGroup) over unstructured create_task + gather.

By design, TaskGroup operates on a "fail-fast" principle. If one task fails, the group immediately sends a cancellation signal to all other running tasks in that group.

But what if I don’t want to cancel the whole task group even if one fails? Should I just use just gather? In that case, you can still utilize TaskGroup by handling exceptions with try and except blocks inside the individual tasks.

