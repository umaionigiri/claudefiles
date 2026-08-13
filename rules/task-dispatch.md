# Task Dispatch Rules

Analyze every prompt → select execution mode.

## Phase 0: Research & Reuse (Mandatory before any new implementation)

Adopted from Everything Claude Code (`development-workflow.md`). Run this **before** scoring complexity.

| Step | Tool / source | When |
|------|---------------|------|
| 1. GitHub code search | `gh search repos` / `gh search code` | First — find existing implementations, templates, patterns |
| 2. Library docs | Context7 (`resolve-library-id` → `query-docs`) or vendor docs | Confirm API behavior, version-specific details |
| 3. Package registries | npm, PyPI, crates.io | Before writing utility code — prefer battle-tested libraries |
| 4. Broader web research | Exa / Gemini MCP | Only if steps 1-3 are insufficient |

**Rule of thumb**: prefer adopting/porting a proven approach over net-new code when it meets requirements. Three similar lines is fine; three similar libraries is wasteful.

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
| 3+ | **Agent Teams** | 複数 `Agent` 並列起動 + `SendMessage` + 共有タスクリスト（`TaskCreate`/`TaskList`）|

## Delegation Monitoring — MANDATORY

委譲したら必ず `/loop` で完了まで監視する。対象は次の2形態、どちらも監視必須:

1. **バックグラウンド SubAgent** — `Agent(run_in_background: true)` で起動したエージェント
2. **teammate 協調** — 複数 `Agent` 並列 + `SendMessage` + 共有タスクリスト（`TaskCreate`/`TaskList`）へ差配したチーム

### 手順
1. 委譲を実行（バックグラウンド `Agent` 起動 / teammate へ差配）
2. **直後に** `/loop 1分ごとに各エージェント／teammate の状況をチェックして。` を実行
3. 各ループで確認する対象:
   - `TaskList` の各タスクのステータス
   - バックグラウンド `Agent` の完了通知
   - teammate からの `SendMessage` 報告
4. 全タスクが completed になったらループを停止する（`/loop` を止める）

### 賢く運用するための注意
- バックグラウンド `Agent` は harness が追跡し、完了時に自動で再呼び出しされる。したがって 1分ポーリングの主目的は「取りこぼし防止」ではなく **進捗の可視化とハング（無反応）検知**。
- 停止済み・完了済みタスクを延々ポーリングし続けない。全 completed を確認したら速やかにループを止める。

## Multi-File Implementation Pattern — MANDATORY

When a task involves **3+ independent file edits** (no shared state between files):

1. **Dependency graph first**: draw or list which tasks block which before touching any file
2. **Batch A** = all leaf tasks (no dependencies) → launch as parallel `Agent` calls in ONE message
3. **Batch B** = tasks that need Batch A done → run after all Batch A agents complete
4. **Batch C** = tasks that need Batch B done → run after all Batch B agents complete
5. **Never** edit files sequentially when they are independent — always parallelize

```
GOOD: 4 independent file edits → 1 message with 4 Agent tool calls (all run at once)
BAD:  4 independent file edits → 4 sequential Edit calls (wastes 3x the time)
```

Each agent prompt must be self-contained (no conversation history access) and include:
- Exact file path
- Current content or key sections (copy from Read output)
- Exact changes to make
- No ambiguity — the agent cannot ask follow-up questions

## SubAgent Best Practices
- Use `model: "haiku"` for research, `"sonnet"` for moderate tasks (see `performance.md` for the model selection table)
- Max 3-5 parallel agents
- Include all context in prompt (no conversation history access)
- Available types: `general-purpose`, `Explore` (read-only), `Plan` (no edits)

## Agent Teams Best Practices
- Team size: 3-5 teammates with `model: "sonnet"`
- 5-6 tasks per teammate
- Never assign same file to multiple teammates
- Use `SendMessage` (not `broadcast`) for corrections
- 片付けは不要ペインを tmux kill-pane で（専用のチーム一括作成/削除ツールはこの環境に無い。協調は複数 `Agent` 起動 + `SendMessage` + `TaskCreate`/`TaskList` で構成する）

## Team Patterns

| Pattern | Composition | Use Case |
|---------|-------------|----------|
| Parallel Review | Security + Perf + Test | PR/design review |
| SDLC Pipeline | PM → Architect → Dev → QA | Feature build |
| Competing Hypotheses | Investigator A + B + C | Complex debugging |
| Estimation | Technical + Benchmark + Risk | Project estimation |

## Task → Agent Mapping

For *which specific agent* to dispatch given a task type, see `agents.md`. This file decides the *mode*, that one decides the *cast*.

## Checklist
- [ ] Phase 0 (Research & Reuse) attempted before deciding to write new code
- [ ] Score calculated, mode selected
- [ ] Tasks decomposed with clear boundaries
- [ ] No file overlap between parallel agents
- [ ] Dependencies defined (blockedBy)
- [ ] All tasks marked completed when done
