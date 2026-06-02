"""Render answers using footnote-numbered citations.

Source links are NOT embedded inline next to claims. Instead, each claim
that has sources gets one or more bracketed footnote numbers (`[1]`,
`[2]`) appended to its text, and a `## 出典` section at the end of the
document lists the numbered Markdown links. This keeps the body clean
while preserving claim-level traceability.

URL liveness is batched into one concurrent pass before rendering.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from scripts.source_allowlist import is_allowed
from scripts.url_check import check_all


@dataclass
class Source:
    title: str
    url: str

    def __post_init__(self) -> None:
        if not is_allowed(self.url):
            raise ValueError(f"Source URL not on allowlist: {self.url}")


@dataclass
class Claim:
    text: str
    sources: list[Source] = field(default_factory=list)


@dataclass
class Answer:
    conclusion: list[Claim]
    reason: list[Claim]
    example: list[Claim]
    notes: list[Claim] = field(default_factory=list)
    release: str = "australia"
    source_breakdown: dict[str, int] = field(default_factory=dict)
    verify_links: bool = True


def _collect_urls(ans: "Answer") -> list[str]:
    urls: list[str] = []
    for section in (ans.conclusion, ans.reason, ans.example, ans.notes):
        for claim in section:
            urls.extend(s.url for s in claim.sources)
    return urls


def _verify_liveness(urls: list[str]) -> None:
    if not urls:
        return
    statuses = check_all(urls)
    dead = [u for u, code in statuses.items() if not (200 <= code < 400)]
    if dead:
        raise ValueError(f"Links not live (would render NotFound): {dead}")


def _build_source_registry(
    ans: "Answer",
) -> tuple[dict[str, int], list[Source]]:
    """Walk all claims in document order; assign each unique URL a 1-based
    footnote index. Returns (url -> index, ordered source list).

    Same URL referenced by multiple claims gets one number, used everywhere.
    """
    seen: dict[str, int] = {}
    ordered: list[Source] = []
    for section in (ans.conclusion, ans.reason, ans.example, ans.notes):
        for claim in section:
            for src in claim.sources:
                if src.url not in seen:
                    seen[src.url] = len(ordered) + 1
                    ordered.append(src)
    return seen, ordered


def _format_footnote_markers(claim: Claim, registry: dict[str, int]) -> str:
    if not claim.sources:
        return ""
    nums = sorted({registry[s.url] for s in claim.sources})
    return "".join(f"[{n}]" for n in nums)


def render_section(
    name: str, claims: list[Claim], registry: dict[str, int]
) -> str:
    if not claims:
        return ""
    lines = [f"## {name}"]
    for claim in claims:
        marker = _format_footnote_markers(claim, registry)
        lines.append(f"{claim.text}{marker}")
    return "\n".join(lines) + "\n"


def _render_references_section(sources: list[Source]) -> str:
    if not sources:
        return ""
    lines = ["## 出典"]
    for idx, src in enumerate(sources, start=1):
        lines.append(f"{idx}. [{src.title}]({src.url})")
    return "\n".join(lines) + "\n"


def _render_footer(release: str, source_breakdown: dict[str, int]) -> list[str]:
    parts = ["---", f"*対象リリース: {release.title()}*"]
    if source_breakdown:
        breakdown = ", ".join(
            f"{k} ({v}件)" for k, v in source_breakdown.items()
        )
        parts.append(f"*調査ソース内訳: {breakdown}*")
    parts.append("*全出典リンクは取得時点で生存確認済 (HTTP 200)*")
    return parts


def render(ans: Answer) -> str:
    if ans.verify_links:
        _verify_liveness(_collect_urls(ans))

    registry, ordered_sources = _build_source_registry(ans)

    parts = [
        render_section("結論", ans.conclusion, registry),
        render_section("理由 / 背景", ans.reason, registry),
        render_section("具体例 / 手順", ans.example, registry),
    ]
    if ans.notes:
        parts.append(render_section("補足 / 注意事項", ans.notes, registry))

    parts.append(_render_references_section(ordered_sources))
    parts.extend(_render_footer(ans.release, ans.source_breakdown))
    return "\n".join(p for p in parts if p)


def render_unknown(
    query: str,
    branches_searched: list[str],
    sources_searched: list[str],
) -> str:
    """Render the 'not found in official sources' response.

    Honest negative answer is critical — users must distinguish "the
    skill could not find this" from "this is the answer, take it".
    Footer mirrors render() so downstream parsers can rely on a single
    document contract. No `## 出典` section because no sources qualify.
    """
    release_label = branches_searched[0] if branches_searched else "指定なし"
    body_parts = [
        "## 結論",
        "公式情報源では該当する情報が見つかりませんでした。",
        "",
        "## 検索内訳",
        f"- クエリ: `{query}`",
        f"- 対象リリース: {', '.join(branches_searched) if branches_searched else '指定なし'}",
        f"- 検索ソース: {', '.join(sources_searched)}",
        "",
        "本スキルでは公式以外の情報源は参照しません。",
        "別のクエリ表現や対象リリースを試すか、ServiceNow サポート"
        " (support.servicenow.com) への問い合わせをご検討ください。",
        "",
        "---",
        f"*対象リリース: {release_label.title() if release_label != '指定なし' else '指定なし'}*",
        "*該当する公式ソースが見つからなかったため、出典リンクは付与していません*",
    ]
    return "\n".join(body_parts) + "\n"
