# Task Dispatch Rules

On every user prompt, analyze and select the optimal execution mode.

## Step 1: Complexity Analysis

Evaluate the prompt against these signals:

| Signal | Score |
|--------|-------|
| Single file change | +0 |
| Multiple files involved | +1 |
| Research/investigation needed | +1 |
| Multiple independent subtasks | +2 |
| Cross-cutting concerns (security + performance + design) | +2 |
| Multi-phase workflow (spec → design → implement → test) | +3 |
| Discussion/debate between perspectives needed | +3 |

## Step 2: Select Execution Mode

| Total Score | Mode | Action |
|-------------|------|--------|
| 0 | **Direct** | Execute immediately, no delegation |
| 1-2 | **SubAgents** | Delegate to background agents |
| 3+ | **Agent Teams** | Create team with shared task list |

## Step 3: Mode-Specific Patterns

### Direct Execution (Score 0)
- Simple questions, single-file edits, quick fixes
- No TaskCreate needed
- Execute and respond directly

### SubAgent Dispatch (Score 1-2)

**When to use:**
- Result only needed (no cross-agent discussion)
- Research / read-only exploration
- Parallel independent tasks that don't share state
- Cost-sensitive operations

**Pattern:**
1. TaskCreate for each subtask
2. Launch SubAgents with `run_in_background: true` for parallel work
3. Collect results, synthesize, respond
4. TaskUpdate to completed

**Best Practices:**
- Use `model: "haiku"` for simple research tasks
- Use `model: "sonnet"` for moderate complexity
- Keep SubAgent prompts focused and specific
- Include all necessary context in the prompt (SubAgents don't see conversation history unless using `subagent_type` with context access)
- Max 3-5 parallel SubAgents to avoid overwhelming

**Available SubAgent types:**
- `general-purpose` — Full tool access, any task
- `Explore` — Read-only, fast codebase exploration
- `Plan` — Architecture planning, no edits

### Agent Teams Dispatch (Score 3+)

**When to use:**
- Cross-agent discussion/debate needed
- Shared task list with dependencies
- Long-running multi-file implementation
- Multiple perspectives on same problem (competing hypotheses)
- Speed-sensitive large projects

**Pattern:**
1. `TeamCreate` with descriptive team name
2. `TaskCreate` for all tasks with dependency chains (`addBlockedBy`)
3. Launch teammates via `Agent` tool with `team_name` parameter
4. Assign tasks via `TaskUpdate` with `owner`
5. Monitor via `TaskList`, intervene via `SendMessage`
6. `SendMessage` type: "shutdown_request" when complete
7. `TeamDelete` to clean up

**Best Practices:**
- Team size: 3-5 teammates (more = coordination overhead)
- Use `model: "sonnet"` for teammates (cost/capability balance)
- 5-6 tasks per teammate for optimal productivity
- Never assign same file to multiple teammates (overwrite risk)
- Use `SendMessage` for course corrections, not `broadcast` (expensive)
- Clean up teams promptly to avoid idle token consumption

**Team Composition Patterns:**

| Pattern | Teammates | Use Case |
|---------|-----------|----------|
| Parallel Review | Security + Performance + Test Coverage | PR/design review |
| SDLC Pipeline | PM → Architect → Developer → QA | Feature implementation |
| Competing Hypotheses | Investigator A + B + C | Debugging complex issues |
| Estimation Team | Technical + Benchmark + Risk | Project estimation |

## Step 4: Execution Checklist

Before dispatching:
- [ ] Complexity score calculated
- [ ] Execution mode selected
- [ ] Tasks decomposed with clear boundaries
- [ ] No file overlap between parallel agents
- [ ] Dependencies defined (blockedBy)

During execution:
- [ ] TaskUpdate status kept current
- [ ] Progress monitored for stuck tasks
- [ ] Results synthesized as they arrive

After completion:
- [ ] All tasks marked completed
- [ ] Teams cleaned up (TeamDelete)
- [ ] Results summarized to user
