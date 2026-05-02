# claudefiles

Claude Code（`~/.claude/`）の設定ファイルを管理するリポジトリ。

## 構成

```
~/.claude/
├── .gitignore             # ランタイムデータ除外
├── CLAUDE.md              # グローバル指示（全プロジェクト共通）
├── settings.json          # 権限・Hooks・環境変数・MCP設定
├── agents/                # カスタムエージェント（7種）
├── commands/              # スラッシュコマンド
│   ├── slash-guide.md
│   └── kiro/              # 仕様駆動開発ワークフロー（11コマンド）
├── skills/                # カスタムスキル（13種）
│   ├── development-rules/
│   ├── testing-rules/
│   ├── git-workflow/
│   ├── gemini-research/
│   ├── serena-codebase/
│   ├── document-converter/
│   └── rough-estimate/
└── scripts/               # 自動化スクリプト
    ├── generate-dashboard.mjs  # ダッシュボード HTML + README 生成
    └── auto-sync.sh            # 設定変更時の自動 commit & push
```

## CLAUDE.md

全プロジェクトに適用されるグローバル指示ファイル。

- **言語**: 日本語で応答、コードは英語
- **スタイル**: 結論ファースト、簡潔でカジュアル
- **原則**: 依頼されたことだけを行う、ファイル作成は最小限
- **コンテキスト管理**: タスク種別に応じた最適な戦略を提案

## settings.json

### 権限

Git 読み取り系（`status`, `diff`, `log`, `branch`, `worktree`）、`npm run`, `pnpm`、MCP ツール（Context7, Azure, o3）等を許可。

### Hooks

| Hook | 内容 |
|------|------|
| **PreToolUse** | 破壊的コマンド（`rm -rf` 等）と `git push --force` をブロック |
| **PostToolUse** | JS/TS ファイル保存時に prettier 自動整形 + 設定変更時にダッシュボード再生成 & 自動 push |
| **Stop** | タスク完了時の通知 |
| **Notification** | terminal-notifier でデスクトップ通知 |

### 環境変数

| 変数 | 値 | 説明 |
|------|-----|------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `70` | コンテキスト70%でオートコンパクション |

### MCP 連携

- **Azure** — Azure リソース操作・ドキュメント参照
- **Context7** — ライブラリドキュメント検索
- **o3** — OpenAI o3 モデル連携
- **Serena** — セマンティックコード解析
- **Playwright** — ブラウザ自動操作
- **GitHub** — GitHub API 連携
- **Notion** — Notion API 連携
- **Gemini** — Google Gemini 連携

## エージェント

| エージェント | 用途 |
|-------------|------|
| `code-reviewer` | コードレビューエージェント |
| `devops-problem-solver` | DevOps 問題解決エージェント |
| `estimation-agent` | 見積りエージェント |
| `senior-consultant-reviewer` | シニアコンサルタントレビューエージェント |
| `task-decomposer` | タスク分解エージェント |
| `test-runner` | テストランナーエージェント |
| `workflow-recorder` | ワークフロー記録エージェント |

## スキル

| スキル | 用途 |
|--------|------|
| `acnpptx` | Accenture PowerPoint 生成スキル |
| `claude-assist` | マルチライン入力GUI スキル |
| `delivery-folder-creator` | delivery-folder-creator |
| `development-rules` | 開発ルール |
| `document-converter` | ドキュメント変換スキル |
| `gemini-research` | Gemini リサーチスキル |
| `git-workflow` | Git ワークフロー |
| `login-eso` | Accenture SSO 認証スキル |
| `reserve-space` | Accenture Places スペース予約スキル |
| `rough-estimate` | 概算見積り作成スキル |
| `serena-codebase` | Serena コードベース分析スキル |
| `skill-maker` | スキル自動構築・改善スキル |
| `testing-rules` | テストルール |

## コマンド

### `/slash-guide`

Claude Code の全スラッシュコマンドを日本語で解説。

### `/kiro/*` — 仕様駆動開発ワークフロー

| コマンド | 用途 |
|---------|------|
| `spec-init` | 仕様の初期化 |
| `spec-requirements` | 要件定義の生成 |
| `spec-design` | 技術設計の作成 |
| `spec-tasks` | 実装タスクの生成 |
| `spec-impl` | TDD による実装実行 |
| `spec-status` | 仕様の進捗確認 |
| `steering` / `steering-custom` | プロジェクト知識の管理 |
| `validate-design` | 技術設計のレビュー |
| `validate-gap` | 要件と実装のギャップ分析 |
| `validate-impl` | 実装の検証 |

## 自動同期

設定ファイル（CLAUDE.md, settings.json, agents/*.md, skills/*/SKILL.md, commands/*.md）を変更すると、PostToolUse hook により以下が自動実行される:

1. ダッシュボード HTML（`claudesettings-CLAUDE設定.html`）を再生成
2. README.md を再生成
3. 全変更を `git commit` + `git push origin main`

## セットアップ

```bash
git clone git@github.com:umaionigiri/claudefiles.git ~/.claude
```

既に `~/.claude/` が存在する場合:

```bash
git clone git@github.com:umaionigiri/claudefiles.git /tmp/claudefiles
ln -sf /tmp/claudefiles/CLAUDE.md ~/.claude/CLAUDE.md
ln -sf /tmp/claudefiles/settings.json ~/.claude/settings.json
ln -sf /tmp/claudefiles/agents ~/.claude/agents
ln -sf /tmp/claudefiles/commands ~/.claude/commands
ln -sf /tmp/claudefiles/skills ~/.claude/skills
```
