# Global Claude Code Settings

## Core Philosophy
1. **Agent-First** — Delegate complex/parallelizable work to subagents (`Agent` tool) or teammates (複数 `Agent` 協調 + `SendMessage`); keep main context lean. **Default to teammates over solo SubAgent when work is multi-perspective, multi-phase, or benefits from cross-critique** (review、debug仮説競合、設計検討など)
2. **Plan-First** — Plan Mode (Shift+Tab×2) before destructive or multi-file work
3. **Research-First** — Verify with Context7/Gemini before coding; trust your training data less than current docs
4. **Test-Behavior** — Test what users observe, not implementation internals
5. **Security-Always** — No secrets in code/logs; validate input at boundaries

## Task Management — MOST VIOLATED RULE
- On every prompt: analyze complexity → choose execution mode (Direct / SubAgent / Agent Teams)
- **Bias toward Agent Teams** when 2つ以上当てはまる: ①multi-file 影響、②独立した観点（security / perf / test など）が並列、③仮説競合や設計議論が有益、④3+ subtask が独立並列可能。単発 SubAgent ではなく複数 `Agent` 協調（+ `SendMessage` + 共有タスクリスト）を選ぶ
- **【MUST】lead で抱え込まず、PM として適切な AGENT に差配する**: 案件作業は該当プロジェクトの PM エージェント（例: 各案件の `<project>-pm`）を起点にワーカーへ差配する
- 3+ steps → TaskCreate/TaskUpdate/TaskList for visible progress tracking
- **【MUST】エージェント／teammate へ委譲したら即座に `/loop` 監視を開始する**: `Agent(run_in_background: true)` でバックグラウンド委譲したとき、または複数 `Agent` 協調（teammate）へ差配したときは、直後に `/loop 1分ごとに各エージェント／teammate の状況をチェックして。` を実行し、全タスク完了までループ監視する。詳細 → `rules/task-dispatch.md`「Delegation Monitoring」
- → See `rules/task-dispatch.md` for dispatch criteria

## Repo Layout (`~/.claude/`)
- `CLAUDE.md` — this file (always loaded, keep short)
- `rules/*.md` — long/topic-specific rules referenced from here (see Modular Rules below)
- `skills/<name>/SKILL.md` — invocable workflows (`Skill` tool)
- `agents/<name>.md` — subagent definitions (`Agent` tool, see Subagents below)
- `commands/<name>.md` — user-defined slash commands; `commands/sc/*.md` — SuperClaude `/sc:` commands (do not hand-edit; regenerate with `superclaude update`)
- `memory/MEMORY.md` + `memory/*.md` — auto memory (managed by system)
- `plugins/` — installed plugins (managed by `/plugin`)
- `scripts/` — `generate-dashboard.mjs` (regen dashboard.html), `auto-sync.sh` (config Git sync)
- **SuperClaude Framework v4.3.0** — installed via `uv tool install SuperClaude` (isolated env; `pip3 --user` is blocked by PEP 668). Manage with `superclaude install|update|doctor|mcp`. Supplies `agents/` Layer 2, `commands/sc/`, and `rules/superclaude/`
- `settings.json` — permissions (177 allow rules) + 6種 hooks: `SessionStart` (git fetch/同期チェック), `PreToolUse` (危険コマンド検知), `PostToolUse:Write|Edit|MultiEdit` (auto-sync 起動), `Stop` (完了通知), `Notification` (通知整形), `PreCompact`

## Modular Rules (`~/.claude/rules/`)
| Rule | Purpose |
|------|---------|
| `task-dispatch.md` | Phase 0 Research & Reuse → Complexity score → execution mode → 委譲後の `/loop` 監視 |
| `agents.md` | Task type → which specific agent to dispatch (complements task-dispatch.md) |
| `pre-commit.md` | Pre-commit checklist (tests/lint/secrets/debug code) |
| `code-quality.md` | Immutability, KISS/DRY/YAGNI, naming, function/file size, error handling, severity levels |
| `security.md` | 8項目pre-commit、secret管理、auth、response protocol、common vulnerabilities |
| `testing.md` | TDD RED-GREEN-IMPROVE、AAA pattern、80%カバレッジ、descriptive test naming |
| `performance.md` | Model selection (Haiku/Sonnet/Opus)、Context window末尾20%回避、Extended Thinking予算 |
| `git-workflow.md` | Conventional Commits、PR履歴全体要約、forbidden ops、amend vs new commit |
| `smoke-test.md` | Step-by-step confirmation for high-impact tasks |
| `naming.md` | Directory/file naming conventions |
| `version-check.md` | Session-start version diff vs latest Claude Code |
| `python/*.md` | Python-specific extensions (coding-style, hooks, patterns, security, testing) |
| `excel-generation.md` | xlsxwriter必須・Meiryo UI 10.5・/tmp経由コピー・openpyxl読み直し検証 |
| `superclaude/*.md` | SuperClaude v4.3.0 の補完ドキュメント13点（下表）。**規範が競合したら常に上記の既存 rules/ を優先** |

### `rules/superclaude/` — 自動ロードしない。必要なときだけ Read する
全文比較の結果、既存 rules/ との**真の矛盾はゼロ**（重なる箇所は同じ内容の言い換え）。安心して参照してよいが、重複部分は既存 rules/ を正とする。既存に無い固有の価値は: フラグ体系（`FLAGS.md`）／経営思想家9人パネル／日付を必ず確認する Temporal Awareness／作業後の一時ファイル掃除／誇大表現の禁止／多ホップ調査の信頼度設計。
| File | 中身 | いつ読むか |
|------|------|-----------|
| `FLAGS.md` | 振る舞い切替フラグ一覧（`--think`/`--think-hard`/`--ultrathink`、`--uc` 圧縮、`--safe-mode`、`--delegate`、MCP 選択 `--c7`/`--seq`/`--serena` 等） | フラグを使う**前に必ず Read**。CLI スイッチではなく規約なので、この表を読み込まないとフラグは効かない |
| `RULES.md` | SuperClaude 版の行動規範（最大 16KB） | 既存 rules/ に無い観点が欲しいときだけ |
| `PRINCIPLES.md` | ソフトウェア工学の原則 | 設計判断の拠り所が欲しいとき |
| `MODE_Brainstorming.md` | 要求を対話で掘る心構え | 要件が曖昧 / `/sc:brainstorm` |
| `MODE_Introspection.md` | 自分の推論を点検する心構え | 判断を誤った / 振り返るとき |
| `MODE_Orchestration.md` | ツール選択の最適化 | どの MCP・ツールを使うか迷うとき |
| `MODE_Task_Management.md` | 階層タスク管理と記憶の持続 | 多段階で長い作業のとき |
| `MODE_Token_Efficiency.md` | 記号による圧縮表現 | 文脈が逼迫したとき |
| `MODE_DeepResearch.md` + `RESEARCH_CONFIG.md` | 深掘り調査の戦略と設定 | `/sc:research` を使うとき |
| `MODE_Business_Panel.md` + `BUSINESS_SYMBOLS.md` + `BUSINESS_PANEL_EXAMPLES.md` | 経営思想家パネルの進め方・記号・実例 | `/sc:business-panel` を使うとき |

## Subagents (`~/.claude/agents/`) — 37 agents in 2 layers

**Layer 1 — 実行手順書 (hand-written, 17).** `tools:`/`model:` declared, concrete CLI (`npm audit`/`knip`/`ruff`/`lighthouse`), phased checklists, output templates. Dispatch when work must be **performed and verified**.

| Agent | Use when |
|-------|----------|
| `task-decomposer` | Breaking large tasks into parallel subtasks |
| `code-reviewer` | General quality+security review (OWASP-aware, confidence-filtered) |
| `senior-consultant-reviewer` | Senior-level architectural/strategic review |
| `test-runner` | Running test suites, interpreting failures |
| `devops-problem-solver` | Build/deploy/infra failures |
| `estimation-agent` | Effort/cost estimation for proposed work |
| `workflow-recorder` | Capture multi-step workflow as a trace |
| `security-reviewer` | OWASP Top 10 / secrets / npm-audit deep dive |
| `database-reviewer` | PostgreSQL: query plan, RLS, index, N+1 |
| `performance-optimizer` | Bundle / Lighthouse / profiling / memory leak |
| `code-explorer` | Trace execution paths, map architecture (legacy onboarding) |
| `pr-test-analyzer` | PR-level behavioral coverage, edge case validation |
| `silent-failure-hunter` | catch{}, null fallback, missing-log detection |
| `refactor-cleaner` | knip/depcheck/ts-prune driven dead-code removal |
| `tdd-guide` | RED-GREEN-IMPROVE step-by-step facilitation |
| `python-reviewer` | Python idioms (after generic code-reviewer) |
| `typescript-reviewer` | TypeScript idioms (after generic code-reviewer) |

**Layer 2 — 人格定義 (SuperClaude v4.3.0, 20).** `category:` only — no `tools:`/`model:`, no CLI commands. These reframe *how you think*, not what you run. Dispatch for design / exploration / spec / teaching:
`backend-architect` `business-panel-experts` `deep-research` `deep-research-agent` `devops-architect` `frontend-architect` `learning-guide` `performance-engineer` `pm-agent` `python-expert` `quality-engineer` `refactoring-expert` `repo-index` `requirements-analyst` `root-cause-analyst` `security-engineer` `self-review` `socratic-mentor` `system-architect` `technical-writer`

**【MUST】名前が似ていても役割は別物。** `security-reviewer` は `npm audit` を実行し、`security-engineer` は設計時の脅威モデルを語るだけ。**「go do it → Layer 1 / help me decide → Layer 2」**。7組の紛らわしいペアの振り分け表は `rules/agents.md`「Look-Alike Pairs」を必ず参照する。

## Agent Teams (tmux split panes)
- **【MUST】効果的な場面では必ず複数エージェント協調を使う。** memory 任せにせず毎プロンプトで判定する。次のいずれか2つ以上が当てはまれば、単発 SubAgent でなく協調（複数 `Agent` 並列 + `SendMessage` + 共有タスクリスト）を選ぶ: ①multi-file 影響 ②独立観点の並列（security/perf/test 等）③仮説競合や設計議論が有益 ④3+ の独立タスクを並列。逆に明確な分業で議論不要なら単発 `Agent` で十分（過剰なチーム化はしない＝適材適所）。
- **【実装メモ】協調は複数 `Agent` 起動（`teammateMode:"tmux"`）+ `SendMessage` + 共有タスクリスト（`TaskCreate`/`TaskList`）で構成する**（専用のチーム一括作成/削除ツールはこの環境に無い＝ToolSearch 確認済み。片付けは不要ペインを tmux kill-pane で）。
- **積極利用ポリシー**: 以下のいずれかが当てはまるなら、SubAgent ではなく teammate を選ぶ
  - **Multi-perspective レビュー**: PR / 設計を security + performance + test など複数観点で並列レビュー
  - **競合仮説**: バグ原因の仮説が複数あり、互いに論破させたい
  - **SDLC パイプライン**: PM → Architect → Dev → QA を段階的に流したい
  - **見積り三者**: Technical / Benchmark / Risk の三本立てで見積もりたい
  - **3+ 独立タスクの並列実装**: ファイル無重複で teammate ごとに 5-6 タスク割当可能なとき
- 機能フラグ: `settings.json` の `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` と `teammateMode: "tmux"` (両方とも設定済み)
- **起動**: `bash ~/.claude/scripts/claude-team.sh` (tmux 外なら自動でセッションを張って claude を起動)
- **既知の制限**: 公式ドキュメントは VS Code 内蔵ターミナル / Windows Terminal / Ghostty を split-pane 非対応と明記。ただし上記スクリプト経由で **必ず tmux pane 内から claude を起動** すれば、pane 分割は tmux 自身の責務になるためターミナル本体の制約は実質回避できる。
- **使い方の例**:
  - "3 人の teammate で PR #142 をレビューして (security/performance/test)"
  - "2 人で原因仮説を競わせて、互いを論破させて"
- **ペイン操作**: `Ctrl+b → h/j/k/l` で teammate 間を移動 (`~/.tmux.conf` 既設定)
- **片付け**: lead に「team を cleanup して」と頼む。孤児セッションが残ったら `tmux ls` → `tmux kill-session -t <name>`
- 詳細仕様は公式: <https://code.claude.com/docs/en/agent-teams>

## Language
- Always respond in Japanese (unless English is explicitly requested)
- Write code, comments, and documentation in English
- Use technical terms in their original form (e.g., API, Docker, Kubernetes)

## Response Style
- **Conclusion first**: Present the solution first, details later
- **平易な表現を最優先 (初心者にも分かる文章で書く)**: チャット欄に出力する応答文では、専門用語・カタカナ英語・略語の多用を避ける。技術的な固有名詞 (例: WebFetch / SubAgent / raw URL / frontmatter / monkey-patch / SPA / allowlist 等) を使うときは、**初出時のみ** 直後の括弧で 1 行の日本語補足を入れる: 例「WebFetch (Web ページの中身を取り出す機能)」「allowlist (許可リスト)」。2 回目以降の同じ用語は補足不要。可能な限り「何をしているか」を平易な日本語で先に伝え、技術名は補助的に使う。**この規則は CLI 応答文に適用、コード本体・コメント・ファイル名には適用しない**
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
- **PR は必ず `/create-pr` 経由**: `gh pr create` の直叩き禁止（テンプレ準拠強制、詳細は `rules/git-workflow.md`）
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
**User-defined (`~/.claude/commands/`):** `/create-pr`, `/slash-guide`, `/learn` (skill化), `/kiro:*` (spec-init, spec-design, spec-impl, validate-* など), `/code-review` (PR+local), `/build-fix`, `/test-coverage`, `/feature-dev`, `/refactor-clean`, `/quality-gate`, `/save-session` + `/resume-session`, `/model-route`, `/learn-eval`
**Plugin-provided:** `/revise-claude-md` (claude-md-management)
**SuperClaude (`~/.claude/commands/sc/`, 30個):** `/sc:brainstorm` (要求を対話で掘る), `/sc:research` (外部Web深掘り調査), `/sc:spec-panel` (専門家パネルで仕様レビュー), `/sc:business-panel` (経営思想家9人で戦略分析), `/sc:index-repo` (リポジトリ索引化・トークン94%削減), `/sc:load`+`/sc:save` (serena経由のセッション文脈保存/復元), `/sc:select-tool`, `/sc:recommend` (どの `/sc:` を使うか推薦), `/sc:help` (全一覧)。他に analyze/build/cleanup/design/document/estimate/explain/git/implement/improve/pm/reflect/spawn/task/test/troubleshoot/workflow/agent/index/sc
- 名前空間が `sc:` で分離されているため既存コマンド・`/kiro:*` と衝突しない
- 既存の自作コマンドと機能が重なる場合は**既存を優先**（`/create-pr` は `/sc:git` より優先、`/code-review` は `/sc:analyze` より優先）

## Context Management

- **【MUST】本筋と別系統の付随作業は別コンテキストに切り出す**: そのセッションの主目的と別系統の付随作業（設定変更・ルール化・調査・レビュー等）は、メイン文脈を汚さないようサブエージェント（別コンテキスト）または `/fork` に隔離し、メインは主目的に集中させる。

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
