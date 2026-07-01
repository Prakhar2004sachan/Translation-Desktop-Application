import concurrent.futures
from typing import Callable

class BackgroundWorker:
    def __init__(self, max_workers: int = 4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit(self, fn: Callable, *args, **kwargs) -> concurrent.futures.Future:
        future = self.executor.submit(fn, *args, **kwargs)
        self.futures.append(future)
        # Clean up done futures
        self.futures = [f for f in self.futures if not f.done()]
        return future
        
    def shutdown(self):
        self.executor.shutdown(wait=False)
