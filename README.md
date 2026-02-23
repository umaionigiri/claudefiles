# claudefiles

Claude Code（`~/.claude/`）の設定ファイルを管理するリポジトリ。

## Structure

```
~/.claude/
├── CLAUDE.md              # グローバル指示（全プロジェクト共通）
├── settings.json          # 権限・Hooks・MCP設定
├── agents/                # カスタムエージェント（6種）
├── commands/              # スラッシュコマンド
│   ├── slash-guide.md
│   └── kiro/              # 仕様駆動開発ワークフロー（11コマンド）
└── skills/                # カスタムスキル（7種）
    ├── development-rules/
    ├── testing-rules/
    ├── git-workflow/
    ├── gemini-research/
    ├── serena-codebase/
    ├── document-converter/
    └── rough-estimate/
```

## CLAUDE.md

グローバル指示ファイル。全プロジェクトに適用される。

- **言語**: 日本語で応答、コードは英語
- **スタイル**: 結論ファースト、簡潔でカジュアル
- **原則**: 依頼されたことだけを行う、ファイル作成は最小限

## settings.json

### Permissions

Git 読み取り系（`status`, `diff`, `log`, `branch`, `worktree`）、`npm run`, `pnpm`、MCP ツール（Context7, Azure, o3）等を許可。

### Hooks

| フック | 内容 |
|--------|------|
| **PreToolUse** | `rm -rf` 等の危険コマンド・`git push --force` をブロック |
| **PostToolUse** | `.js/.ts/.jsx/.tsx` ファイル保存時に prettier 自動整形 |
| **Notification** | terminal-notifier でデスクトップ通知 |

### MCP 連携

- **Azure** — Azure リソース操作・ドキュメント参照
- **Context7** — ライブラリドキュメント検索
- **o3** — OpenAI o3 モデル連携
- **Serena** — セマンティックコード解析
- **Playwright** — ブラウザ自動操作
- **GitHub** — GitHub API 連携
- **Notion** — Notion API 連携
- **Gemini** — Google Gemini 連携

## Agents

| エージェント | 用途 |
|-------------|------|
| `estimation-agent` | プロジェクト見積り・見積書作成 |
| `senior-consultant-reviewer` | 要件・設計・見積りのレビュー |
| `code-reviewer` | コード品質・セキュリティレビュー |
| `test-runner` | テスト実行・コード検証 |
| `task-decomposer` | プロジェクト分解・タスク計画 |
| `devops-problem-solver` | エラー対応・インシデント・デバッグ |

## Commands

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

## Skills

| スキル | 用途 |
|--------|------|
| `development-rules` | SOLID/DRY/KISS に基づく開発ルール適用 |
| `testing-rules` | TDD サイクルに基づくテストルール |
| `git-workflow` | Worktree 必須のブランチ管理 |
| `gemini-research` | Gemini MCP による外部リサーチ |
| `serena-codebase` | Serena MCP によるコード探索 |
| `document-converter` | Markdown → Word/Excel/PDF 変換 |
| `rough-estimate` | 概算見積り作成（Scibit LLC） |

## Setup

```bash
git clone git@github.com:umaionigiri/claudefiles.git ~/.claude
```

既に `~/.claude/` が存在する場合は、必要なファイルを個別にコピーまたはシンボリックリンクで配置する。

```bash
git clone git@github.com:umaionigiri/claudefiles.git /tmp/claudefiles
ln -sf /tmp/claudefiles/CLAUDE.md ~/.claude/CLAUDE.md
ln -sf /tmp/claudefiles/settings.json ~/.claude/settings.json
ln -sf /tmp/claudefiles/agents ~/.claude/agents
ln -sf /tmp/claudefiles/commands ~/.claude/commands
ln -sf /tmp/claudefiles/skills ~/.claude/skills
```
