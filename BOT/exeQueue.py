import queue
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

from BOT.utils import Colors

q = queue.Queue()

def addItem(command, *args, **kwargs):
    """Add an item to the queue."""
    message = (
        f"{Colors.Green}[Info] "
        f"{Colors.White}exeQueue: "
        f"{Colors.Blue} Adding job: {getattr(
            command, "__name__", str(command)
        )}"
    )
    print(message)
    
    q.put((command, args, kwargs))


def jobProcessor(max_threads=3):
    """Process jobs concurrently"""
    
    message = (
        f"{Colors.Green}[Info] "
        f"{Colors.White}exeQueue: "
        f"{Colors.Blue} Job processor started with max_threads={max_threads}"
    )
    print(message)
    
    last_heartbeat = time.time()
    
    def job_wrapper(command, *args, **kwargs):
        """Start jobs and report on their status."""
        
        job_name = getattr(command, "__name__", str(command))
        
        message = (
            f"{Colors.Green}[Info] "
            f"{Colors.White}exeQueue: "
            f"{Colors.Blue} Starting job: {job_name}"
        )
        print(message)
        
        try:
            result = command(*args, **kwargs)
            
            message = (
                f"{Colors.Green}[Info] "
                f"{Colors.White}exeQueue: "
                f"{Colors.Blue} Job completed: {job_name}"
            )
            print(message)
            
            return result
        
        except Exception as e:
            
            message = (
                f"{Colors.Red}[Error] "
                f"{Colors.White}exeQueue: "
                f"{Colors.Blue}Job failed: {job_name} Exception: {e}"
            )
            print(message)
            
            traceback.print_exc()
            
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        
        futures = set()
        
        while True:
            # Heartbeat log every 60 seconds
            now = time.time()
            
            if now - last_heartbeat > 60:
                
                message = (
                    f"{Colors.Red}[Info] "
                    f"{Colors.White}exeQueue: "
                    f"{Colors.Blue}Heartbeat: Job processor alive."
                    f"Active threads: {threading.active_count()}"
                )
                print(message)
                
                last_heartbeat = now
                
            command, args, kwargs = q.get()  # Blocks until item available
            
            message = (
                f"{Colors.Red}[Info] "
                f"{Colors.White}exeQueue: "
                f"{Colors.Blue}Got job: "
                f"{getattr(command, "__name__", str(command))}"
            )
            print(message)
            
            # Clean up completed futures
            futures = {f for f in futures if not f.done()}
            
            # If pool is full, wait for at least one to finish
            while len(futures) >= max_threads:
                
                message = (
                    f"{Colors.Red}[Info] "
                    f"{Colors.White}exeQueue: "
                    f"{Colors.Blue}Thread pool full. "
                    "Waiting for a job to complete..."
                )
                print(message)
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
                
            # Start the new job
            f = executor.submit(job_wrapper, command, *args, **kwargs)
            futures.add(f)
            q.task_done()