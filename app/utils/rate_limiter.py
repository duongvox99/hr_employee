# TODO: Use Redis or similar distributed storage instead of in-memory storage (just for demo)
# TODO: Add logging to track rate limit hits
# TODO: Consider adding header like: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` to responses
# TODO: For unauthenticated endpoints, implement IP-based rate limiting

import time
from collections import defaultdict, deque


class RateLimiter:
    """
    Sliding window rate limiter to track requests per user.
    Use a deque to store timestamps of requests and automatically removes expired entries.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps per user_id
        self._requests: defaultdict[int, deque[float]] = defaultdict(deque)

    def is_allowed(self, user_id: int) -> bool:
        """
        Check if a request from the user is allowed.

        Args:
            user_id: The ID of the authenticated user

        Returns:
            True if the request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        user_requests = self._requests[user_id]

        # Remove expired timestamps (older than the window)
        cutoff_time = current_time - self.window_seconds
        while user_requests and user_requests[0] < cutoff_time:
            user_requests.popleft()

        # Check if under the limit
        if len(user_requests) < self.max_requests:
            user_requests.append(current_time)
            return True

        return False

    def get_retry_after(self, user_id: int) -> int:
        """
        Get the number of seconds until the user can make another request.

        Args:
            user_id: The ID of the authenticated user

        Returns:
            Seconds until the oldest request expires (0 if requests available)
        """
        user_requests = self._requests[user_id]

        if not user_requests or len(user_requests) < self.max_requests:
            return 0

        current_time = time.time()
        oldest_request = user_requests[0]
        retry_after = oldest_request + self.window_seconds - current_time

        return max(0, int(retry_after) + 1)  # Round up to nearest second

    def reset(self, user_id: int | None = None) -> None:
        """
        Reset rate limiting for a specific user or all users.

        Args:
            user_id: The ID of the user to reset, or None to reset all users
        """
        if user_id is None:
            self._requests.clear()
        elif user_id in self._requests:
            del self._requests[user_id]
