"""Shared decorator turning any fetcher exception into a degraded FetcherResult.

The pipeline never crashes on a single API outage — the section just reports unavailable
with a reason, and the rest of the dossier still assembles.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from ds_common.logging import get_logger

from site_dossier.models import FetcherResult

log = get_logger(__name__)


def degrade_on_failure(name: str) -> Callable:
    """Wrap a fetcher so exceptions become FetcherResult(status='unavailable')."""

    def decorator(fn: Callable[..., FetcherResult]) -> Callable[..., FetcherResult]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> FetcherResult:
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                log.warning("fetcher.degraded", section=name, error=str(exc))
                return FetcherResult(
                    status="unavailable",
                    source=name,
                    data=None,
                    notes=[f"{type(exc).__name__}: {exc}"],
                )

        return wrapper

    return decorator
