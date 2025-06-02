import queue
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
q = queue.Queue()

def addItem(command, *args, **kwargs):
    """Add an item to the queue."""
    q.put((command, args, kwargs))

def jobProcessor(max_threads=8):
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = set()
        while True:
            command, args, kwargs = q.get()  # Blocks until item available
            # Clean up completed futures
            futures = {f for f in futures if not f.done()}
            # If pool is full, wait for at least one to finish
            while len(futures) >= max_threads:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
            # Start the new job
            f = executor.submit(command, *args, **kwargs)
            futures.add(f)
            q.task_done()