#!/usr/bin/env python3
"""cost_helper.py — 外部 API スキル向けのコスト計算/報告テンプレート.

新スキルにコピーして ``Pricing`` の line items を差し替えれば動く.

機能:
  1. ``compute_breakdown(usage_dict, rates)`` — USD 内訳を返す純粋関数.
  2. ``load_usdjpy()`` — ``~/.claude/cache/usdjpy.json`` (TTL 30 日) を読み込み.
  3. ``warn_if_pricing_stale()`` — ``LAST_VERIFIED_DATE`` が 90 日経過で警告.
  4. ``render_console_table()`` — 固定幅整形のコンソール表.
  5. ``compute_and_report(usage, output_dir)`` — 一括実行 + cost_report.json.

使い方:
  - ``Pricing`` の ``line_items`` を自分のスキルの料金体系に書き換える.
  - ``LAST_VERIFIED_DATE`` を更新日に揃える.
  - CLI: ``python3 cost_helper.py --usage usage.json --output-dir ./out``
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 料金表 (このスキルに合わせて差し替える)
# ---------------------------------------------------------------------------
LAST_VERIFIED_DATE: str = "2026-05-10"
PRICING_STALE_WARN_DAYS: int = 90

DEFAULT_USDJPY: float = 155.0
USDJPY_CACHE_PATH: Path = Path.home() / ".claude" / "cache" / "usdjpy.json"
USDJPY_TTL_DAYS: int = 30


@dataclass(frozen=True)
class LineItem:
    """単一料金行 (例: GPT-4o input tokens)."""
    key: str               # usage dict のキー (例: "prompt_tokens")
    label: str             # 表示名 (例: "GPT-4o input")
    unit: str              # "tokens" | "seconds" | "requests"
    unit_divisor: float    # tokens なら 1_000_000、hour 課金なら 3600
    usd_per_unit: float    # 単価


@dataclass(frozen=True)
class Pricing:
    """このスキルが扱う料金体系一式."""
    line_items: tuple[LineItem, ...] = field(default_factory=lambda: (
        LineItem("audio_seconds", "Speech (audio hour)", "seconds", 3600.0, 0.36),
        LineItem("prompt_tokens", "GPT-4o input",  "tokens", 1_000_000.0, 2.50),
        LineItem("completion_tokens", "GPT-4o output", "tokens", 1_000_000.0, 10.00),
    ))


DEFAULT_PRICING = Pricing()


# ---------------------------------------------------------------------------
# USDJPY キャッシュ
# ---------------------------------------------------------------------------
def load_usdjpy(cache_path: Path = USDJPY_CACHE_PATH) -> tuple[float, str, str | None]:
    """``(rate, source, cached_at)`` を返す. キャッシュ無効なら default."""
    if not cache_path.exists():
        return DEFAULT_USDJPY, "default", None
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        rate = float(payload["rate"])
        cached_at_str = str(payload["cached_at"])
        cached_at = datetime.fromisoformat(cached_at_str.replace("Z", "+00:00"))
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
        print(f"[cost_helper] WARN: USDJPY cache 読み込み失敗 ({exc}), default 使用",
              file=sys.stderr)
        return DEFAULT_USDJPY, "default", None
    if (datetime.now(timezone.utc) - cached_at).days > USDJPY_TTL_DAYS:
        print(f"[cost_helper] WARN: USDJPY cache が TTL ({USDJPY_TTL_DAYS}日) 超過, default 使用",
              file=sys.stderr)
        return DEFAULT_USDJPY, "default", None
    return rate, "cache", cached_at_str


def warn_if_pricing_stale(today: datetime | None = None) -> None:
    today = today or datetime.now(timezone.utc)
    last = datetime.fromisoformat(LAST_VERIFIED_DATE).replace(tzinfo=timezone.utc)
    age = (today - last).days
    if age > PRICING_STALE_WARN_DAYS:
        print(f"[cost_helper] WARN: 料金表 ({LAST_VERIFIED_DATE}) が {age} 日経過. "
              f"references/cost-model.md を更新してください.", file=sys.stderr)


# ---------------------------------------------------------------------------
# 計算 (純粋関数)
# ---------------------------------------------------------------------------
def compute_breakdown(usage: dict[str, float], pricing: Pricing = DEFAULT_PRICING) -> dict[str, Any]:
    """USD 内訳を計算する純粋関数. usage は line_item.key → 使用量の dict."""
    breakdown: dict[str, float] = {}
    total = 0.0
    for item in pricing.line_items:
        amount = float(usage.get(item.key, 0))
        if amount < 0:
            raise ValueError(f"{item.key} は 0 以上である必要があります.")
        usd = (amount / item.unit_divisor) * item.usd_per_unit
        breakdown[item.key] = round(usd, 6)
        total += usd
    breakdown["total"] = round(total, 6)
    return breakdown


# ---------------------------------------------------------------------------
# レンダリング
# ---------------------------------------------------------------------------
def render_console_table(usage: dict[str, float], breakdown_usd: dict[str, float],
                         usdjpy: float, source: str, cached_at: str | None,
                         pricing: Pricing = DEFAULT_PRICING) -> str:
    sep, dash = "=" * 57, "-" * 57
    lines = [sep, "  コスト見積り", sep]
    for item in pricing.line_items:
        usd = breakdown_usd[item.key]
        jpy = round(usd * usdjpy)
        amount = usage.get(item.key, 0)
        lines.append(f"  {item.label:<22}: {amount:>10,.1f} {item.unit:<8}"
                     f"→ ${usd:>7.3f} (¥{jpy:>5d})")
    lines.append(dash)
    total_usd = breakdown_usd["total"]
    lines.append(f"  {'合計':<22}: ${total_usd:>7.3f} (¥{round(total_usd * usdjpy):>5d})")
    cached_label = cached_at[:10] if (source == "cache" and cached_at) else "default"
    lines.append(f"  単価レート             : 1 USD = ¥{usdjpy:.2f} ({cached_label})")
    lines.append(sep)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 高レベル wrapper
# ---------------------------------------------------------------------------
def compute_and_report(usage: dict[str, float], output_dir: Path,
                       pricing: Pricing = DEFAULT_PRICING) -> dict[str, Any]:
    warn_if_pricing_stale()
    rate, source, cached_at = load_usdjpy()
    breakdown_usd = compute_breakdown(usage, pricing)
    breakdown_jpy = {k: round(v * rate) for k, v in breakdown_usd.items()}
    print(render_console_table(usage, breakdown_usd, rate, source, cached_at, pricing))
    output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": dict(usage),
        "rates": {"usdjpy": rate, "usdjpy_source": source,
                  "usdjpy_cached_at": cached_at, "last_verified_date": LAST_VERIFIED_DATE,
                  "line_items": [{"key": i.key, "usd_per_unit": i.usd_per_unit,
                                  "unit_divisor": i.unit_divisor} for i in pricing.line_items]},
        "breakdown_usd": breakdown_usd,
        "breakdown_jpy": breakdown_jpy,
    }
    (output_dir / "cost_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  内訳JSON: {output_dir / 'cost_report.json'}")
    return report


def _cli() -> int:
    p = argparse.ArgumentParser(description="Compute external API cost.")
    p.add_argument("--usage", type=Path, required=True, help='Usage JSON: {"<key>": <amount>, ...}')
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    try:
        usage = json.loads(args.usage.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"[cost_helper][ERR] usage 読み込み失敗: {exc}", file=sys.stderr)
        return 2
    compute_and_report(usage, args.output_dir)
    return 0


def _smoke() -> int:
    print("[cost_helper] smoke: 90 分会議の典型値で計算")
    compute_and_report(
        {"audio_seconds": 5292.0, "prompt_tokens": 28_431, "completion_tokens": 3_210},
        Path("/tmp/cost-helper-smoke"))
    return 0


if __name__ == "__main__":
    sys.exit(_cli() if len(sys.argv) > 1 else _smoke())
