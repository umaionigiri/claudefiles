# Global Claude Code Settings

## Task Management — MOST VIOLATED RULE
- On every prompt: analyze complexity → choose execution mode (Direct / SubAgent / Agent Teams)
- 3+ steps → TaskCreate/TaskUpdate/TaskList for visible progress tracking
- → See `rules/task-dispatch.md` for dispatch criteria

## Language
- Always respond in Japanese (unless English is explicitly requested)
- Write code, comments, and documentation in English
- Use technical terms in their original form (e.g., API, Docker, Kubernetes)

## Response Style
- **Conclusion first**: Present the solution first, details later
- **Avoid code duplication**: Do not unnecessarily redisplay user-provided code
- **Concise and casual**: Skip excessive politeness and long introductions
- **Code references**: Use `file_path:line_number` format

## Pre-Implementation Steps
1. **Context7 API check**: Run `resolve-library-id` → `query-docs` when using frameworks/libraries
2. **Existing patterns**: Use Grep/Glob to check existing implementation patterns
3. **Impact analysis**: Identify affected files/modules before making changes

## MCP Tool Selection
| Purpose | Tool |
|---------|------|
| Library API docs | Context7 |
| External research | Gemini |
| Code analysis | Serena |
| GitHub operations | GitHub MCP |
| Azure operations | Azure MCP |
| Browser automation | Playwright |

## Workflow Principles
- **No direct work on main**: All changes via feature/topic branches
- **Worktree required**: `git worktree add .git/worktrees/<name> <branch>`
- **No over-engineering**: Implement only what's requested
- **Respect existing patterns**: Follow project's code style and architecture
- **Confirm destructive operations**: Always ask before force push, reset --hard

## Context Management

| Task Type | Strategy |
|-----------|----------|
| Large exploration | SubAgent delegation; summary only to parent |
| Multiple approaches | `/fork` to branch session |
| Long implementation | `/compact <focus>` at ~60%; Plan Mode first |
| Quick fix | Direct execution |
| Code review | SubAgent with read-only tools |
| Unrelated follow-up | `/clear` then start fresh |

Key techniques: `/compact`, `/rewind` (Esc×2), `/fork`, `/btw`, Plan Mode (Shift+Tab×2), `/context`

## Session Naming
- `/rename` with task-reflecting name (15-20 chars), format: `<action>-<target>`

## Compact Instructions
Preserve: task goal + progress, modified files, unresolved issues, user preferences, architecture decisions

## Pre-Commit
→ See `rules/pre-commit.md`

## Code Quality
→ See `rules/code-quality.md`

## Security
→ See `rules/security.md`

## Important Reminders
- Do not create files or generate documentation unless explicitly asked
- Test behavior, not implementation details
- Investigate root causes on errors; avoid naive retries or bypasses

## Config Self-Improvement — EVALUATE ON EVERY PROMPT
1. Should this instruction become a permanent rule? → Add to appropriate config
2. Existing rule conflict or duplicate? → Update/consolidate
3. Decision tree: hooks (enforced) → CLAUDE.md (short, always) → rules/ (long/path-specific) → skills/ (workflow) → agents/ (isolated)
4. After config change → `node ~/.claude/scripts/generate-dashboard.mjs`
