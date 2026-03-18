# Skill Architecture Guide

Detailed reference for deciding what infrastructure a skill needs. Read this when planning a new skill's directory structure, or when reviewing whether an existing skill has the right components.

## Table of Contents

1. [Decision Flowchart](#decision-flowchart)
2. [Component Patterns](#component-patterns)
3. [Anti-Patterns](#anti-patterns)
4. [Complete Exemplar: slide-deck](#complete-exemplar-slide-deck)
5. [Tier Examples](#tier-examples)

---

## Decision Flowchart

For each question, if the answer is "yes", add the indicated component:

```
Does the skill produce files (PPTX, HTML, PDF, images, etc.)?
  YES → scripts/ (generation script that handles layout, formatting, structure)

Does the skill apply domain-specific rules, design specs, or detailed guidelines?
  YES → references/ (domain docs loaded on demand)

Is there >50 lines of format/schema/spec detail?
  YES → references/ (keeps SKILL.md lean)

Does the skill support multiple variants (frameworks, platforms, languages)?
  YES → references/ organized by variant (e.g., react.md, vue.md)

Does the skill orchestrate multi-step workflows with distinct subtasks?
  YES → agents/ (focused subagent instructions)

Does the output need templates, icons, fonts, or static files?
  YES → assets/ (bundled directly)

Would every invocation write the same boilerplate code?
  YES → scripts/ (bundle it once)

Does the skill need a viewer, dashboard, or interactive HTML?
  YES → assets/ or scripts/ (HTML template + generation script)

Does the skill need to visually reproduce reference binary files (PPTX, images, PDFs)?
  YES → Run agents/asset-extractor.md BEFORE writing any scripts or SKILL.md.
         assets/reference/ (copies of source files — immutable ground truth)
         assets/template.pptx (base PPTX template if applicable — inherits theme/master)
         references/visual-spec.md (extracted color palette, fonts, geometry)
         The visual-spec.md becomes the authoritative design system for all scripts.

Does the skill have mandatory output invariants (design rules, format constraints, schema validation)?
  YES → scripts/validate_*.py (enforces invariants programmatically; Claude runs this after generation)
         Without enforcement, rules documented in SKILL.md decay across repeated invocations.
         The validator runs after generation, before Claude declares success.

Does the skill define named, reusable layout building blocks (patterns, card types, section templates, UI components)?
  YES → references/pattern-specs.md — per-pattern spec for each named layout:
         ASCII diagram + shape table (x/y/w/h/fill/pt/bold) + font hierarchy + sizing rules.
         The code in scripts/ is the implementation; the spec is the ground truth.
         Without it: coordinates drift silently (0.06" → 0.09"), font sizes shrink (28pt → 20pt),
         and no one notices until the output visibly looks wrong.
```

**Minimum viable infrastructure**: If 2+ questions are "yes", the skill is at least Tier 3. Plan accordingly.

---

## Component Patterns

### scripts/ — Deterministic Logic

**When to create**: The skill involves file generation, data transformation, validation, or any repeatable logic that should be identical every invocation.

**What goes here**:
- File generators (PPTX, HTML, PDF, DOCX builders)
- Data processors (CSV→JSON, aggregators, formatters)
- Validators (schema checks, linting, quality gates)
- Utility scripts (packaging, deployment, templating)

**Pattern**: Scripts should be importable modules with a clear API, not just standalone CLIs. This lets the SKILL.md show example usage:

```python
# Good: importable with clear API
from scripts.create_pptx import SlideBuilder
sb = SlideBuilder("output.pptx")
sb.add_title("Headline", subtitle="Sub")
sb.save()

# Bad: opaque CLI that hides the logic
# python create_pptx.py --title "Headline" --subtitle "Sub"
```

**Required: `scripts/__init__.py`**: For `from scripts.module import func` and `python -m scripts.module` to work, `scripts/` must be a Python package. Always create an empty `scripts/__init__.py` alongside any `.py` files. Without it, module imports fail with `ModuleNotFoundError` at runtime — `check_completeness.py` Check 10 flags this automatically.

**Naming**: Use descriptive names that indicate the output — `create_pptx.py`, `validate_schema.py`, `aggregate_results.py`.

### references/ — Domain Knowledge

**When to create**: The skill applies rules, specs, or knowledge that would bloat SKILL.md past 500 lines, or that only applies in specific contexts.

**What goes here**:
- Design systems (colors, typography, layout rules)
- API specifications and schemas
- Domain-specific guidelines (medical writing, legal formatting, etc.)
- Variant-specific instructions (AWS vs GCP, React vs Vue)
- Workflow procedures too detailed for SKILL.md

**Pattern**: Each reference file should have a clear scope. SKILL.md points to them with context on when to read:

```markdown
## Design Principles
[summary of key principles here]
For detailed color palette, typography specs, and layout rules, read `references/design-system.md`.
```

**Organization by variant**:
```
references/
├── aws.md          ← only loaded when deploying to AWS
├── gcp.md          ← only loaded when deploying to GCP
└── common.md       ← shared patterns, always loaded
```

### agents/ — Focused Subagents

**When to create**: The skill has distinct subtasks that benefit from isolated context — the subtask is complex enough that mixing it with the main flow would be confusing or error-prone.

**What goes here**:
- Review/audit agents (quality checks, security reviews)
- Generation agents (specialized content creation)
- Analysis agents (comparison, grading, summarization)
- Observer agents (trace analysis, pattern extraction)

**Pattern**: Each agent file defines inputs, process, and output format:

```markdown
# Agent Name
[Role description]
## Inputs
- param_1: what it is
- param_2: what it is
## Process
[Steps the agent follows]
## Output Format
[JSON or file structure the agent produces]
```

**Key principle**: Agents are spawned as subagents. They receive focused context and produce structured output. Keep them blind to things they don't need — this prevents bias and keeps them focused.

#### agents/ vs scripts/ — decision rules

These two components solve different problems. Choosing wrong leads to either over-engineering (agent for a deterministic task) or under-engineering (script for something that needs judgment):

| Signal | Use | Reason |
|--------|-----|--------|
| Output is deterministic — same input always produces same output | `scripts/` | Scripts are fast, testable, and don't consume LLM tokens |
| Output requires judgment — comparison, grading, quality assessment | `agents/` | LLM judgment can't be captured in code |
| Subtask needs to read 50+ lines of spec before executing | `agents/` | Isolated context window is cleaner |
| Subtask produces a structured JSON artifact (review.json, grading.json) | `agents/` | The artifact documents the reasoning |
| Subtask is reused by multiple invocations with the same logic | `scripts/` | Bundle once, import everywhere |
| Subtask transforms data (CSV→JSON, extract fields, validate schema) | `scripts/` | Deterministic transforms belong in code |
| Subtask compares two outputs to pick a winner | `agents/` | Requires subjective evaluation |
| Subtask generates a file (PPTX, HTML, PDF) | `scripts/` | File generation is deterministic layout logic |

**Rule of thumb**: If you would write the same Python function every time a skill invokes this subtask, it's a script. If you need an LLM to make a judgment call, it's an agent.

### assets/ — Static Files

**When to create**: The output needs files that are constant across invocations — templates, icons, fonts, HTML viewers, CSS stylesheets.

**What goes here**:
- HTML templates for viewers/dashboards
- Icon sets (SVG, PNG)
- Font files
- CSS/JS libraries
- Starter templates

**Pattern**: Assets are referenced by scripts or SKILL.md instructions, never generated at runtime:

```python
# In a script
icon_path = os.path.join(SKILL_DIR, "assets", "icons", "check.svg")
```

### assets/reference/ — Source Reference Files (Visual Reproduction Skills)

**When to create**: The user provided binary reference files (PPTX, images, PDFs) as examples of what the output should look like. These files are the *source of truth* for the visual design.

**Why this matters**: Describing a visual design in text is unreliable — colors, fonts, and positions drift from the description. The actual source files don't. A skill that loads `assets/template.pptx` will always match the original; a skill rebuilt from a text description will gradually diverge.

**What goes here**:
- `assets/reference/<filename>` — verbatim copy of each reference file provided by the user
- `assets/template.pptx` — PPTX file used as `Presentation(template_path)` base (inherits theme colors, slide master, fonts automatically)
- `assets/thumbnails/` — PNG thumbnails of reference slides (for gradient agent visual comparison)

**Companion file**: `references/visual-spec.md` — extracted color palette, typography, and geometry spec that scripts use for any design tokens not inherited from the template.

**Hard rule**: Run `agents/asset-extractor.md` before writing scripts or SKILL.md. The extraction report's `critical_findings` and `generation_recommendations` tell the generated scripts *exactly* which fonts to specify explicitly, whether to use the template base, and what pitfalls to avoid. Scripts written without this context will drift from the reference.

**Directory layout**:
```
skill-name/
├── SKILL.md
├── scripts/
│   └── slide_builder.py          ← imports specs from references/visual-spec.md
├── references/
│   └── visual-spec.md            ← extracted design tokens (color palette, fonts, geometry)
└── assets/
    ├── reference/
    │   └── original.pptx         ← verbatim copy; never modified
    ├── template.pptx             ← base for Presentation(template_path)
    └── thumbnails/
        └── slide_001.png         ← reference screenshots for comparison
```

---

## Anti-Patterns

### "Just Tell Claude to Write It" (Tier 1 for a Tier 3 Task)

**Problem**: SKILL.md says "write a Python script to generate the PPTX" instead of bundling the script. Every invocation reinvents the wheel — different quality each time, wastes tokens, and the user waits while Claude writes 200 lines of boilerplate.

**Fix**: Bundle the script. SKILL.md should say "import the bundled SlideBuilder and use it" with a usage example.

**How to spot it**: The SKILL.md contains phrases like "write a script to...", "create a helper that...", or "generate code for..." for tasks that should be deterministic.

**Variant: "Copy This Into Every Script" (Documentation Masquerading as Infrastructure)**

A subtler but equally damaging form: SKILL.md contains code that users are expected to copy-paste into their generation scripts each invocation.

Symptoms:
- `references/pattern-code.md` contains full function definitions (not just API docs or signatures)
- SKILL.md has a "Boilerplate (copy into every generation script)" section
- Each invocation writes slightly different setup code → quality drifts silently over time
- No `scripts/*.py` files exist despite the skill producing files

Why it still fails: the code *exists*, but it lives in documentation rather than an importable module. Every invocation reinvents the foundation slightly differently. After 3–4 uses, copy-paste drift accumulates — wrong parameters, missed steps, stale patterns.

Fix: Move the repeated code into `scripts/consulting_patterns.py` (or equivalent). SKILL.md's usage example becomes `from consulting_patterns import add_agenda, add_stat_cards`. The `pattern-code.md` then documents the module's API, not the module itself.

Run `python -m scripts.check_completeness <skill-path>` to detect this automatically — it flags file-producing skills that lack `scripts/*.py` files.

### Monolithic SKILL.md

**Problem**: Everything is in SKILL.md — design specs, API docs, step-by-step procedures, schemas. The file is 800+ lines and Claude struggles to follow it all.

**Fix**: Extract into references. SKILL.md should contain workflow + pointers. Each reference file covers one topic.

**How to spot it**: SKILL.md is over 500 lines and contains large blocks of non-workflow content (specs, schemas, detailed examples).

### Missing Domain Knowledge

**Problem**: The skill tells Claude to "follow best practices for X" without specifying what those practices are. Claude guesses, sometimes wrong.

**Fix**: Write the practices down in a reference doc. Be specific — colors, fonts, spacing, rules, examples.

**How to spot it**: The SKILL.md uses vague phrases like "professional style", "clean design", "follow conventions" without defining them.

### Orphaned Infrastructure

**Problem**: Scripts or references exist but SKILL.md never mentions them, or mentions them but doesn't explain when to use them.

**Fix**: Every bundled file must have a clear pointer from SKILL.md with context: "Read `references/design-system.md` when customizing colors or typography."

### Missing Reference Assets (Visual Reproduction Without Ground Truth)

**Problem**: The user provided PPTX/image/PDF reference files, but the skill was built from scratch using a text description of the design instead of the actual files. The skill's `assets/` directory is empty (or doesn't exist), and `references/visual-spec.md` was written by eye rather than extracted programmatically.

**Why this fails**: Color descriptions like "dark purple" produce `#4B0082` (generic CSS purple), not `#5F0095` (the actual Accenture purple). Font fallback behavior is invisible until Japanese text renders in the wrong script. Template base selection (`Presentation()` vs `Presentation(template_path)`) affects whether slide master decorations appear. These gaps are impossible to detect from text description alone.

**Symptoms**:
- `assets/` directory is absent or empty despite reference files being provided
- `references/visual-spec.md` was written manually rather than extracted
- Generated slides "look similar" but differ in specific colors, fonts, or proportions
- No `extraction_report.json` anywhere in the skill

**Fix**: Run `agents/asset-extractor.md` with the original reference files. It will copy them to `assets/reference/`, extract the actual design tokens, and document critical findings (e.g., "Meiryo UI must be specified explicitly for Japanese text"). Then regenerate all scripts using the extracted `visual-spec.md` as the authoritative design system.

**How to spot it**: The skill produces files that look like the reference but aren't pixel-accurate, AND no `assets/reference/` directory exists.

### No Verification Step (Generate and Declare Success)

**Problem**: The skill generates files but has no post-generation verification. Claude generates output, assumes it's correct, and declares success without checking key invariants. Evals typically check text content ("output contains the word X"), not structural properties. A PPTX with all-black slides, invisible text, or missing sections will pass text-based evals while being completely unusable.

**Why this is a silent killer**: The eval loop catches many problems, but only during skill creation. Once the skill is packaged and running in production, every invocation that produces broken output goes undetected unless the user opens the file. A validator script inside the skill catches these failures at generation time, not just during eval.

**Fix**: Add a "Verify and Fix" step as the final workflow step in the skill:
1. Bundle a `scripts/validate_*.py` that checks key invariants after generation (font names, color values, schema requirements, section count, link integrity, etc.)
2. Add explicit verification instructions in SKILL.md: what to check, what to fix if wrong
3. For visual output: export thumbnails and verify against the visual spec checklist
4. Require at least one pass of verification before declaring success

**How to spot it**: The skill's last workflow step is "save the file" or "report the output path", with no verification or self-review. The skill's verification consists only of checking whether a file exists and has non-zero size.

### Undocumented Patterns (Implementation Without Spec)

**Problem**: The skill defines named layout patterns (card grids, step lists, two-column panels) as Python functions in `scripts/`, but there's no per-pattern spec in `references/`. The coordinates and font sizes exist only in code — numbers like `left=Inches(0.42)` or `Pt(20)` with no documented ground truth.

**Why this fails**: When a reviewer reads `Pt(20)` in a generation script, there's no way to know if 20pt is correct or if it drifted from the original 28pt. Each time the pattern is rebuilt or adapted, the author uses the code as a reference — and slightly wrong code becomes the new source of truth. After three iterations, titles are 20pt, leads are 10pt, and the output looks noticeably worse than the reference with no single commit to blame.

**Real-world example**: A PPTX skill built with 8 layout patterns had titles hardcoded at 20pt and lead text at 13pt because those were the values in the initial generation script. The reference design used 28pt titles and 20pt leads. The 30% font size gap degraded visual quality significantly — but there was no spec to compare against, so it went undetected across 15 eval runs.

**What's missing**: Each named pattern should have a spec in `references/pattern-specs.md` with:
- ASCII diagram of the layout zones with approximate dimensions
- Shape table: name, x, y, w, h, fill color, font pt, bold flag, purpose (extracted from reference slides)
- Font hierarchy: which role uses which size/weight/color
- Dynamic sizing rules: which dimensions are fixed vs computed from content count

**Fix**: Use `agents/asset-extractor.md`'s Step 3.5 (Pattern Decomposition) to extract per-shape coordinates from the reference slides programmatically. This produces verifiable numbers — not estimates — directly from the source material. When reference slides aren't available, reverse-engineer the table from the generation script's constants and document them in `references/`.

**How to spot it**: The skill has `scripts/patterns.py` (or equivalent) with multiple layout functions, but `references/` only contains global design tokens (`visual-spec.md`) with no per-pattern shape tables.

### Statistical Typography (Counts Without Zones)

**Problem**: The asset extractor reports "12pt used 244 times, 14pt used 17 times, Meiryo UI 382 times" — but the generation script has no idea which zone should use which size. A title placeholder gets 12pt because 12 is the most common size. A card header gets 14pt because that was in the examples. But the relationship between zone and style was never established.

**Why this fails**: Typography statistics tell you what values exist; they don't tell you which zone uses which value. A 14pt card header on a dark background has completely different visual weight than 14pt body text on white. When generation code assigns styles statistically rather than zone-specifically, the output has the right font and roughly the right sizes but the wrong emphases — titles look like body text, headers look like captions.

**Symptoms**:
- `visual-spec.md` documents font sizes with counts ("244 uses of 12pt") but no mapping to zones
- Generation scripts use a single font size for all text boxes in a pattern, rather than per-element sizes
- Output has correct font name but noticeably different weight/hierarchy from reference

**Fix**: Use `agents/asset-extractor.md`'s Steps 5 (zone-to-style mapping) and 3.5 (pattern decomposition) to build a **zone-style table** that maps each functional zone to its exact style:
```
| Zone              | bg fill  | font      | pt  | bold | color   |
|------------------|----------|-----------|-----|------|---------|
| Title placeholder | NONE     | Meiryo UI | 13  | T    | #333333 |
| Card header       | 7E00FF   | Meiryo UI | 16  | T    | #FFFFFF |
| Body content      | NONE     | Meiryo UI | 12  | F    | #333333 |
```
The generation script then applies styles per-zone, not statistically.

**How to spot it**: `visual-spec.md` has a "Font sizes" section with usage counts but no per-zone mapping. The extracted shape table in `references/pattern-specs.md` has blank or missing `pt` values.

---

### Phantom Decorations (Adding Fills to No-Fill Zones)

**Problem**: The generation code adds background fills (colored rectangles, panel backgrounds) to zones that are plain transparent text areas in the reference. The most common case: a "breadcrumb" or "header label" zone is transparent in the reference, but the generation script renders a purple bar behind it because "the header area should look accented."

**Why this is hard to catch**: The text content is correct. The eval passes ("slide contains the word '会社概要'"). But visually, the output has an extra element that doesn't belong, making it look cluttered or wrong.

**Root cause**: Extraction recorded what fills are present in the reference, but didn't explicitly record which zones have NO fill. Without an explicit "this zone is transparent" statement in the spec, the generation code fills in the gap with decoration that seems plausible but wasn't there.

**Fix**: In `references/visual-spec.md` and pattern specs, **always explicitly record fill=NONE for transparent zones**. Never leave the fill column blank — blank is ambiguous. An explicit `NONE` in the spec becomes a constraint: generation code must not add a fill to that zone. Capture this in `critical_findings`:
```json
"NO-FILL ZONES: breadcrumb (idx=11), title (idx=0), lead (idx=10), footer (idx=20) — DO NOT add filled rectangles behind these zones"
```

**How to spot it**: The generated output has decorative elements (bars, panels, backgrounds) that don't appear in the reference slides. The pattern specs in `references/` have a blank or absent fill column for text zones.

---

### Rhythm-Free Spacing (Positions Without Padding)

**Problem**: The spec captures shape positions (x, y, w, h) but not internal text margins, paragraph spacing, or line height. The generation code sets the same coordinates as the reference, but the text inside looks more cramped or more spacious because the internal padding is wrong.

**Why this matters**: Two text boxes at identical x/y/w/h coordinates can look very different if one has 0pt internal margin and the other has 14pt left margin. The whitespace rhythm — the breathing room around text — is a key part of what makes professional documents feel "premium" vs "dense."

**Symptoms**: Coordinates match the reference exactly, but text feels cramped or over-padded. Labels that should feel generous and legible feel tight. Body text that should feel light and scannable feels dense.

**Fix**: In `agents/asset-extractor.md` Step 6 (internal spacing extraction), capture `text_frame.margin_left`, `text_frame.margin_top`, paragraph `space_before/after`, and `line_spacing`. Include non-default values in the pattern spec's "Spacing notes" section. Generation code should then set these values explicitly rather than relying on defaults.

**How to spot it**: Pattern specs have x/y/w/h columns but no spacing notes. Generated text areas look slightly off despite correct dimensions.

---

### One-Shot Agent for Simple Logic

**Problem**: A subagent is created for something that's just a 20-line function — overhead without benefit.

**Fix**: Only use agents for tasks that benefit from isolated context. Simple logic belongs in a script.

---

## Complete Exemplar: slide-deck

This is a Tier 3 skill that generates PowerPoint presentations. It demonstrates proper infrastructure for a file-generation skill.

### Directory Structure
```
slide-deck/
├── SKILL.md              ← Workflow: understand → plan → generate → iterate
├── scripts/
│   └── create_pptx.py    ← SlideBuilder class with 13 slide types (~555 lines)
└── references/
    └── design-system.md  ← Color palette, typography, layout specs, slide type reference
```

### Why Each Component Exists

| Component | Why it exists | What would happen without it |
|-----------|--------------|------------------------------|
| `scripts/create_pptx.py` | Deterministic PPTX generation with consistent design | Every invocation writes a different script, inconsistent quality, wastes 2-3 minutes per run |
| `references/design-system.md` | Defines the exact visual language (colors, fonts, spacing) | Claude guesses at design tokens, every deck looks different |
| SKILL.md workflow | Guides Claude through content→plan→generate→iterate | Claude skips planning, jumps to generation, misses slide types |

### How SKILL.md References Infrastructure

```markdown
## Workflow
### 3. Generate the PPTX
Write a Python script that imports the bundled `SlideBuilder`:
\```python
from create_pptx import SlideBuilder
sb = SlideBuilder("output.pptx")
sb.add_title("Headline", subtitle="Sub")
sb.save()
\```

## Available Slide Types
| Type | Method | Best for |
|------|--------|----------|
| title | add_title(headline, subtitle, description) | Cover slide |
| stats | add_stats(headline, stats, bottom_text) | Impressive numbers |
...

For detailed parameter shapes and design specs, read `references/design-system.md`.
```

### What Makes This Exemplar Good

1. **Script as API**: `SlideBuilder` is a class with clear methods, not a CLI. SKILL.md shows exactly how to use it.
2. **Design system extracted**: Colors, fonts, and layout rules are in a reference doc, not scattered through SKILL.md.
3. **Slide type table in SKILL.md**: Quick reference for the most common decision (which slide type to use).
4. **Progressive disclosure**: SKILL.md has the workflow and method signatures. The reference doc has the deep detail.
5. **Clear iteration path**: "After generating, offer to adjust specific slides" — the skill anticipates the edit loop.

---

## Tier Examples

### Tier 1 — Instructions Only
**Commit message formatter**: Takes a diff and produces a conventional commit message. Pure prompt engineering — no files to generate, no domain specs, no subtasks.
```
commit-formatter/
└── SKILL.md
```

### Tier 2 — With References
**API documentation writer**: Generates API docs from code. Needs style guide and template structure as reference, but the actual writing is Claude's job.
```
api-docs/
├── SKILL.md
└── references/
    ├── style-guide.md
    └── template-structure.md
```

### Tier 3 — With Scripts + References
**Slide deck generator**: Produces PPTX files with consistent design. Needs a generation script (deterministic layout) and design system reference.
```
slide-deck/
├── SKILL.md
├── scripts/
│   └── create_pptx.py
└── references/
    └── design-system.md
```

**Data dashboard builder**: Produces HTML dashboards from CSV data. Needs a chart generation script, HTML template, and styling reference.
```
dashboard/
├── SKILL.md
├── scripts/
│   └── build_dashboard.py
├── references/
│   └── chart-types.md
└── assets/
    └── dashboard-template.html
```

### Tier 4 — Full Infrastructure
**Full-stack app generator**: Scaffolds applications with multiple framework options, testing, and deployment. Needs scripts for scaffolding, variant-specific references, a review agent, and starter templates.
```
app-scaffold/
├── SKILL.md
├── scripts/
│   ├── scaffold.py
│   └── validate_structure.py
├── references/
│   ├── react.md
│   ├── vue.md
│   ├── common-patterns.md
│   └── testing-guide.md
├── agents/
│   └── structure-reviewer.md
└── assets/
    ├── templates/
    │   ├── react-starter/
    │   └── vue-starter/
    └── configs/
        ├── eslint.json
        └── tsconfig.json
```
