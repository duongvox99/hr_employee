from app.auth import create_access_token


class TestRateLimitingAPI:
    """Integration tests for rate limiting on employee endpoints."""

    async def test_rate_limit_allows_requests_under_limit(
        self, client, sample_employees, sample_users
    ):
        """Test that requests under the rate limit are allowed."""
        user = sample_users[0]
        token = create_access_token(user.id)
        headers = {"Authorization": f"Bearer {token}"}

        # Make several requests under the limit (2 per 60 seconds)
        for i in range(2):
            response = await client.get("/api/v1/employees", headers=headers)
            assert response.status_code == 200, f"Request {i + 1} failed"

    async def test_rate_limit_blocks_requests_over_limit(
        self, client, sample_employees, sample_users
    ):
        """Test that requests over the rate limit are blocked."""
        user = sample_users[0]
        token = create_access_token(user.id)
        headers = {"Authorization": f"Bearer {token}"}

        # Make requests up to the limit (2 requests per 60 seconds)
        for i in range(2):
            response = await client.get("/api/v1/employees", headers=headers)
            assert response.status_code == 200, f"Request {i + 1} failed unexpectedly"

        # The 3rd request should be rate limited
        response = await client.get("/api/v1/employees", headers=headers)
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]

    async def test_rate_limit_different_users_have_separate_limits(
        self, client, sample_employees, sample_users
    ):
        """Test that different users have separate rate limits."""
        user1 = sample_users[0]
        user2 = sample_users[1]

        token1 = create_access_token(user1.id)
        token2 = create_access_token(user2.id)

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 1 makes 2 requests
        for _ in range(2):
            response = await client.get("/api/v1/employees", headers=headers1)
            assert response.status_code == 200

        # User 1's next request should be blocked
        response = await client.get("/api/v1/employees", headers=headers1)
        assert response.status_code == 429

        # User 2 should still be able to make requests
        response = await client.get("/api/v1/employees", headers=headers2)
        assert response.status_code == 200

    async def test_rate_limit_requires_authentication(self, client, sample_employees):
        """Test that rate limiting requires authentication."""
        # Request without authentication token
        response = await client.get("/api/v1/employees")
        # Should get 403 Forbidden due to missing authentication, not 429
        assert response.status_code == 403


# TODO: add integrations for list employee with different org configs and filters
