"""Small in-memory sliding-window rate limiter.

Enough for a single-instance deployment (Render free tier). With several
instances, move the counters to a shared store such as Redis.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


def client_ip(request: Request) -> str:
    # Render sits behind Cloudflare, which sets CF-Connecting-IP and overwrites
    # any client-supplied value, so it can't be spoofed the way
    # X-Forwarded-For can.
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    # Fallback for other proxies. A spoofed value can only dodge the limit,
    # never lock out someone else, which beats sharing one proxy IP globally.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float, name: str) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.max_requests:
                retry_after = max(1, int(hits[0] + self.window_seconds - now) + 1)
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many {self.name} requests. Try again in {retry_after}s.",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)
            # Drop idle keys so memory stays bounded.
            if len(self._hits) > 10_000:
                for stale in [k for k, v in self._hits.items() if not v or v[-1] <= cutoff]:
                    del self._hits[stale]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()

    def dependency(self, request: Request) -> None:
        self.check(client_ip(request))


# 10 login attempts per IP per 5 minutes slows password guessing to a crawl.
login_limiter = RateLimiter(max_requests=10, window_seconds=300, name="login")
# The public demo calls a paid LLM API: 5 analyses per IP per minute.
demo_limiter = RateLimiter(max_requests=5, window_seconds=60, name="demo")
