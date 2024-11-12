import sys
sys.path.append("") 

from asyncio import Lock
import time

class RateLimiter:
    def __init__(self, max_requests_per_min):
        self.max_requests = max_requests_per_min
        self.request_times = []
        self.lock = Lock()

    async def is_allowed(self) -> bool:
        async with self.lock:
            current_time = time.time()
            # Remove requests older than 1 minute
            self.request_times = [t for t in self.request_times if current_time - t < 60]
            # Check if rate limit exceeded
            if len(self.request_times) >= self.max_requests:
                return False
            # Record current request time
            self.request_times.append(current_time)
            return True