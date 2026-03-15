# Task Dispatch Rules

Analyze every prompt → select execution mode.

## Complexity Score

| Signal | Score |
|--------|-------|
| Single file, simple change | 0 |
| Multiple files or research needed | +1 |
| Multiple independent subtasks | +2 |
| Cross-cutting concerns (security + perf + design) | +2 |
| Multi-phase workflow or debate needed | +3 |

## Execution Mode

| Score | Mode | Action |
|-------|------|--------|
| 0 | **Direct** | Execute immediately |
| 1-2 | **SubAgents** | `Agent(run_in_background: true)` parallel |
| 3+ | **Agent Teams** | `TeamCreate` → shared task list |

## SubAgent Best Practices
- Use `model: "haiku"` for research, `"sonnet"` for moderate tasks
- Max 3-5 parallel agents
- Include all context in prompt (no conversation history access)
- Available types: `general-purpose`, `Explore` (read-only), `Plan` (no edits)

## Agent Teams Best Practices
- Team size: 3-5 teammates with `model: "sonnet"`
- 5-6 tasks per teammate
- Never assign same file to multiple teammates
- Use `SendMessage` (not `broadcast`) for corrections
- Clean up with `TeamDelete` promptly

## Team Patterns

| Pattern | Composition | Use Case |
|---------|-------------|----------|
| Parallel Review | Security + Perf + Test | PR/design review |
| SDLC Pipeline | PM → Architect → Dev → QA | Feature build |
| Competing Hypotheses | Investigator A + B + C | Complex debugging |
| Estimation | Technical + Benchmark + Risk | Project estimation |

## Checklist
- [ ] Score calculated, mode selected
- [ ] Tasks decomposed with clear boundaries
- [ ] No file overlap between parallel agents
- [ ] Dependencies defined (blockedBy)
- [ ] All tasks marked completed when done
