"""HEAD-request URL liveness checker.

After drafting an answer, every cited URL is re-validated here so the final
output never carries a NotFound source. GitHub raw URLs return 404 for
missing files, which lets us catch typos in branch/path construction.
"""
from __future__ import annotations

import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

USER_AGENT = "claude-code-servicenow-research/1.0"
TIMEOUT_SECONDS = 8


def _head(url: str) -> int:
    req = urllib.request.Request(
        url, method="HEAD", headers={"User-Agent": USER_AGENT}
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0


def check(url: str) -> int:
    """Return HTTP status code (0 if connection failed)."""
    return _head(url)


def check_all(urls: list[str], max_workers: int = 5) -> dict[str, int]:
    """Concurrent HEAD checks. Returns {url: status}."""
    if not urls:
        return {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(pool.map(_head, urls))
    return dict(zip(urls, results))


def is_live(url: str) -> bool:
    """True if URL returns 2xx or 3xx."""
    code = _head(url)
    return 200 <= code < 400


def filter_live(urls: list[str]) -> list[str]:
    statuses = check_all(urls)
    return [u for u, s in statuses.items() if 200 <= s < 400]
