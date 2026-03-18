# Reference-Based Skill Creation

This document describes the reference-based workflow for creating Skills from existing gold-standard outputs. It is used when the user has examples of correct outputs (past human work) and wants a Skill that reproduces that quality consistently.

Instead of relying on human feedback in every iteration, this workflow uses "text gradients" (structured comparisons between generated outputs and reference outputs) to automatically identify gaps and improve the Skill.

**When to use this mode:** The user says something like "I have these example documents and I want a skill that can produce similar ones", or "here are some proposals my team wrote, make a skill that can replicate this quality", or references existing completed work as the target standard.

**Prerequisites:**
- Input context files (what the Skill will receive as raw material — e.g., hearing memos, survey data, meeting notes)
- Reference outputs (the gold standard — e.g., completed proposals, reports, documents that a human created from those inputs)
- At least 3 input/reference pairs (more is better for generalization; 3-5 is the practical minimum)

**Environment requirements:** This mode requires subagents for parallel Skill execution and gradient generation. It works in Claude Code and Cowork. It does NOT work in Claude.ai (no subagents available). See the environment notes at the end of this document.

---

## Step 1: Gather Training Data

Ask the user to provide their input/reference pairs. For each pair, you need:
1. The input files (context that the Skill will work with)
2. The reference output (the human-created gold standard)

Organize them in the workspace and save a `training_data.json`:

```json
{
  "skill_name": "proposal-writer",
  "task_description": "Create a SaaS adoption proposal from hearing memos",
  "output_description": "A proposal document with executive summary, analysis, recommendations, and ROI calculation",
  "pairs": [
    {
      "id": "crm-case",
      "description": "CRM adoption for mid-size manufacturer",
      "input_files": ["training-data/crm-case/input/hearing_memo.md"],
      "reference_files": ["training-data/crm-case/reference/proposal.md"],
      "notes": ""
    }
  ]
}
```

See `references/schemas.md` for the full schema. Each pair's `id` becomes the eval directory name (e.g., `eval-crm-case/`), so keep them descriptive and kebab-case.

Recommend that the user include diverse examples that cover different aspects of the task — different domains, edge cases, varying complexity levels. If all training examples are too similar, the Skill may not generalize well.

## Step 1b: Extract Assets from Binary Reference Files (if applicable)

**When to run this step**: If any reference files in `training_data.json` are binary files — PPTX presentations, images (PNG/JPEG/SVG), or PDFs — run the asset extractor before drafting the skill.

The core insight: **you cannot reverse-engineer a design from a binary file by looking at it**. The exact hex values of brand colors, the specific font names (including CJK fallbacks), the precise EMU coordinates of layout zones — none of these are safely guessable from visual inspection. A skill drafted from text description will drift from the original in ways that only appear at render time.

For each binary reference file, spawn `agents/asset-extractor.md`:

```
Read the instructions in agents/asset-extractor.md, then extract assets from:
- skill_path: <target-skill-directory>
- reference_files: [<list of binary reference file paths>]
- skill_type: <what the skill should do>
- output_path: <workspace>/extraction_report.json
```

Wait for all extraction reports before proceeding to Step 2. The extractor will create:
- `<skill>/assets/reference/<filename>` — verbatim copies (immutable ground truth)
- `<skill>/assets/template.pptx` — PPTX template base (if applicable)
- `<skill>/references/visual-spec.md` — extracted color palette, fonts, geometry

**Read `extraction_report.json` carefully before drafting the skill.** Pay special attention to:
- `critical_findings` — font names, CJK fallbacks, template usage requirements
- `generation_recommendations` — specific code patterns the scripts MUST follow

In Step 2, treat `references/visual-spec.md` as the authoritative design system. Do not write color values or font names from memory — copy them verbatim from the spec file. The gradient agent in Step 4 will catch any remaining discrepancies via PPTX structural comparison.

## Step 2: Draft the Initial Skill from References

Before writing any instructions, read ALL reference outputs and ALL input contexts. Your goal is to reverse-engineer the implicit rules that the human followed.

Look for two things:
- **What is CONSISTENT across all references** — these are the rules. If every reference starts with an executive summary, that's a structural rule. If every reference includes a quantified ROI section, that's a content rule. These become explicit instructions in the Skill.
- **What VARIES across references** — these are judgment calls. If the tone shifts based on the client type, or the depth of analysis varies based on data availability, those are adaptive behaviors. Describe these as guidance ("adjust the level of detail based on...") rather than rigid instructions.

Follow the Skill Writing Guide in the main SKILL.md for structure, naming, and writing style. Draft a SKILL.md that captures the patterns you identified. It does not need to be perfect — the iteration loop will improve it. But a thoughtful initial draft converges faster than a generic one.

Save a snapshot of the initial skill:
```bash
cp -r <skill-path> <workspace>/iteration-0/skill-snapshot/
```

## Step 3: Run the Skill on Training Inputs

For EACH training pair, spawn a subagent that executes the Skill on the input context. This step is nearly identical to the standard eval run, with one critical difference:

**The subagent MUST NOT see the reference outputs.** It receives only the Skill and the input context. This is essential — if the subagent can see the reference, it will just copy it, and the Skill instructions won't actually be tested.

For each pair:

1. Copy input files for the gradient agent to access later:
```bash
cp -r <pair's input_files> <workspace>/iteration-N/eval-<pair-id>/inputs/
```

2. Copy reference files for comparison:
```bash
cp -r <pair's reference_files> <workspace>/iteration-N/eval-<pair-id>/reference/outputs/
```

3. Spawn the subagent:
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <task_description from training_data.json>
- Input files: <pair's input_files from training_data.json>
- Save outputs to: <workspace>/iteration-N/eval-<pair-id>/generated/outputs/
- Outputs to save: <what the skill should produce>
```

4. Write `eval_metadata.json` for each eval case:
```json
{
  "eval_id": "crm-case",
  "eval_name": "CRM adoption proposal",
  "prompt": "Create a SaaS adoption proposal from the provided hearing memo",
  "mode": "reference_based"
}
```

Spawn all pairs in parallel for speed.

## Step 4: Generate Text Gradients

Once all runs complete, spawn a gradient agent for each pair. The gradient agent compares the generated output against the reference output and produces a structured analysis of what differs and why. Read `agents/gradient.md` for the full instructions.

For each pair, spawn:
```
Read the instructions in agents/gradient.md, then perform the gradient analysis:
- eval_id: <pair-id>
- task_description: <task_description from training_data.json>
- input_context_path: <workspace>/iteration-N/eval-<pair-id>/inputs/
- generated_output_path: <workspace>/iteration-N/eval-<pair-id>/generated/outputs/
- reference_output_path: <workspace>/iteration-N/eval-<pair-id>/reference/outputs/
- output_path: <workspace>/iteration-N/eval-<pair-id>/gradient.json
```

Spawn all gradient agents in parallel — they are independent of each other.

After all gradients are produced, run the aggregation script:
```bash
python -m scripts.aggregate_gradients <workspace>/iteration-N --skill-name <name>
```

This produces `gradient_summary.json` and `gradient_summary.md`. Read the summary — it shows the mean similarity, the most common generalizations, and convergence data.

## Step 5: Rewrite the Skill Based on Gradients

Read `gradient_summary.json` and use it to improve the Skill. This is where the "text gradient descent" happens — each rewrite should close the gaps identified by the gradients.

**What to focus on:**
1. Start with `top_generalizations` — these are patterns that appeared across multiple training pairs, sorted by frequency and severity. A generalization that shows up in 3 out of 4 eval cases is almost certainly a real gap in the Skill.
2. Check `critical`-severity gradients even if they appear in only one eval case — a critical gap in any single case is worth addressing.
3. Read `preserved_strengths` and make sure your rewrite does not remove things that are working.
4. Check `reference_patterns` — these are conventions the reference outputs follow consistently. If the Skill doesn't mention these patterns, consider adding them.

**How to make changes:**
- For each generalization, decide: should this become (a) a new instruction, (b) a modification to an existing instruction, (c) a new example, or (d) a new script/template?
- Explain the **why** behind each instruction. "Calculate ROI" is weaker than "Calculate ROI by enumerating cost categories from the input, because decision-makers need concrete numbers to justify budget allocation."
- Keep the Skill general. If you find yourself writing "when the input mentions CRM, include a section on customer data migration," that's overfitting to one training example. Instead: "when the input mentions a system category, include a section addressing domain-specific migration or integration concerns."

**Anti-overfitting guardrails:**
- Each change should be justifiable by a general principle, not by a single example.
- If a gradient appears in only one eval case and has no clear generalization beyond that case, note it but don't change the Skill for it.
- If you're adding very specific domain knowledge (e.g., "MDR costs for security products"), make it conditional and explain when it applies rather than hardcoding it.
- Prefer explaining reasoning over rigid rules. "ALWAYS include exactly 5 ROI categories" is fragile. "Break down ROI by the cost categories present in the input data, typically 3-6 categories" is robust.

Save a snapshot and update the iteration history:
```bash
cp -r <skill-path> <workspace>/iteration-N/skill-snapshot/
```

After each iteration, update `<workspace>/iteration_history.json` (create if it doesn't exist):
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
    }
  ],
  "best_iteration": 1
}
```

## Step 6: Convergence and Iteration

Repeat Steps 3-5. After each iteration, check `gradient_summary.json` for convergence:

- **`mean_similarity > 0.85` AND `improving == false`**: The Skill has converged. The remaining differences are likely noise or stylistic preferences rather than substantive gaps. Stop here. (The 0.85 threshold is a default — adjust based on the task. Creative tasks may converge lower; mechanical tasks may reach higher.)
- **`improving == true`**: Keep going. The Skill is still getting better.
- **`improving == false` but `mean_similarity < 0.85`**: The Skill may be stuck. Read the remaining critical/major gradients carefully — there might be a structural issue that incremental changes won't fix. Consider a more substantial rewrite, or discuss with the user.
- **5 iterations without meaningful improvement** (delta < 0.02 for 2+ consecutive iterations): Stop and use the best snapshot (the iteration with the highest `mean_similarity` in `iteration_history.json`). Continued iteration is unlikely to help.

Track progress across iterations. After each iteration, briefly report to the user:
- Current mean similarity and delta
- What the main changes were
- How many critical/major gradients remain

For users with 8+ training pairs, consider holding out 2-3 pairs as a test set (don't use them for gradient generation, only for evaluating the final Skill). This mirrors the train/test split in the description optimization workflow and provides a more honest measure of generalization.

## Step 7: Optional Human Review

After convergence (or when you decide to stop iterating), optionally launch the existing eval viewer for a final human review. The generated outputs from the last iteration are in `eval-<id>/generated/outputs/` which the viewer will discover automatically.

```python
import subprocess, sys
viewer = subprocess.Popen(
    [sys.executable,
     "<skill-maker-path>/eval-viewer/generate_review.py",
     "<workspace>/iteration-N",
     "--skill-name", "my-skill"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    **({'creationflags': 0x08000000} if sys.platform == 'win32' else {}))
print(f"Viewer: http://localhost:3117 (PID {viewer.pid})")
```

The human can compare outputs against references, provide final polish feedback, and if needed, you can do one more round of manual improvement using the standard human-in-the-loop workflow.

## Step 8: Self-Review (mandatory)

After convergence and any final human review, run the self-review loop before packaging. See `references/self-review-workflow.md` for the full process. This step is not optional — do not package a skill without running self-review first.

## Workspace Structure

```
<skill>-workspace/
  training_data.json              # Input/reference pair definitions
  iteration_history.json          # Cross-iteration tracking (best iteration, similarity progression)
  iteration-0/
    skill-snapshot/               # Copy of initial Skill draft
  iteration-1/
    skill-snapshot/               # Copy of Skill after first rewrite
    eval-crm-case/
      eval_metadata.json
      inputs/                     # Copy of input context files
      generated/
        outputs/                  # What the Skill produced
        transcript.md
      reference/
        outputs/                  # The gold-standard reference
      gradient.json               # Text gradient for this pair
    eval-accounting-case/
      ...
    gradient_summary.json         # Aggregated gradient data
    gradient_summary.md           # Human-readable summary
  iteration-2/
    ...
```

---

## Environment Notes

**Claude Code:** Full support. All steps work as described, including parallel subagent execution and the eval viewer.

**Cowork:** Full support with minor adjustments. When launching the eval viewer in Step 7, use `--static <output_path>` to write a standalone HTML file instead of starting a server, then proffer a link the user can click. Everything else works the same.

**Claude.ai:** This workflow is NOT supported in Claude.ai because it requires subagents for parallel Skill execution (Step 3) and gradient generation (Step 4). If on Claude.ai, use the standard human-in-the-loop workflow instead — you can still use the reference outputs as inspiration when drafting and improving the Skill manually.
