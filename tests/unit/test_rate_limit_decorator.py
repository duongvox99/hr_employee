"""
Unit tests for the rate limit decorator to verify endpoint separation.
"""

import pytest

from app.decorators.rate_limit import rate_limit, reset_all_limiters
from app.models.user import User


class MockUser:
    """Mock user for testing."""

    def __init__(self, user_id: int):
        self.id = user_id


class TestRateLimitDecorator:
    """Test cases for rate limit decorator."""

    def setup_method(self):
        """Reset limiters before each test."""
        reset_all_limiters()

    def teardown_method(self):
        """Reset limiters after each test."""
        reset_all_limiters()

    async def test_different_endpoints_have_separate_limits(self):
        """Test that different endpoints have completely separate rate limits."""

        # Define two endpoints with the same rate limit configuration
        @rate_limit(max_requests=3, window_seconds=60)
        async def endpoint_a(current_user: User):
            return "endpoint_a"

        @rate_limit(max_requests=3, window_seconds=60)
        async def endpoint_b(current_user: User):
            return "endpoint_b"

        user = MockUser(user_id=1)

        # Make 3 requests to endpoint_a (should all succeed)
        for _ in range(3):
            result = await endpoint_a(current_user=user)
            assert result == "endpoint_a"

        # 4th request to endpoint_a should fail
        with pytest.raises(Exception) as exc_info:
            await endpoint_a(current_user=user)
        assert "429" in str(exc_info.value.status_code)

        # But endpoint_b should still have its full quota (separate limiter)
        for _ in range(3):
            result = await endpoint_b(current_user=user)
            assert result == "endpoint_b"

        # 4th request to endpoint_b should also fail
        with pytest.raises(Exception) as exc_info:
            await endpoint_b(current_user=user)
        assert "429" in str(exc_info.value.status_code)

    async def test_different_endpoints_different_limits(self):
        """Test that endpoints can have different rate limit configurations."""

        # Endpoint A: 2 requests per minute
        @rate_limit(max_requests=2, window_seconds=60)
        async def endpoint_a(current_user: User):
            return "endpoint_a"

        # Endpoint B: 5 requests per minute
        @rate_limit(max_requests=5, window_seconds=60)
        async def endpoint_b(current_user: User):
            return "endpoint_b"

        user = MockUser(user_id=1)

        # Make 2 requests to endpoint_a (should succeed)
        for _ in range(2):
            await endpoint_a(current_user=user)

        # 3rd request should fail
        with pytest.raises(Exception) as exc_info:
            await endpoint_a(current_user=user)
        assert "429" in str(exc_info.value.status_code)

        # But endpoint_b should allow 5 requests
        for _ in range(5):
            await endpoint_b(current_user=user)

        # 6th request should fail
        with pytest.raises(Exception) as exc_info:
            await endpoint_b(current_user=user)
        assert "429" in str(exc_info.value.status_code)

    async def test_same_endpoint_different_users(self):
        """Test that different users have separate quotas for the same endpoint."""

        @rate_limit(max_requests=2, window_seconds=60)
        async def endpoint_a(current_user: User):
            return f"result_for_user_{current_user.id}"

        user1 = MockUser(user_id=1)
        user2 = MockUser(user_id=2)

        # User 1 makes 2 requests (should succeed)
        for _ in range(2):
            await endpoint_a(current_user=user1)

        # User 1's 3rd request should fail
        with pytest.raises(Exception) as exc_info:
            await endpoint_a(current_user=user1)
        assert "429" in str(exc_info.value.status_code)

        # User 2 should still have full quota
        for _ in range(2):
            await endpoint_a(current_user=user2)

        # User 2's 3rd request should also fail
        with pytest.raises(Exception) as exc_info:
            await endpoint_a(current_user=user2)
        assert "429" in str(exc_info.value.status_code)
