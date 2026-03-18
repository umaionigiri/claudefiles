# Self-Review Workflow

Automated review-and-fix loop for skills after creation or modification. Spawns a reviewer agent to find issues, fixes them, and repeats until clean or 5 iterations.

**When to run:**

1. **Per-iteration (security and infrastructure focus)**: After each improvement iteration, before launching the next eval run. Spawn reviewer.md and fix all CRITICAL/MAJOR findings. Security issues found during iteration are cheap to fix; security issues discovered at packaging are expensive. This is especially important for Tier 3+ skills with scripts — reviewer.md will flag missing `scripts/` for file-producing skills, unsafe subprocess calls, and path traversal risks. For trivial Tier 1 skills (instructions only, no scripts), a quick manual scan of the security checklist below is sufficient.

2. **Pre-packaging (full quality gate)**: After the iteration loop ends, before packaging. Full review required; zero critical/major findings needed to proceed.

Also run after reference-based workflow convergence (Step 7).

**Prerequisites:** A complete skill directory with SKILL.md and any bundled resources. Subagent support (Claude Code or Cowork).

---

## Step 1: Initial Review

Spawn a reviewer subagent:

```
Read the instructions in agents/reviewer.md, then review the skill:
- skill_path: <path-to-skill>
- output_path: <workspace>/self-review/review-1.json
- iteration: 1
```

## Step 2: Check Results

Read `review-1.json`. Check `summary.clean`:

- If `clean == true`: No critical or major issues. Skip to Step 5.
- If `clean == false`: Continue to Step 3.

## Step 3: Fix Issues

For each finding, ordered by severity (critical first, then major, then minor):

1. Read the finding's file, line, description, and suggestion
2. Apply the fix
3. If a fix would change the skill's behavior (not just its quality), note it for the user — do not silently change functionality

Focus on critical and major findings. Minor findings are acceptable to leave if fixing them risks introducing new issues.

## Step 4: Re-Review

Spawn the reviewer again with the previous review for regression checking:

```
Read the instructions in agents/reviewer.md, then review the skill:
- skill_path: <path-to-skill>
- output_path: <workspace>/self-review/review-N.json
- previous_review_path: <workspace>/self-review/review-(N-1).json
- iteration: N
```

Check results and decide:

- **`clean == true`**: Done. Go to Step 5.
- **`iteration >= 5`**: Stop. Report remaining findings to the user. Go to Step 5.
- **`total_findings` decreased**: Progress. Go back to Step 3.
- **`total_findings` increased OR new critical/major findings appeared that were not in the previous review**: Safety valve. Revert all changes made in Step 3 of this iteration (use `git diff` or the skill snapshot to identify what to revert). Report the regression to the user with specific before/after finding counts. Go to Step 5.
- **Same findings persist for 2 consecutive iterations**: No progress. Stop and report remaining findings. Go to Step 5.

## Step 5: Report

Briefly tell the user what happened:

- **Clean on first pass**: "Self-review passed — no issues found."
- **Fixed everything**: "Self-review found N issues (X critical, Y major, Z minor) and fixed all of them in K iterations."
- **Some remain**: "Self-review found N issues and fixed M. Remaining items: [list critical/major unfixed items]."
- **Reverted**: "Self-review fixes introduced new issues. Changes were reverted. Manual review recommended for: [list items]."

---

## Security and Quality Checklist

The reviewer agent (`agents/reviewer.md`) checks for these categories. This list also serves as a manual spot-check reference when subagents are not available.

**Security:**
- Command injection: user input in shell commands, `shell=True` in subprocess
- Path traversal: unchecked `..` in file paths, paths escaping expected directories
- Symlink traversal: directory walks following symlinks without validation
- XSS: user values interpolated as raw HTML instead of `textContent` or JSON
- Unsafe deserialization: `yaml.load()` without `safe_load`, `pickle` on untrusted data

**Error handling:**
- JSON/YAML parsing without try/except
- File operations without error handling
- Missing input validation (empty strings, wrong types, missing fields)
- HTTP endpoints without payload size limits

**Code quality:**
- Unused imports and dead functions
- Hardcoded values that should be parameters
- External dependencies where stdlib alternatives exist

**Consistency:**
- Files referenced in SKILL.md that do not exist
- Scripts that nothing references (orphaned files)
- Schema definitions that do not match actual output formats

**Output verification:**
- For file-producing skills: is there a validator script in `scripts/` OR explicit verification instructions in SKILL.md that require Claude to check output before declaring success?
- For visual output skills: is there a self-review step (export thumbnails, check against visual spec)?
- A file-size check alone does NOT count as verification
- Absence of a verification step in a file-producing skill is a **major** gap — add it before packaging

**Documentation-code consistency:**
- If reference docs (visual-spec.md, design-system.md) and generation scripts were created by different processes (e.g., auto-extracted docs + hand-written scripts), spot-check 3 key constants: font names, color hex values, measurements/sizes
- If docs and code diverge on key constants, this is a **major** gap — fix the discrepancy before packaging
- This is especially critical for Visual Reproduction skills where extraction was automated

---

## Environment Notes

**Claude Code:** Full support. Spawn reviewer as subagent.

**Cowork:** Full support. Same as Claude Code.

**Claude.ai:** No subagent support. Perform the review inline — read `agents/reviewer.md` and follow its process yourself. Limit to 2 iterations since you are reviewing your own work. Focus on security and error handling checks.
