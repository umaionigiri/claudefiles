"""WebFetch fallback helper using stdlib only.

When the host's WebFetch tool returns JS-rendered SPA content, or when
running outside an environment that has WebFetch, this module fetches
HTML directly with urllib and extracts plain-text content via a minimal
HTMLParser. The output is intentionally lossy — anchors, scripts, and
styles are dropped — but it's enough to identify whether a target page
contains the query terms and to extract titles/headings.

Use this from a subagent via:
    python -m scripts.web_fetch_helper "https://..."

It prints a JSON object: {"url", "status", "title", "text", "links"}.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

from scripts.source_allowlist import is_allowed

USER_AGENT = "claude-code-servicenow-research/1.0"
TIMEOUT_SECONDS = 12
MAX_BYTES = 5 * 1024 * 1024
DROP_TAGS = frozenset({"script", "style", "noscript", "svg", "nav", "footer", "header"})
WHITESPACE = re.compile(r"\s+")


class _TextExtractor(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self._in_title = False
        self._skip_depth = 0
        self._chunks: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._current_anchor: str | None = None
        self._anchor_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in DROP_TAGS:
            self._skip_depth += 1
            return
        if tag == "title":
            self._in_title = True
        elif tag == "a":
            href = dict(attrs).get("href")
            if href and not href.startswith("#"):
                self._current_anchor = urljoin(self.base_url, href)
                self._anchor_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in DROP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag == "title":
            self._in_title = False
        elif tag == "a" and self._current_anchor:
            anchor_text = WHITESPACE.sub(" ", "".join(self._anchor_text)).strip()
            if anchor_text and is_allowed(self._current_anchor):
                self.links.append((anchor_text, self._current_anchor))
            self._current_anchor = None
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_title:
            self.title += data
        else:
            self._chunks.append(data)
            if self._current_anchor is not None:
                self._anchor_text.append(data)

    def get_text(self) -> str:
        joined = " ".join(self._chunks)
        return WHITESPACE.sub(" ", joined).strip()


def fetch(url: str, max_chars: int = 8000) -> dict:
    """Fetch a URL and return a parsed-text summary.

    Returns: {"url", "status", "title", "text" (truncated), "links" (allowlisted only)}
    `status` is HTTP status code (0 if connection failed).
    """
    if not is_allowed(url):
        return {"url": url, "status": 0, "title": "", "text": "",
                "links": [], "error": "URL not on allowlist"}
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            status = resp.status
            raw = resp.read(MAX_BYTES).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "title": "", "text": "",
                "links": [], "error": str(e.reason)}
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return {"url": url, "status": 0, "title": "", "text": "",
                "links": [], "error": str(e)}
    parser = _TextExtractor(url)
    try:
        parser.feed(raw)
    except Exception as e:
        return {"url": url, "status": status, "title": parser.title.strip(),
                "text": "", "links": [], "error": f"parse: {e}"}
    text = parser.get_text()
    if len(text) > max_chars:
        text = text[:max_chars] + "\n…[truncated]"
    return {
        "url": url,
        "status": status,
        "title": parser.title.strip(),
        "text": text,
        "links": [{"text": t, "url": u} for t, u in parser.links[:50]],
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('{"error": "Usage: python -m scripts.web_fetch_helper <url> [max_chars]"}',
              file=sys.stderr)
        return 1
    url = sys.argv[1]
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    print(json.dumps(fetch(url, max_chars=max_chars), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
