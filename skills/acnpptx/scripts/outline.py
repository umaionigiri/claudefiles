"""
PPTX Skill — Outline (骨子) Schema and Generator

Before generating slides, Claude creates a JSON outline to confirm the
structure with the user. This module provides:

  1. OUTLINE_SCHEMA     — the JSON structure spec
  2. generate_outline() — create a skeleton outline from a topic + notes
  3. validate_outline() — check the outline is well-formed
  4. format_outline_md()— render the outline as readable Markdown for review
  5. save/load helpers

Usage:
    from outline import generate_outline, format_outline_md, save_outline

    outline = generate_outline(
        title="AIISプロジェクト概要",
        language="ja",
        notes="背景、ソリューション、効果、まとめの4章構成にしたい"
    )
    print(format_outline_md(outline))
    save_outline(outline, "outline.json")
"""

import json
import os
from collections import Counter

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# Valid slide patterns
VALID_PATTERNS = {
    "cover": "表紙 (カバースライド)",
    "C": "セクション区切り (Pattern C)",
    "section": "セクション区切り (Pattern C)",
    "A": "タイトル＋本文 (標準)",
    "B": "2カラム比較",
    "D": "キーメッセージ (インパクト文)",
    "E": "GTアイコン付き箇条書き",
    "F": "カードグリッド 2×2",
    "G": "テーブル",
    "I": "アジェンダ（目次）",
    "J": "KPI / 数値実績",
    "K": "3カラム",
    "L": "Do / Don't 比較",
    "M": "チャート（棒/折れ線/円グラフ）",
    "N": "チーム紹介",
    "P": "シェブロンフロー",
    "Q": "アイコングリッド",
    "R": "スプリットビジュアル（画像＋テキスト）",
    "S": "フレームワーク行列（診断・評価基準表）",
    "T": "2段フロー矢印（課題→提案）",
    "U": "3カラムアイコン＋フッターバー",
    "V": "番号付きカードグリッド",
    "W": "Open-Canvas KPI（大数値統計）",
    "X": "フェーズ付きステップチャート",
    "H": "循環フロー（PDCAサイクル等）",
    "Y": "ガントチャート / ロードマップ",
    "Z": "成熟度モデル（現在 vs 目標）",
    "AA": "2×2 象限マトリクス（優先度評価）",
    "AB": "ロジックツリー / イシューツリー",
    "AC": "積み上げピラミッド",
    "AD": "RAGステータスダッシュボード",
    "AE": "ベン図（3円交差）",
    "AF": "プルクォート（引用スライド）",
    "AG": "アーキテクチャ / コネクター図",
    "AH": "デシジョンマトリクス（◎○△×評価）",
    "AI": "評価スコアカード",
    "AJ": "レーダーチャート",
    "AK": "カレンダー（3ヶ月）",
    "AL": "ビジネスモデルキャンバス",
    "AM": "インタビューカード",
    "AN": "レイヤー図（システム構成）",
}

# Pattern categories for diversity validation
PATTERN_CATEGORIES = {
    "text":      {"A", "D", "E", "AF"},
    "grid":      {"B", "F", "K", "Q", "U", "V"},
    "data":      {"G", "J", "M", "W", "S", "AH", "AI", "AJ"},
    "flow":      {"P", "H", "T", "X"},
    "structure": {"AA", "AB", "AC", "AD", "AE", "AG", "AN", "Z"},
    "special":   {"L", "N", "R", "Y", "AK", "AL", "AM"},
}

# Valid chart types for pattern M
VALID_CHART_TYPES = ["column", "bar", "line", "pie", "stacked_column", "area",
                     "radar", "doughnut", "scatter", "bubble", "combination", "range_bar"]

# ─────────────────────────────────────────────────────────────────────────────
# OUTLINE SCHEMA EXAMPLE (for reference / documentation)
# ─────────────────────────────────────────────────────────────────────────────

OUTLINE_SCHEMA = {
    "title": "プレゼンタイトル",
    "subtitle": "サブタイトル（任意）",
    "date": "2026-03",
    "author": "発表者名",
    "language": "ja",       # "ja" | "en"
    "slides": [
        # Cover slide
        {
            "pattern": "cover",
            "title": "プレゼンタイトル",
            "subtitle": "サブタイトル"
        },
        # Agenda
        {
            "pattern": "I",
            "title": "アジェンダ",
            "breadcrumb": "",
            "items": ["1. 背景", "2. ソリューション", "3. まとめ"]
        },
        # Section divider
        {
            "pattern": "section",
            "title": "セクションタイトル",
            "subtitle": "任意のサブテキスト"
        },
        # Standard content
        {
            "pattern": "A",
            "title": "スライドタイトル",
            "breadcrumb": "セクション > トピック",
            "lead": "リード文（任意）",
            "bullets": ["ポイント1", "ポイント2", "ポイント3"]
        },
        # Two-column
        {
            "pattern": "B",
            "title": "スライドタイトル",
            "left": {"header": "左見出し", "bullets": ["項目1", "項目2"]},
            "right": {"header": "右見出し", "bullets": ["項目A", "項目B"]}
        },
        # Chart
        {
            "pattern": "M",
            "title": "スライドタイトル",
            "breadcrumb": "セクション > データ",
            "chart_type": "column",
            "chart_title": "グラフタイトル",
            "categories": ["Q1", "Q2", "Q3", "Q4"],
            "series": [
                {"name": "2025年", "values": [100, 120, 130, 150]},
                {"name": "2026年", "values": [110, 135, 145, 170]}
            ]
        },
        # KPI
        {
            "pattern": "J",
            "title": "スライドタイトル",
            "kpis": [
                {"value": "82%", "label": "KPI達成率", "detail": "前年比+12%"},
                {"value": "1.8x", "label": "生産性向上", "detail": "AI導入後"},
            ]
        },
        # Key message
        {
            "pattern": "D",
            "title": "スライドタイトル",
            "message": "大きく伝えたいメッセージ",
            "supporting": "補足説明テキスト"
        }
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE OUTLINE (skeleton from notes)
# ─────────────────────────────────────────────────────────────────────────────

def generate_outline(title, language="ja", sections=None, notes="",
                     include_cover=True, include_agenda=True):
    """
    Generate a skeleton outline dict from high-level information.

    This creates a starting point for Claude to refine with actual content.
    Claude should fill in the 'bullets', 'message', 'series', etc. fields
    based on the user's actual content before generating slides.

    Args:
        title       : presentation title
        language    : "ja" | "en"
        sections    : list of section names (e.g. ["背景", "課題", "解決策", "まとめ"])
        notes       : free-form notes about the content (used as breadcrumb hints)
        include_cover : add a cover slide (default True)
        include_agenda: add an agenda slide (default True)

    Returns:
        dict conforming to OUTLINE_SCHEMA structure
    """
    if sections is None:
        sections = (
            ["背景", "ソリューション", "効果", "まとめ"] if language == "ja"
            else ["Background", "Solution", "Results", "Summary"]
        )

    outline = {
        "title": title,
        "subtitle": "",
        "date": _today_ym(),
        "author": "",
        "language": language,
        "slides": []
    }

    # Cover
    if include_cover:
        outline["slides"].append({
            "pattern": "cover",
            "title": title,
            "subtitle": outline["date"]
        })

    # Agenda
    if include_agenda and sections:
        agenda_items = [f"{i+1}. {s}" for i, s in enumerate(sections)]
        outline["slides"].append({
            "pattern": "I",
            "title": "アジェンダ" if language == "ja" else "Agenda",
            "breadcrumb": "",
            "items": agenda_items
        })

    # Section + placeholder content slides
    for i, section in enumerate(sections):
        # Section divider
        outline["slides"].append({
            "pattern": "section",
            "title": section,
            "subtitle": ""
        })

        # Default content slide for this section
        outline["slides"].append({
            "pattern": "A",
            "title": f"{section}：概要",
            "breadcrumb": f"{section} > 概要",
            "lead": "（ここにリード文を入力）",
            "bullets": [
                "（ポイント1）",
                "（ポイント2）",
                "（ポイント3）"
            ]
        })

    return outline


def _today_ym():
    """Return current year-month string like '2026-03'."""
    import datetime
    d = datetime.date.today()
    return d.strftime("%Y-%m")


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

def validate_outline(outline):
    """
    Validate an outline dict for required fields and valid patterns.

    Returns:
        (is_valid: bool, errors: list[str], warnings: list[str])
    """
    errors = []
    warnings = []

    if not isinstance(outline, dict):
        return False, ["Outline must be a dict"], []

    if "title" not in outline:
        errors.append("Missing 'title' at top level")
    if "slides" not in outline:
        errors.append("Missing 'slides' list")
        return False, errors, warnings
    if not isinstance(outline["slides"], list):
        errors.append("'slides' must be a list")
        return False, errors, warnings

    for i, slide in enumerate(outline["slides"]):
        prefix = f"slides[{i}]"
        if "pattern" not in slide:
            errors.append(f"{prefix}: missing 'pattern'")
            continue
        pattern = slide["pattern"]
        if pattern not in VALID_PATTERNS:
            errors.append(f"{prefix}: unknown pattern '{pattern}'. "
                          f"Valid: {list(VALID_PATTERNS.keys())}")

        # Pattern-specific checks
        if pattern == "M":
            if "chart_type" not in slide:
                errors.append(f"{prefix}: pattern M requires 'chart_type'")
            elif slide["chart_type"] not in VALID_CHART_TYPES:
                errors.append(f"{prefix}: invalid chart_type '{slide['chart_type']}'")
            if "categories" not in slide or "series" not in slide:
                errors.append(f"{prefix}: pattern M requires 'categories' and 'series'")

        if pattern == "B":
            for side in ("left", "right"):
                if side not in slide:
                    errors.append(f"{prefix}: pattern B requires '{side}'")

        if pattern == "J":
            if "kpis" not in slide or not slide["kpis"]:
                errors.append(f"{prefix}: pattern J requires non-empty 'kpis' list")

        if pattern == "E":
            if "items" not in slide:
                errors.append(f"{prefix}: パターン E には 'items' リストが必要です")

        if pattern == "F":
            if "cards" not in slide:
                errors.append(f"{prefix}: パターン F には 'cards' リストが必要です")
            elif len(slide["cards"]) != 4:
                errors.append(f"{prefix}: パターン F には 'cards' が4つ必要です（現在 {len(slide['cards'])} 個）")

        if pattern == "K":
            if "columns" not in slide:
                errors.append(f"{prefix}: パターン K には 'columns' リストが必要です")
            elif len(slide["columns"]) != 3:
                errors.append(f"{prefix}: パターン K には 'columns' が3つ必要です（現在 {len(slide['columns'])} 個）")

        if pattern == "P":
            if "steps" not in slide:
                errors.append(f"{prefix}: パターン P には 'steps' リストが必要です")
            elif len(slide["steps"]) < 3:
                errors.append(f"{prefix}: パターン P には 'steps' が3つ以上必要です（現在 {len(slide['steps'])} 個）")

        if pattern == "D":
            if "message" not in slide:
                errors.append(f"{prefix}: パターン D には 'message' が必要です")

        if pattern == "G":
            if "headers" not in slide:
                errors.append(f"{prefix}: パターン G には 'headers' が必要です")
            if "rows" not in slide:
                errors.append(f"{prefix}: パターン G には 'rows' が必要です")

        if pattern == "T":
            if "sections" not in slide:
                errors.append(f"{prefix}: パターン T には 'sections' リストが必要です")
            elif not (2 <= len(slide["sections"]) <= 4):
                errors.append(f"{prefix}: パターン T には 'sections' が2〜4個必要です（現在 {len(slide['sections'])} 個）")

    # ─── Diversity checks (content slides only) ───
    _excluded = {"cover", "section", "I"}
    content_patterns = [
        s["pattern"] for s in outline.get("slides", [])
        if "pattern" in s and s["pattern"] not in _excluded
    ]

    # Consecutive same pattern → warning
    for idx in range(1, len(content_patterns)):
        if content_patterns[idx] == content_patterns[idx - 1]:
            warnings.append(
                f"パターン '{content_patterns[idx]}' が連続で使用されています "
                f"（コンテンツスライド {idx} と {idx + 1}）"
            )

    # Pattern frequency checks
    pattern_counts = Counter(content_patterns)
    for pat, count in pattern_counts.items():
        if count >= 3:
            errors.append(f"パターン '{pat}' が {count} 回使用されています（最大2回まで）")
        elif count == 2:
            warnings.append(f"パターン '{pat}' が2回使用されています — バリエーションを検討してください")

    # Category diversity for larger decks (10+ content slides)
    if len(content_patterns) >= 10:
        used_categories = set()
        for pat in content_patterns:
            for cat_name, cat_patterns in PATTERN_CATEGORIES.items():
                if pat in cat_patterns:
                    used_categories.add(cat_name)
                    break
        if len(used_categories) < 3:
            warnings.append(
                f"ビジュアルカテゴリが {len(used_categories)} 種類しか使われていません "
                f"（10枚以上のデッキでは3種類以上を推奨）"
            )

    return len(errors) == 0, errors, warnings


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN RENDERING (for user review)
# ─────────────────────────────────────────────────────────────────────────────

def format_outline_md(outline):
    """
    Render an outline dict as a human-readable Markdown string.

    Used by Claude to present the outline for user review before generating slides.

    Returns:
        str: Markdown representation
    """
    lines = []

    lines.append(f"# {outline.get('title', '（タイトル未設定）')}")
    if outline.get("subtitle"):
        lines.append(f"*{outline['subtitle']}*")
    meta = []
    if outline.get("date"):    meta.append(f"日付: {outline['date']}")
    if outline.get("author"):  meta.append(f"作成者: {outline['author']}")
    if outline.get("language"): meta.append(f"言語: {outline['language']}")
    if meta:
        lines.append("  ".join(meta))
    lines.append("")

    for i, slide in enumerate(outline.get("slides", [])):
        pattern = slide.get("pattern", "?")
        title = slide.get("title", "（タイトルなし）")
        pattern_label = VALID_PATTERNS.get(pattern, pattern)

        lines.append(f"## スライド {i+1}  `[{pattern}]` {pattern_label}")
        lines.append(f"**タイトル**: {title}")

        if slide.get("subtitle"):
            lines.append(f"**サブタイトル**: {slide['subtitle']}")
        if slide.get("breadcrumb"):
            lines.append(f"**パンくず**: {slide['breadcrumb']}")
        if slide.get("lead"):
            lines.append(f"**リード**: {slide['lead']}")
        if slide.get("message"):
            lines.append(f"**メッセージ**: {slide['message']}")
        if slide.get("supporting"):
            lines.append(f"**補足**: {slide['supporting']}")

        # Bullets
        if slide.get("bullets"):
            lines.append("**本文**:")
            for b in slide["bullets"]:
                lines.append(f"  - {b}")

        # Two-column
        for side in ("left", "right"):
            if slide.get(side):
                s = slide[side]
                lines.append(f"**{side.upper()}** [{s.get('header', '')}]:")
                for b in s.get("bullets", []):
                    lines.append(f"  - {b}")

        # Agenda items
        if slide.get("items"):
            lines.append("**項目**:")
            for item in slide["items"]:
                lines.append(f"  - {item}")

        # KPIs
        if slide.get("kpis"):
            lines.append("**KPI**:")
            for kpi in slide["kpis"]:
                lines.append(f"  - **{kpi.get('value', '?')}** {kpi.get('label', '')}"
                              + (f"  _{kpi.get('detail', '')}_" if kpi.get("detail") else ""))

        # Chart
        if pattern == "M":
            lines.append(f"**グラフ種別**: {slide.get('chart_type', 'column')}")
            if slide.get("chart_title"):
                lines.append(f"**グラフタイトル**: {slide['chart_title']}")
            if slide.get("categories"):
                lines.append(f"**カテゴリ**: {', '.join(str(c) for c in slide['categories'])}")
            if slide.get("series"):
                for s in slide["series"]:
                    vals = ", ".join(str(v) for v in s.get("values", []))
                    lines.append(f"  - {s.get('name', '?')}: [{vals}]")

        # Steps for P (chevron flow)
        if slide.get("steps"):
            lines.append("**ステップ**:")
            for step in slide["steps"]:
                label = step if isinstance(step, str) else step.get("label", "?")
                lines.append(f"  - {label}")

        lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# FILE I/O
# ─────────────────────────────────────────────────────────────────────────────

def save_outline(outline, path):
    """Save outline dict to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(outline, f, ensure_ascii=False, indent=2)


def load_outline(path):
    """Load outline dict from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────────────────────
# CLI DEMO
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    outline = generate_outline(
        title="プロジェクト概要",
        language="ja",
        sections=["背景", "課題", "解決策", "効果", "まとめ"]
    )
    print(format_outline_md(outline))
    valid, errors, warnings = validate_outline(outline)
    print(f"\n検証: {'OK' if valid else 'エラーあり'}")
    for e in errors:
        print(f"  ERROR: {e}")
    for w in warnings:
        print(f"  WARNING: {w}")
