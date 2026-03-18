# JSON Schemas

This document defines the JSON schemas used by skill-maker.

> **Naming collision warning — `expectations`**: This field name appears in THREE different files with DIFFERENT structures. Always confirm which file you are reading/writing before parsing.
> - `evals.json`: `expectations: [string]` — plain assertion strings, ungraded
> - `eval_metadata.json`: `assertions: [string]` — same concept, different field name, different file
> - `grading.json`: `expectations: [{text, passed, evidence}]` — graded objects; **field names must be exactly `text`, `passed`, `evidence`**

---

## evals.json

Defines the evals for a skill. Located at `evals/evals.json` within the skill directory.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "eval_name": "basic-transform",
      "prompt": "User's example prompt",
      "expected_output": "Description of expected result",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "The output includes X",
        "The skill used script Y"
      ]
    }
  ]
}
```

**Fields:**
- `skill_name`: Name matching the skill's frontmatter name field exactly. Validated by `check_completeness.py` Check 8.
- `evals[].id`: Unique integer identifier. Must be unique within the file — duplicate ids cause silent data loss in benchmark aggregation.
- `evals[].eval_name`: (optional but recommended) Kebab-case string identifier used as the eval directory name (e.g., `eval-basic-transform/`). When omitted, the directory is named by numeric id. Maps to `eval_id` in `eval_metadata.json`.

**Directory naming rule**: The eval directory name is always derived as follows:
- `eval_name` present → directory is `eval-{eval_name}` (e.g., `eval-basic-transform/`)
- `eval_name` absent → directory is `eval-{id}` (e.g., `eval-1/`)

The numeric `id` is used for ordering and history tracking; `eval_name` is preferred for human-readable directory names and when using the reference-based workflow (where `training_data.json` `pairs[].id` maps to `eval_name`).
- `evals[].prompt`: The task to execute
- `evals[].expected_output`: Human-readable description of success
- `evals[].files`: Optional list of input file paths (relative to skill root)
- `evals[].expectations`: List of verifiable assertion strings (plain text — NOT objects). These describe *what to check*, written before running. During grading, each string becomes the `text` field of an object `{text, passed, evidence}` in `grading.json`. The two formats share the name `expectations` but are structurally different: evals.json has `[string]`, grading.json has `[{text, passed, evidence}]`.

---

## history.json

> **Legacy schema** — not currently used by the autonomous loop or manual eval workflow. Retained for reference only. Do not create or read this file in new skills.

Tracks version progression in Improve mode. Located at workspace root.

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**Fields:**
- `started_at`: ISO timestamp of when improvement started
- `skill_name`: Name of the skill being improved
- `current_best`: Version identifier of the best performer
- `iterations[].version`: Version identifier (v0, v1, ...)
- `iterations[].parent`: Parent version this was derived from
- `iterations[].expectation_pass_rate`: Pass rate from grading
- `iterations[].grading_result`: "baseline", "won", "lost", or "tie"
- `iterations[].is_current_best`: Whether this is the current best version

---

## grading.json

Output from the grader agent. Located at `<config-dir>/grading.json` — that is, the configuration directory (e.g., `eval-<name>/with_skill/grading.json` or `eval-<name>/without_skill/grading.json`). In multi-run mode, at `<config-dir>/run-N/grading.json`.

```json
{
  "expectations": [
    {
      "text": "The output includes the name 'John Smith'",
      "passed": true,
      "evidence": "Found in transcript Step 3: 'Extracted names: John Smith, Sarah Johnson'"
    },
    {
      "text": "The spreadsheet has a SUM formula in cell B10",
      "passed": false,
      "evidence": "No spreadsheet was created. The output was a text file."
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "The form has 12 fillable fields",
      "type": "factual",
      "verified": true,
      "evidence": "Counted 12 fields in field_info.json"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["Used 2023 data, may be stale"],
    "needs_review": [],
    "workarounds": ["Fell back to text overlay for non-fillable fields"]
  },
  "eval_feedback": {
    "suggestions": [
      {
        "assertion": "The output includes the name 'John Smith'",
        "reason": "A hallucinated document that mentions the name would also pass"
      }
    ],
    "overall": "Assertions check presence but not correctness."
  }
}
```

**Fields:**
- `expectations[]`: Graded expectations with evidence
- `summary`: Aggregate pass/fail counts
- `execution_metrics`: Tool usage and output size (from executor's metrics.json)
- `timing`: Wall clock timing (from timing.json)
- `claims`: Extracted and verified claims from the output
- `user_notes_summary`: Issues flagged by the executor
- `eval_feedback`: (optional) Improvement suggestions for the evals, only present when the grader identifies issues worth raising

**Relationship to evals.json and benchmark.json:**
- Each grading.json captures results for *one run of one eval case*. The `expectations` array uses `{text, passed, evidence}` objects — do NOT use field names like `name`/`met`/`details`; the eval-viewer and `aggregate_benchmark.py` depend on the exact field names `text`, `passed`, and `evidence`.
- The `text` values here correspond to the plain strings in `evals.json` `expectations[]`. They share the field name but differ structurally: evals.json has `[string]` (ungraded), grading.json has `[{text, passed, evidence}]` (graded).
- `benchmark.json` (below) aggregates multiple grading.json files across eval cases and configurations into summary statistics.

---

## metrics.json

Output from the executor agent. Located at `<run-dir>/outputs/metrics.json`.

```json
{
  "tool_calls": {
    "Read": 5,
    "Write": 2,
    "Bash": 8,
    "Edit": 1,
    "Glob": 2,
    "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

**Fields:**
- `tool_calls`: Count per tool type
- `total_tool_calls`: Sum of all tool calls
- `total_steps`: Number of major execution steps
- `files_created`: List of output files created
- `errors_encountered`: Number of errors during execution
- `output_chars`: Total character count of output files
- `transcript_chars`: Character count of transcript

---

## timing.json

Wall clock timing for a run. Located at `<config-dir>/timing.json` — that is, the config directory (e.g., `eval-<name>/with_skill/timing.json`), NOT inside a nested `run-N/` subdirectory. This matches where grader.md writes its timing fallback and what `aggregate_benchmark.py` reads in the flat layout.

**How to capture:** When a subagent task completes, the task notification includes `total_tokens` and `duration_ms`. Save these immediately — they are not persisted anywhere else and cannot be recovered after the fact.

**Fallback structure:** When timing data is unavailable (e.g., the grader ran before the executor finished, or subagent notifications were missed), `agents/grader.md` writes a minimal fallback:

```json
{
  "note": "timing unavailable — grader created this placeholder"
}
```

Scripts reading `timing.json` must handle both structures. Check for the `note` field and treat it as missing data rather than a crash. `aggregate_benchmark.py` already handles this gracefully by checking for `total_tokens` before accessing it.

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## eval_metadata.json

Per-eval-case metadata. Located at `<workspace>/iteration-N/eval-<name>/eval_metadata.json`. Written when spawning eval runs; updated when adding assertions.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": [
    "The output includes a chart with labeled axes",
    "The CSV has a header row"
  ],
  "mode": "standard"
}
```

**Fields:**
- `eval_id`: Numeric identifier (integer) or string identifier (for reference-based mode, e.g., `"crm-case"`)
- `eval_name`: Human-readable name describing what this eval tests (also used as directory name)
- `prompt`: The task prompt given to the subagent
- `assertions`: List of verifiable statements (added in Step 2 of the eval workflow, may start empty). **Naming note**: `eval_metadata.json` calls this field `assertions` (strings); `evals.json` calls the equivalent field `expectations` (also strings); `grading.json` reuses `expectations` for graded `{text, passed, evidence}` objects. All three are the same concept at different stages — pre-run strings vs post-grading objects. Do not confuse them when reading or writing these files.
- `mode`: (optional) indicates which workflow produced this eval — `"standard"` (default, intent-based), `"reference_based"` (reference-based workflow), or `"capture_by_doing"` (Capture by Doing / observer workflow)
- `baseline_skipped`: (optional boolean) `true` when the without_skill / old_skill baseline run was intentionally skipped. Document this when the baseline trivially fails every format assertion (e.g., Claude without the skill cannot produce a PPTX file at all). See `references/eval-workflow.md` for when to skip.
- `baseline_skip_reason`: (optional string) One-sentence explanation of why the baseline was skipped. Required when `baseline_skipped: true` to preserve institutional memory across iterations.

---

## benchmark.json

Output from `aggregate_benchmark.py`. Located at `<workspace>/iteration-N/benchmark.json` — the iteration directory passed to the script (e.g., `my-skill-workspace/iteration-1/benchmark.json`).

```json
{
  "metadata": {
    "skill_name": "pdf",
    "skill_path": "/path/to/pdf",
    "executor_model": "claude-sonnet-4-20250514",
    "analyzer_model": "most-capable-model",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },

  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": [
        "Used 2023 data, may be stale",
        "Fell back to text overlay for non-fillable fields"
      ]
    }
  ],

  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },

  "notes": [
    "Assertion 'Output is a PDF file' passes 100% in both configurations - may not differentiate skill value",
    "Eval 3 shows high variance (50% ± 40%) - may be flaky or model-dependent",
    "Without-skill runs consistently fail on table extraction expectations",
    "Skill adds 13s average execution time but improves pass rate by 50%"
  ]
}
```

**Fields:**
- `metadata`: Information about the benchmark run
  - `skill_name`: Name of the skill
  - `timestamp`: When the benchmark was run
  - `evals_run`: List of eval names or IDs
  - `runs_per_configuration`: Number of runs per config (e.g. 3)
- `runs[]`: Individual run results
  - `eval_id`: Numeric eval identifier
  - `eval_name`: Human-readable eval name (used as section header in the viewer)
  - `configuration`: Config name string — valid values are `"with_skill"`, `"new_skill"` (primary/skill under evaluation) and `"without_skill"`, `"old_skill"`, `"baseline"` (comparison baseline). The viewer uses this field for grouping and color coding.
  - `run_number`: Integer run number (1, 2, 3...)
  - `result`: Nested object with `pass_rate`, `passed`, `total`, `time_seconds`, `tokens`, `errors`
- `run_summary`: Statistical aggregates per configuration
  - `with_skill` / `without_skill`: Each contains `pass_rate`, `time_seconds`, `tokens` objects with `mean` and `stddev` fields
  - `delta`: Difference strings like `"+0.50"`, `"+13.0"`, `"+1700"`
- `notes`: Freeform observations from the analyzer

**Important:** The viewer reads these field names exactly. Using `config` instead of `configuration`, or putting `pass_rate` at the top level of a run instead of nested under `result`, will cause the viewer to show empty/zero values. Always reference this schema when generating benchmark.json manually.

---

## feedback.json

Output from the eval viewer when the user clicks "Submit All Reviews". Located at `<workspace>/feedback.json` (written by the viewer to the workspace root). Read by skill-maker in `references/eval-workflow.md` Step 5.

```json
{
  "reviews": [
    {
      "run_id": "eval-basic-transform-with_skill",
      "feedback": "The chart is missing axis labels",
      "timestamp": "2026-01-15T10:45:00Z"
    },
    {
      "run_id": "eval-edge-case-with_skill",
      "feedback": "",
      "timestamp": "2026-01-15T10:46:00Z"
    }
  ],
  "status": "complete"
}
```

**Fields:**
- `reviews[]`: One entry per reviewed run
  - `run_id`: Identifier combining eval directory name and config (e.g., `eval-basic-transform-with_skill`)
  - `feedback`: User's free-text comment. Empty string = user found nothing wrong.
  - `timestamp`: When the review was submitted (ISO 8601)
- `status`: `"complete"` once the user clicks "Submit All Reviews"

**How to read:** Empty `feedback` = acceptable output; focus improvements on runs with non-empty feedback. The viewer also writes a `feedback.complete` sentinel file alongside `feedback.json` to signal that all reviews were submitted (used by automated watchers).

---

## iteration_history.json

Cross-iteration tracking file for the reference-based workflow. Located at `<skill>-workspace/iteration_history.json`. Updated after each iteration by the skill-maker when following `references/reference-based-workflow.md`.

```json
{
  "skill_name": "proposal-writer",
  "iterations": [
    {
      "iteration": 1,
      "mean_similarity": 0.58,
      "delta": null,
      "num_critical": 3,
      "num_major": 5,
      "snapshot_path": "iteration-1/skill-snapshot/",
      "summary": "Added ROI calculation procedure and executive summary structure"
    },
    {
      "iteration": 2,
      "mean_similarity": 0.72,
      "delta": 0.14,
      "num_critical": 1,
      "num_major": 3,
      "snapshot_path": "iteration-2/skill-snapshot/",
      "summary": "Addressed document ordering and executive summary placement"
    }
  ],
  "best_iteration": 2
}
```

**Fields:**
- `skill_name`: Name of the skill being optimized
- `iterations[]`: One entry per reference-based workflow iteration
  - `iteration`: Iteration number (1-based)
  - `mean_similarity`: Mean similarity from `gradient_summary.json` `convergence.mean_similarity`
  - `delta`: Change from previous iteration (`null` for iteration 1)
  - `num_critical` / `num_major`: Count of gradients at each severity level
  - `snapshot_path`: Relative path to the skill snapshot taken at this iteration
  - `summary`: One-sentence description of what changed this iteration
- `best_iteration`: The iteration number with the highest `mean_similarity`

**When to use:** After 5 iterations without convergence, read `best_iteration` and restore the snapshot from that iteration rather than continuing with the current (potentially overfitted) version.

---

## comparison.json

Output from blind comparator. Located at `<grading-dir>/comparison-N.json`.

```json
{
  "winner": "A",
  "reasoning": "Output A provides a complete solution with proper formatting and all required fields. Output B is missing the date field and has formatting inconsistencies.",
  "rubric": {
    "A": {
      "content": {
        "correctness": 5,
        "completeness": 5,
        "accuracy": 4
      },
      "structure": {
        "organization": 4,
        "formatting": 5,
        "usability": 4
      },
      "content_score": 4.7,
      "structure_score": 4.3,
      "overall_score": 9.0
    },
    "B": {
      "content": {
        "correctness": 3,
        "completeness": 2,
        "accuracy": 3
      },
      "structure": {
        "organization": 3,
        "formatting": 2,
        "usability": 3
      },
      "content_score": 2.7,
      "structure_score": 2.7,
      "overall_score": 5.4
    }
  },
  "output_quality": {
    "A": {
      "score": 9,
      "strengths": ["Complete solution", "Well-formatted", "All fields present"],
      "weaknesses": ["Minor style inconsistency in header"]
    },
    "B": {
      "score": 5,
      "strengths": ["Readable output", "Correct basic structure"],
      "weaknesses": ["Missing date field", "Formatting inconsistencies", "Partial data extraction"]
    }
  },
  "expectation_results": {
    "A": {
      "passed": 4,
      "total": 5,
      "pass_rate": 0.80,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    },
    "B": {
      "passed": 3,
      "total": 5,
      "pass_rate": 0.60,
      "details": [
        {"text": "Output includes name", "passed": true}
      ]
    }
  }
}
```

---

## analysis.json

Output from post-hoc analyzer. Located at `<grading-dir>/analysis.json`.

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill",
    "comparator_reasoning": "Brief summary of why comparator chose winner"
  },
  "winner_strengths": [
    "Clear step-by-step instructions for handling multi-page documents",
    "Included validation script that caught formatting errors"
  ],
  "loser_weaknesses": [
    "Vague instruction 'process the document appropriately' led to inconsistent behavior",
    "No script for validation, agent had to improvise"
  ],
  "instruction_following": {
    "winner": {
      "score": 9,
      "issues": ["Minor: skipped optional logging step"]
    },
    "loser": {
      "score": 6,
      "issues": [
        "Did not use the skill's formatting template",
        "Invented own approach instead of following step 3"
      ]
    }
  },
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "Replace 'process the document appropriately' with explicit steps",
      "expected_impact": "Would eliminate ambiguity that caused inconsistent behavior"
    }
  ],
  "transcript_insights": {
    "winner_execution_pattern": "Read skill -> Followed 5-step process -> Used validation script",
    "loser_execution_pattern": "Read skill -> Unclear on approach -> Tried 3 different methods"
  }
}
```

---

## training_data.json

Defines input/reference pairs for reference-based skill creation. Located at `<skill>-workspace/training_data.json`.

```json
{
  "skill_name": "example-skill",
  "task_description": "Create a SaaS adoption proposal from a hearing memo",
  "output_description": "A proposal document covering executive summary, current state analysis, solution recommendation, and ROI calculation",
  "pairs": [
    {
      "id": "crm-case",
      "description": "CRM adoption proposal for mid-size manufacturer",
      "input_files": ["training-data/crm-case/input/hearing_memo.md"],
      "reference_files": ["training-data/crm-case/reference/proposal.md"],
      "notes": "Includes complex ROI calculation with multiple cost categories"
    },
    {
      "id": "accounting-case",
      "description": "Accounting system migration for retail chain",
      "input_files": ["training-data/accounting-case/input/hearing_memo.md", "training-data/accounting-case/input/current_system_info.csv"],
      "reference_files": ["training-data/accounting-case/reference/proposal.md"],
      "notes": "Migration-specific considerations: data transfer, parallel operation period"
    }
  ]
}
```

**Fields:**
- `skill_name`: Name for the skill being created
- `task_description`: What the skill should do (used as context for gradient generation)
- `output_description`: What the expected output looks like (format, structure)
- `pairs[]`: Array of input/reference pairs (recommend 3-5 minimum)
  - `pairs[].id`: Descriptive identifier (used as directory name, e.g. `eval-crm-case/`)
  - `pairs[].description`: Brief description of this example
  - `pairs[].input_files`: Paths to input context files (relative to workspace)
  - `pairs[].reference_files`: Paths to gold-standard reference outputs (relative to workspace)
  - `pairs[].notes`: Optional notes about edge cases or special characteristics

---

## gradient.json

Output from the gradient agent. Located at `<workspace>/iteration-N/eval-<id>/gradient.json`.

```json
{
  "eval_id": "crm-case",
  "overall_similarity": 0.65,
  "overall_assessment": "The generated output captures the basic proposal structure but lacks the reference's systematic ROI calculation and misses industry-specific cost categories.",
  "gradients": [
    {
      "dimension": "completeness",
      "severity": "critical",
      "observation": "Reference includes a 5-row ROI table with per-category cost breakdown (licensing, implementation, training, maintenance, opportunity cost). Generated output has only a single qualitative sentence: 'ROI is expected to be significant.'",
      "why_reference_is_better": "Quantified ROI with line-by-line breakdown gives decision-makers concrete numbers to evaluate. A qualitative statement provides no actionable information.",
      "generalization": "The skill should include explicit instructions for calculating ROI: enumerate cost categories from the input, estimate savings per category, and compute payback period."
    },
    {
      "dimension": "structure",
      "severity": "major",
      "observation": "Reference places the executive summary first with key metrics highlighted. Generated output buries the summary after a lengthy background section.",
      "why_reference_is_better": "Executive stakeholders read the summary first and may not read further. Front-loading key metrics respects their time and increases proposal impact.",
      "generalization": "The skill should specify document structure with executive summary as the first section, containing the most important metrics and recommendations."
    },
    {
      "dimension": "accuracy",
      "severity": "critical",
      "observation": "Validator passes slides with 8pt font sizes. Reference output never uses text below 12pt.",
      "why_reference_is_better": "8pt text is illegible in rendered slides. The validator must reject font sizes below the reference minimum.",
      "generalization": "Raise the font size validation threshold to 12pt to match the reference's observed minimum.",
      "target_component": "scripts/validate.py"
    }
  ],
  "strengths": [
    "Correctly identified the client's core pain points from the hearing memo",
    "Appropriate vendor recommendations based on company size",
    "Professional tone consistent with a formal proposal"
  ],
  "reference_patterns": [
    "Every section ends with a concrete next-step or action item",
    "All numerical claims are traceable to specific input data points",
    "Risk mitigation section always pairs each risk with a specific countermeasure"
  ]
}
```

**Fields:**
- `eval_id`: Matches the training pair ID
- `overall_similarity`: 0.0-1.0 score of how close the generated output is to the reference (used for convergence tracking)
- `overall_assessment`: Brief narrative summary of the comparison
- `gradients[]`: Array of specific differences (the "text gradients")
  - `dimension`: Category of difference — one of: `content`, `structure`, `quality`, `completeness`, `accuracy`
  - `severity`: Impact level — `critical` (would change the output's usefulness), `major` (noticeable quality gap), `minor` (polish issue)
  - `observation`: Factual description of what differs between generated and reference
  - `why_reference_is_better`: Analysis of why the reference's approach is superior
  - `generalization`: **The general principle the Skill should learn** — abstracted from this specific example to be applicable across all inputs
  - `target_component` *(optional)*: Which skill file this gradient should update. Omit when it's an instruction/workflow issue (defaults to `"SKILL.md"`). Set only when the root cause is clearly in a specific non-instruction file: `"scripts/<filename>"` for script constants/algorithms, `"references/<filename>"` for spec/design doc errors, `"agents/<filename>"` for subagent instruction issues.
- `strengths[]`: Things the generated output did well that should be preserved in skill rewrites
- `reference_patterns[]`: Recurring patterns observed in the reference that seem intentional and important

---

## gradient_summary.json

Aggregated gradient data across all training pairs for one iteration. Located at `<workspace>/iteration-N/gradient_summary.json`. Generated by `scripts/aggregate_gradients.py`.

```json
{
  "metadata": {
    "skill_name": "proposal-writer",
    "iteration": 2,
    "timestamp": "2026-01-15T10:30:00Z",
    "num_eval_cases": 4
  },
  "convergence": {
    "mean_similarity": 0.72,
    "similarity_stats": {"mean": 0.72, "stddev": 0.08, "min": 0.61, "max": 0.83},
    "previous_similarity": 0.58,
    "delta": 0.14,
    "improving": true
  },
  "gradient_distribution": {
    "by_dimension": {
      "content": 4,
      "structure": 7,
      "quality": 3,
      "completeness": 2,
      "accuracy": 1
    },
    "by_severity": {
      "critical": 2,
      "major": 8,
      "minor": 7
    }
  },
  "top_generalizations": [
    {
      "text": "The skill should include explicit instructions for calculating ROI with per-category cost breakdown",
      "frequency": 3,
      "severity_max": "critical"
    },
    {
      "text": "Document structure should place executive summary first with key metrics highlighted",
      "frequency": 2,
      "severity_max": "major"
    }
  ],
  "component_routing": {
    "SKILL.md": [
      {
        "text": "The skill should include explicit instructions for calculating ROI with per-category cost breakdown",
        "frequency": 3,
        "severity_max": "critical"
      }
    ],
    "scripts/validate.py": [
      {
        "text": "Raise the font size validation threshold to 12pt to match the reference's observed minimum",
        "frequency": 2,
        "severity_max": "critical"
      }
    ]
  },
  "preserved_strengths": [
    "Correctly identified the client's core pain points from the hearing memo",
    "Professional tone consistent with a formal proposal",
    "Appropriate vendor recommendations based on company size"
  ],
  "reference_patterns": [
    "Every section ends with a concrete next-step or action item",
    "All numerical claims cite their source data from the input"
  ],
  "all_gradients": [
    {
      "eval_id": "crm-case",
      "dimension": "completeness",
      "severity": "critical",
      "observation": "Reference includes a 5-row ROI table...",
      "generalization": "The skill should include explicit instructions for calculating ROI...",
      "target_component": "SKILL.md"
    }
  ]
}
```

**Fields:**
- `metadata`: Information about the aggregation run
  - `skill_name`: Name of the skill being optimized
  - `iteration`: Which iteration this summary is for
  - `timestamp`: When the aggregation was run
  - `num_eval_cases`: Number of training pairs evaluated
- `convergence`: Convergence tracking data
  - `mean_similarity`: Average `overall_similarity` across all eval cases this iteration
  - `similarity_stats`: Full statistics (mean, stddev, min, max) for similarity across eval cases
  - `previous_similarity`: The `mean_similarity` from the previous iteration (null if first iteration)
  - `delta`: Change from previous iteration (positive = improving)
  - `improving`: Whether `delta > 0`
- `gradient_distribution`: Counts of gradients by category
  - `by_dimension`: How many gradients in each dimension
  - `by_severity`: How many gradients at each severity level
- `top_generalizations[]`: Most frequently occurring generalizations across all eval cases, sorted by frequency (all components combined)
  - `text`: The generalization text
  - `frequency`: How many eval cases produced this or a similar generalization
  - `severity_max`: The highest severity associated with this generalization
- `component_routing`: Generalizations grouped by which skill file they should update. The improvement step applies each entry to the named file rather than SKILL.md. Keys are file paths relative to the skill root (e.g. `"scripts/validate.py"`, `"references/visual-spec.md"`, `"SKILL.md"`). Values are deduplicated generalization lists (same shape as `top_generalizations`).
- `preserved_strengths[]`: Union of all strengths across eval cases
- `reference_patterns[]`: Union of all recurring patterns observed in the references across eval cases
- `all_gradients[]`: Flat list of all individual gradients from all eval cases (for detailed inspection). Each item now includes `target_component` (always present, defaulting to `"SKILL.md"` when the gradient agent omitted it).

---

## review.json

Output from the reviewer agent (`agents/reviewer.md`). Located at `<workspace>/self-review/review-N.json`.

```json
{
  "iteration": 1,
  "skill_path": "/path/to/skill",
  "timestamp": "2026-01-15T10:30:00Z",
  "summary": {
    "total_findings": 5,
    "critical": 1,
    "major": 2,
    "minor": 2,
    "clean": false
  },
  "findings": [
    {
      "id": "SEC-001",
      "severity": "critical",
      "category": "security",
      "file": "scripts/process_data.py",
      "line": 42,
      "description": "User input passed directly to subprocess with shell=True",
      "suggestion": "Use subprocess.run with a list argument instead of a shell string",
      "evidence": "Line 42: subprocess.run(f'convert {user_file}', shell=True)"
    }
  ],
  "regressions": [],
  "unfixed_from_previous": [],
  "strengths": [
    "Clean directory structure following skill conventions"
  ],
  "overall_assessment": "One critical security issue needs immediate attention."
}
```

**Fields:**
- `iteration`: Review iteration number (1-5)
- `skill_path`: Path to the reviewed skill directory
- `timestamp`: When the review was performed (ISO 8601)
- `summary`: Aggregate counts
  - `total_findings`: Total number of issues found
  - `critical` / `major` / `minor`: Count by severity
  - `clean`: Boolean — `true` when `critical == 0 AND major == 0`
- `findings[]`: Individual issues found
  - `id`: Unique identifier (category prefix + number, e.g., SEC-001, BUG-001, ERR-001, BP-001, DC-001, CON-001, INF-001)
  - `severity`: `critical`, `major`, or `minor`
  - `category`: One of: `security`, `error`, `bug`, `best-practice`, `dead-code`, `consistency`, `infrastructure`
  - `file`: Relative path within the skill directory
  - `line`: Line number (null if not applicable)
  - `description`: What the issue is
  - `suggestion`: How to fix it
  - `evidence`: The specific code or text that demonstrates the issue
- `regressions[]`: Issues from the previous review that were fixed but reappeared (same format as findings)
- `unfixed_from_previous[]`: Critical/major finding IDs from the previous review that were not addressed
- `strengths[]`: Positive aspects of the skill worth preserving during fixes
- `overall_assessment`: Brief narrative summary of the review

---

## workflow_trace.json

Structured execution log produced by the executor during "Capture by Doing" mode. Located at `<skill-name>-workspace/workflow_trace.json`. Written incrementally during task execution — each step is appended as the executor completes it.

```json
{
  "metadata": {
    "task_summary": "Convert quarterly sales CSV into a formatted executive report with charts",
    "domain": "data-transform",
    "task_outcome": "success",
    "failure_reason": null,
    "timestamp_start": "2026-01-15T10:30:00Z",
    "timestamp_end": "2026-01-15T10:45:00Z",
    "working_directory": "/c/Users/user/project",
    "input_files": ["data/q4_sales.csv", "templates/report_template.md"],
    "output_files": ["reports/q4_executive_report.md", "reports/charts/revenue_by_region.png"],
    "initial_state": "git repo with 1 CSV and 1 markdown template",
    "input_characterization": "standard CSV with clean data, no encoding anomalies",
    "assumptions": ["assumed UTF-8 encoding", "assumed in-place file overwriting is acceptable"]
  },
  "steps": [
    {
      "seq": 1,
      "phase": "analysis",
      "action": "Read the input CSV and inspect column headers and data types",
      "step_type": "exploratory",
      "tools_used": ["Read", "Bash"],
      "reasoning": "Need to understand the data schema before deciding on transformation approach",
      "inputs": ["data/q4_sales.csv"],
      "outputs": []
    },
    {
      "seq": 2,
      "phase": "implementation",
      "action": "Choose pandas over raw CSV module for the data transformation",
      "step_type": "productive",
      "tools_used": [],
      "reasoning": "Input has 50+ columns with mixed types; pandas handles type inference and groupby operations natively",
      "inputs": [],
      "outputs": [],
      "decision_point": true,
      "alternatives_considered": ["csv module", "polars"],
      "why_chosen": "pandas is the most widely available, handles the mixed-type edge cases in this data, and has mature charting integration via matplotlib"
    },
    {
      "seq": 3,
      "phase": "implementation",
      "action": "Write a Python script to load, clean, and aggregate the sales data by region",
      "step_type": "productive",
      "tools_used": ["Write", "Bash"],
      "reasoning": "Aggregation logic is multi-step (null handling, currency normalization, groupby) so a script is cleaner than inline commands",
      "inputs": ["data/q4_sales.csv"],
      "outputs": ["scripts/aggregate_sales.py", "data/aggregated.json"]
    }
  ],
  "error_recoveries": [
    {
      "step_seq": 3,
      "error": "UnicodeDecodeError on line 847 of q4_sales.csv",
      "recovery": "Re-opened with encoding='utf-8-sig' to handle BOM marker",
      "generalizable": true
    }
  ],
  "patterns_noticed": [
    "All date columns used MM/DD/YYYY format and needed ISO conversion",
    "Currency values had mixed formats ($1,234 vs 1234.00) requiring normalization",
    "The report template expected specific section headers that must be matched exactly"
  ],
  "efficiency_notes": [
    "Step 1 read 3 files that turned out irrelevant — a skill could grep for the target pattern first to avoid unnecessary reads"
  ]
}
```

**Fields:**
- `metadata`: Task-level information, written once at start (and updated at end)
  - `task_summary`: One-sentence description of what the user asked for
  - `domain`: Category of work — common values: `data-transform`, `document-generation`, `code-refactor`, `setup-config`, `analysis`, `automation`
  - `task_outcome`: Set at completion — `"success"` | `"partial"` | `"failed"`. `partial` = completed with limitations; `failed` = could not complete
  - `failure_reason`: `null` on success; plain-English explanation for `partial` or `failed`
  - `timestamp_start`: When execution began (ISO 8601)
  - `timestamp_end`: When execution completed (ISO 8601, filled in at end)
  - `working_directory`: Absolute path of the working directory at task start; allows observers to resolve relative paths in `input_files`/`output_files`
  - `input_files`: Paths to files the user explicitly provided or referenced (not every file read during exploration)
  - `output_files`: Paths to final deliverable files produced for the user (not intermediate files)
  - `initial_state`: Brief description of the working directory state before the task started (e.g., `"git repo with 3 Python files and a CSV"`, `"empty directory"`)
  - `input_characterization`: One sentence on whether the input is typical or atypical — set after first reading the input (e.g., `"standard CSV with clean data"`, `"large file with BOM encoding anomaly"`)
  - `assumptions`: List of things the executor assumed without verifying (encoding, file existence, user intent, acceptable side effects)
- `steps[]`: The core trace — one entry per logical step (not per tool call)
  - `seq`: Sequential step number (1-indexed)
  - `phase` (optional): Broad execution phase — `"research"` | `"analysis"` | `"setup"` | `"implementation"` | `"verification"` | `"cleanup"`. Add when the task has distinct phases.
  - `action`: What was done, in imperative form
  - `step_type`: Role in the execution — `"productive"` (directly contributed to output) | `"exploratory"` (investigation that informed later steps) | `"recovery"` (fixing a mistake)
  - `tools_used`: List of Claude Code tools used in this step (Read, Write, Edit, Bash, Glob, Grep, etc.)
  - `reasoning`: Why this step was needed — the most important field for skill generation
  - `inputs`: Files or data consumed by this step
  - `outputs`: Files or data produced by this step
  - `decision_point`: `true` if the executor chose between alternatives, `false` or omitted otherwise
  - `alternatives_considered`: (Only when `decision_point` is `true`) Other approaches that were considered
  - `why_chosen`: (Only when `decision_point` is `true`) Why this approach was selected over alternatives
- `error_recoveries[]`: Errors encountered and how they were resolved — disproportionately valuable for skill creation
  - `step_seq`: Which step the error occurred in
  - `error`: What went wrong
  - `recovery`: How it was fixed
  - `generalizable`: `true` if this error could occur with different inputs (not specific to this data)
- `patterns_noticed[]`: Recurring observations the executor noticed during execution — free-text strings, written at end
- `efficiency_notes[]`: Free-text strings describing more efficient approaches for specific steps — written during the retrospective at completion. Each entry should reference the step number (e.g., `"Step 4 read 3 files that turned out irrelevant…"`). Empty array if no meaningful inefficiencies.

---

## observer_notes.json

Companion output from the observer agent alongside the draft SKILL.md. Located at `<skill-name>-workspace/observer_notes.json`. Documents the abstraction decisions made during skill synthesis and flags areas of uncertainty.

```json
{
  "trace_summary": {
    "total_steps": 10,
    "universal_steps": 7,
    "conditional_steps": 2,
    "specific_steps": 1,
    "decision_points": 3,
    "error_recoveries": 1
  },
  "abstraction_decisions": [
    {
      "trace_step": 3,
      "original": "Write a Python script using pandas to aggregate sales data by region",
      "generalized_to": "Write a data aggregation script appropriate for the input size and complexity",
      "confidence": "high",
      "reason": "The specific library choice depends on input characteristics, not the task type"
    },
    {
      "trace_step": 5,
      "original": "Parse dates from MM/DD/YYYY to ISO format",
      "generalized_to": "Detect and normalize date formats in the input data",
      "confidence": "medium",
      "reason": "Date format is input-dependent; only one format was observed in this trace"
    }
  ],
  "suggested_improvements": [
    "Only one execution was observed. Running 2-3 more diverse examples through the eval loop would significantly improve the skill's generalization.",
    "Step 3 involved a multi-step aggregation script that could be bundled as a reusable script in scripts/"
  ],
  "bundled_script_candidates": [
    {
      "name": "aggregate_data.py",
      "purpose": "Load, clean, and aggregate tabular data with configurable groupby columns",
      "source_step": 3,
      "priority": "high"
    },
    {
      "name": "normalize_currencies.py",
      "purpose": "Detect and normalize mixed currency formats in a dataframe",
      "source_step": 4,
      "priority": "medium"
    }
  ]
}
```

**Fields:**
- `trace_summary`: Statistics about how the trace steps were classified
  - `total_steps`: Number of steps in the original trace
  - `universal_steps`: Steps that would apply to every instance of this task type
  - `conditional_steps`: Steps that depend on input characteristics
  - `specific_steps`: Steps only relevant to this particular execution (not included in skill)
  - `decision_points`: Number of steps where alternatives were considered
  - `error_recoveries`: Number of error recovery events
- `abstraction_decisions[]`: How specific trace steps were generalized into skill instructions
  - `trace_step`: The `seq` number from workflow_trace.json
  - `original`: What the trace recorded (specific to this execution)
  - `generalized_to`: How it was abstracted in the skill (applicable across inputs)
  - `confidence`: `high` (clear generalization), `medium` (reasonable but unverified), `low` (uncertain, needs eval loop validation)
  - `reason`: Why this level of abstraction was chosen
- `suggested_improvements[]`: Free-text recommendations for strengthening the skill
- `bundled_script_candidates[]`: Scripts observed during execution that could be included in the skill
  - `name`: Suggested filename for the bundled script
  - `purpose`: What the script does
  - `source_step`: Which trace step produced or used this script
  - `priority`: `high` (core to workflow), `medium` (useful but optional), `low` (nice to have)

---

## loop-state.json

Progress checkpoint for the autonomous loop. Located at `<workspace>/loop-state.json`. Written by the loop-running agent using the Write tool after each phase transition — NOT produced by any Python script. Read to resume an interrupted loop.

```json
{
  "skill_path": "~/.claude/skills/my-skill/",
  "current_phase": 3,
  "phase3_iteration": 2,
  "global_iteration_count": 5,
  "last_quality_score": 0.74,
  "last_pass_rate": 0.68,
  "created_files": ["scripts/generate.py", "references/design-system.md"],
  "known_issues": ["SKILL.md is 512 lines — needs trimming before packaging"],
  "pending_improvements": ["Observer suggested: bundle aggregate_data.py as a reusable script"],
  "status": "iterating"
}
```

**Fields:**
- `skill_path`: Absolute path to the skill directory (expand `~` before use)
- `current_phase`: Phase number (1–5)
- `phase3_iteration`: Current iteration within Phase 3 (reset on Phase 3 restart)
- `global_iteration_count`: Total iterations across all phases (counts against the 15-iteration budget)
- `last_quality_score`: Most recent quality score from quality-judge.json (null if not yet run)
- `last_pass_rate`: Most recent assertion pass rate from grading.json (null if not yet run)
- `created_files`: Relative paths of files created during this loop (for Phase 5 report)
- `known_issues`: Issues from check_completeness or reviewer that are deferred
- `pending_improvements`: Improvement targets seeded from observer_notes.json or quality-judge top_gaps
- `status`: `"iterating"` | `"converged"` | `"escalated"` | `"complete"`

---

## quality-judge.json

Output from the quality judge agent. Located at `<workspace>/iteration-N/quality-judge.json`.

```json
{
  "iteration": 2,
  "overall_quality_score": 0.83,
  "pass_rate": 0.78,
  "recommendation": "proceed",
  "regression": false,
  "criteria": [
    {
      "name": "Output is a valid file matching described format",
      "weight": 1.0,
      "score": 0.95,
      "evidence": "PPTX file generated with 5 slides, passes verify_pptx.py",
      "gap": ""
    }
  ],
  "top_gaps": [
    "Dynamic height calculation missing in stat cards",
    "Content density below 75% on 2 of 3 evals"
  ],
  "strengths": [
    "Correct PPTX format and template usage"
  ],
  "summary": "Skill produces valid output but visual density needs improvement."
}
```

**Fields:**
- `iteration`: Which Phase 3 iteration this judgment covers (1-based)
- `overall_quality_score`: Weighted average of criterion scores (0.0–1.0)
- `pass_rate`: Assertion pass rate from grading.json — proportion of expectations that passed (0.0–1.0). `0.0` if grading.json is missing.
- `recommendation`: `"proceed"` (convergence) | `"iterate"` (continue improving) | `"escalate"` (human review)
- `regression`: `true` if quality score dropped > 0.10 OR pass_rate dropped > 0.15 from previous iteration
- `criteria[]`: Per-criterion evaluation used to derive the overall score
  - `name`: What was evaluated
  - `weight`: Relative importance (1.0 = full weight)
  - `score`: 0.0–1.0
  - `evidence`: What in the outputs supports this score
  - `gap`: What would need to change to reach 1.0 (empty if score ≥ 0.9)
- `top_gaps[]`: Free-text strings describing the most impactful improvements — **read by autonomous-loop.md Phase 3 to drive the next iteration**. Each entry should be actionable: name the specific component to change and why.
- `strengths[]`: Patterns working well — preserved during next iteration improvements
- `summary`: One-sentence narrative of the overall assessment
