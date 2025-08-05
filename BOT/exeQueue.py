import queue
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import threading
import time
import traceback
q = queue.Queue()

def addItem(command, *args, **kwargs):
    """Add an item to the queue."""
    print(f"[exeQueue] Adding job: {getattr(command, '__name__', str(command))} args={args} kwargs={kwargs}")
    q.put((command, args, kwargs))

def jobProcessor(max_threads=4):
    print(f"[exeQueue] Job processor started with max_threads={max_threads}")
    last_heartbeat = time.time()
    def job_wrapper(command, *args, **kwargs):
        job_name = getattr(command, '__name__', str(command))
        print(f"[exeQueue] Starting job: {job_name} args={args} kwargs={kwargs}")
        try:
            result = command(*args, **kwargs)
            print(f"[exeQueue] Job completed: {job_name}")
            return result
        except Exception as e:
            print(f"[exeQueue] Job failed: {job_name} Exception: {e}")
            traceback.print_exc()
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = set()
        while True:
            # Heartbeat log every 60 seconds
            now = time.time()
            if now - last_heartbeat > 60:
                print(f"[exeQueue] Heartbeat: Job processor alive. Active threads: {threading.active_count()}")
                last_heartbeat = now
            command, args, kwargs = q.get()  # Blocks until item available
            print(f"[exeQueue] Got job: {getattr(command, '__name__', str(command))}")
            # Clean up completed futures
            futures = {f for f in futures if not f.done()}
            # If pool is full, wait for at least one to finish
            while len(futures) >= max_threads:
                print(f"[exeQueue] Thread pool full. Waiting for a job to complete...")
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
            # Start the new job
            f = executor.submit(job_wrapper, command, *args, **kwargs)
            futures.add(f)
            q.task_done()