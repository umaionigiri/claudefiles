# Global Claude Code Settings

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
2. **Existing patterns**: Use Grep/Glob to check existing implementation patterns in the project
3. **Impact analysis**: Identify affected files/modules before making changes

## Pre-Commit Checklist
- Tests pass (`npm test` / `pytest` / project-specific command)
- Lint/type checks pass
- `git diff --staged` confirms only intended changes
- No secrets (.env, credentials) included

## MCP Tool Selection
| Purpose | Tool | Use Case |
|---------|------|----------|
| Library API reference | Context7 | Latest docs before implementation |
| External research | Gemini | Best practices, tech comparison, trend analysis |
| Code analysis | Serena | Symbol search, dependency analysis, refactor impact |
| GitHub operations | GitHub MCP | PR creation, issue management, code search |
| Azure operations | Azure MCP | Resource management, documentation reference |
| Browser automation | Playwright | E2E testing, web scraping |

## Workflow Principles
- **No direct work on main**: All changes via feature/topic branches; main updated only through approved PR merges
- **Worktree required**: Use `git worktree add` for branch isolation. Create under `.git/worktrees/` (e.g., `git worktree add .git/worktrees/<name> <branch>`)
- **No over-engineering**: Implement only what's requested; no "just in case" features
- **Respect existing patterns**: Follow the project's code style and architecture
- **Confirm destructive operations**: Always ask before force push, reset --hard, etc.

## Context Management

Before starting any task, analyze the request and propose the optimal strategy:

| Task Type | Recommended Strategy |
|-----------|---------------------|
| Large exploration (many files) | Delegate to subagents; only summary enters parent context |
| Multiple approaches to try | `/fork` to branch session, compare results |
| Long implementation | `/compact <focus>` proactively at ~60%; Plan Mode first |
| Quick fix / small change | Direct execution, no special management needed |
| Code review / investigation | Subagent with read-only tools |
| Unrelated follow-up task | `/clear` then start fresh |

Techniques:
- **Subagent delegation**: Research/exploration in isolated context; parent receives summary only
- **`/compact <focus>`**: Proactive compression with explicit preservation instructions
- **`/rewind` (Esc×2)**: "Conversation only" resets context keeping code; "Summarize from here" for partial compaction
- **`/fork`**: Branch session for alternative approaches without polluting main session
- **`/btw`**: Side questions with zero context cost (not stored in history)
- **Plan Mode (Shift+Tab×2)**: Read-only exploration before implementation
- **`/context`**: Monitor token usage periodically

## Session Naming
- Rename sessions with `/rename` to reflect the task (15-20 chars)
- Update the name as the task evolves
- Format: `<action>-<target>` (e.g., "設定最適化-CLAUDE.md", "API実装-認証機能")
- Rename at: session start, major task change, or when scope becomes clear

## Compact Instructions
Preserve on compaction:
- Current task goal and progress
- Modified file paths with change summaries
- Unresolved issues and blockers
- User's explicit preferences
- Architecture decisions with reasoning

## Task Management
- 3+ steps → Use TaskCreate/TaskUpdate/TaskList to track progress visibly
- Independent tasks → Launch SubAgents in parallel (Agent tool with run_in_background)
- Always update task status: pending → in_progress → completed
- After completing a task, check TaskList for next available work

## Important Reminders
- Do not create files or generate documentation unless explicitly asked
- Test behavior, not implementation details
- Investigate root causes on errors; avoid naive retries or bypasses

## Config Self-Improvement
On every user prompt, silently evaluate:
1. Is the user giving an instruction that should become a permanent rule? → Add to appropriate config file
2. Does an existing rule conflict with or duplicate this request? → Update/consolidate
3. Where does it belong? Use this decision tree:
   - Mechanically enforced, no exceptions → `settings.json` hooks
   - Always apply, short → `CLAUDE.md`
   - Always apply, long → `.claude/rules/*.md` (no paths)
   - File-type specific → `.claude/rules/*.md` (with paths frontmatter)
   - Multi-step workflow with checklist → `skills/`
   - Needs tool restrictions or isolated context → `agents/`
4. After adding/updating config, run `node ~/.claude/scripts/generate-dashboard.mjs` to sync
