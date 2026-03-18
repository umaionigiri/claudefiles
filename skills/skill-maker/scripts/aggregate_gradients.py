#!/usr/bin/env python3
"""
Aggregate individual gradient.json files into a summary for convergence tracking.

Reads gradient.json files from eval directories within an iteration and produces:
- Mean overall_similarity (primary convergence metric)
- Distribution of gradients by dimension and severity
- Top generalizations ranked by frequency
- Delta from previous iteration for convergence tracking

Usage:
    python -m scripts.aggregate_gradients <iteration_dir> --skill-name <name>

Example:
    python -m scripts.aggregate_gradients proposal-workspace/iteration-2 --skill-name proposal-writer

Directory layout expected:
    <iteration_dir>/
    └── eval-<id>/
        └── gradient.json
"""

import argparse
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


def calculate_stats(values: list[float]) -> dict:
    """Calculate mean, stddev, min, max for a list of values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def deduplicate_generalizations(
    generalizations: list[dict], similarity_threshold: float = 0.6
) -> list[dict]:
    """
    Group similar generalizations and count frequency.

    Uses SequenceMatcher for fuzzy string matching to merge similar
    generalizations that may be worded differently across eval cases.
    """
    groups: list[dict] = []

    for gen in generalizations:
        text = gen["text"]
        severity = gen.get("severity", "minor")
        merged = False

        for group in groups:
            ratio = SequenceMatcher(None, text.lower(), group["text"].lower()).ratio()
            if ratio >= similarity_threshold:
                group["frequency"] += 1
                # Keep the highest severity
                severity_order = {"critical": 3, "major": 2, "minor": 1}
                if severity_order.get(severity, 0) > severity_order.get(
                    group["severity_max"], 0
                ):
                    group["severity_max"] = severity
                # Keep the longer (more detailed) text
                if len(text) > len(group["text"]):
                    group["text"] = text
                merged = True
                break

        if not merged:
            groups.append(
                {"text": text, "frequency": 1, "severity_max": severity}
            )

    # Sort by frequency descending, then by severity
    severity_order = {"critical": 3, "major": 2, "minor": 1}
    groups.sort(
        key=lambda g: (g["frequency"], severity_order.get(g["severity_max"], 0)),
        reverse=True,
    )

    return groups


def load_gradients(iteration_dir: Path) -> list[dict]:
    """Load all gradient.json files from an iteration directory."""
    gradients = []

    for eval_dir in sorted(iteration_dir.glob("eval-*")):
        gradient_file = eval_dir / "gradient.json"
        if not gradient_file.exists():
            print(f"Warning: gradient.json not found in {eval_dir}")
            continue

        try:
            with open(gradient_file, encoding="utf-8") as f:
                gradient = json.load(f)
            gradients.append(gradient)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {gradient_file}: {e}")
        except OSError as e:
            print(f"Warning: Could not read {gradient_file}: {e}")

    return gradients


def load_previous_summary(iteration_dir: Path) -> dict | None:
    """Try to load gradient_summary.json from the previous iteration."""
    current_name = iteration_dir.name  # e.g. "iteration-2"
    try:
        parts = current_name.rsplit("-", 1)
        current_num = int(parts[1])
        if current_num <= 1:
            return None
        prev_name = f"{parts[0]}-{current_num - 1}"
    except (ValueError, IndexError):
        return None

    prev_summary = iteration_dir.parent / prev_name / "gradient_summary.json"
    if not prev_summary.exists():
        return None

    try:
        with open(prev_summary, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def aggregate(gradients: list[dict], skill_name: str, iteration_dir: Path) -> dict:
    """Aggregate multiple gradient results into a summary."""

    # Extract iteration number from directory name
    try:
        iteration_num = int(iteration_dir.name.rsplit("-", 1)[1])
    except (ValueError, IndexError):
        iteration_num = 0

    # Compute mean similarity
    similarities = [g.get("overall_similarity", 0.0) for g in gradients]
    similarity_stats = calculate_stats(similarities)
    mean_similarity = similarity_stats["mean"]

    # Load previous iteration for convergence tracking
    prev_summary = load_previous_summary(iteration_dir)
    prev_similarity = None
    delta = None
    improving = None

    if prev_summary and "convergence" in prev_summary:
        prev_similarity = prev_summary["convergence"].get("mean_similarity")
        if prev_similarity is not None:
            delta = round(mean_similarity - prev_similarity, 4)
            improving = delta > 0

    # Count by dimension and severity
    dimension_counter: Counter = Counter()
    severity_counter: Counter = Counter()

    all_gradient_items = []
    all_generalizations = []
    # Keyed by target_component; each value is a list of generalization dicts
    generalizations_by_component: dict[str, list[dict]] = {}
    all_strengths = []
    all_reference_patterns = []

    for gradient in gradients:
        eval_id = gradient.get("eval_id", "unknown")

        for item in gradient.get("gradients", []):
            dimension = item.get("dimension", "unknown")
            severity = item.get("severity", "unknown")
            # target_component is optional; absent means "SKILL.md"
            target = item.get("target_component", "SKILL.md")
            dimension_counter[dimension] += 1
            severity_counter[severity] += 1

            all_gradient_items.append(
                {
                    "eval_id": eval_id,
                    "dimension": dimension,
                    "severity": severity,
                    "observation": item.get("observation", ""),
                    "generalization": item.get("generalization", ""),
                    "target_component": target,
                }
            )

            if item.get("generalization", "").strip():
                gen_entry = {"text": item["generalization"].strip(), "severity": severity}
                all_generalizations.append(gen_entry)
                generalizations_by_component.setdefault(target, []).append(gen_entry)

        all_strengths.extend(gradient.get("strengths", []))
        all_reference_patterns.extend(gradient.get("reference_patterns", []))

    # Deduplicate generalizations (global list, unchanged for backwards compat)
    top_generalizations = deduplicate_generalizations(all_generalizations)

    # Build component_routing: per-component deduplicated generalizations
    # Only populated for components that have at least one routed generalization.
    # "SKILL.md" entries are also included so the improvement step sees a complete picture.
    component_routing: dict[str, list[dict]] = {}
    for component, gen_list in generalizations_by_component.items():
        deduped = deduplicate_generalizations(gen_list)
        if deduped:
            component_routing[component] = deduped

    # Deduplicate strengths (simple exact match)
    unique_strengths = list(dict.fromkeys(all_strengths))

    # Deduplicate reference patterns
    unique_patterns = list(dict.fromkeys(all_reference_patterns))

    summary = {
        "metadata": {
            "skill_name": skill_name or "<skill-name>",
            "iteration": iteration_num,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "num_eval_cases": len(gradients),
        },
        "convergence": {
            "mean_similarity": mean_similarity,
            "similarity_stats": similarity_stats,
            "previous_similarity": prev_similarity,
            "delta": delta,
            "improving": improving,
        },
        "gradient_distribution": {
            "by_dimension": dict(dimension_counter.most_common()),
            "by_severity": dict(severity_counter.most_common()),
        },
        "top_generalizations": top_generalizations,
        # component_routing: maps each target file to its deduplicated generalizations.
        # The improvement step should apply each entry's generalizations to the named file,
        # not to SKILL.md. Non-SKILL.md entries represent concrete script/spec/agent fixes.
        "component_routing": component_routing,
        "preserved_strengths": unique_strengths,
        "reference_patterns": unique_patterns,
        "all_gradients": all_gradient_items,
    }

    return summary


def generate_markdown(summary: dict) -> str:
    """Generate human-readable gradient_summary.md."""
    metadata = summary["metadata"]
    convergence = summary["convergence"]

    lines = [
        f"# Gradient Summary: {metadata['skill_name']} (Iteration {metadata['iteration']})",
        "",
        f"**Date**: {metadata['timestamp']}",
        f"**Eval cases**: {metadata['num_eval_cases']}",
        "",
        "## Convergence",
        "",
        f"- **Mean similarity**: {convergence['mean_similarity']:.2f}",
    ]

    if convergence.get("previous_similarity") is not None:
        lines.append(
            f"- **Previous**: {convergence['previous_similarity']:.2f}"
        )
        lines.append(f"- **Delta**: {convergence['delta']:+.4f}")
        status = "Improving" if convergence["improving"] else "Not improving"
        lines.append(f"- **Status**: {status}")

    # Distribution
    lines.extend(["", "## Gradient Distribution", ""])

    by_dim = summary["gradient_distribution"]["by_dimension"]
    if by_dim:
        lines.append("**By dimension:**")
        for dim, count in by_dim.items():
            lines.append(f"- {dim}: {count}")

    by_sev = summary["gradient_distribution"]["by_severity"]
    if by_sev:
        lines.append("")
        lines.append("**By severity:**")
        for sev, count in by_sev.items():
            lines.append(f"- {sev}: {count}")

    # Component routing (non-SKILL.md targets only — these need direct file edits)
    routing = summary.get("component_routing", {})
    non_skill_routing = {k: v for k, v in routing.items() if k != "SKILL.md"}
    if non_skill_routing:
        lines.extend(["", "## Component Routing (apply to specific files)", ""])
        lines.append("These gradients target specific skill files, not SKILL.md:")
        for component, gens in non_skill_routing.items():
            lines.extend(["", f"### `{component}`"])
            for i, gen in enumerate(gens[:5], 1):
                sev = gen["severity_max"]
                freq = gen["frequency"]
                lines.append(f"{i}. [{sev}] (x{freq}) {gen['text']}")

    # Top generalizations
    top_gens = summary.get("top_generalizations", [])
    if top_gens:
        lines.extend(["", "## Top Generalizations (all components)", ""])
        for i, gen in enumerate(top_gens[:10], 1):
            freq = gen["frequency"]
            sev = gen["severity_max"]
            lines.append(f"{i}. [{sev}] (x{freq}) {gen['text']}")

    # Strengths to preserve
    strengths = summary.get("preserved_strengths", [])
    if strengths:
        lines.extend(["", "## Strengths to Preserve", ""])
        for s in strengths:
            lines.append(f"- {s}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate gradient.json files into a summary for convergence tracking"
    )
    parser.add_argument(
        "iteration_dir", type=Path, help="Path to the iteration directory"
    )
    parser.add_argument(
        "--skill-name", default="", help="Name of the skill being optimized"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for gradient_summary.json (default: <iteration_dir>/gradient_summary.json)",
    )

    args = parser.parse_args()

    if not args.iteration_dir.exists():
        print(f"Directory not found: {args.iteration_dir}")
        sys.exit(1)

    # Load all gradients
    gradients = load_gradients(args.iteration_dir)
    if not gradients:
        print(f"No gradient.json files found in {args.iteration_dir}/eval-*/")
        sys.exit(1)

    # Aggregate
    summary = aggregate(gradients, args.skill_name, args.iteration_dir)

    # Determine output paths
    output_json = args.output or (args.iteration_dir / "gradient_summary.json")
    output_md = output_json.with_suffix(".md")

    # Write gradient_summary.json
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Generated: {output_json}")

    # Write gradient_summary.md
    markdown = generate_markdown(summary)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Generated: {output_md}")

    # Print summary
    convergence = summary["convergence"]
    print(f"\nSummary:")
    print(f"  Mean similarity: {convergence['mean_similarity']:.2f}")
    if convergence.get("delta") is not None:
        print(f"  Delta:           {convergence['delta']:+.4f}")
        print(
            f"  Status:          {'Improving' if convergence['improving'] else 'Not improving'}"
        )

    top_gens = summary.get("top_generalizations", [])
    if top_gens:
        print(f"  Top generalizations: {len(top_gens)}")
        for gen in top_gens[:3]:
            text_preview = gen['text'][:80] + ('...' if len(gen['text']) > 80 else '')
            print(f"    [{gen['severity_max']}] (x{gen['frequency']}) {text_preview}")


if __name__ == "__main__":
    main()
