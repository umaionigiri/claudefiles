---
description: Extract reusable patterns from the current session and save them as candidate skills.
---

# /learn — Extract Reusable Patterns

Analyze the current session and extract any patterns worth saving as skills.

## Trigger

Run `/learn` at any point during a session when you've solved a non-trivial problem.

## What to Extract

Look for:

1. **Error Resolution Patterns**
   - What error occurred?
   - What was the root cause?
   - What fixed it?
   - Is this reusable for similar errors?

2. **Debugging Techniques**
   - Non-obvious debugging steps
   - Tool combinations that worked
   - Diagnostic patterns

3. **Workarounds**
   - Library quirks
   - API limitations
   - Version-specific fixes

4. **Project-Specific Patterns**
   - Codebase conventions discovered
   - Architecture decisions made
   - Integration patterns

## Output Format

Create a skill file at `~/.claude/skills/learned/<pattern-name>/SKILL.md`:

```markdown
---
name: <pattern-name>
description: <one-line trigger description — used to decide when to auto-invoke>
---

# <Descriptive Pattern Name>

**Extracted:** <YYYY-MM-DD>
**Context:** <Brief description of when this applies>

## Problem
<What problem this solves — be specific>

## Solution
<The pattern/technique/workaround>

## Example
<Code example if applicable>

## When to Use
<Trigger conditions — what should activate this skill>
```

Use `kebab-case` for `<pattern-name>` (e.g., `wsl-path-mismatch-fix`, `gh-api-base64-decode`).

## Process

1. Review the session for extractable patterns
2. Identify the **single most valuable/reusable** insight (one skill per `/learn` invocation)
3. Draft the SKILL.md
4. **Ask user to confirm** before saving (show diff/path)
5. Save to `~/.claude/skills/learned/<pattern-name>/SKILL.md`
6. Remind user to run `/reload-plugins` if the skill should be invocable in the current session

## Don't Extract

- Typos or simple syntax errors
- One-time issues (specific API outages, expired credentials, etc.)
- Patterns already covered by an existing skill in `~/.claude/skills/`
- Project-specific knowledge that belongs in the project's CLAUDE.md instead

## Keep It Focused

- **One pattern per skill** — split if you find multiple
- **Trigger description must be specific** — vague descriptions cause skills to never fire
- **Include a runnable example** when possible — abstract advice is harder to apply
