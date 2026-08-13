# Agent Orchestration — Task → Agent Map

Adapted from Everything Claude Code. Complements `task-dispatch.md` (which decides *complexity → execution mode*); this file decides *task type → which specific agent*.

## Quick Decision Map

| Trigger | Agent | Why |
|---------|-------|-----|
| Complex feature request | **task-decomposer** → planner pattern | Break work into parallelizable subtasks |
| Just wrote/modified code | **code-reviewer** | Quality + security pass |
| Suspect security issue | **security-reviewer** | OWASP / secrets / auth deep dive |
| Database / SQL change | **database-reviewer** | PostgreSQL specialist (queries, RLS, indexes) |
| Performance complaint | **performance-optimizer** | Bundle, profiling, N+1, memory |
| Onboarding into legacy code | **code-explorer** | Trace execution paths, map architecture |
| PR review for test quality | **pr-test-analyzer** | Behavioral coverage, edge cases |
| Suspect silent failure | **silent-failure-hunter** | catch{}, null fallback, missing logs |
| Dead code suspected | **refactor-cleaner** | knip / depcheck / ts-prune driven cleanup |
| Architectural / strategic call | **senior-consultant-reviewer** | Senior-level review |
| TDD facilitation | **tdd-guide** | RED-GREEN-IMPROVE step-by-step |
| Build/CI failure | **devops-problem-solver** | Build/deploy/infra specialist |
| Effort estimation | **estimation-agent** | Effort / cost estimation |
| Capture multi-step workflow | **workflow-recorder** | Trace into reusable structure |

Python/TypeScript-specific (after Phase 2):

| Trigger | Agent |
|---------|-------|
| Python file changed | **python-reviewer** (after generic code-reviewer) |
| TypeScript file changed | **typescript-reviewer** (after generic code-reviewer) |

## Two-Stage Review Pattern

For language-specific changes:
```
Generic: code-reviewer  →  Specialist: python-reviewer / typescript-reviewer
```
Generic catches universal issues (security, large functions, unhandled errors).
Specialist catches language idioms (type safety, EAFP vs LBYL, strict null checks).

## Parallel vs Sequential

ALWAYS use parallel Task execution for independent operations:

```
GOOD: Launch 3 agents in parallel:
  1. security-reviewer on auth module
  2. performance-optimizer on cache system
  3. database-reviewer on query layer

BAD: Run them sequentially when there's no data dependency
```

See `task-dispatch.md` for parallel-vs-sequential decision criteria.

## Multi-Perspective Analysis

For complex problems, deploy a **team** with split roles:
- Factual reviewer (what does the code actually do?)
- Senior engineer (is the design right?)
- Security expert (what could break?)
- Consistency reviewer (does it match the rest of the codebase?)

Use multiple `Agent` calls + `SendMessage` + a shared task list (`TaskCreate`/`TaskList`) for this. See task-dispatch.md "Agent Teams Best Practices".

## Anti-Patterns

- ❌ Running every agent in sequence "just to be thorough" — runs up cost and noise
- ❌ Calling `code-reviewer` after every micro-edit — batch reviews at logical checkpoints
- ❌ Using `senior-consultant-reviewer` for routine code review — reserve for strategic decisions
- ❌ Skipping the specialist when the generic agent already raised a flag in its territory
