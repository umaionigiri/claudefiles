# Agent Orchestration — Task → Agent Map

Adapted from Everything Claude Code. Complements `task-dispatch.md` (which decides *complexity → execution mode*); this file decides *task type → which specific agent*.

`~/.claude/agents/` holds **37 agents in two layers**. Pick the layer first, then the agent.

| Layer | Count | Frontmatter | Content | Dispatch when |
|-------|-------|-------------|---------|---------------|
| **Execution guides** (hand-written) | 17 | `tools:` + `model:` declared | Concrete CLI commands (`npm audit`, `knip`, `ruff`, `lighthouse`), phased checklists, output templates | You want work *performed and verified* — running tools, producing a report |
| **Personas** (SuperClaude v4.3.0) | 20 | `category:` only, no `tools:`/`model:` | Behavioral mindset, priority hierarchies, "Key Actions" prose | You want *thinking reframed* — design debate, exploration, teaching, requirements |

Neither layer supersedes the other. Names overlap; scope does not — see the split table below before assuming two agents are duplicates.

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

## Look-Alike Pairs — Which One To Call

These pairs share a topic but not a job. Reading the name alone will pick the wrong one.

| Topic | Execution guide (run tools, report findings) | Persona (reframe thinking, design, teach) |
|-------|----------------------------------------------|-------------------------------------------|
| Security | **security-reviewer** — runs `npm audit`, secret scan, OWASP checklist against existing code | **security-engineer** — threat modeling and compliance posture at design time |
| Performance | **performance-optimizer** — runs `lighthouse`, bundle analysis, `node --prof`, reports numbers | **performance-engineer** — decides *what* to measure and which bottleneck class to attack |
| Python | **python-reviewer** — reviews a diff with `ruff` / `mypy` / `bandit` | **python-expert** — writes new production Python (SOLID, typed, tested) |
| Refactoring | **refactor-cleaner** — removes dead code via `knip` / `depcheck` / `ts-prune`, classifies SAFE/CAREFUL/RISKY | **refactoring-expert** — restructures for SOLID and clean-code principles |
| DevOps | **devops-problem-solver** — diagnoses a failing build/deploy, 6-phase incident triage | **devops-architect** — designs IaC, CI/CD topology, observability |
| Quality | **code-reviewer** — reviews a diff, returns approve / warn / block | **quality-engineer** — designs the test strategy and coverage plan |
| Codebase map | **code-explorer** — traces one feature's execution path in depth | **repo-index** — generates a whole-repo briefing index |

Rule of thumb: **"go do it" → execution guide. "help me decide" → persona.**

## SuperClaude Personas With No Existing Counterpart

| Trigger | Agent |
|---------|-------|
| Vague idea needs to become a spec | **requirements-analyst** |
| Whole-system / long-horizon architecture call | **system-architect** |
| API, data integrity, fault tolerance design | **backend-architect** |
| UI component, accessibility, framework choice | **frontend-architect** |
| Bug with competing hypotheses, cause unclear | **root-cause-analyst** |
| Needs external research beyond the repo | **deep-research** / **deep-research-agent** (`/sc:research`) |
| Verify own implementation before calling it done | **self-review** |
| Write docs, API reference, user guide | **technical-writer** |
| Explain a concept / teach step by step | **learning-guide** (direct) / **socratic-mentor** (question-led) |
| Business strategy, market, positioning | **business-panel-experts** (`/sc:business-panel`) |
| Cross-session context + PDCA knowledge base | **pm-agent** (`/sc:pm`) |

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
- ❌ Picking between a look-alike pair by name similarity — check the split table; `security-engineer` will not run `npm audit` for you
- ❌ Dispatching a persona and expecting a tool-verified report — personas have no `tools:` declaration and no concrete commands; pair one with an execution guide when you need evidence
