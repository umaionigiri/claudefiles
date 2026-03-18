"""
check_completeness.py — Validate a skill directory for production-readiness.

Checks (in order):
  0.  SKILL.md frontmatter — name: and description: both required, description value non-empty (FAIL)
  1.  File-producing skills must have scripts/ with at least one .py file
  1b. Copy-paste documentation smell (WARN — boilerplate belongs in scripts/)
  2.  Evals defined — evals.json must have expectations strings (WARN if missing)
  3.  SKILL.md length ≤ 500 lines (WARN if exceeded)
  4.  File-producing skills should have a references/ directory (WARN if absent)
  5.  Orphaned references — SKILL.md mentions files that don't exist (WARN per file)
      Detects both backtick-quoted paths and markdown link [text](path) format.
  6.  Visual reproduction skill has assets/reference/ and references/visual-spec.md
  7.  evals.json schema validation — id, prompt, no duplicate IDs, expectations[] are
      strings not graded objects (FAIL per error)
  8.  evals.json skill_name matches SKILL.md frontmatter name (WARN if mismatch)
  9.  Python script syntax — ast.parse() all .py files (FAIL per syntax error)
  10. scripts/ present but missing __init__.py — python -m scripts.x imports fail (WARN)
  11. evals.json eval_name is a non-string when present (FAIL — violates schema contract, causes unexpected directory names)
  12. File-producing skill has no validate_*.py — cannot detect broken output at generation time (WARN)
  13. evals.json files[] lists files that don't exist in the skill directory (WARN per file)
  14. Windows-incompatible patterns in Python scripts — nohup, lsof, /dev/null,
      select.select on pipes, os.fork, os.mkfifo, signal.SIGKILL (WARN per pattern found)
  15. evals.json has fewer than 5 evals — statistically unreliable results (WARN)

Optional --check-grading <workspace-path>:
  Scans the workspace's iteration-*/eval-*/grading.json files and verifies:
  - All assertions have been graded (no passed=null)
  - All expectations have the correct field names {text, passed, evidence}
  - passed values are boolean true/false (not null, string, or number)
  This check cannot be done from the skill directory alone because grading.json
  files live in the workspace, not the skill directory.

Usage:
    python -m scripts.check_completeness <skill-path>
    python scripts/check_completeness.py <skill-path>
    python -m scripts.check_completeness <skill-path> --check-grading <workspace-path>

Exit codes:
    0 — all checks PASS (WARNs are acceptable)
    1 — one or more FAILs
"""

import sys
import os
import json
import re
import glob


# ── Keywords that indicate a skill produces files ─────────────────────────────
FILE_PRODUCING_KEYWORDS = [
    r"\bpptx\b", r"\bpowerpoint\b", r"\bhtml\b", r"\bpdf\b", r"\bdocx\b",
    r"\bword document\b", r"\bspreadsheet\b", r"\bexcel\b", r"\bcsv\b",
    r"\bimage\b", r"\bpng\b", r"\bjpeg\b", r"\bsvg\b",
    r"\bgenerate[s]?\b", r"\bcreate[s]? (?:a |an )?file\b",
    r"\boutput file\b", r"\bsave[s]? (?:a |the )?file\b",
    r"\breport\b", r"\bdeck\b", r"\bslide\b", r"\bpresentation\b",
    r"\bdashboard\b", r"\bnotebook\b",
]

# ── Keywords that indicate a skill is doing visual reproduction ────────────────
# IMPORTANT: These are checked against the frontmatter DESCRIPTION only (not the full body).
# Checking the full body causes false positives on skills that DOCUMENT the visual
# reproduction pattern (like skill-maker itself) without BEING visual reproduction skills.
# A skill's description captures its INTENT; the body may reference patterns as documentation.
VISUAL_REPRODUCTION_KEYWORDS = [
    r"visual reproduction",    # explicit phrase
    r"faithfully reproduc",    # "faithfully reproduce/reproduces"
    r"match the original",
    r"reproduce.*style",
    r"reproduce.*format",
    r"reproduce.*design",
]

# ── Output symbols ─────────────────────────────────────────────────────────────
PASS_SYM = "[PASS] "
FAIL_SYM = "[FAIL] "
WARN_SYM = "[WARN] "


def _read_skill_md(skill_path: str) -> str:
    """Read SKILL.md content; return empty string if missing."""
    path = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _extract_description(skill_md: str) -> str:
    """Extract the frontmatter description field from SKILL.md.

    Handles both single-line descriptions and YAML block scalars (|, >, |-, >-).
    Bug fix: previously returned the raw indicator character ("|") for block scalars,
    causing _is_file_producing and _is_visual_reproduction to silently miss matches
    on skills with multiline descriptions.
    """
    fm_match = re.match(r"^---\s*\n(.*?)\n---", skill_md, re.DOTALL)
    if not fm_match:
        return ""
    frontmatter = fm_match.group(1)
    # Extract description value (single-line or quoted)
    desc_match = re.search(r'^description\s*:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    if not desc_match:
        return ""

    value = desc_match.group(1).strip()

    # Handle YAML block scalar indicators (|, >, |-, >-).
    # These mean the actual content follows as indented continuation lines.
    # Without this handling, _is_file_producing / _is_visual_reproduction would check
    # the literal "|" character instead of the description text and silently return False.
    if value in ("|", ">", "|-", ">-"):
        fm_lines = frontmatter.split("\n")
        desc_line_idx = None
        for i, line in enumerate(fm_lines):
            if re.match(r'^description\s*:', line):
                desc_line_idx = i
                break
        if desc_line_idx is None:
            return ""
        content_lines = []
        for line in fm_lines[desc_line_idx + 1:]:
            if line.startswith("  ") or line.startswith("\t"):
                content_lines.append(line.strip())
            else:
                break  # End of block scalar content
        return " ".join(content_lines).lower()

    return value.lower()


def _is_file_producing(skill_md: str) -> bool:
    """
    Return True if the skill's frontmatter description indicates it produces files.
    We check the description (not the full body) to avoid false positives from
    skills that merely discuss file generation as a concept.
    """
    description = _extract_description(skill_md)
    if not description:
        # Fallback: check first 50 lines of body (after frontmatter) only
        lines = skill_md.splitlines()
        # Find end of frontmatter
        in_fm = False
        body_start = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if not in_fm:
                    in_fm = True
                else:
                    body_start = i + 1
                    break
        # Check first 50 body lines only
        body_sample = "\n".join(lines[body_start:body_start + 50]).lower()
        description = body_sample

    for pattern in FILE_PRODUCING_KEYWORDS:
        if re.search(pattern, description):
            return True
    return False


def _count_python_files(skill_path: str) -> int:
    """Count .py files in scripts/ (excluding __init__.py)."""
    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return 0
    py_files = [
        f for f in os.listdir(scripts_dir)
        if f.endswith(".py") and f != "__init__.py"
    ]
    return len(py_files)


def _count_skill_md_lines(skill_md: str) -> int:
    return len(skill_md.splitlines())


def _check_evals(skill_path: str) -> tuple[bool, int, int, bool]:
    """
    Check evals/evals.json for defined expectations.
    Returns (exists, no_expectations_count, total_evals, parse_error).

    evals.json stores expectations as plain strings (not graded objects).
    This check verifies that assertions are *defined*, not that they have been *graded*.
    Grading results live in grading.json inside the eval workspace and cannot be
    verified from the skill directory alone — grading verification is a manual step.

    NOTE: evals.json uses the field name 'expectations' (list of strings).
    eval_metadata.json uses 'assertions' (also strings) — same concept, different file.
    grading.json uses 'expectations' again but as [{text, passed, evidence}] objects.
    Do not confuse these three; they share names but differ in structure and location.

    parse_error=True means the file exists but could not be parsed — the caller must
    surface this as FAIL. Returning (True, 0, 0, False) would silently pass all
    evals checks as if the file had no evals, masking a corrupt file.
    """
    evals_path = os.path.join(skill_path, "evals", "evals.json")
    if not os.path.isfile(evals_path):
        return False, 0, 0, False
    try:
        with open(evals_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return True, 0, 0, True
    except OSError:
        return True, 0, 0, True

    no_expectations_count = 0
    total_evals = 0
    evals = data.get("evals", [])
    for ev in evals:
        total_evals += 1
        # evals.json uses "expectations" (list of strings) — NOT "assertions"
        expectations = ev.get("expectations", [])
        if not expectations:
            no_expectations_count += 1
    return True, no_expectations_count, total_evals, False


def _check_references(skill_path: str) -> bool:
    """Return True if references/ directory exists with at least one .md file."""
    refs_dir = os.path.join(skill_path, "references")
    if not os.path.isdir(refs_dir):
        return False
    md_files = [f for f in os.listdir(refs_dir) if f.endswith(".md")]
    return len(md_files) > 0


def _check_orphaned_references(skill_path: str, skill_md: str) -> list[str]:
    """
    Find files mentioned in SKILL.md that don't exist.
    Detects two formats:
      - Backtick-quoted paths: `references/foo.md`
      - Markdown link paths:   [text](references/foo.md)
    Returns list of missing file paths.
    """
    # Backtick-quoted paths: `references/foo.md`, `scripts/bar.py`, etc.
    backtick_pattern = r"`((?:references|scripts|agents|assets)/[^`\s]+)`"
    # Markdown link paths: [text](references/foo.md) — also covers evals/ references
    link_pattern = r"\[[^\]]*\]\(((?:references|scripts|agents|assets|evals)/[^)#\s]+)\)"
    mentioned = set(re.findall(backtick_pattern, skill_md))
    mentioned.update(re.findall(link_pattern, skill_md))
    missing = []
    for rel_path in sorted(mentioned):
        full_path = os.path.join(skill_path, rel_path)
        if not os.path.exists(full_path):
            missing.append(rel_path)
    return missing


def _is_visual_reproduction(skill_md: str) -> bool:
    """
    Return True if this skill is a visual reproduction skill — i.e., it was built
    to faithfully reproduce the visual design of reference binary files.

    We check the frontmatter DESCRIPTION only (not the full body). This avoids
    false positives on skills that *document* the visual reproduction pattern
    (such as skill-maker itself) without actually being visual reproduction skills.
    A skill's description captures its intent; the body may reference patterns
    as instructional documentation rather than as an indication of what the skill does.
    """
    description = _extract_description(skill_md)
    if not description:
        return False
    for pattern in VISUAL_REPRODUCTION_KEYWORDS:
        if re.search(pattern, description):
            return True
    return False


def _check_visual_reproduction_assets(skill_path: str) -> tuple[bool, bool]:
    """
    Check that a visual reproduction skill has its required asset structure.
    Returns (has_reference_dir_with_files, has_visual_spec).
    """
    ref_dir = os.path.join(skill_path, "assets", "reference")
    has_reference_files = False
    if os.path.isdir(ref_dir):
        entries = [f for f in os.listdir(ref_dir) if not f.startswith(".")]
        has_reference_files = len(entries) > 0

    visual_spec = os.path.join(skill_path, "references", "visual-spec.md")
    has_visual_spec = os.path.isfile(visual_spec)

    return has_reference_files, has_visual_spec


def _check_copy_paste_smell(skill_md: str) -> bool:
    """
    Return True if SKILL.md has copy-paste documentation smell:
    phrases that suggest users should copy code rather than import it.
    """
    smell_patterns = [
        r"copy into every generation script",
        r"copy.{0,20}boilerplate",
        r"paste.{0,30}script",
        r"step 1.*boilerplate",
    ]
    text = skill_md.lower()
    for p in smell_patterns:
        if re.search(p, text):
            return True
    return False


def _check_evals_schema(skill_path: str) -> list[str]:
    """
    Validate evals/evals.json for structural correctness (schema consistency).
    Returns list of error descriptions (empty = OK).
    Checks: valid JSON, skill_name present, evals array present,
    each eval has id + prompt, no duplicate ids.
    Missing evals.json is handled by Check 2; this function only validates structure.
    """
    evals_path = os.path.join(skill_path, "evals", "evals.json")
    if not os.path.isfile(evals_path):
        return []

    try:
        with open(evals_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"evals/evals.json is not valid JSON: {e}"]
    except OSError:
        return []

    if not isinstance(data, dict):
        return ["evals/evals.json must be a JSON object, not a list or primitive."]

    errors = []

    if "skill_name" not in data:
        errors.append("evals/evals.json is missing required field 'skill_name'.")

    evals = data.get("evals")
    if evals is None:
        errors.append("evals/evals.json is missing required field 'evals'.")
        return errors

    if not isinstance(evals, list):
        errors.append("evals/evals.json field 'evals' must be an array.")
        return errors

    seen_ids: set = set()
    for i, ev in enumerate(evals):
        if not isinstance(ev, dict):
            errors.append(f"evals/evals.json evals[{i}] is not a JSON object.")
            continue
        if "id" not in ev:
            errors.append(f"evals/evals.json evals[{i}] is missing required field 'id'.")
        else:
            ev_id = ev["id"]
            if ev_id in seen_ids:
                errors.append(
                    f"evals/evals.json has duplicate eval id '{ev_id}' — "
                    f"duplicate ids cause silent data loss in benchmark aggregation."
                )
            seen_ids.add(ev_id)
        if "prompt" not in ev:
            errors.append(f"evals/evals.json evals[{i}] is missing required field 'prompt'.")

        # eval_name, when present, must be a string (not an int or other type).
        # A non-string eval_name causes unexpected directory names and confuses the
        # benchmark aggregator (e.g., eval_name: 1 produces "eval-1" instead of "eval-myname").
        eval_name = ev.get("eval_name")
        if eval_name is not None and not isinstance(eval_name, str):
            errors.append(
                f"evals/evals.json evals[{i}].eval_name must be a string "
                f"(got {type(eval_name).__name__}: {eval_name!r}). "
                f"Use a kebab-case string like 'basic-transform' — "
                f"it becomes the eval directory name (e.g., eval-basic-transform/)."
            )

        # evals.json expectations[] must be plain strings — NOT graded objects.
        # A common mistake is accidentally writing {text, passed, evidence} objects here
        # (which belong in grading.json). The grader receives expectation strings and
        # converts them to graded objects; pre-graded objects in evals.json skip grading silently.
        expectations = ev.get("expectations")
        if expectations is not None:
            if not isinstance(expectations, list):
                errors.append(
                    f"evals/evals.json evals[{i}].expectations must be an array of strings, "
                    f"got {type(expectations).__name__}."
                )
            else:
                for j, exp in enumerate(expectations):
                    if not isinstance(exp, str):
                        errors.append(
                            f"evals/evals.json evals[{i}].expectations[{j}] must be a plain "
                            f"string (not {type(exp).__name__}). "
                            f"Write assertion text directly (e.g., \"Output contains X\") — "
                            f"graded objects {{\"text\": ..., \"passed\": ..., \"evidence\": ...}} "
                            f"belong in grading.json, not evals.json."
                        )

    return errors


def _check_evals_skill_name(skill_path: str, skill_md: str) -> str | None:
    """
    Check that evals/evals.json skill_name matches SKILL.md frontmatter name.
    Returns a warning message string or None if OK / not applicable.
    Naming drift is a low-priority but common mistake when skills are renamed.
    """
    evals_path = os.path.join(skill_path, "evals", "evals.json")
    if not os.path.isfile(evals_path):
        return None

    # Extract name from frontmatter
    fm_match = re.match(r"^---\s*\n(.*?)\n---", skill_md, re.DOTALL)
    if not fm_match:
        return None
    name_match = re.search(r"^name\s*:\s*['\"]?([^'\"\n]+)['\"]?\s*$", fm_match.group(1), re.MULTILINE)
    if not name_match:
        return None
    skill_name = name_match.group(1).strip()

    try:
        with open(evals_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    evals_name = str(data.get("skill_name", "")).strip()
    if evals_name and evals_name != skill_name:
        return (
            f"evals/evals.json skill_name '{evals_name}' does not match "
            f"SKILL.md frontmatter name '{skill_name}'. "
            f"Update evals/evals.json to keep them in sync."
        )
    return None


def _check_script_syntax(skill_path: str) -> list[str]:
    """
    Parse Python scripts in scripts/ with ast to detect syntax errors before packaging.
    Returns list of error descriptions (empty = OK).
    Skips __init__.py.
    """
    import ast

    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return []

    errors = []
    for fname in sorted(os.listdir(scripts_dir)):
        if not fname.endswith(".py") or fname == "__init__.py":
            continue
        fpath = os.path.join(scripts_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                source = f.read()
            ast.parse(source, filename=fpath)
        except SyntaxError as e:
            errors.append(
                f"scripts/{fname} has a syntax error at line {e.lineno}: {e.msg}. "
                f"Fix before packaging — this script will fail on import."
            )
        except OSError:
            pass

    return errors


def _check_scripts_init(skill_path: str) -> str | None:
    """
    Return a warning if scripts/ has .py files but no __init__.py.

    Without __init__.py, 'python -m scripts.module_name' fails with ModuleNotFoundError.
    Skills that bundle generation scripts must be importable as a package so SKILL.md
    examples like 'from scripts.create_pptx import SlideBuilder' work correctly.
    """
    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return None
    py_files = [
        f for f in os.listdir(scripts_dir)
        if f.endswith(".py") and f != "__init__.py"
    ]
    if not py_files:
        return None
    init_path = os.path.join(scripts_dir, "__init__.py")
    if not os.path.isfile(init_path):
        return (
            "scripts/ has .py files but no __init__.py. "
            "Without it, 'python -m scripts.module_name' fails with ModuleNotFoundError "
            "and 'from scripts.module import func' is broken. "
            "Create an empty scripts/__init__.py to make the directory a package."
        )
    return None


def _check_validate_script(skill_path: str) -> str | None:
    """
    Return a warning if a file-producing skill has no validate_*.py in scripts/.

    Without programmatic validation, Claude cannot detect broken output (wrong colors,
    invisible text, missing sections) at generation time — it declares success based
    on file existence alone. reviewer.md flags this as INF-VER-001 (major);
    this check provides the same detection earlier in the automated pipeline.

    A file-size check does NOT count as validation — it confirms a file was written,
    not that its content is correct.
    """
    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return None
    validate_files = [
        f for f in os.listdir(scripts_dir)
        if f.startswith("validate_") and f.endswith(".py")
    ]
    if not validate_files:
        return (
            "File-producing skill has no validate_*.py script in scripts/. "
            "Without it, Claude cannot detect structurally broken output "
            "(wrong colors, invisible text, missing sections) at generation time — "
            "it checks only that a file was written, not that its content is correct. "
            "Add a scripts/validate_*.py that verifies key output invariants after generation."
        )
    return None


def _check_eval_files(skill_path: str) -> list[str]:
    """
    Check that files listed in evals.json files[] actually exist.
    Returns list of missing file paths (relative to skill root).

    Missing eval input files cause eval runs to silently fail or produce wrong
    outputs that pass anyway (the skill runs without the intended input).
    This check catches the gap between evals.json being written and the actual
    test fixtures being created.
    """
    evals_path = os.path.join(skill_path, "evals", "evals.json")
    if not os.path.isfile(evals_path):
        return []
    try:
        with open(evals_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    missing = []
    for ev in data.get("evals", []):
        for file_ref in ev.get("files", []):
            full_path = os.path.join(skill_path, file_ref)
            if not os.path.exists(full_path):
                missing.append(file_ref)
    return missing


def _strip_tokens(source: str, token_types: set) -> str:
    """
    Replace the text of specified token types with spaces (preserving newlines).

    token_types: set of tokenize token type constants (e.g. {tokenize.COMMENT,
    tokenize.STRING}).  Used to avoid false positives when a pattern keyword
    appears only in documentation, not in executable code.

    Falls back to the original source on tokenization error.
    """
    import io
    import tokenize as _tokenize

    try:
        lines = source.splitlines(keepends=True)
        line_start = [0]
        for ln in lines:
            line_start.append(line_start[-1] + len(ln))

        result = list(source)
        tokens = _tokenize.generate_tokens(io.StringIO(source).readline)
        for tok_type, _tok_str, (srow, scol), (erow, ecol), _ in tokens:
            if tok_type not in token_types:
                continue
            abs_start = line_start[srow - 1] + scol
            abs_end = line_start[erow - 1] + ecol
            for i in range(abs_start, min(abs_end, len(result))):
                if result[i] != "\n":
                    result[i] = " "
        return "".join(result)
    except _tokenize.TokenError:
        return source


def _check_windows_compat(skill_path: str) -> list[str]:
    """
    Scan Python scripts in scripts/ for Windows-incompatible patterns.

    Skills must run on Windows (the user's platform). These patterns work on
    Unix/macOS but silently fail or crash on Windows:
    - nohup / lsof           — command not found on Windows
    - /dev/null              — use os.devnull for cross-platform
    - select.select on pipes — fails on non-socket fds on Windows (use threading+queue)
    - os.fork()              — not available on Windows
    - os.mkfifo()            — not available on Windows
    - signal.SIGKILL         — not available on Windows (use SIGTERM or process.kill())

    Patterns are split into two groups:
    - IDENTIFIER_PATTERNS: identifier/attribute/call expressions that appear in code
      (not string args). These are checked on comment-stripped source to avoid
      false positives when a pattern name appears only in a comment.
    - STRING_PATTERNS: command strings passed to subprocess calls (e.g. "nohup").
      These must be matched against the raw source because the bad usage IS inside
      a string literal. False positives from documentation strings are accepted for
      these patterns — they are rare in practice.

    Returns list of warning messages, one per distinct pattern violation per file.
    """
    # Matched against comment-stripped source (the bad usage is in code, not strings).
    IDENTIFIER_PATTERNS = [
        (r'select\.select\b',  "select.select() on non-socket file descriptors fails on Windows; use threading + queue.Queue instead"),
        (r'os\.fork\(\)',      "os.fork() is not available on Windows; use subprocess or multiprocessing instead"),
        (r'os\.mkfifo\(',      "os.mkfifo() is not available on Windows; use a temp file or socket instead"),
        (r'signal\.SIGKILL\b', "signal.SIGKILL is not available on Windows; use process.kill() or signal.SIGTERM instead"),
    ]
    # Matched against raw source (the bad usage IS inside string arguments to subprocess).
    STRING_PATTERNS = [
        (r'\bnohup\b',               "nohup is not available on Windows; spawn detached processes with Popen(creationflags=0x08000000) instead"),
        (r'\blsof\b',                "lsof is not available on Windows; use psutil or skip the check"),
        (r"['\"]\/dev\/null['\"]",   "/dev/null is not available on Windows; use os.devnull for cross-platform compatibility"),
    ]

    scripts_dir = os.path.join(skill_path, "scripts")
    if not os.path.isdir(scripts_dir):
        return []

    import tokenize as _tok

    warnings = []
    for fname in sorted(os.listdir(scripts_dir)):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(scripts_dir, fname)
        try:
            source = open(fpath, encoding="utf-8").read()
        except OSError:
            continue
        # IDENTIFIER_PATTERNS: the bad usage is code (attribute access, function call).
        # Strip both strings and comments so the patterns don't fire on documentation.
        code_only = _strip_tokens(source, {_tok.STRING, _tok.COMMENT})
        for pattern, explanation in IDENTIFIER_PATTERNS:
            if re.search(pattern, code_only):
                warnings.append(f"scripts/{fname} uses a Windows-incompatible pattern: {explanation}.")
        # STRING_PATTERNS: the bad usage IS inside a string arg to subprocess.
        # Strip comments only (preserve string content so we can detect "nohup", lsof, etc.).
        comment_stripped = _strip_tokens(source, {_tok.COMMENT})
        for pattern, explanation in STRING_PATTERNS:
            if re.search(pattern, comment_stripped):
                warnings.append(f"scripts/{fname} uses a Windows-incompatible pattern: {explanation}.")
    return warnings


def _rel(path: str, base: str) -> str:
    """Return path relative to base, for display purposes."""
    try:
        return os.path.relpath(path, base)
    except ValueError:
        return path


def _check_grading(workspace_path: str) -> tuple[list[str], list[str]]:
    """
    Scan a skill creation workspace for grading.json files and verify that all
    assertions have been graded (passed = true or false, not null).

    Looks for grading.json in all known config-directory locations:
      with_skill/  (standard — skill being evaluated)
      without_skill/  (baseline for new-skill runs)
      old_skill/  (baseline for improvement runs)
      Each config can use flat layout (grading.json directly in config dir) or
      multi-run layout (grading.json inside run-N/ subdirs).

    Returns (fails, warns).

    grading.json uses field name 'expectations' with objects {text, passed, evidence}.
    A 'passed: null' value means the assertion was defined but the grader never ran —
    the eval should be treated as incomplete and not counted toward pass rate thresholds.
    """
    workspace_path = os.path.expanduser(workspace_path)
    if not os.path.isdir(workspace_path):
        return [f"Workspace path not found: {workspace_path}"], []

    fails = []
    warns = []

    # Search all known config-directory / layout combinations:
    #   with_skill/    — the skill being evaluated (all run types)
    #   without_skill/ — baseline for new-skill runs
    #   old_skill/     — baseline for improvement runs (eval-workflow.md Step 1)
    # For each, support both flat layout (grading.json directly in config dir)
    # and multi-run layout (grading.json inside run-N/ subdirs).
    # Missing old_skill/ grading silently underrepresents baseline coverage in the benchmark.
    grading_files = (
        glob.glob(os.path.join(workspace_path, "iteration-*", "eval-*", "with_skill", "grading.json"))
        + glob.glob(os.path.join(workspace_path, "iteration-*", "eval-*", "without_skill", "grading.json"))
        + glob.glob(os.path.join(workspace_path, "iteration-*", "eval-*", "old_skill", "grading.json"))
        + glob.glob(os.path.join(workspace_path, "iteration-*", "eval-*", "with_skill", "run-*", "grading.json"))
        + glob.glob(os.path.join(workspace_path, "iteration-*", "eval-*", "without_skill", "run-*", "grading.json"))
        + glob.glob(os.path.join(workspace_path, "iteration-*", "eval-*", "old_skill", "run-*", "grading.json"))
    )

    if not grading_files:
        warns.append(
            "No grading.json files found in workspace — evals have not been run yet. "
            "Run the eval pipeline (see references/eval-workflow.md) before packaging."
        )
        return fails, warns

    null_count_total = 0
    field_error_total = 0
    null_locations: list[str] = []
    field_error_locations: list[str] = []
    empty_locations: list[str] = []

    for gpath in sorted(grading_files):
        rel = _rel(gpath, workspace_path)
        try:
            with open(gpath, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            warns.append(f"{rel}: invalid JSON ({e}) — cannot verify grading status.")
            continue
        except OSError:
            warns.append(f"{rel}: could not read file.")
            continue

        expectations = data.get("expectations", [])
        if not expectations:
            empty_locations.append(rel)
            continue

        null_in_file = 0
        field_errors_in_file: list[str] = []
        for i, e in enumerate(expectations):
            if not isinstance(e, dict):
                field_errors_in_file.append(
                    f"expectations[{i}] is {type(e).__name__}, expected object"
                )
                continue
            # Field name contract: ONLY {text, passed, evidence} are valid.
            # name/met/verified/details etc. silently break the eval viewer and aggregator.
            bad_fields = [f for f in ("text", "passed", "evidence") if f not in e]
            if bad_fields:
                field_errors_in_file.append(
                    f"expectations[{i}] missing required fields {bad_fields} "
                    f"— only {{text, passed, evidence}} are valid"
                )
            # passed must be a bool — null means ungraded, string/number means wrong type
            passed_val = e.get("passed")
            if passed_val is None:
                null_in_file += 1
            elif not isinstance(passed_val, bool):
                field_errors_in_file.append(
                    f"expectations[{i}].passed={passed_val!r} ({type(passed_val).__name__}) "
                    f"— must be true/false bool, never a string or number"
                )

        if null_in_file > 0:
            null_count_total += null_in_file
            null_locations.append(
                f"{rel}: {null_in_file}/{len(expectations)} assertions ungraded (passed=null)"
            )
        if field_errors_in_file:
            field_error_total += len(field_errors_in_file)
            field_error_locations.append(
                f"{rel}:\n    " + "\n    ".join(field_errors_in_file)
            )

    if null_locations:
        fails.append(
            f"{null_count_total} ungraded assertion(s) (passed=null) across "
            f"{len(null_locations)} grading file(s). "
            "Ungraded evals must be run before packaging — "
            "they count as failures against the ≥75% pass rate threshold:\n  "
            + "\n  ".join(null_locations)
        )

    if field_error_locations:
        fails.append(
            f"{field_error_total} field name error(s) across {len(field_error_locations)} grading file(s). "
            "The eval viewer and aggregate_benchmark.py read ONLY {{text, passed, evidence}} — "
            "any other field names silently produce blank or zero results:\n  "
            + "\n  ".join(field_error_locations)
        )

    if empty_locations:
        warns.append(
            f"{len(empty_locations)} grading.json file(s) have an empty 'expectations' array "
            "(grader ran but produced no verdicts):\n  "
            + "\n  ".join(empty_locations)
        )

    return fails, warns


def run_checks(skill_path: str) -> tuple[list[str], list[str], int]:
    """
    Run all checks against the skill at skill_path.
    Returns (fails, warns, exit_code).
    """
    skill_path = os.path.expanduser(skill_path)
    fails = []
    warns = []

    # ── Read SKILL.md ──────────────────────────────────────────────────────────
    skill_md = _read_skill_md(skill_path)
    if not skill_md:
        fails.append("SKILL.md not found — is this a valid skill directory?")
        return fails, warns, 1

    # ── Check 0: SKILL.md frontmatter validation ───────────────────────────────
    # Both 'name' and 'description' are required. Missing description means the
    # skill never triggers (no signal for Claude to act on). Missing name breaks
    # evals.json consistency checks and package_skill.py validation.
    fm_match = re.match(r"^---\s*\n(.*?)\n---", skill_md, re.DOTALL)
    if not fm_match:
        fails.append(
            "SKILL.md is missing YAML frontmatter (--- ... ---). "
            "Add 'name:' and 'description:' fields between '---' delimiters "
            "at the top of the file — without them the skill cannot be loaded."
        )
    else:
        fm = fm_match.group(1)
        if not re.search(r"^name\s*:", fm, re.MULTILINE):
            fails.append(
                "SKILL.md frontmatter is missing required field 'name:'. "
                "Add 'name: <skill-name>' — this is the identifier used for "
                "evals.json consistency checks and package_skill.py."
            )
        if not re.search(r"^description\s*:", fm, re.MULTILINE):
            fails.append(
                "SKILL.md frontmatter is missing required field 'description:'. "
                "Add 'description: <when to use, what it does>' — this is the "
                "primary signal Claude uses to decide whether to invoke the skill. "
                "Without it the skill will never trigger."
            )
        else:
            desc_value = _extract_description(skill_md)
            if not desc_value:
                fails.append(
                    "SKILL.md frontmatter 'description:' key is present but the value is empty. "
                    "Add a meaningful description explaining when to use this skill and what it does — "
                    "an empty description means the skill will never trigger."
                )

    # ── Check 1: File-producing → scripts/ required ────────────────────────────
    file_producing = _is_file_producing(skill_md)
    if file_producing:
        py_count = _count_python_files(skill_path)
        if py_count == 0:
            # Show hint keywords from the same scope _is_file_producing() searched
            # (description, or first 50 body lines) — not the full document — to avoid
            # showing misleading keywords from deep in the SKILL.md body.
            hint_scope = _extract_description(skill_md)
            if not hint_scope:
                lines = skill_md.splitlines()
                in_fm = False
                body_start = 0
                for i, line in enumerate(lines):
                    if line.strip() == "---":
                        if not in_fm:
                            in_fm = True
                        else:
                            body_start = i + 1
                            break
                hint_scope = "\n".join(lines[body_start:body_start + 50]).lower()
            triggered = [
                kw.strip(r"\b")
                for kw in FILE_PRODUCING_KEYWORDS
                if re.search(kw, hint_scope)
            ][:3]
            kw_hint = ", ".join(triggered) if triggered else "(file-producing keywords)"
            fails.append(
                f"Skill appears to produce files (keywords: {kw_hint}) "
                f"but scripts/ has no .py files. "
                f"Bundle the generation logic as an importable module."
            )
        else:
            pass  # OK

        # ── Check 1b: Copy-paste smell ─────────────────────────────────────────
        if _check_copy_paste_smell(skill_md):
            warns.append(
                "SKILL.md contains copy-paste documentation patterns "
                "(e.g. 'copy into every generation script'). "
                "Consider moving this code into scripts/ as an importable module."
            )

    # ── Check 2: Evals defined ────────────────────────────────────────────────

    # Verifies that expectations are *defined* in evals.json.
    # Cannot verify grading status (grading.json lives in the workspace, not skill dir).
    evals_exist, no_expectations_count, total, evals_parse_error = _check_evals(skill_path)
    if not evals_exist:
        warns.append(
            "evals/evals.json not found. "
            "Consider adding test cases to verify the skill works reliably."
        )
    elif evals_parse_error:
        fails.append(
            "evals/evals.json exists but cannot be parsed as valid JSON. "
            "Fix the syntax error — a malformed file silently disables all evals checks "
            "and will cause eval pipeline scripts to crash at runtime."
        )
    elif no_expectations_count > 0:
        warns.append(
            f"{no_expectations_count}/{total} evals in evals.json have no expectations "
            f"defined. Add verifiable assertion strings before running the eval pipeline "
            f"— evals without expectations cannot be graded."
        )

    # ── Check 3: SKILL.md length ──────────────────────────────────────────────
    line_count = _count_skill_md_lines(skill_md)
    if line_count > 500:
        warns.append(
            f"SKILL.md is {line_count} lines (> 500 limit). "
            f"Move detailed specs into references/ to keep SKILL.md lean."
        )

    # ── Check 4: References directory for file-producing skills ──────────────
    if file_producing and not _check_references(skill_path):
        warns.append(
            "File-producing skill has no references/ directory. "
            "Consider adding a design-system.md or domain spec for consistent output."
        )

    # ── Check 5: Orphaned file references ────────────────────────────────────
    missing_refs = _check_orphaned_references(skill_path, skill_md)
    for ref in missing_refs:
        warns.append(f"SKILL.md mentions `{ref}` but the file does not exist.")

    # ── Check 6: Visual reproduction skill needs assets/reference/ and visual-spec.md ──
    if _is_visual_reproduction(skill_md):
        has_ref_files, has_visual_spec = _check_visual_reproduction_assets(skill_path)

        if not has_ref_files:
            fails.append(
                "Skill description indicates visual reproduction intent "
                "(matched: 'visual reproduction', 'faithfully reproduce', "
                "'match the original', 'reproduce.*style/format/design') "
                "but assets/reference/ is missing or empty. "
                "The original binary files must be preserved as ground truth — "
                "run agents/asset-extractor.md to copy them into assets/reference/ "
                "and extract the design system."
            )

        if not has_visual_spec:
            warns.append(
                "Visual reproduction skill is missing references/visual-spec.md "
                "(extracted color palette, typography, geometry). "
                "Scripts relying on guessed color values will drift from the original. "
                "Run agents/asset-extractor.md to generate this file."
            )

    # ── Check 7: evals.json schema validation (HIGH — schema inconsistency) ─────
    for err in _check_evals_schema(skill_path):
        fails.append(err)

    # ── Check 8: evals.json skill_name ↔ SKILL.md name (LOW — naming drift) ────
    name_mismatch = _check_evals_skill_name(skill_path, skill_md)
    if name_mismatch:
        warns.append(name_mismatch)

    # ── Check 9: Python script syntax (MEDIUM — functional, silent import fail) ─
    for err in _check_script_syntax(skill_path):
        fails.append(err)

    # ── Check 10: scripts/__init__.py missing (WARN — module imports fail) ───────
    init_warn = _check_scripts_init(skill_path)
    if init_warn:
        warns.append(init_warn)

    # ── Check 11: evals.json eval_name type (FAIL — non-string violates schema, causes wrong dir names) ─
    # Handled inside _check_evals_schema() — eval_name type errors are reported as FAILs
    # because they violate the schema contract, not just style.

    # ── Check 12: File-producing skill has no validate_*.py (WARN) ───────────────
    # reviewer.md flags this as INF-VER-001 (major); this provides automated early detection.
    if file_producing:
        validate_warn = _check_validate_script(skill_path)
        if validate_warn:
            warns.append(validate_warn)

    # ── Check 13: evals.json files[] existence (WARN) ────────────────────────────
    missing_eval_files = _check_eval_files(skill_path)
    for f in missing_eval_files:
        warns.append(
            f"evals.json references input file '{f}' but the file does not exist. "
            "Eval runs will silently run without this input, producing wrong or unreliable results."
        )

    # ── Check 14: Windows-incompatible patterns in Python scripts (WARN) ──────────
    # Skills must run cross-platform (Windows is the primary target environment).
    # Patterns like nohup, lsof, /dev/null, select.select on pipes crash silently on Windows.
    for w in _check_windows_compat(skill_path):
        warns.append(w)

    # ── Check 15: evals.json minimum eval count (WARN) ────────────────────────────
    # Fewer than 5 evals give statistically unreliable results — a single lucky or
    # unlucky run can swing pass rate by 20+pp. Aim for 10+ evals for stable signals.
    # Only applies when evals.json exists and parsed successfully (total > 0 means parse OK).
    if evals_exist and not evals_parse_error and total < 5:
        warns.append(
            f"evals/evals.json has only {total} eval(s). "
            "Fewer than 5 evals give statistically unreliable results — "
            "a single lucky run can swing pass rate by 20+ points. "
            "Aim for 10+ evals for stable quality signals."
        )

    exit_code = 1 if fails else 0
    return fails, warns, exit_code


def main(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]

    if not args:
        print("Usage: python -m scripts.check_completeness <skill-path>")
        print("       python scripts/check_completeness.py <skill-path>")
        print("       python -m scripts.check_completeness <skill-path> --check-grading <workspace-path>")
        return 2

    # Parse arguments
    skill_path: str | None = None
    workspace_path: str | None = None
    i = 0
    while i < len(args):
        if args[i] == "--check-grading" and i + 1 < len(args):
            workspace_path = args[i + 1]
            i += 2
        else:
            skill_path = args[i]
            i += 1

    if not skill_path:
        print("Error: skill-path is required.")
        return 2

    display_path = os.path.expanduser(skill_path)
    print(f"\nChecking skill: {display_path}\n")

    fails, warns, exit_code = run_checks(skill_path)

    # Optional grading check (requires workspace path)
    if workspace_path:
        display_ws = os.path.expanduser(workspace_path)
        print(f"Checking grading in: {display_ws}\n")
        g_fails, g_warns = _check_grading(workspace_path)
        fails.extend(g_fails)
        warns.extend(g_warns)
        if g_fails:
            exit_code = 1

    if not fails and not warns:
        print(f"{PASS_SYM}All checks passed.")
    else:
        for msg in fails:
            print(f"{FAIL_SYM}{msg}")
        for msg in warns:
            print(f"{WARN_SYM}{msg}")

    total_fails = len(fails)
    total_warns = len(warns)
    result_parts = []
    if total_fails:
        result_parts.append(f"{total_fails} FAIL")
    if total_warns:
        result_parts.append(f"{total_warns} WARN")
    if not result_parts:
        result_parts.append("all PASS")

    print(f"\nResult: {', '.join(result_parts)}")
    if total_fails:
        print("Fix FAIL items before packaging.")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
