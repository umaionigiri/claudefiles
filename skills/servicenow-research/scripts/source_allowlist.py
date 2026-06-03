"""Allowlist of official ServiceNow domains.

Non-official sources (Qiita, Stack Overflow, personal blogs) silently
contaminate answers when relying on LLM judgment alone, so this module
enforces the allowlist programmatically: any URL whose host is not in
ALLOWED_HOSTS gets rejected at the boundary.
"""
from __future__ import annotations

from urllib.parse import urlparse

ALLOWED_HOSTS: frozenset[str] = frozenset({
    "github.com",
    "raw.githubusercontent.com",
    "developer.servicenow.com",
    "docs.servicenow.com",
    "community.servicenow.com",
    "support.servicenow.com",
    "www.servicenow.com",
})


def is_allowed(url: str) -> bool:
    """Return True only if the URL host is in the official allowlist."""
    if not url:
        return False
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return host in ALLOWED_HOSTS


def filter_allowed(urls: list[str]) -> list[str]:
    return [u for u in urls if is_allowed(u)]


def assert_all_allowed(urls: list[str]) -> None:
    """Raise ValueError if any URL is outside the allowlist.

    Use this at integration points where a non-official URL must never pass
    through (e.g., right before rendering the final answer).
    """
    bad = [u for u in urls if not is_allowed(u)]
    if bad:
        raise ValueError(f"Non-official URLs detected: {bad}")
