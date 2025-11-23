from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException, status

from app.models.user import User
from app.utils.rate_limiter import RateLimiter

# TODO: Use Redis or similar distributed storage instead of in-memory storage (just for demo)
# Global dict to store limiters per endpoint (by function name)
_limiters: dict[str, RateLimiter] = {}


def rate_limit(max_requests: int, window_seconds: int):
    """
    Decorator to apply rate limiting to FastAPI endpoints.

    Each decorated endpoint gets its own independent rate limiter, so rate limits
    are tracked separately per endpoint. Users are tracked separately within each
    endpoint's rate limiter.

    This decorator expects the endpoint to have a 'current_user' parameter
    that contains the authenticated User object.

    Args:
        max_requests: Maximum number of requests allowed in the time window
        window_seconds: Time window in seconds

    Example:
        @rate_limit(max_requests=10, window_seconds=60)
        async def my_endpoint(current_user: User = Depends(get_current_user)):
            ...

        @rate_limit(max_requests=100, window_seconds=3600)
        async def another_endpoint(current_user: User = Depends(get_current_user)):
            ...

    Raises:
        HTTPException: 429 Too Many Requests if rate limit is exceeded
    """

    def decorator(func: Callable):
        # Create a separate limiter for this specific endpoint
        endpoint_key = f"{func.__module__}.{func.__qualname__}"
        if endpoint_key not in _limiters:
            _limiters[endpoint_key] = RateLimiter(
                max_requests=max_requests, window_seconds=window_seconds
            )
        limiter = _limiters[endpoint_key]

        # With @wraps(func), it copies all that metadata from the original function to the wrapper
        # -> Don't change function metadata like __name__, __doc__, __module__, ...
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user: User | None = kwargs.get("current_user")

            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Rate limiter requires authenticated user",
                )

            # Check rate limit
            if not limiter.is_allowed(current_user.id):
                retry_after = limiter.get_retry_after(current_user.id)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds.",
                    headers={"X-RateLimit-Retry-After": str(retry_after)},
                )

            # Call the original function
            result = await func(*args, **kwargs)

            # TODO: Add rate limit info to response headers
            # FastAPI doesn't make it easy to add headers in decorators
            # For production, consider using middleware or dependency injection
            return result

        return wrapper

    return decorator


def reset_all_limiters():
    """
    Reset all rate limiters.

    This is useful for testing to clear state between test cases.
    """
    for limiter in _limiters.values():
        limiter.reset()
