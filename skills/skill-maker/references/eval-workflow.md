# Eval Workflow

Full procedure for running and evaluating test cases. Referenced from SKILL.md.

**When to read:** Before running test cases for any mode (human-in-the-loop, reference-based, or capture-by-doing).

---

This section is one continuous sequence — don't stop partway through. Do NOT use `/skill-test` or any other testing skill.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize results by iteration (`iteration-1/`, `iteration-2/`, etc.) and within that, each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Don't create all of this upfront — just create directories as you go.

## Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. This is important: don't spawn the with-skill runs first and then come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<eval_name>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline Decision (read before spawning)**

Ask: "Would Claude produce a plausible, comparable output without the skill?"

**Skip without-skill** when ALL of these hold:
- This is a new skill (not an improvement iteration)
- The skill bundles scripts, templates, or binary assets (Tier 3+)
- Assertions test structural correctness of a specific file format (existence, schema, layout validity)

In these cases, without-skill trivially fails every format assertion — the delta is always ~100% and tells you nothing. Skipping saves time and tokens. When skipping, add `"baseline_skipped": true` and `"baseline_skip_reason": "<one sentence>"` to each `eval_metadata.json`.

**Run baseline** when ANY of these holds:
- **Improvement iteration** — always compare new vs. old-skill snapshot (most valuable use of baselines)
- **Tier 1–2 skill** (instructions/references only) — Claude can produce *something* without the skill; the delta reveals whether the skill actually helps
- **Assertions test behavioral constraints** — style rules, naming conventions, output schemas — where Claude might accidentally comply without the skill
- **Assertions test content quality** — where without-skill output is plausibly comparable

**Baseline run** (once you've decided to run one — the type depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case (assertions can be empty for now). Give each eval a descriptive name based on what it's testing — not just "eval-0". Use this name for the directory too. If this iteration uses new or modified eval prompts, create these files for each new eval directory — don't assume they carry over from previous iterations.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

## Step 2: While runs are in progress, draft assertions

Don't just wait for the runs to finish — you can use this time productively. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at the results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update the `eval_metadata.json` files and `evals/evals.json` with the assertions once drafted. Also explain to the user what they'll see in the viewer — both the qualitative outputs and the quantitative benchmark.

## Step 3: As runs complete, capture timing data

When each subagent task completes, you receive a notification containing `total_tokens` and `duration_ms`. Save this data immediately to the config directory. The path depends on which baseline was used (see Step 1):
- **New-skill runs**: `eval-<name>/with_skill/timing.json` and `eval-<name>/without_skill/timing.json`
- **Improvement runs (existing skill)**: `eval-<name>/with_skill/timing.json` and `eval-<name>/old_skill/timing.json`

Example content:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

Save timing.json as a sibling to grading.json — both live in the config directory (`with_skill/`, `without_skill/`, or `old_skill/`), NOT inside a nested `outputs/` subdirectory. This is where `aggregate_benchmark.py` looks for timing data in the flat layout.

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere. Process each notification as it arrives rather than trying to batch them.

## Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory. The grading.json expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants) — the viewer depends on these exact field names. For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and can be reused across iterations.

   **After grading all runs, verify completeness** — run from the workspace root (parent of all `iteration-*` directories, NOT from within an iteration directory):
   ```bash
   python -m scripts.check_completeness <skill-path> --check-grading <workspace>
   ```
   Any `[FAIL]` output means assertions with `passed: null` exist — those evals were defined but never graded. Fix before proceeding: re-run the grader for the affected eval directories. Do NOT advance to Step 5 (feedback review) or self-review with ungraded evals — they count as failures and will understate the true pass rate.

2. **Aggregate into benchmark** — run the aggregation script from the skill-maker directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean +/- stddev and the delta. If generating benchmark.json manually, see `references/schemas.md` for the exact schema the viewer expects.
   Put each `with_skill` version before its baseline counterpart in the `runs` array.

3. **Do an analyst pass** — read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for — things like assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

4. **Launch the viewer** with both qualitative outputs and quantitative data:
   ```python
   import subprocess, sys
   viewer = subprocess.Popen(
       [sys.executable,
        "<skill-maker-path>/eval-viewer/generate_review.py",
        "<workspace>/iteration-N",
        "--skill-name", "my-skill",
        "--benchmark", "<workspace>/iteration-N/benchmark.json"],
       stdout=subprocess.DEVNULL,
       stderr=subprocess.DEVNULL,
       **({'creationflags': 0x08000000} if sys.platform == 'win32' else {}))
   viewer_pid = viewer.pid
   print(f"Viewer: http://localhost:3117 (PID {viewer_pid})")
   ```
   For iteration 2+, also add `"--previous-workspace", "<workspace>/iteration-<N-1>"` to the args list.

   **Cowork / headless environments:** If `webbrowser.open()` is not available or the environment has no display, use `--static <output_path>` to write a standalone HTML file instead of starting a server. Feedback will be downloaded as a `feedback.json` file when the user clicks "Submit All Reviews". After download, copy `feedback.json` into the workspace directory for the next iteration to pick up.

Note: please use generate_review.py to create the viewer; there's no need to write custom HTML.

5. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you click 'Submit All Reviews', a `feedback.complete` file will be written to the workspace. After that, come back here and let me know."

## What the user sees in the viewer

The "Outputs" tab shows one test case at a time:
- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, shown below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage for each configuration, with per-eval breakdowns and analyst observations.

Navigation is via prev/next buttons or arrow keys. When done, they click "Submit All Reviews" which saves all feedback to `feedback.json`.

## Step 5: Read the feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus your improvements on the test cases where the user had specific complaints.

Kill the viewer server when you're done with it:

```python
viewer.terminate()
```
