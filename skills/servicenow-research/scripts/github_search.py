"""Wrapper around `gh search code` scoped to ServiceNow/ServiceNowDocs.

GitHub Code Search lacks per-branch filtering, so this returns paths only;
the caller chooses the branch (release family) when calling raw_fetch.

The repo qualifier is forced internally — callers cannot accidentally
search outside the official ServiceNowDocs repository.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field

REPO_QUALIFIER = "repo:ServiceNow/ServiceNowDocs"
DEFAULT_LIMIT = 20
TIMEOUT_SECONDS = 30


@dataclass
class SearchHit:
    path: str
    repository: str
    text_matches: list[str] = field(default_factory=list)


def gh_available() -> bool:
    return shutil.which("gh") is not None


def search(query: str, limit: int = DEFAULT_LIMIT) -> list[SearchHit]:
    """Run `gh search code` and return parsed hits.

    The repo qualifier is appended automatically. Do not include
    'repo:...' in `query`.
    """
    if not gh_available():
        return []
    full_query = f"{query} {REPO_QUALIFIER}"
    cmd = [
        "gh", "search", "code", full_query,
        "--limit", str(limit),
        "--json", "path,repository,textMatches",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=TIMEOUT_SECONDS, check=False,
        )
    except subprocess.TimeoutExpired:
        return []
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []
    hits: list[SearchHit] = []
    for item in data:
        repo = item.get("repository", {}) or {}
        repo_name = repo.get("nameWithOwner", "")
        if repo_name != "ServiceNow/ServiceNowDocs":
            continue
        fragments = [
            tm.get("fragment", "")
            for tm in (item.get("textMatches", []) or [])
        ]
        hits.append(SearchHit(
            path=item.get("path", ""),
            repository=repo_name,
            text_matches=fragments,
        ))
    return hits
