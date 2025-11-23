"""
Unit tests for the rate limiter utility.
"""

import time

from app.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test cases for RateLimiter class."""

    def test_allows_requests_under_limit(self):
        """Test that requests under the limit are allowed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        user_id = 1

        # Should allow 5 requests
        for _ in range(5):
            assert limiter.is_allowed(user_id) is True

    def test_blocks_requests_over_limit(self):
        """Test that requests over the limit are blocked."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        user_id = 1

        # Allow first 3 requests
        for _ in range(3):
            assert limiter.is_allowed(user_id) is True

        # Block the 4th request
        assert limiter.is_allowed(user_id) is False

    def test_different_users_have_separate_limits(self):
        """Test that different users have separate rate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        user1_id = 1
        user2_id = 2

        # User 1 makes 2 requests
        assert limiter.is_allowed(user1_id) is True
        assert limiter.is_allowed(user1_id) is True
        assert limiter.is_allowed(user1_id) is False  # Blocked

        # User 2 should still be able to make requests
        assert limiter.is_allowed(user2_id) is True
        assert limiter.is_allowed(user2_id) is True
        assert limiter.is_allowed(user2_id) is False  # Blocked

    def test_sliding_window_expiration(self):
        """Test that old requests expire after the window."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        user_id = 1

        # Make 2 requests
        assert limiter.is_allowed(user_id) is True
        assert limiter.is_allowed(user_id) is True

        # Should be blocked
        assert limiter.is_allowed(user_id) is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.is_allowed(user_id) is True

    def test_reset_single_user(self):
        """Test resetting rate limit for a single user."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        user1_id = 1
        user2_id = 2

        # Both users make requests
        limiter.is_allowed(user1_id)
        limiter.is_allowed(user1_id)
        limiter.is_allowed(user2_id)

        # Reset user 1
        limiter.reset(user1_id)

    def test_reset_all_users(self):
        """Test resetting rate limit for all users."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        user1_id = 1
        user2_id = 2

        # Both users make requests
        limiter.is_allowed(user1_id)
        limiter.is_allowed(user2_id)

        # Reset all
        limiter.reset()
