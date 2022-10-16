#!/usr/bin/python3
import threading
import time
import random


# Define a function for the thread
def print_time(threadName):
    sleep_time = random.randint(1, 5)
    time.sleep(sleep_time)
    print(sleep_time, "%s: %s" % (threadName, time.ctime(time.time())))


threads = []
for i in range(10):
    # Create two threads as follows
    try:
        t = threading.Thread(
            target=print_time,
            args=(f"Thread-{i}",),
        )
        t.start()
        threads.append(t)
    except:
        print("Error: unable to start thread")

for t in threads:
    t.join()

# import threading
# import queue
# import time
# import random

# q = queue.PriorityQueue()


# def worker():
#     while True:
#         item = q.get()
#         sleep_time = random.randint(1, 5)
#         time.sleep(sleep_time)
#         print()
#         print(f"Sleep time {sleep_time}")
#         print(f"Working on {item}")
#         print(f"Finished {item}")
#         q.task_done()


# # Turn-on the worker thread.
# for i in range(10):
#     threading.Thread(target=worker, daemon=True).start()


# # Send thirty task requests to the worker.
# for item in range(10):
#     q.put(item)

# # Block until all tasks are done.
# q.join()
# print("All work completed")
