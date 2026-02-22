"""Sliding window rate limiter dla Postiz API (30 req/h)."""

import time
from collections import deque


class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: deque[float] = deque()

    def _cleanup(self):
        """Usuń stare timestampy poza oknem."""
        now = time.time()
        while self._timestamps and self._timestamps[0] < now - self.window_seconds:
            self._timestamps.popleft()

    def can_request(self) -> bool:
        """Sprawdź, czy można wykonać kolejne żądanie."""
        self._cleanup()
        return len(self._timestamps) < self.max_requests

    def wait_if_needed(self):
        """Poczekaj, aż będzie można wykonać żądanie."""
        self._cleanup()
        if len(self._timestamps) >= self.max_requests:
            oldest = self._timestamps[0]
            wait_time = oldest + self.window_seconds - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
                self._cleanup()

    def record_request(self):
        """Zarejestruj wykonane żądanie."""
        self._timestamps.append(time.time())

    @property
    def remaining(self) -> int:
        """Ile żądań pozostało w bieżącym oknie."""
        self._cleanup()
        return max(0, self.max_requests - len(self._timestamps))

    @property
    def reset_in(self) -> float:
        """Za ile sekund zwolni się najstarszy slot."""
        self._cleanup()
        if not self._timestamps:
            return 0.0
        return max(0.0, self._timestamps[0] + self.window_seconds - time.time())
