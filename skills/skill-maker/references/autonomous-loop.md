# Autonomous Skill Creation Loop

Self-directing feedback loop for skill creation. Run this by default when the user provides intent and a "go" signal. Human input is only required at two mandatory checkpoints (Phase 0 and Phase 5); everything in between runs autonomously.

## Loop Overview

```
Phase 0: Intent Capture        ← HUMAN INPUT REQUIRED
    ↓
Phase 1: Bootstrap             (autonomous)
    ↓
Phase 2: Reference Alignment   (autonomous, skip if no references)
    ↓
Phase 3: Eval + AI Judge Loop  (autonomous, max 5 iterations)
    ↓ converged OR exhausted
Phase 4: Final Quality Gate    (autonomous)
    ↓
Phase 5: Report                ← HUMAN INPUT (review + optional direction)
    ↓ (if user gives direction)
    → back to Phase 3
```

Total iteration budget: **15 iterations** across all phases (global cap).

---

## Phase 0: Intent Capture (human-required)

Collect the minimum inputs needed to build without further clarification:

1. **What the skill should do** (use case, output format, who uses it)
2. **Reference outputs** (optional): past human work, gold-standard examples
3. **Infrastructure signals**: does it produce files? Apply domain rules? Need multi-step agents?
4. **Test prompts**: 2-3 realistic invocations the skill should handle
5. **Visual Reproduction Mode** (from Q7 in SKILL.md): Has the user provided binary reference files (PPTX, images, PDFs) as the design target? If yes, flag this. Asset extraction will run at the **start of Phase 1** before any scripts or SKILL.md are written.
6. **Visual output flag** (from Q8 in SKILL.md): Does this skill produce any visual output (slides, HTML, PDFs, charts, reports, UIs, images)? If yes, a visual specification must be included in the Phase 0 plan and confirmed by the user before Phase 1 begins.

Present the plan in the following sections and wait for user confirmation ("go" / "start" / any affirmative):

1. **Skill + Tier**: Skill name, tier number (1–4), and a one-sentence justification for the tier choice.

2. **Directory structure**: Annotated directory tree using actual planned file names. Add an inline note (e.g., `← generates PPTX from input data`) for each non-obvious file so the user can see exactly what will be created.

3. **Skill flow** *(skip for Tier 1 instruction-only skills)*: How inputs move through the skill to produce outputs. A single arrow string works for linear flows (`Input → step → step → Output`); use a numbered list for branching or multi-agent flows.

4. **Scripts** *(file-producing / Tier 3+ skills; skip otherwise)*: A short table or bullet list with each planned script and a one-line description of what it does and what inputs/outputs it has.

5. **Visual specification** *(only for skills producing visual output — slides, HTML, PDFs, charts, dashboards, UIs, reports, images; skip otherwise)*: A human-readable description of what the output will look like. Include:
   - Layout sketch: main zones and how they're arranged (text description is fine)
   - Color palette: background, primary accent, secondary accent, text colors — as hex codes or explicit names
   - Typography: for each text role (heading, body, label) → font name, pt size, weight, color. **If the output has multiple distinct contexts** (cover page vs. content page, landing screen vs. detail screen, hero section vs. body section), list typography **per context** in separate subsections — never merge into one table. Different contexts often use different fonts for the same role.
   - Key components and how each looks (e.g., "white card, thin `#7E00FF` top bar, bold `#5F0095` title")
   - One-sentence overall impression

   Wait for the user to confirm this spec before Phase 1 begins. If using Visual Reproduction Mode, present the extracted values here — do not assume extraction = correct. A wrong spec confirmed at Phase 0 costs nothing; a wrong spec discovered after coding costs 5+ iterations.

5a. **Fidelity delta** *(Visual Reproduction Mode only — REQUIRED when reference files are provided)*: Immediately after the visual spec, explicitly state what the skill WILL and WILL NOT reproduce. This is the single most important communication for Visual Reproduction skills — missing it leads to user surprise when the output is structurally correct but looks different from the reference.

   Format:
   ```
   WILL reproduce exactly:
   - [list: e.g., color palette, font family, layout coordinates, named patterns A–F]

   WILL NOT reproduce / will differ:
   - [list: e.g., "SVG icons and decorative charts from slides 4–6 (automated extraction cannot read embedded SVG objects)"]
   - [list: e.g., "Content density — reference slides had 8+ lines per card; test prompts have 2–3 lines; cards will appear sparser than the reference unless more content is provided"]
   - [list: e.g., "Background photographs in cover slide (embedded image, not a color fill)"]

   User should know: [one sentence on the largest visual gap]
   ```

   The content density gap deserves special attention: reference slides are usually authored with dense, polished content. Eval prompts and typical invocations may have sparse content. When the skill uses stretch-to-fill containers, the output will always look sparser than the reference unless this is explicitly addressed in the generation script (by either using content-driven sizing or requiring richer content).

6. **Tentative test cases**: 2–3 realistic user prompts with expected output shapes (not just "something correct" — describe the shape: file format, content summary, key fields).

7. **Suggestions / open questions** *(3–5 items max — highest-impact only)*: Surface what the user likely hasn't considered, prioritizing from:
   - External dependencies (packages, CLI tools, API keys) the user needs to know about upfront
   - Triggering collision risk with other installed skills (same phrases, overlapping scope)
   - Edge cases that may need explicit handling in the skill instructions
   - Scope exclusions worth confirming ("this skill won't handle X — is that OK?")
   - Missing information that would materially affect the architecture if wrong

If Visual Reproduction Mode is active, add: "→ `asset-extractor` will run before any scripts or SKILL.md are written to extract design tokens from the reference files."
If visual output is detected (from Q8), add: "→ Visual specification (item 5 above) must be confirmed before Phase 1 begins — generation code will not be written until you approve the visual design."

**Do not ask follow-up questions after confirmation.** Make decisions autonomously in later phases. If assumptions turn out wrong, they'll surface in the eval loop and get fixed.

**After confirmation, immediately create `<workspace>/session-plan.md`** — the single context anchor for this skill creation session. Use this template:

```markdown
# Skill Plan: <skill-name>

## Objective
<one-sentence description from Phase 0>

## Architecture
- **Tier**: <1-4>
- **Skill path**: `<skill-path>`
- **Scripts**: <planned scripts with one-line purpose each, or "none">
- **References**: <planned reference files, or "none">

## Status: Phase 1 — Bootstrap
_Last updated: <ISO timestamp>_

## Completed
- [x] Phase 0: Intent captured, plan confirmed by user

## Current work
Phase 1: Creating skill directory and infrastructure

## Next steps
1. Write SKILL.md (draft)
2. Create scripts/ and references/
3. Run check_completeness

## Key decisions
- <decision 1> (reason)
- <decision 2> (reason)
```

Update this file at every phase transition and after major decisions. When context compresses or a new session starts, reading `session-plan.md` restores working context without re-reading all history.

---

## Phase 1: Bootstrap (autonomous)

Create the complete skill directory in one pass:

**Step 0 (Visual Reproduction Mode only)**: If Phase 0 identified binary reference files (PPTX, images, PDFs), run asset extraction BEFORE writing any scripts or SKILL.md:
```
Spawn agents/asset-extractor.md with:
- skill_path: <new skill directory>
- reference_files: [<list of paths provided by user>]
- skill_type: <what the skill should do>
- output_path: <workspace>/extraction_report.json
```
Wait for completion. Read `extraction_report.json` — especially `critical_findings` and `generation_recommendations`. These findings drive all design decisions in steps 1-2 below. Do not write any design constants (colors, font names, positions) from memory; use the extracted values from `references/visual-spec.md` exclusively.

**Step 0b (Capture by Doing only)**: If Phase 0 started from a recorded task execution (user provided `workflow_trace.json`), the observer agent produces `observer_notes.json` in the **workspace root** (same directory as `workflow_trace.json`, e.g., `<skill-name>-workspace/observer_notes.json`). Read it before creating any infrastructure:
- `bundled_script_candidates[]` → create each listed script in `scripts/`; these were identified from actual task execution and are high-confidence infrastructure additions
- `suggested_improvements[]` → add to `loop-state.json` as `pending_improvements` to seed Phase 3 improvements
- `abstraction_decisions[]` entries with `confidence: "low"` → flag as priority validation targets in the eval loop

If this is intent-based skill creation (not from a trace), `observer_notes.json` will not exist — proceed without it.

1. Write SKILL.md (draft quality — will be refined)
2. Create all required infrastructure (scripts, references, agents, assets) identified in Phase 0
   - **File-producing skills**: `scripts/` MUST exist before SKILL.md is finalized
   - **Visual Reproduction skills**: use `Presentation("assets/template.pptx")` as the generation base, never `Presentation()` — see extraction_report for the exact template path and the correct slide-deletion pattern
   - If a script is needed, write and test it now (run `python <script.py>` to confirm it imports cleanly)
   - **Visual / file-producing skills — smoke test (mandatory)**: After writing generation scripts, actually run them to produce a minimal test output. Then run `python scripts/validate_*.py <test_output>` (or an equivalent structural check). If no validator exists yet, write a minimal one first (file exists + size > threshold + key structural checks), then fix until it passes. Do **not** leave Phase 1 with a script that has only been import-tested. A script that imports cleanly but produces structurally wrong output (wrong colors, phantom shapes, wrong fonts) will silently pass Phase 1 and consume 1–2 full eval iterations before the problem surfaces — diagnosing it here costs one step.
   - If a reference doc is needed, write it now (not later)
3. Run `python -m scripts.check_completeness <skill-path>`
   - Fix ALL FAIL items immediately — do not proceed to Phase 2 with any FAILs
   - WARN items: fix if they take < 5 minutes; otherwise log for Phase 3

**Autonomous resource creation rule**: When you detect a gap during any phase, fill it immediately and log the action in `<workspace>/loop-state.json`. Do not ask permission. The Phase 5 report will list everything that was created or modified.

**Exit criteria**: `check_completeness` exits 0.

Update `session-plan.md`: mark Phase 1 complete, set Status to "Phase 2" (or "Phase 3" if skipping), list what was created.

---

## Phase 2: Reference Alignment (autonomous, 3-iteration cap)

**Skip this phase entirely if no reference outputs were provided in Phase 0.**

**If reference binary files WERE provided but Phase 2 cannot run** (e.g., gradient agent or subagent permissions denied, environment limitation): document this as an explicit unresolved gap before proceeding to Phase 3. Add to `loop-state.json`: `"known_issues": ["Phase 2 reference alignment not performed — visual density and fidelity differences from reference files may not be detected by automated checks"]`. Include this gap in the Phase 5 report. Visual density mismatches in particular (containers that look sparse compared to the reference) are invisible to structural evals and will only surface through gradient comparison or user visual review.

For each provided reference:

1. Run the skill on the corresponding input (subagent, MUST NOT see references)
2. Spawn `agents/gradient.md` to compare output vs reference
3. Aggregate: `python -m scripts.aggregate_gradients`
4. Read `gradient_summary.json`:
   - `mean_similarity ≥ 0.85` → convergence reached, exit Phase 2
   - `improving: true` AND `iteration < 3` → apply rewrites and repeat
   - `improving: false` OR `iteration ≥ 3` → apply remaining rewrites and proceed to Phase 3

Rewrite SKILL.md based on `top_generalizations` from gradient summary. Also create any infrastructure that all reference runs needed but the skill didn't provide.

**Exit criteria**: `mean_similarity ≥ 0.85` OR `iteration ≥ 3`.
**Iteration cap**: 3.

Update `session-plan.md`: mark Phase 2 complete (or note "skipped"), record final similarity score.

---

## Phase 3: Eval + AI Judge Loop (autonomous, 5-iteration cap)

This is the core improvement loop. All quality checks are machine-readable; no human review is needed unless the loop exhausts its budget.

### Per-iteration steps (in order):

**3a. Apply improvements** (skip on first iteration — start from current skill state)

**3b. Infrastructure check**
```bash
python -m scripts.check_completeness <skill-path>
```
Fix all FAILs before proceeding. If a new FAIL appears that wasn't there before → revert the change that introduced it.

**3c. Security check**
Spawn `agents/reviewer.md` with:
- `skill_path`: `<skill-path>`
- `output_path`: `<workspace>/iteration-N/review.json`
- `previous_review_path`: `<workspace>/iteration-(N-1)/review.json` (if exists)
- `iteration`: N

Fix all CRITICAL and MAJOR findings.
- If `summary.clean = true` after fixes → continue
- If CRITICAL remains after one fix attempt → escalate (see below)

**3d. Run evals**
Before spawning, apply the **Baseline Decision rule** in `references/eval-workflow.md` Step 1 — decide whether to run a baseline or skip it. For new Tier 3+ skills whose assertions test structural file correctness, skip without-skill (record `"baseline_skipped": true` in `eval_metadata.json`); otherwise spawn baseline in parallel.

Spawn eval runs in parallel (with-skill + baseline, if baseline applies). When each task notification arrives, immediately save `total_tokens`, `duration_ms`, and `total_duration_seconds` (= `duration_ms / 1000`) to the config directory's `timing.json` — this is the only opportunity to capture timing data; it is not persisted elsewhere:
- New-skill runs: `eval-<name>/with_skill/timing.json` and `eval-<name>/without_skill/timing.json`
- Improvement runs (existing skill): `eval-<name>/with_skill/timing.json` and `eval-<name>/old_skill/timing.json`

Grade all assertions. See `references/eval-workflow.md` Steps 3–4 for details.

**3e. Spawn quality judge**
```
Read agents/quality-judge.md, then evaluate:
- skill_path: <skill-path>
- eval_outputs_dir: <workspace>/iteration-N/          ← pass the iteration root, not a single eval path
- output_path: <workspace>/iteration-N/quality-judge.json
- previous_judge_path: <workspace>/iteration-(N-1)/quality-judge.json (if exists)
- iteration: N
```
Passing the iteration root lets the judge read ALL eval-* subdirectories in one pass and aggregate quality across every eval. Do not pass a single `eval-<name>/with_skill/` path unless you are debugging a specific eval — that would silently ignore the rest of the eval set.

**3f. Convergence check**
Update `session-plan.md` with current iteration number, quality score, pass rate, and the `top_gaps` driving the next iteration. This ensures that if the conversation context is compressed, the next turn starts with a clear picture of where things stand.

Read `quality-judge.json`:

| Condition | Action |
|-----------|--------|
| `recommendation: proceed` (quality ≥ 0.80 + pass_rate ≥ 0.75) | → Phase 4 |
| `recommendation: iterate` AND `iteration < 5` | Apply `top_gaps` as improvements → next iteration |
| `recommendation: escalate` | → Human Checkpoint (see below) |
| `iteration ≥ 5` without convergence | → Human Checkpoint |
| `regression: true` | Revert last improvements → Human Checkpoint |

### Improving the skill between iterations

Focus improvements on `top_gaps` from `quality-judge.json`. For each gap:
1. Is it a SKILL.md wording issue? → Edit SKILL.md
2. Is it a missing infrastructure piece? → Create it (scripts, references, agents)
3. Is it a structural/architectural issue? → Rebuild that component

**Do not make broad rewrites.** Target the specific gaps identified. Broad changes risk introducing regressions.

### Human Checkpoint (Phase 3 escape valve)

If Phase 3 exhausts 5 iterations or a regression occurs, pause and report:

> "自律ループが [N] 回反復しましたが収束しませんでした。現在のスコア: [X]. 残課題: [list top_gaps]. 追加の方向性をいただければ次のループを再開します。"

Wait for user direction. Apply direction, then restart Phase 3 from iteration 1 (within the global 15-iteration budget).

**Exit criteria**: `recommendation: proceed` OR human redirect.
**Iteration cap**: 5 (Phase 3 only).

---

## Phase 4: Final Quality Gate (autonomous)

One-pass validation before handing off to the user. Allow up to 2 fix attempts per check.

| Check | Pass Condition | On Fail |
|-------|---------------|---------|
| `check_completeness --check-grading <workspace>` | Exit 0 | Fix FAILs, re-run |
| `reviewer.md` | `summary.clean = true` | Fix CRITICAL/MAJOR, re-spawn |
| SKILL.md length | ≤ 500 lines | Extract detail to references/ |
| All references reachable | No orphaned mentions | Create or remove missing files |

Run: `python -m scripts.check_completeness <skill-path> --check-grading <workspace-path>`

If any check still fails after 2 fix attempts → proceed anyway, but mark as "known issue" in the Phase 5 report.

---

## Phase 5: Final Report (human-facing)

Summarize and hand off. Include:

1. **What was built**: skill name, tier, directory structure, new files created
2. **Loop statistics**: total iterations, phases completed, final quality score, assertion pass rate
3. **Remaining issues**: any unfixed FAILs or WARNs from Phase 4
4. **Suggested next steps**: e.g., "run `python -m scripts.package_skill` to install" or "run description optimization to tune triggering"

Report template:
> "スキル [name] を自律ループで作成しました。[N] フェーズ / [M] 回反復。最終スコア: [quality] / Pass rate: [X]%。残課題: [list]. 追加の修正指示があれば Phase 3 から再開します。"

Before delivering the report, update `loop-state.json` with `"status": "complete"` (or `"escalated"` if Phase 4 had unfixed FAILs) so a resumed session knows the loop is done.

After report: wait for user direction. If direction provided → restart Phase 3. If none → proceed to packaging (if `present_files` available) or stop.

---

## Global Budget Table

| Resource | Limit |
|----------|-------|
| Phase 2 iterations | 3 |
| Phase 3 iterations | 5 |
| Phase 4 fix attempts per check | 2 |
| Phase 3 restarts (after human redirect) | 2 |
| **Total iterations (all phases)** | **15** |

If the global budget is exhausted: stop, report remaining issues, and let the user decide whether to continue manually.

---

## State Tracking

Write loop state to `<workspace>/loop-state.json` after each phase transition:

```json
{
  "skill_path": "~/.claude/skills/my-skill/",
  "current_phase": 3,
  "phase3_iteration": 2,
  "global_iteration_count": 5,
  "last_quality_score": 0.74,
  "last_pass_rate": 0.68,
  "created_files": ["scripts/generate.py", "references/design-system.md"],
  "known_issues": [],
  "pending_improvements": ["Observer suggested: bundle aggregate_data.py as a reusable script"],
  "status": "iterating"
}
```

This file lets you resume an interrupted loop by reading where it left off.

**Important**: `loop-state.json` is written by the loop-running agent using the Write tool after each phase transition — it is not produced by any Python script. If a conversation is interrupted, start a new session, read `loop-state.json`, and restart from `current_phase` with `phase3_iteration` and `global_iteration_count` already set to avoid re-running completed work.

---

## When NOT to Run the Autonomous Loop

Default to the autonomous loop. Override it (run manually) when:
- The user explicitly wants to review and direct each iteration ("見ながら一緒に作りたい")
- The skill is Tier 1 (instructions only) and quick to assess by eye
- The user is debugging a specific known issue and doesn't need the full loop

In these cases, follow the manual workflow described in SKILL.md's "Improving the skill" section.
