---
name: skill-maker
description: Create, improve, test, and benchmark skills. Use when users want to build a skill from scratch, iterate on an existing skill, run evals, optimize a skill description for triggering, create skills from reference outputs (past human work, example documents, gold-standard deliverables), or turn a workflow trace into a reusable skill ("skillify this", "capture this workflow", "turn this into a skill").
---

# Skill Creator

Creates, improves, and quality-tests skills using a self-directing feedback loop.

**Default mode: Autonomous.** When the user provides intent (and optionally reference outputs), run the full autonomous loop. Read `references/autonomous-loop.md` for the complete spec. The loop handles bootstrapping, reference alignment, eval cycles, security review, and quality checks — human checkpoints occur only twice: initial plan confirmation (Phase 0) and the final report (Phase 5).

**Override to manual mode** when the user explicitly wants to guide each step ("一緒に作りたい", "ステップバイステップで", etc.), when working on a quick Tier 1 skill, or when the user says "just vibe with me".

**Three starting points:**
1. **From intent** — user describes what the skill should do (most common)
2. **From reference outputs** — user provides past human work to replicate; gradient-based alignment runs automatically (Phase 2)
3. **From workflow trace** — user has a recorded task execution to skillify ("turn this into a skill")

**If a skill already exists**, go straight to Phase 3 of the autonomous loop (eval + improve) using the existing SKILL.md as the starting point.

After quality thresholds are reached, offer description optimization to tune triggering.

## Communicating with the user

Users range from plumbers opening their terminal for the first time to seasoned developers. Pay attention to context cues. Terms like "evaluation" and "benchmark" are borderline OK; for "JSON" and "assertion", look for cues that the user knows what they mean before using them without explanation. When in doubt, briefly explain terms.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed. The user may need to fill the gaps, and should confirm before proceeding to the next step.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.
5. What infrastructure does this skill need beyond instructions? Probe for: deterministic logic that should be a script (file generation, data transforms, calculations), domain knowledge or design specs that should be reference docs, multi-step subtasks that benefit from focused agents, and templates or assets the output needs. See `references/architecture-guide.md` for the decision framework. Plan the full directory structure before writing any code.
6. Does this skill produce any files (PPTX, HTML, PDF, images, reports, DOCX, spreadsheets)? If YES: what code would Claude write identically on every invocation? That code belongs in `scripts/` — not as copy-paste examples in SKILL.md, but as importable modules. File-producing skills are automatically Tier 3. Plan the `scripts/` content before writing any SKILL.md body.
7. Has the user provided reference binary files (PPTX, images, PDFs, design files) as examples of what the output should look like? If YES: this is **Visual Reproduction Mode**. Run `agents/asset-extractor.md` immediately — before writing any SKILL.md or scripts. The extractor copies reference files to the skill's assets/reference/ directory, generates references/visual-spec.md, and produces extraction_report.json with critical_findings (e.g. font fallbacks, template usage) that MUST be reflected in the generation scripts. A skill built from a text description of colors and coordinates will drift; a skill that imports from the extracted template file will stay accurate.
8. Does this skill produce any visual output that a user looks at — slides, HTML pages, dashboards, PDFs, charts, images, reports, UI screens, or any rendered result? If YES: a **visual specification** must be confirmed with the user before any generation code is written. See the "Visual Specification Gate" under "Design the Skill Architecture". This applies whether or not reference files were provided — automated extraction can misidentify colors, misread layout intent, or miss key design rules. The user is the only reliable source of "does this look right."

### Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs - if useful for research (searching docs, finding similar skills, looking up best practices), research in parallel via subagents if available, otherwise inline. Come prepared with context to reduce burden on the user.

### Design the Skill Architecture

Before writing any code, decide what infrastructure the skill needs. Map interview findings to components:

| Signal from interview | What to bundle |
|----------------------|----------------|
| File generation, data transforms, calculations | `scripts/` — deterministic logic, written once, reused every invocation |
| Domain rules, design specs, API details (>30 lines) | `references/` — loaded on demand, keeps SKILL.md lean |
| Multi-step subtasks needing focused context | `agents/` — subagent instructions with clear inputs/outputs |
| Templates, icons, fonts, HTML viewers | `assets/` — files used directly in output |
| Multiple output variants (AWS/GCP, React/Vue) | `references/` organized by variant |
| **Reference binary files provided (PPTX, images, PDFs)** | **assets/reference/ + assets/template.* + references/visual-spec.md — run asset-extractor first** |
| **Mandatory output invariants (design rules, format constraints, schema validation)** | **`scripts/validate_*.py` — enforces invariants programmatically; Claude runs this after generation** |

**Rules of thumb:**
- If the skill produces files (PPTX, HTML, PDF, DOCX), it almost certainly needs a generation script
- If the skill applies a design system or domain rules, it needs reference docs
- If the skill orchestrates complex multi-step work, it needs agent instructions
- If every invocation would write the same helper code, bundle it as a script now
- If the skill reads or writes JSON that flows through multiple stages (generate → grade → aggregate), keep field names identical across all producers and consumers — silent name drift (e.g., `id` vs `eval_id`, `name` vs `text`) breaks pipelines without errors; document the schema in `references/` upfront

Plan and write out the full directory structure. Then build the infrastructure components (scripts, references, agents, assets) **before or alongside** SKILL.md — not as an afterthought. The SKILL.md should reference existing, tested infrastructure.

**Hard gate for Tier 3+ (file-producing skills)**: Create `scripts/` and write the core generation logic BEFORE finalizing SKILL.md. For visual skills (slides, HTML, PDFs, charts, UI), "tested" means more than `import` — it means *running* the script to produce a test output and structurally verifying it (correct font, no phantom fills, layout within bounds). Write `scripts/validate_*.py` alongside the generation script, not afterward, so you can verify the first test output immediately. SKILL.md should then import these modules — not re-document them as copy-paste boilerplate.

**Hard gate for Visual Reproduction skills** (user provided reference PPTX/images/PDFs): Run `agents/asset-extractor.md` BEFORE writing any generation scripts. Scripts must use `extraction_report.json`'s `critical_findings` and `generation_recommendations` — especially font specifications and whether to use a template base. A generation script that ignores the extractor's font and template guidance will produce output that looks wrong. This is not optional.

**Visual Specification Gate** (for any skill producing visual output — slides, HTML, PDFs, charts, UIs, reports, images, rendered documents): Before writing any generation code, write a human-readable visual spec and get explicit user confirmation. The spec must cover:

| Aspect | What to specify |
|--------|-----------------|
| **Layout** | Main zones and their arrangement: header, sidebar, content area, footer, card grid — with rough proportions |
| **Colors** | Background, primary accent, secondary accent, text colors — as hex codes |
| **Typography** | For each text role (heading, subheading, body, label, caption): font name, pt size, weight, text color **AND background fill of the zone** (hex color or "no fill/transparent"). Both are required — a zone with 13pt bold text looks completely different with vs without a colored background. **If the output has multiple distinct contexts** (cover page vs. content page, modal vs. main screen, hero section vs. body section), create a **separate typography table for each context** — never merge into one. Different contexts routinely use different fonts for the same role (e.g., cover title in a decorative heading font, content title in a readable body font), and a merged table invisibly destroys that distinction. |
| **Components** | Key visual elements and how each looks: e.g., "white card with thin `#7E00FF` top bar, bold `#5F0095` title on `NONE` (no fill) background, `#333` body text" |
| **Negative space** | Which zones explicitly have NO background fill, border, or decoration. What is absent is as important as what is present. Stating "breadcrumb zone: plain text, no fill" prevents generation code from adding a phantom purple bar. |
| **Spacing rhythm** | Key spacing values: internal text padding, paragraph spacing, gaps between sections. Even if approximate, these set the visual rhythm. |
| **Content density & sizing** | For each container-type element (card, panel, row, column): (a) how should it size — stretch-to-fill available area, collapse to content height, or fixed height? (b) what is the expected typical content volume (e.g., "each card: 2–4 sentences of body text", "each row: 1 short label + 2-line description")? A card designed for stretch-to-fill looks sparse when the content is only 2 lines. A card designed to collapse around content overflows when content is long. Specifying both the sizing mode AND expected content volume before writing generation code prevents the most common visual density failure. |
| **Impression** | One sentence: e.g., "White background, purple accents, clean and professional — no heavy chrome, generous whitespace" |

Present this in the Phase 0 plan (see "Present Plan and Confirm"). Wait for the user to confirm before writing generation code. If using Visual Reproduction Mode, present the extracted values here for confirmation — do not assume extraction = correct. Extraction can misidentify colors, misread layout intent, or miss key design rules. A wrong spec caught at planning time costs one message; a generation script built on a wrong spec costs 5+ iterations.

**Output Verification Gate** (for any skill that produces files or structured output): Before finalizing the skill's workflow, define what verification Claude will run after generation, before declaring success. Every file-producing skill should include a "Verify and Fix" step as the last workflow step. Without this, Claude generates output, assumes it's correct, and declares success without checking invariants — a skill can produce all-black slides, invisible text, or missing sections and still pass evals that only check text content.

Two verification layers to plan:
- **Automated checks** (programmatic): Bundle a `scripts/validate_*.py` that enforces key invariants — font names, color values, layout density, required fields, schema validation. Rules documented in SKILL.md get forgotten over repeated use; rules enforced by a validator run every time.

  **For visual skills specifically**: a validator that only checks "file exists" is not a validator — it passes broken output. Minimum checks: font size floor (≥12pt), layout density (≥75% content area filled), overflow (shapes within page bounds), shape overlap, text clipping, container fill ratio (body text ≥35% of container height). See `~/.claude/skills/pptx/scripts/verify_pptx.py` as a reference implementation.

- **Manual spot-check**: Instructions in SKILL.md for what Claude should verify before declaring success. For visual output: export thumbnails and check against the visual spec. For data output: read a sample and confirm key values look right. Require at least one fix cycle if issues are found.

This applies beyond visual skills: a PDF generator should check section count; a data exporter should validate schema; an HTML builder should check for broken references. Verification is how the skill catches what evals miss.

**Pattern Specification Standard** (for skills that define reusable layout building blocks): Every named pattern (card, row, column, section template) must have a written spec in `references/` — ASCII layout, shape table with x/y/w/h/fill/pt, zone-to-style summary, font hierarchy, spacing notes, sizing mode. Code alone (`Inches(0.42)`, `Pt(20)`) is an implementation, not a spec; without the spec, coordinates and font sizes drift invisibly. See `references/architecture-guide.md` for the spec format. Use `agents/asset-extractor.md` Step 3.5 to extract tables from reference slides.

**Fill column rule** (critical): In shape tables, write the actual hex color OR `NONE` for shapes with no fill. Never leave blank — blank is ambiguous. `NONE` means transparent; generation code **must not** add a fill to that zone. A zone with phantom fill (e.g., a purple bar added to a "NONE" zone) is a common and invisible generation error.

See `references/architecture-guide.md` for detailed patterns, a decision flowchart, and a complete multi-tier exemplar.

### Present Plan and Confirm

Before writing any code or files, present the plan and wait for user confirmation. This is the last human checkpoint before work begins — a misalignment here costs one message; the same misalignment after the eval loop has run costs 5+ iterations.

In **autonomous mode**, this is Phase 0's plan presentation — see `references/autonomous-loop.md` for the exact section format. In **manual mode**, present the following sections (item 5 applies only to skills producing visual output):

1. **Skill + Tier** — Name and tier (1–4) with a one-sentence justification.
2. **Directory structure** — Annotated tree using actual planned file names and inline comments for non-obvious files.
3. **Skill flow** *(Tier 2+ only)* — How inputs move through the skill to outputs. Arrow string for linear flows; numbered list for branching/multi-agent flows.
4. **Scripts** *(file-producing skills)* — Bullet list or table: each script's name and what it does (inputs → outputs in one sentence).
5. **Visual specification** *(for any skill producing visual output: slides, HTML, PDFs, dashboards, UIs, reports, images, etc.)* — A human-readable description of what the output will look like:
   - **Layout sketch** (text is fine): what are the main zones and how are they arranged?
   - **Color palette**: background, primary accent, secondary accent, text — as hex codes or explicit color names
   - **Typography**: for each text role (heading, body, label, caption) → font name, pt size, weight, text color, **and the background fill of that zone (hex or "no fill")**. A heading at 14pt on a white background looks completely different from the same heading on a `#5F0095` panel. **If the output has multiple distinct contexts** (cover page vs. content page, modal vs. main screen, header vs. body section), list typography **per context** — a cover page title may use a different font than a content page title. A single merged table silently hides these structural differences.
   - **Negative space inventory**: which zones have no decorative fill, border, or chrome. Being explicit about what is absent prevents generation code from adding decorations that don't exist in the reference (phantom bars, panels, backgrounds).
   - **Components**: key UI elements and how each looks (e.g., "white card, thin `#7E00FF` top bar, label text `#FFFFFF` bold on `#5F0095` fill, body text `#333333` on NONE/transparent background")
   - **Spacing rhythm**: key internal padding, gap sizes, line spacing — even rough values ("generous whitespace", "tight text" is useful context)
   - **Overall impression**: one sentence (e.g., "White canvas with purple accents; clean and professional — no heavy chrome, generous whitespace")
   The user should be able to read this and immediately say "yes, that's right" or point out what's wrong. This is the lowest-cost correction — do it before any code exists. If extracted from reference files, present those values here and ask the user to confirm: extraction can misidentify colors or misread layout intent.
6. **Tentative test cases** — 2–3 realistic user prompts with expected output shapes (format + key content, not just "a correct answer").
7. **Suggestions / open questions** *(3–5 items max)* — Dependencies the user needs to install, triggering collision risk with other installed skills, edge cases that need explicit handling, scope exclusions worth confirming, any architecture decision that hinges on information you don't have yet.

Wait for "go" or any affirmative before proceeding to writing code or SKILL.md.

**After confirmation, immediately create `<skill-name>-workspace/session-plan.md`** — the single context anchor for this skill creation session. The workspace is a sibling directory to the skill (e.g., skill at `~/.claude/skills/my-skill/` → workspace at `~/.claude/skills/my-skill-workspace/`). If improving an existing skill, read the existing `session-plan.md` to resume context rather than creating a new one. Use the template from `references/autonomous-loop.md` (Phase 0 section). Update it at each major phase transition (after bootstrap, after each eval iteration, after self-review). If the conversation is interrupted or context is compressed, reading this file at the start of the next turn restores working context without re-reading all history.

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. This is the primary triggering mechanism - include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body. Note: currently Claude has a tendency to "undertrigger" skills -- to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit "pushy". So for instance, instead of "How to build a simple fast dashboard to display internal Anthropic data.", you might write "How to build a simple fast dashboard to display internal Anthropic data. Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"
- **compatibility**: Required tools, dependencies (optional, rarely needed)
- **the rest of the skill :)**

### Skill Writing Guide

#### Anatomy of a Skill

Skills range from simple (instructions only) to complex (full infrastructure). Most useful skills are Tier 2-3. If you're producing a Tier 1 skill for a non-trivial task, that's a red flag — ask what scripts, references, or assets would make it more reliable.

**Tier 1 — Instructions Only**: Pure prompt engineering. SKILL.md is the entire skill. Example: commit message formatter.
**Tier 2 — With References**: Add `references/` for domain knowledge or specs too large for SKILL.md.
**Tier 3 — With Scripts + References**: Add `scripts/` for deterministic logic, file generation, data processing.
**Tier 4 — Full Infrastructure**: Add `agents/` and `assets/` for orchestrated, multi-step, asset-heavy skills.

See `references/architecture-guide.md` for the full decision framework, patterns, and a complete multi-tier exemplar.

#### Progressive Disclosure

Skills use three loading levels: metadata (always in context) → SKILL.md body (triggers when skill activates, keep <500 lines) → bundled resources (loaded on demand). Keep SKILL.md lean: reference-link to files in `references/` rather than inlining detail. For large reference files (>300 lines), add a table of contents. For multi-domain skills, organize `references/` by variant (aws.md, gcp.md, azure.md) so Claude reads only the relevant file.

#### Principle of Lack of Surprise

This goes without saying, but skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't go along with requests to create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities. Things like a "roleplay as an XYZ" are OK though.

#### Security and Quality Review

Before packaging, run the self-review loop (see "Self-Review" below). For the full checklist of security, error handling, and quality items to check manually, see `references/self-review-workflow.md`.

#### Writing Patterns

Use imperative form. Define output formats with explicit templates (e.g., `## Report structure / ALWAYS use this exact template: / # [Title] / ## Executive summary / ...`). Include 1–2 concrete input/output examples for non-trivial outputs.

### Writing Style

Try to explain to the model why things are important in lieu of heavy-handed musty MUSTs. Use theory of mind and try to make the skill general and not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

### Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: [you don't have to use this exact language] "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json` with fields `id`, `prompt`, `expected_output`, `files`. Don't write `expectations` (assertions) yet — you'll add them while runs are in progress. See `references/schemas.md` for the full schema.

**Writing good assertions** (add these while eval runs are in progress):

A useful assertion is *objective* and *discriminating* — it passes for a correct output and fails for an incorrect one. Aim for 3–6 per eval.

```json
// Good: specific and verifiable
{"text": "Output file output.pptx exists and is > 100KB", "passed": null, "evidence": ""}
{"text": "Slide 2 uses two-column layout with numbered badges, not a simple bullet list", "passed": null, "evidence": ""}

// Bad: vague and hard to grade
{"text": "The output looks professional", "passed": null, "evidence": ""}
{"text": "Content is correct", "passed": null, "evidence": ""}
```

**For skills producing visual output**, also add structural assertions — these are often more discriminating than content checks:

```json
{"text": "Background is white/near-white; no full-canvas dark rectangle covers content", "passed": null, "evidence": ""}
{"text": "Content containers are not predominantly empty — body text fills ≥30% of container height", "passed": null, "evidence": ""}
```

Visual assertions catch what content-only checks miss. Where possible, verify programmatically (python-pptx XML for fill colors, BeautifulSoup for CSS, PIL for pixel sampling) rather than relying on visual inspection.

**Visual spec coverage check** (for skills producing visual output): After drafting assertions, do a quick scan: for each dimension in the confirmed visual specification — layout, colors, typography, components, negative space, spacing, **content density**, **visual enrichment elements** — ask "Is there at least one assertion that would FAIL if this dimension was wrong?" Two dimensions are almost always uncovered:
- *Content density*: assertions check "text is present" but not "text fills the container" — the most common miss that produces sparse-looking output
- *Visual enrichment*: assertions check "file exists" or "correct colors" but not "non-placeholder shape count matches reference richness" — output can have correct colors but look empty compared to reference

If any dimension has no corresponding assertion, add one before finalizing the eval.

Avoid: too strict ("Exactly 3 paragraphs"), vague ("Professional tone"), too easy ("Output is a file"), or too many (15+ dilutes focus). Aim for 3–6 assertions per eval; 2–3 evals for simple skills, 5–10 for complex ones.

## Running and evaluating test cases

**Read `references/eval-workflow.md` for the full step-by-step procedure.** The short version:

1. Apply the **Baseline Decision rule** (`references/eval-workflow.md` Step 1): spawn with-skill AND baseline together — OR skip baseline (with a documented reason in `eval_metadata.json`) if the skill is Tier 3+ and assertions test structural file correctness
2. While runs execute, draft quantitative assertions and update `eval_metadata.json`
3. Capture `total_tokens` and `duration_ms` from each task notification into `timing.json` — this data is only available at notification time and cannot be recovered later
4. Grade each run, aggregate into `benchmark.json` (`python -m scripts.aggregate_benchmark`), run an analyst pass, and launch the eval viewer (`eval-viewer/generate_review.py`)
5. Read `feedback.json` after the user submits reviews

Put results in `<skill-name>-workspace/iteration-<N>/eval-<name>/`. The grading.json `expectations` array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or variants) — the viewer depends on these exact field names.

For programmatically checkable assertions, write and run a script rather than eyeballing it.

**Eval completion gate**: Before self-review or packaging, verify:
- Every assertion in every `grading.json` has `"passed": true` or `"passed": false` — any `null` means that eval was never run, which is the same as having no evals at all
- Pass rate ≥ 75% across all evals (below this: iterate again)
- A `grading.json` exists for every eval defined in `evals.json`

Run the automated check:
```bash
python -m scripts.check_completeness <skill-path>
```

A skill with unrun evals is not ready for packaging — the assertions are promises you haven't kept.

**What to do when the gate fails:**
- *`passed: null` everywhere* → Evals were defined but never executed. Run the eval pipeline (see `references/eval-workflow.md`).
- *Pass rate 50–74%* → Iterate: revise the skill based on the failed assertions, then re-run evals.
- *Pass rate < 50%* → Stop and diagnose: are the assertions reasonable? Is the SKILL.md missing infrastructure? Is the test prompt representative? Fix the root cause before iterating.
- *Pass rate ≥ 75% but some assertions fail* → Check whether the failing assertions are overly strict (consider loosening) or reflect a real gap (iterate on the skill).

---

## Improving the skill

This is the heart of the loop. You've run the test cases, the user has reviewed the results, and now you need to make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The big picture thing that's happening here is that we're trying to create skills that can be used a million times (maybe literally, maybe even more who knows) across many different prompts. Here you and the user are iterating on only a few examples over and over again because it helps move faster. The user knows these examples in and out and it's quick for them to assess new outputs. But if the skill you and the user are codeveloping works only for those examples, it's useless. Rather than put in fiddly overfitty changes, or oppressively constrictive MUSTs, if there's some stubborn issue, you might try branching out and using different metaphors, or recommending different patterns of working. It's relatively cheap to try and maybe you'll land on something great.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Make sure to read the transcripts, not just the final outputs — if it looks like the skill is making the model waste a bunch of time doing things that are unproductive, you can try getting rid of the parts of the skill that are making it do that and seeing what happens.

3. **Explain the why.** Try hard to explain the **why** behind everything you're asking the model to do. Today's LLMs are *smart*. They have good theory of mind and when given a good harness can go beyond rote instructions and really make things happen. Even if the feedback from the user is terse or frustrated, try to actually understand the task and why the user is writing what they wrote, and what they actually wrote, and then transmit this understanding into the instructions. If you find yourself writing ALWAYS or NEVER in all caps, or using super rigid structures, that's a yellow flag — if possible, reframe and explain the reasoning so that the model understands why the thing you're asking for is important. That's a more humane, powerful, and effective approach.

4. **Extract reusable infrastructure from transcripts.** Read the transcripts from the test runs and look for patterns that signal missing infrastructure:
   - All test cases wrote similar helper scripts → bundle the canonical version in `scripts/`
   - All test cases independently researched the same domain facts or applied the same rules → capture that knowledge in `references/`
   - All test cases spent significant time on a subtask that could be a focused agent → create agent instructions in `agents/`
   - All test cases created similar templates, icons, or boilerplate files → bundle them in `assets/`
   The principle: every invocation should start with the right tools and knowledge, not reinvent them from scratch. A skill that just tells Claude "write a script to do X" when it could bundle that script is wasting the user's time and tokens.

5. **Check infrastructure completeness against the tier model.** After each iteration, step back and ask: does this skill have everything it needs to succeed reliably? Quick sanity check:
   - Does the skill produce files? → It should have a generation script in `scripts/`
   - Does the skill apply domain-specific rules or design specs? → They should be in `references/`
   - Does the skill orchestrate multi-step work? → Consider agent instructions in `agents/`
   - Does the skill need templates, fonts, or icons? → They belong in `assets/`
   If the answer is "yes" but the corresponding component doesn't exist, build it now — don't wait for the packaging step.

Take your time with revisions — thoughtful iteration is more valuable than speed. Write a draft revision, review it with fresh eyes, and improve it. Get into the head of the user and understand what they want and need.

### The iteration loop

**In autonomous mode**, follow Phase 3 of `references/autonomous-loop.md` — convergence is determined by machine-readable signals (quality score ≥ 0.80 + assertion pass rate ≥ 0.75), not human sign-off.

**In manual mode** (when the user is guiding each step):

1. Apply your improvements to the skill
2. **Security and infrastructure check** — Spawn `reviewer.md` and run `check_completeness`. Fix all CRITICAL and MAJOR findings before proceeding.
3. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs.
4. Launch the **eval viewer** (`eval-viewer/generate_review.py`) with `--previous-workspace` pointing at the previous iteration
5. Wait for the user to review and tell you they're done
6. Read the new feedback, improve again, repeat

Manual mode convergence:
- The user says they're happy, OR
- Feedback is all empty (everything looks good), OR
- No meaningful progress for 2 consecutive iterations — "meaningful" = assertion pass rate improved by > 5 percentage points, OR the user left substantively new feedback (not just repeating the same complaint). Two iterations with the same complaints and the same pass rate signal a structural gap — stop iterating and diagnose the root cause instead of running another round.

Regardless of mode, **always run self-review** (see "Self-Review" below) once the loop ends, before packaging.

---

## Reference-Based Skill Creation

This mode is for when the user has existing examples of correct outputs (past human work) and wants a Skill that reproduces that quality. Instead of human feedback every iteration, it uses "text gradients" to automatically identify gaps and improve the Skill.

**When to use:** The user mentions reference documents, example outputs, past deliverables, or wants to replicate existing work quality. Requires subagents (Claude Code or Cowork only, not Claude.ai).

**Read `references/reference-based-workflow.md` for the full 8-step workflow.** The short version:
1. Gather input/reference pairs from the user (3-5 minimum)
2. Draft an initial Skill by reverse-engineering patterns from the references
3. Run the Skill on each input (subagent MUST NOT see references)
4. Generate text gradients — compare outputs vs references using `agents/gradient.md`
5. Aggregate gradients (`python -m scripts.aggregate_gradients`) and rewrite the Skill
6. Repeat until convergence (`mean_similarity > 0.85`) or 5 iterations
7. Optionally launch the eval viewer for final human review
8. Run self-review (see "Self-Review" below) before packaging

---

## Capture by Doing

This mode turns an existing workflow trace into a reusable skill. A workflow trace (`workflow_trace.json`) is a structured log of how a task was actually executed — including decisions, error recoveries, and tool patterns. Traces are typically produced by the `workflow-recorder` custom agent (see below), but any JSON file following the `workflow_trace.json` schema in `references/schemas.md` works.

The insight: observing an actual execution produces better skills than having a user describe the workflow from scratch. The trace captures decisions, error recoveries, and tool patterns that a user would forget to mention.

**When to use:** The user says "turn this into a skill", "skillify this", "capture this workflow", or you detect a `workflow_trace.json` in the working directory and the user expresses interest in skill creation.

### Step 1: Locate and Evaluate the Trace

Look for `workflow_trace.json` in the current working directory or a directory the user specifies. If no trace exists, tell the user:

> "I don't see a workflow trace. If you want to execute a task while recording one, you can use the `workflow-recorder` agent — it produces a trace file automatically. Then come back and I'll turn it into a skill."

If a trace exists, read it and check these heuristics. If **2 or more** trigger, the trace is a good candidate for skill creation:

| Heuristic | What it detects |
|-----------|----------------|
| 5+ logical steps | Complex, multi-step workflow |
| Decision points present | Non-trivial choices were made |
| Error recovery occurred | Pitfalls worth documenting |
| Repeated tool pattern (3+ times) | Automation candidate |
| Script creation during execution | Reusable tooling emerged |
| File format transformation | Input and output have different formats |

**Suppress if:** under 3 steps, purely conversational, or the task was itself about skill creation (avoid recursion).

If fewer than 2 heuristics trigger, tell the user the workflow may be too simple to benefit from skillification but offer to proceed anyway if they want.

### Step 2: Generate the Skill Draft

1. **Copy any task outputs** referenced in `metadata.output_files` to `<skill-name>-workspace/original-outputs/` as a reference baseline.

2. **Spawn an observer subagent** to synthesize the trace into a skill:
   ```
   Read the instructions in agents/observer.md, then synthesize a skill
   from the workflow trace:
   - trace_path: <path>/workflow_trace.json
   - output_path: <skill-path>/SKILL.md
   - skill_name: <suggested-name>
   - transcript_path: <path>/transcript.md (if available)
   ```

3. **Review `observer_notes.json`** for flagged uncertainties. Pay attention to `confidence: "low"` abstraction decisions — these are places where the observer had to guess and the eval loop should validate.

4. **Present the draft** to the user for initial review. Highlight the observer's suggested improvements and any bundled script candidates.

### Connecting to the Eval Loop

The observer's output is a draft SKILL.md — the same artifact that "Write the SKILL.md" (above) produces. From here, proceed to the standard eval/improve cycle:

1. **Auto-generate test prompts**: Use `metadata.task_summary` from the trace as the first test case. Generate 2-3 variations by abstracting the input (different files, different parameters, different edge cases). Save to `evals/evals.json`.

2. **Built-in reference output**: The original executor output serves as a quasi-reference. This opens the option to use the Reference-Based improvement loop (gradient agents) instead of or in addition to human-feedback iteration. Offer this to the user if the original output was high quality.

3. **Standard eval runs, grading, viewer, improvement loop**: All work exactly as documented in `references/eval-workflow.md`.

### The Workflow-Recorder Agent

The `workflow-recorder` is a Claude Code custom agent that executes tasks while recording a structured trace. It is **independent from skill-maker** — it records traces without knowing about skills. The connection is the `workflow_trace.json` file.

**Note:** The workflow-recorder agent is NOT bundled with skill-maker. It is a separate custom agent. To use it:
1. Check if `~/.claude/agents/workflow-recorder.md` already exists (your user may have installed it separately)
2. If not, you can create it manually as a custom agent, or — more practically — skip it and instead just use any `workflow_trace.json` produced by a prior task execution (or write one manually following `references/schemas.md`)

Once installed, Claude may auto-delegate complex multi-step tasks to it based on its description. Users can also invoke it explicitly: "use the workflow-recorder agent to [task]". After execution, the agent leaves a `workflow_trace.json` in the working directory.

The agent does not suggest skill creation — that's skill-maker's job. This separation means the agent works even without skill-maker installed.

### Workspace Structure

Skill lives at `~/.claude/skills/<skill-name>/` (SKILL.md + evals/evals.json). Workspace is a sibling directory `<skill-name>-workspace/` containing: `workflow_trace.json`, `original-outputs/`, `observer_notes.json`, `session-plan.md`, `loop-state.json`, and `iteration-N/eval-<name>/{with_skill,without_skill}/{outputs/,grading.json,timing.json}` + `eval_metadata.json`, `benchmark.json`, `quality-judge.json`. See `references/schemas.md` for full file formats.

---

## Self-Review (mandatory before packaging)

Automated review-and-fix loop. **Read `references/self-review-workflow.md` for the full process.** The short version:
1. Spawn a reviewer subagent (`agents/reviewer.md`) to audit the skill
2. Fix critical and major findings; re-review to verify fixes
3. Repeat until clean (zero critical/major) or 5 iterations
4. Report results to the user, then proceed to packaging

---

## Advanced: Blind comparison

For rigorous A/B comparison between two skill versions, read `agents/comparator.md` and `agents/analyzer.md`. Two outputs are given to an independent agent without revealing which is which, then analyzed for why the winner won. Optional, requires subagents, and most users won't need it.

---

## Description Optimization

The description field in SKILL.md frontmatter determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize it.

**Read `references/description-optimization-workflow.md` for the full procedure.** The short version: generate 30 realistic trigger-eval queries (mix of should-trigger and should-not-trigger), review them with the user via `assets/eval_review.html`, then run `python -m scripts.run_loop` to optimize. The script handles train/test splitting, multi-run evaluation, and extended-thinking rewrites automatically.

---

### Pre-Packaging Completeness Check

Before packaging, verify the skill is complete. Start with the automated check:

```bash
# Skill structure checks only:
python -m scripts.check_completeness <skill-path>

# Skill structure + verify grading.json files (recommended before packaging):
python -m scripts.check_completeness <skill-path> --check-grading <workspace-path>
```

Fix all FAIL items before touching the manual checklist. WARN items need judgment.

Then verify manually:

- **Self-review passed** — zero critical/major findings (see "Self-Review" above)
- **Infrastructure matches complexity** — if the skill produces files, transforms data, or applies domain rules, the corresponding scripts/references/agents exist (not just instructions telling Claude to figure it out at runtime). **File-producing skills with only copy-paste documentation are Tier 2 masquerading as Tier 3 — bundle the code into importable scripts.**
- **No reinvention-from-scratch** — test run transcripts show the skill using bundled resources, not recreating them each invocation
- **SKILL.md under 500 lines** — detail is in references, not inline
- **All references reachable** — every file mentioned in SKILL.md exists in the skill directory
- **Schema consistency** — if the skill defines or consumes JSON files in a pipeline, field names are consistent across all producers and consumers (e.g., `grading.json` `expectations` must use `{text, passed, evidence}` — not `name/met/details`). `check_completeness` validates `evals.json` structure, `skill_name` consistency, and script syntax automatically.
- **Description optimized** — the frontmatter description accurately triggers the skill

If any item fails, fix it before proceeding. The most common failure is shipping a Tier 1 skill for a Tier 3 task — instructions that tell Claude to "write a script to generate the output" instead of bundling the script.

### Package and Present (only if `present_files` tool is available)

**Before packaging, confirm the completeness check above has passed.** If it hasn't, address the gaps now.

Check whether you have access to the `present_files` tool. If you don't, skip this step. If you do, package the skill and present the .skill file to the user:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

After packaging, direct the user to the resulting `.skill` file path so they can install it.

---

## Environment Notes

**Claude Code:** Full workflow support including subagents, browser viewer, and description optimization.

**Cowork:** Full workflow support with these adjustments:
- Use `--static <output_path>` for the eval viewer (no display available) and proffer a download link
- Feedback arrives as a downloaded `feedback.json` file from the viewer's "Submit All Reviews" button
- Description optimization works (uses `claude -p` via subprocess)
- If subagent timeouts occur, run test cases in series instead of parallel
- Always generate the eval viewer (`generate_review.py`) before revising the skill yourself — get results in front of the human first

**Claude.ai:** Reduced workflow — no subagents, no `claude` CLI:
- Run test cases inline (one at a time, using the skill yourself); skip baseline runs
- Present results in the conversation instead of the browser viewer; ask for inline feedback
- Skip quantitative benchmarking (requires baseline comparisons with subagents)
- Skip description optimization (requires `claude -p`) and blind comparison (requires subagents)
- Packaging works if Python and filesystem are available

---

## Reference files

Read these when you need to spawn the relevant subagent or follow a workflow:
- `references/autonomous-loop.md` — **Primary**: Phase definitions, convergence criteria, iteration limits, human checkpoint triggers. Read this first when starting any skill creation task.
- `references/architecture-guide.md` — Decision framework for skill infrastructure: when to create scripts, references, agents, assets. Includes patterns, anti-patterns, and a complete multi-tier exemplar
- `agents/grader.md` — Evaluate assertions against outputs
- `agents/quality-judge.md` — AI quality judge for subjective evaluation without references. Produces quality_score (0.0-1.0) and recommendation (proceed/iterate/escalate). Used in Phase 3 of the autonomous loop.
- `agents/comparator.md` — Blind A/B comparison between two outputs
- `agents/analyzer.md` — Analyze why one version beat another
- `agents/gradient.md` — Compare generated vs reference outputs (text gradients + binary/visual structure comparison)
- `agents/reviewer.md` — Review a skill for security, bugs, and quality
- `agents/observer.md` — Synthesize workflow traces into skill drafts (Capture by Doing)
- `agents/asset-extractor.md` — **Visual Reproduction Mode**: extract assets from reference binary files (PPTX, images, PDFs) into the skill's assets/reference/ dir, generate references/visual-spec.md, produce critical_findings on fonts and template usage. Run at Phase 0 when reference binary files are provided.
- `workflow-recorder` (not bundled) — Custom Agent that records workflow traces during task execution. Install to `~/.claude/agents/` if available; see "The Workflow-Recorder Agent" section for alternatives if not installed.
- `references/schemas.md` — JSON structures for evals.json, grading.json, eval_metadata.json, gradient.json, workflow_trace.json, etc.
- `references/reference-based-workflow.md` — Full 8-step reference-based skill creation workflow
- `references/self-review-workflow.md` — Automated review-and-fix loop (per-iteration + pre-packaging)
- `references/eval-workflow.md` — Full 5-step eval workflow (spawn runs, grade, aggregate, viewer, feedback)
- `references/description-optimization-workflow.md` — Trigger eval generation, review, and optimization loop
- `scripts/quick_validate.py` — Validate a skill's SKILL.md (frontmatter, naming, description length); also called by `package_skill.py`
- `scripts/generate_report.py` — Generate HTML report from optimization loop output; also called by `run_loop.py`
- `scripts/check_completeness.py` — Validate infrastructure completeness: checks for missing scripts/ in file-producing skills, unrun evals (null assertions), SKILL.md length, orphaned references. Accepts `--check-grading <workspace-path>` to also verify that all grading.json assertions have been graded (no `passed: null`). Run before packaging or after each iteration.

---

**Autonomous mode**: read `references/autonomous-loop.md` and follow it. Human input needed only at Phase 0 (plan confirmation) and Phase 5 (final report). All improvement, security, and quality checks run autonomously within iteration budgets (max 15 total).

**Manual mode**: draft → run test cases → generate eval viewer → improve → repeat → self-review → package. Add these steps to your TodoList to make sure nothing gets skipped.