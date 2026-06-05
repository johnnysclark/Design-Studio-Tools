"""Shared HTTP client. Use `get_client()` from any fetcher — never construct a bare httpx client.

Centralizing this here means every API call across the kit shares:
- a polite User-Agent (some open APIs require one)
- sane timeouts
- automatic retries on transient failures
"""

from __future__ import annotations

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

USER_AGENT = "DesignStudioTools/0.1 (+https://github.com/johnnysclark/Design-Studio-Tools)"
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


def get_client(timeout: httpx.Timeout | float | None = None) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        timeout=timeout or DEFAULT_TIMEOUT,
        follow_redirects=True,
    )


_RETRYABLE = (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(_RETRYABLE),
)
def get_json(url: str, params: dict | None = None, *, timeout: float | None = None) -> dict | list:
    """One-shot JSON GET with retries. Caller handles HTTPStatusError."""
    with get_client(timeout=timeout) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
