"""Disk cache used by every fetcher to avoid hammering free APIs.

Key the cache by rounded lat/lon (~1 km cells) since climate normals don't vary at finer scale.
TTLs are per-fetcher and supplied via the `ttl_days` argument to `@cached`.
"""

from __future__ import annotations

import functools
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import diskcache
from platformdirs import user_cache_dir

_cache: diskcache.Cache | None = None


def cache_dir() -> Path:
    override = os.environ.get("DS_CACHE_DIR")
    if override:
        return Path(override)
    return Path(user_cache_dir("design-studio-tools"))


def get_cache() -> diskcache.Cache:
    global _cache
    if _cache is None:
        path = cache_dir()
        path.mkdir(parents=True, exist_ok=True)
        _cache = diskcache.Cache(str(path))
    return _cache


def set_cache_dir(path: Path | str) -> None:
    """Reset the cache to a specific directory. Used by tests and the --cache-dir CLI flag."""
    global _cache
    if _cache is not None:
        _cache.close()
    Path(path).mkdir(parents=True, exist_ok=True)
    _cache = diskcache.Cache(str(path))


def cached(*, key: Callable[..., str], ttl_days: int) -> Callable:
    """Decorator: cache the return value of a fetcher keyed by `key(*args, **kwargs)`."""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = f"{fn.__module__}.{fn.__name__}:{key(*args, **kwargs)}"
            cache = get_cache()
            hit = cache.get(cache_key)
            if hit is not None:
                return hit
            value = fn(*args, **kwargs)
            cache.set(cache_key, value, expire=ttl_days * 86400)
            return value

        return wrapper

    return decorator
