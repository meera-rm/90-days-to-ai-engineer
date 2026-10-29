asyncio.run - runs the asynchronous main function and manages the event loop
#it creates an concurrent object for the asynchronous code to run within.
# while the asynchronous code is running, the event loop can handle other tasks concurrently.
#### What is the concurrent object?
# The concurrent object is typically a task or a future that represents the asynchronous code running within the event loop.
# what creates this object?
# The event loop creates this object when it schedules the asynchronous code to run.
# what is the relationship between the concurrent object and the event loop?
# The concurrent object is managed by the event loop, which ensures that the asynchronous code runs efficiently and concurrently with other tasks.  
# what is the role of the concurrent object?
# The concurrent object represents the asynchronous code running within the event loop and 
# allows the event loop to manage and schedule it efficiently.
# In summary, the concurrent object is a representation of the asynchronous code running
#  within the event loop, and it allows the event loop to manage and schedule the code efficiently.
# what is the relationship between the concurrent object and the asynchronous code?
# The concurrent object is essentially a wrapper or representation of the asynchronous code running within the event loop.
# It allows the event loop to track, manage, and schedule the asynchronous code efficiently.
# In essence, the concurrent object serves as a bridge between the asynchronous code and the event loop, ensuring that the code can run concurrently while the event loop manages its execution.

#what does asyncio do
# asyncio provides a framework for writing asynchronous code in Python using coroutines, 
# event loops, and futures.
# It allows for non-blocking I/O operations, making it suitable for handling multiple tasks 
# concurrently without the overhead of multiple threads.
# In summary, asyncio enables efficient concurrent execution of tasks in a single-threaded manner, 
# leveraging the event loop to manage and schedule asynchronous code.
# This approach allows for high concurrency without the complexity 
# and overhead of traditional multi-threading.






import asyncio




async def main():
    print("Hello, World!")
    await asyncio.sleep(1)
    print("Goodbye, World!")


#
asyncio.run(main())


# Define a coroutine that simulates a time-consuming task
async def fetch_data(delay):
    print("Fetching data...")
    await asyncio.sleep(delay)  # Simulate an I/O operation with a sleep
    print("Data fetched")
    return {"data": "Some data"}  # Return some data


# Define another coroutine that calls the first coroutine
async def main2():
    print("Start of main coroutine")
    task = fetch_data(2)
    # Await the fetch_data coroutine, pausing execution of main until fetch_data completes
    result = await task
    print(f"Received result: {result}")
    print("End of main coroutine")


# Run the main coroutine
asyncio.run(main2())


# Define a coroutine that simulates a time-consuming task, now with an id
async def fetch_data(delay, id):
    print("Fetching data... id:", id)
    await asyncio.sleep(delay)  # Simulate an I/O operation with a sleep
    print("Data fetched, id:", id)
    return {"data": "Some data", "id": id}  # Return some data


# Define another coroutine that calls two fetch_data coroutines this is not running concurrently. 
# it is waiting for one task to complete before moving on to the next

async def main():
    task1 = fetch_data(2, 1)
    task2 = fetch_data(2, 2)

    result1 = await task1
    print(f"Received result: {result1}")

    result2 = await task2
    print(f"Received result: {result2}")


# Run the main coroutine
asyncio.run(main())




### USING TASKS
# Define a coroutine that simulates a time-consuming task
async def fetch_data(id,sleep_time):
    print("Coroutine: Fetching data... id:", id)
    await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    print("Data fetched, id:", id)
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data


# Define another coroutine that calls the first coroutine
async def main2():
    print("Start of main coroutine")
    task1 = asyncio.create_task(fetch_data(1, 2)) # coroutine obj as this is async def fetch_data(id,sleep_time):couroutine function
    task2 = asyncio.create_task(fetch_data(2, 3))
    task3 = asyncio.create_task(fetch_data(3, 1))

#when one thread completes, the event loop will switch to another task, allowing concurrent execution 
# while the other tasks are still running and await asyncio.sleep(sleep_time) is waiting for the earlier tasks

    # Await the fetch_data coroutine, pausing execution of main until fetch_data completes
    result1 = await task1
    result2 = await task2
    result3 = await task3
    
    print(f"Received result: {result1}")
    print(f"Received result: {result2}")
    print(f"Received result: {result3}")
    print("End of main coroutine")

asyncio.run(main2())


#the sequence where we put the await matters for the order of execution

# Define a coroutine that simulates a time-consuming task
async def fetch_data(id,sleep_time):
    print("Coroutine: Fetching data... id:", id)
    await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    print("Data fetched, id:", id)
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data

async def main2():
    print("Start of main coroutine")
    task1 = asyncio.create_task(fetch_data(1, 2)) # coroutine obj as this is async def fetch_data(id,sleep_time):couroutine function
    task2 = asyncio.create_task(fetch_data(2, 3))
     # Await the fetch_data coroutine, pausing execution of main until fetch_data completes
     
    result1 = await task1
    result2 = await task2
    #the third task is created after awaiting the first two tasks and after it is run
    task3 = asyncio.create_task(fetch_data(3, 1))

#when one thread completes, the event loop will switch to another task, allowing concurrent execution 
# while the other tasks are still running and await asyncio.sleep(sleep_time) is waiting for the earlier tasks

    # Await the fetch_data coroutine, pausing execution of main until fetch_data completes
 
    result3 = await task3
    
    print(f"Received result: {result1}")
    print(f"Received result: {result2}")
    print(f"Received result: {result3}")
    print("End of main coroutine")

asyncio.run(main2())

#USING GATHER
# Define a coroutine that simulates a time-consuming task
# This demonstrates how to run multiple coroutines concurrently using asyncio.gather
# not helps with error handling and if one of the coroutines raises an exception, 
# it will propagate immediately but doesn't cancel other coroutines
# This is useful when you want to run multiple coroutines concurrently and collect their results.
# the other coroutines will continue running even if one fails

async def fetch_data(id,sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data

async def main3():
    print("Start of main coroutine using gather")
    results = await asyncio.gather(
        fetch_data(1, 2),
        fetch_data(2, 3),
        fetch_data(3, 1)
    )
    for result in results:
        print(f"Received result: {result}")
    print("End of main coroutine using gather")

asyncio.run(main3())


#USING GATHER WITH ERROR HANDLING
# This demonstrates how to handle errors when using asyncio.gather
# If one of the coroutines raises an exception, it will be returned in the results list instead of 
# propagating immediately.

async def fetch_data_with_error(id,sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    if id == 2:
        raise ValueError("Simulated error for id 2")
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data

async def main4():
    print("Start of main coroutine using gather with error handling")
    results = await asyncio.gather(
        fetch_data_with_error(1, 2),
        fetch_data_with_error(2, 3),
        fetch_data_with_error(3, 1),
        return_exceptions=True
    )
    for result in results:
        if isinstance(result, Exception):
            print(f"Received error: {result}")
        else:
            print(f"Received result: {result}")
    print("End of main coroutine using gather with error handling")

asyncio.run(main4())


#USING GATHER WITH CANCELLATION
# This demonstrates how to handle cancellation when using asyncio.gather
# If one of the coroutines is cancelled, it will be returned in the results list instead of propagating immediately.        

async def fetch_data_with_cancellation(id,sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    try:
        await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    except asyncio.CancelledError:
        print(f"Coroutine cancelled, id: {id}")
        raise
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data

async def main5():
    print("Start of main coroutine using gather with cancellation")
    tasks = [
        asyncio.create_task(fetch_data_with_cancellation(1, 2)),
        asyncio.create_task(fetch_data_with_cancellation(2, 3)),
        asyncio.create_task(fetch_data_with_cancellation(3, 1))
    ]
    # Cancel the second task
    tasks[1].cancel()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"Received error: {result}")
        else:
            print(f"Received result: {result}")
    print("End of main coroutine using gather with cancellation")

asyncio.run(main5())



#USING GATHER WITH TIMEOUTS
# This demonstrates how to handle timeouts when using asyncio.gather
# If one of the coroutines takes longer than the specified timeout, it will be cancelled and returned in the results list.          

async def fetch_data_with_timeout(id,sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    try:
        await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    except asyncio.CancelledError:
        print(f"Coroutine cancelled due to timeout, id: {id}")
        raise
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data

async def main6():
    print("Start of main coroutine using gather with timeouts")
    tasks = [
        asyncio.create_task(fetch_data_with_timeout(1, 2)),
        asyncio.create_task(fetch_data_with_timeout(2, 3)),
        asyncio.create_task(fetch_data_with_timeout(3, 1))
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f"Received error: {result}")
        else:
            print(f"Received result: {result}")
    print("End of main coroutine using gather with timeouts")

asyncio.run(main6())


#USING TASKGATHER
# This demonstrates how to use asyncio.TaskGroup (available in Python 3.11+) to run multiple tasks concurrently.
# If any task fails, the entire group will be cancelled.    

# Define the main coroutine for TaskGroup usage
async def fetch_data_with_timeout(id, sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    try:
        await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    except asyncio.CancelledError:
        print(f"Coroutine cancelled due to timeout, id: {id}")
        raise
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data



async def main7():
    print("Start of main coroutine using TaskGroup")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data_with_timeout(1, 2))
        task2 = tg.create_task(fetch_data_with_timeout(2, 3))
        task3 = tg.create_task(fetch_data_with_timeout(3, 1))
    print("End of main coroutine using TaskGroup")

asyncio.run(main7())        

#USING TASKGROUP WITH CANCELLATION
# This demonstrates how to handle cancellation when using asyncio.TaskGroup
# If any task is cancelled, the entire group will be cancelled.

async def fetch_data_with_timeout(id, sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    try:
        await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    except asyncio.CancelledError:
        print(f"Coroutine cancelled due to timeout, id: {id}")
        raise
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data



async def main8():
    print("Start of main coroutine using TaskGroup with cancellation")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data_with_timeout(1, 2))
        task2 = tg.create_task(fetch_data_with_timeout(2, 3))
        task3 = tg.create_task(fetch_data_with_timeout(3, 1))
        # Simulate cancelling one of the tasks
        task2.cancel()
    print("End of main coroutine using TaskGroup with cancellation")

asyncio.run(main8())


#USING TASKGROUP WITH EXCEPTIONS
# This demonstrates how to handle exceptions when using asyncio.TaskGroup
# If any task raises an exception, the entire group will be cancelled.      

async def fetch_data_with_timeout(id, sleep_time):
    print(f"Coroutine: Fetching data... id: {id}")
    try:
        await asyncio.sleep(sleep_time)  # Simulate an I/O operation with a sleep
    except asyncio.CancelledError:
        print(f"Coroutine cancelled due to timeout, id: {id}")
        raise
    print(f"Data fetched, id: {id}")
    return {"id":id, "data": f"Some data from coroutine{id}"}  # Return some data

async def main9():
    print("Start of main coroutine using TaskGroup with exceptions")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data_with_timeout(1, 2))
        task2 = tg.create_task(fetch_data_with_timeout(2, 3))
        task3 = tg.create_task(fetch_data_with_timeout(3, 1))
        # Simulate raising an exception in one of the tasks
        task2.raise_exception()
    print("End of main coroutine using TaskGroup with exceptions")

asyncio.run(main9())    


#USING TASKGROUP WITH BOTH CANCELLATION AND EXCEPTIONS
# This demonstrates how to handle both cancellation and exceptions when using asyncio.TaskGroup
# If any task is cancelled or raises an exception, the entire group will be cancelled.          


async def main10():
    print("Start of main coroutine using TaskGroup with both cancellation and exceptions")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data_with_timeout(1, 2))
        task2 = tg.create_task(fetch_data_with_timeout(2, 3))
        task3 = tg.create_task(fetch_data_with_timeout(3, 1))
        # Simulate cancelling one of the tasks
        task2.cancel()
        # Simulate raising an exception in one of the tasks
        task3.raise_exception()
    print("End of main coroutine using TaskGroup with both cancellation and exceptions")

asyncio.run(main10())       

#USINGTASKGROUP WITH ALL SCENARIOS
# This demonstrates how to handle all scenarios when using asyncio.TaskGroup
# If any task is cancelled or raises an exception, the entire group will be cancelled.              


async def fetch_data_with_timeout(task_id, time_out):
    print(f"Coroutine: Fetching data... id: {task_id}")
    await asyncio.sleep(time_out)
    print(f"Data fetched, id: {task_id}")
    return f"Data from task {task_id}"



async def main11():
    print("Start of main coroutine using TaskGroup with all scenarios")
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_data_with_timeout(1, 2))
        task2 = tg.create_task(fetch_data_with_timeout(2, 3))
        task3 = tg.create_task(fetch_data_with_timeout(3, 1))
        # Simulate cancelling one of the tasks
        task2.cancel()
        # Simulate raising an exception in one of the tasks
        task3.raise_exception()
        # Simulate a normal task completing
        await task1
    print("End of main coroutine using TaskGroup with all scenarios")

asyncio.run(main11())   



#USING TASKGROUP WITH ALL SCENARIOS AND COLLECTING RESULTS

async def fetch_data(task_id, sleep_time):
    await asyncio.sleep(sleep_time)
    return f"Data from task {task_id}"

async def main12():
    print("Start of main coroutine using TaskGroup with all scenarios")
    async with asyncio.TaskGroup() as tg:
        tasks = []
        for i, sleep_time in enumerate([2,1,3], start=1):
           
            task = tg.create_task(fetch_data(i, sleep_time))
            tasks.append(task)


            #await asyncio.gather(*tasks)
                #for task in tasks:
                    #result = await task
                    # print(result)   

    results = [task.result() for task in tasks]
    print(results)
    for result in results:
        print(result)

     
    print("End of main coroutine using TaskGroup with all scenarios")

asyncio.run(main12())


#USING TASKGROUP WITH ALL SCENARIOS AND COLLECTING RESULTS WITH TIMEOUTS

async def fetch_data_with_timeout(task_id, time_out):
    await asyncio.sleep(time_out)
    return f"Data from task {task_id}"



async def main13():
    print("Start of main coroutine using TaskGroup with all scenarios")
    async with asyncio.TaskGroup() as tg:
        for i, (task_id,time_out) in enumerate([(1,2),(2,3),(3,1)], start=1):
            if i == 0:
                task1 = tg.create_task(fetch_data_with_timeout(task_id, time_out))
            elif i == 1:
                task2 = tg.create_task(fetch_data_with_timeout(task_id, time_out))
            elif i == 2:
                task3 = tg.create_task(fetch_data_with_timeout(task_id, time_out))

        
    print("End of main coroutine using TaskGroup with all scenarios")

asyncio.run(main13())