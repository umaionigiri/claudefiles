"""Fetch and parse Markdown docs from raw.githubusercontent.com.

ServiceNowDocs stores release-specific content per branch (australia,
zurich, yokohama, xanadu). We never clone the repo — too large, too
frequently updated — and instead fetch individual documents on demand.

Frontmatter is parsed with a small stdlib regex parser (no PyYAML
dependency) so the skill works on a clean Python install.
"""
from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

from scripts.source_allowlist import is_allowed

REPO_OWNER = "ServiceNow"
REPO_NAME = "ServiceNowDocs"
RAW_BASE = "https://raw.githubusercontent.com"
USER_AGENT = "claude-code-servicenow-research/1.0"
TIMEOUT_SECONDS = 15
MAX_BYTES = 5 * 1024 * 1024

ALLOWED_BRANCHES: frozenset[str] = frozenset({
    "australia", "zurich", "yokohama", "xanadu",
})

_KV_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")


@dataclass
class MarkdownDoc:
    url: str
    branch: str
    path: str
    frontmatter: dict
    body: str

    @property
    def title(self) -> str:
        return str(self.frontmatter.get("title", "(untitled)"))

    @property
    def doc_type(self) -> str:
        return str(self.frontmatter.get("doc_type", ""))

    @property
    def bundle(self) -> str:
        return str(self.frontmatter.get("bundle", ""))


def build_raw_url(path: str, branch: str) -> str:
    branch = branch.lower().strip()
    if branch not in ALLOWED_BRANCHES:
        raise ValueError(
            f"Unknown branch '{branch}'. Allowed: {sorted(ALLOWED_BRANCHES)}"
        )
    normalized = path.replace("\\", "/").lstrip("/")
    if ".." in normalized.split("/"):
        raise ValueError(f"Path contains traversal segment: {path!r}")
    encoded = urllib.parse.quote(normalized)
    return f"{RAW_BASE}/{REPO_OWNER}/{REPO_NAME}/{branch}/{encoded}"


def fetch(path: str, branch: str = "australia") -> MarkdownDoc | None:
    url = build_raw_url(path, branch)
    if not is_allowed(url):
        raise ValueError(f"URL outside allowlist: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw = resp.read(MAX_BYTES).decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return None
    fm, body = _split_frontmatter(raw)
    return MarkdownDoc(url=url, branch=branch, path=path, frontmatter=fm, body=body)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm_raw, body = parts[1], parts[2].lstrip("\n")
    return _parse_frontmatter(fm_raw), body


def _parse_frontmatter(fm_text: str) -> dict:
    """Minimal stdlib frontmatter parser (no PyYAML dependency).

    Recognizes:
      - `key: value`           — bare scalar
      - `key: "quoted value"`  — double-quoted string
      - `key: 'value'`         — single-quoted string
      - `key: [a, b, c]`       — single-line list (kept as raw string)

    Multi-line nested structures are returned as their raw string. We
    only consume top-level key-value lines, which is what ServiceNowDocs
    frontmatter consistently uses for the fields we care about (title,
    doc_type, bundle, release, last_updated).
    """
    out: dict = {}
    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or line.startswith(" "):
            continue
        match = _KV_LINE.match(line)
        if not match:
            continue
        key, raw_val = match.groups()
        val = raw_val.strip()
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]
        out[key] = val
    return out
