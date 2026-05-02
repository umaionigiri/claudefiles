# Global Claude Code Settings

## Core Philosophy
1. **Agent-First** — Delegate complex/parallelizable work to subagents (`Agent` tool); keep main context lean
2. **Plan-First** — Plan Mode (Shift+Tab×2) before destructive or multi-file work
3. **Research-First** — Verify with Context7/Gemini before coding; trust your training data less than current docs
4. **Test-Behavior** — Test what users observe, not implementation internals
5. **Security-Always** — No secrets in code/logs; validate input at boundaries

## Task Management — MOST VIOLATED RULE
- On every prompt: analyze complexity → choose execution mode (Direct / SubAgent / Agent Teams)
- 3+ steps → TaskCreate/TaskUpdate/TaskList for visible progress tracking
- → See `rules/task-dispatch.md` for dispatch criteria

## Repo Layout (`~/.claude/`)
- `CLAUDE.md` — this file (always loaded, keep short)
- `rules/*.md` — long/topic-specific rules referenced from here (see Modular Rules below)
- `skills/<name>/SKILL.md` — invocable workflows (`Skill` tool)
- `agents/<name>.md` — subagent definitions (`Agent` tool, see Subagents below)
- `commands/<name>.md` — user-defined slash commands
- `memory/MEMORY.md` + `memory/*.md` — auto memory (managed by system)
- `plugins/` — installed plugins (managed by `/plugin`)
- `scripts/` — `generate-dashboard.mjs` (regen dashboard.html), `auto-sync.sh` (config Git sync)
- `settings.json` — permissions (156 allow rules) + 5種 hooks: `SessionStart` (git fetch/同期チェック), `PreToolUse:Bash` (危険コマンド検知), `PostToolUse:Write|Edit|MultiEdit` (auto-sync 起動), `Stop` (完了通知), `Notification` (通知整形)

## Modular Rules (`~/.claude/rules/`)
| Rule | Purpose |
|------|---------|
| `task-dispatch.md` | Complexity score → execution mode (Direct/SubAgent/Team) |
| `pre-commit.md` | Pre-commit checklist (tests/lint/secrets/debug code) |
| `code-quality.md` | Naming, function size, error handling, comments |
| `security.md` | Secrets, input validation, auth/authorization |
| `smoke-test.md` | Step-by-step confirmation for high-impact tasks |
| `naming.md` | Directory/file naming conventions |
| `version-check.md` | Session-start version diff vs latest Claude Code |

## Subagents (`~/.claude/agents/`)
| Agent | Use when |
|-------|----------|
| `task-decomposer` | Breaking large tasks into parallel subtasks |
| `code-reviewer` | Quality review of staged/unstaged changes |
| `senior-consultant-reviewer` | Senior-level architectural/strategic review |
| `test-runner` | Running test suites, interpreting failures |
| `devops-problem-solver` | Build/deploy/infra failures |
| `estimation-agent` | Effort/cost estimation for proposed work |
| `workflow-recorder` | Capture multi-step workflow as a trace |

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
1. **Research with MCP** before coding — Library API docs: `Context7` (`resolve-library-id` → `query-docs`) / External research: `Gemini` / Code analysis: `Serena` / GitHub: `GitHub MCP` / Azure: `Azure MCP` / Browser: `Playwright`
2. **Existing patterns**: Grep/Glob で既存実装を確認
3. **Impact analysis**: 影響範囲（ファイル/モジュール）を特定

## Workflow Principles
- **No direct work on main**: All changes via feature/topic branches
- **Worktree required**: `git worktree add .git/worktrees/<name> <branch>`
- **Plugin install via `/plugin`** (not `claude plugin install` CLI directly): UIから入れて `/reload-plugins` で反映
- **No over-engineering**: Implement only what's requested. Don't create files/docs unless explicitly asked
- **Respect existing patterns**: Follow project's code style and architecture
- **Confirm destructive operations**: Always ask before force push, reset --hard
- **Root cause first**: エラーは naive retry/bypass せず原因究明

## Quick Commands
```bash
node ~/.claude/scripts/generate-dashboard.mjs        # config変更後、ダッシュボード再生成
bash ~/.claude/scripts/auto-sync.sh                  # 設定変更を Git 同期
find ~/.claude/skills -maxdepth 2 -name SKILL.md     # スキル一覧
find ~/.claude/agents -maxdepth 1 -name '*.md'       # subagent 一覧
```

## Slash Commands
**Built-in:** `/plugin`, `/reload-plugins`, `/compact <focus>`, `/fork`, `/clear`, `/context`, `/effort low|med|high`, `/init`, `/rename`, `/rewind` (=Esc×2)
**User-defined (`~/.claude/commands/`):** `/create-pr`, `/slash-guide`, `/learn` (skill化), `/kiro:*` (spec-init, spec-design, spec-impl, validate-* など)
**Plugin-provided:** `/revise-claude-md` (claude-md-management)

## Context Management

| Task Type | Strategy |
|-----------|----------|
| Large exploration | SubAgent delegation; summary only to parent |
| Multiple approaches | `/fork` to branch session |
| Long implementation | `/compact <focus>` at ~60%; Plan Mode first |
| Quick fix | Direct execution |
| Code review | SubAgent with read-only tools |
| Unrelated follow-up | `/clear` then start fresh |

**Session naming:** `/rename` with `<action>-<target>` format (15-20 chars)
**Compact preserves:** task goal/progress, modified files, unresolved issues, user preferences, architecture decisions

## Privacy & Secrets (highlights)
- **Never paste secrets** (API keys/tokens/passwords/JWTs) — neither in code, logs, commits, nor chat
- Redact before sharing tool output; check `git diff --staged` before commit
- → Full rules: `rules/security.md`

## Knowledge Capture — Where Does What Go?
| Knowledge type | Destination |
|----------------|-------------|
| User identity, preferences, role | `~/.claude/memory/` (auto memory) |
| Long-term project facts (deadlines, ownership) | `memory/` project entries |
| Code patterns, architecture | The code itself + project's docs |
| Universal rules across all projects | `~/.claude/CLAUDE.md` (this file) |
| Topic-specific long rules | `~/.claude/rules/<topic>.md` |
| Reusable workflows | `~/.claude/skills/<name>/SKILL.md` |
| One-off task progress | TaskCreate (not memory) |

Do not duplicate. If the project already documents it, link don't restate.

## Tips (non-obvious)
- **`#` キー** — 任意のメッセージを CLAUDE.md / memory に永続化する quick capture
- **`/btw`** — メイン文脈を汚さない横道質問
- **`/rewind`** = `Esc×2`（直近の状態に戻す）
- **Plan Mode** = `Shift+Tab×2`
- **auto-sync** は `PostToolUse:Write|Edit|MultiEdit` hook で自動起動（手動 `bash auto-sync.sh` 不要）
- **`/plugin install` CLI 直叩きは罠** — `installLocation` がOS間でズレる。必ず `/plugin` UI 経由で

## Smoke Test for Large Tasks
- For high-impact / multi-step / hard-to-revert tasks (3+ chained ops, formatted Office files, prod folders, external systems), pause between logical steps and confirm with `AskUserQuestion` before proceeding
- Single-file edits and read-only work are exempt
- → See `rules/smoke-test.md`

## Success Criteria
A task is "done" when: tests pass · lint/type clean · `git diff --staged` shows only intended changes · no secrets · root cause addressed (not bypassed) · user requirement met as worded.

## Config Self-Improvement — EVALUATE ON EVERY PROMPT
1. Should this instruction become a permanent rule? → Add to appropriate config
2. Existing rule conflict or duplicate? → Update/consolidate
3. Decision tree: hooks (enforced) → CLAUDE.md (short, always) → rules/ (long/path-specific) → skills/ (workflow) → agents/ (isolated)
4. After config change → `node ~/.claude/scripts/generate-dashboard.mjs`
