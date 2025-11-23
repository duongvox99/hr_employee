"""
Simple in-memory pagination cache for mapping page numbers to cursors.
This will be replaced with Redis in production.
"""


class PaginationCache:
    """
    In-memory cache for pagination cursors.
    Maps (endpoint, cache_key, page_number) -> cursor (last id of previous page).
    to facilitate page-based pagination using keyset pagination under the hood
    for performance with large datasets rather than offset-based pagination.
    """

    def __init__(self):
        # endpoint -> cache_key (include query params) -> page_number -> cursor (last id of previous page)
        # TODO: Replace with Redis later, just for demo
        self._cache: dict[str, dict[str, dict[int, int]]] = {}

    def get_cursor(self, endpoint: str, cache_key: str, page: int) -> str | None:
        """
        Get cursor for a specific page.

        Args:
            endpoint: API endpoint name
            cache_key: Unique key for the query (includes filters)
            page: Page number

        Returns:
            Cursor string or None if not cached
        """
        if endpoint not in self._cache:
            return None
        if cache_key not in self._cache[endpoint]:
            return None
        return self._cache[endpoint].get(cache_key, {}).get(page)

    def set_cursor(self, endpoint: str, cache_key: str, page: int, previous_id: int) -> None:
        """
        Store cursor for a specific page.

        Args:
            endpoint: API endpoint name
            cache_key: Unique key for the query (includes filters)
            page: Page number
            previous_id: last id of previous page to be used as cursor
        """
        if endpoint not in self._cache:
            self._cache[endpoint] = {}
        if cache_key not in self._cache[endpoint]:
            self._cache[endpoint][cache_key] = {}
        self._cache[endpoint][cache_key][page] = previous_id

    def clear(self, endpoint: str | None = None) -> None:
        """
        Clear cache. If endpoint is provided, only clear that key.

        Args:
            endpoint: Optional specific endpoint to clear
        """
        # TODO: Call when relevant employee data changes (e.g., created/updated/deleted) for cache invalidation
        if endpoint:
            self._cache.pop(endpoint, None)
        else:
            self._cache.clear()

    @staticmethod
    def generate_cache_key(**kwargs) -> str:
        """
        Generate a unique cache key based on query parameters.
        """
        parts = []
        for key, value in kwargs.items():
            if isinstance(value, list):
                value = ",".join(str(v) for v in sorted(value))
            parts.append(f"{key}:{value}")

        return "|".join(parts)


# Global cache instance
pagination_cache = PaginationCache()
