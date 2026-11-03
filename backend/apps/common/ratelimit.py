"""Redis-backed fixed-window rate limiting."""

from django.core.cache import cache

from .errors import ApiError


def _key(scope: str, identity: str) -> str:
    return f"rl:{scope}:{identity}"


def check_rate_limit(scope: str, identity: str, limit: int, window_seconds: int) -> int:
    """Increment a counter; raise 429 when over the limit. Returns remaining."""
    key = _key(scope, identity)
    try:
        added = cache.add(key, 0, timeout=window_seconds)
        if added:
            current = cache.get(key, 0) + 1
            cache.set(key, current, timeout=window_seconds)
        else:
            try:
                current = cache.incr(key)
            except ValueError:
                cache.set(key, 1, timeout=window_seconds)
                current = 1
    except Exception:  # pragma: no cover - cache outage must not break auth
        return limit
    if current > limit:
        raise ApiError(429, "rate_limited", "Too many requests. Try again later.")
    return limit - current


def peek_rate_limit(scope: str, identity: str) -> int | None:
    return cache.get(_key(scope, identity))


def reset_rate_limit(scope: str, identity: str) -> None:
    cache.delete(_key(scope, identity))
