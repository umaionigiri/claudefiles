# Code Quality Rules

Always apply these rules when writing or reviewing code. Synthesizes ECC `code-review.md` and `coding-style.md` with the existing baseline.

## Core Principles (Adopted from ECC `coding-style.md`)

### Immutability (CRITICAL)

ALWAYS create new objects, NEVER mutate existing ones.
```
WRONG:  modify(original, field, value)        // mutates in place
RIGHT:  update(original, field, value)        // returns a new copy
```
Rationale: prevents hidden side effects, makes debugging easier, enables safe concurrency.

### KISS / DRY / YAGNI
- **KISS**: simplest solution that actually works; clarity over cleverness
- **DRY**: extract repeated logic only when repetition is real, not speculative
- **YAGNI**: don't build features or abstractions before they're needed

## Naming
- Meaningful, descriptive names
- Project conventions: `camelCase` for JS/TS, `snake_case` for Python
- Boolean variables: prefix with `is`/`has`/`can`/`should`
- Interfaces/types/components: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- React custom hooks: `camelCase` with `use` prefix

## Functions & Files
- **Single responsibility** per function
- **Function size**: <50 lines (extract if longer)
- **File size**: 200-400 lines typical, **800 max** — extract modules when larger
- **Nesting**: max 4 levels — use early returns
- **No magic numbers**: use named constants
- **Pure functions** preferred; minimize side effects

## Error Handling
- Handle errors at the appropriate level
- **Never** swallow exceptions silently
- Provide actionable error messages
- Log detailed context server-side; show user-friendly text in UI

## Comments
- Explain "why", not "what"
- Delete commented-out code (use git history instead)
- Japanese supplementary comments are acceptable

## Input Validation (System Boundaries)
- Validate all user input before processing
- Use schema-based validation (Zod / Pydantic) where available
- Fail fast with clear error messages
- Never trust external data: API responses, user input, file content

## Code Review — When to Trigger

Mandatory review triggers:
- After writing or modifying code
- Before any commit to shared branches
- When security-sensitive code changes (auth, payments, user data)
- Architectural changes
- Before merging PRs

Pre-review must-haves:
- All CI/CD checks passing
- Merge conflicts resolved
- Branch up-to-date with target

## Severity Levels (for review findings)

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Security vulnerability or data loss risk | **BLOCK** — must fix before merge |
| **HIGH** | Bug or significant quality issue | **WARN** — should fix before merge |
| **MEDIUM** | Maintainability concern | **INFO** — consider fixing |
| **LOW** | Style or minor suggestion | **NOTE** — optional |

Approve if no CRITICAL/HIGH; warning if HIGH only; block if CRITICAL.

## Specialist Agent Delegation (Stop and call when)

| Trigger | Agent |
|---------|-------|
| Auth / authorization / token handling | **security-reviewer** |
| User input handling, file ops, crypto | **security-reviewer** |
| Database queries / migrations | **database-reviewer** |
| Performance complaint / regression | **performance-optimizer** |
| Suspect silent failure (catch{}, null) | **silent-failure-hunter** |
| Dead code suspected | **refactor-cleaner** |
| Python file changed | **python-reviewer** (after generic) |
| TypeScript file changed | **typescript-reviewer** (after generic) |

See `agents.md` for the full task → agent map.

## Code Quality Checklist

Before marking work complete:
- [ ] Code is readable and well-named
- [ ] Functions are small (<50 lines)
- [ ] Files are focused (<800 lines)
- [ ] No deep nesting (>4 levels)
- [ ] Errors handled explicitly
- [ ] No hardcoded secrets / credentials
- [ ] No `console.log` / `print` / `debugger` statements
- [ ] Tests exist for new functionality
- [ ] Coverage ≥ 80%
- [ ] Immutable patterns used where possible
- [ ] No magic numbers
