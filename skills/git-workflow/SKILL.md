---
name: git-workflow
description: |
  ブランチ管理とコミットのためのGitワークフロールールを適用。
  Worktree必須、安全なブランチ操作、GitHub MCPとの連携。
  トリガー: 「ブランチ作成」「git workflow」「コミット」「PR作成」「worktree」
---

# Git Workflow Rules

安全で効率的なGit操作のためのワークフロースキル。

## ワークフロー

```mermaid
flowchart TD
    A[作業開始] --> B[Worktree 作成]
    B --> C[ブランチ作成]
    C --> D[コード実装]
    D --> E[テスト実行]
    E --> F{テスト成功?}
    F -->|No| D
    F -->|Yes| G[コミット]
    G --> H{追加作業?}
    H -->|Yes| D
    H -->|No| I[プッシュ]
    I --> J[PR 作成]
    J --> K[CI 確認]
    K --> L{CI 成功?}
    L -->|No| D
    L -->|Yes| M[レビュー対応]
    M --> N[マージ]
    N --> O[Worktree 削除]
    O --> P[完了]
```

## Step 1: Worktree 作成（必須）

**作業開始時に必ず実行:**

```bash
# Worktree 作成
git worktree add .worktrees/<branch-name> -b <branch-name>

# 移動
cd .worktrees/<branch-name>
```

## Step 2: ブランチ作成

| タイプ | パターン | 例 |
|--------|----------|-----|
| Feature | `feature/<name>` | `feature/user-auth` |
| Bugfix | `fix/<name>` | `fix/login-error` |
| Test | `test/<name>` | `test/api-coverage` |
| Refactor | `refactor/<name>` | `refactor/cleanup` |

## Step 3: コミット

**コミットメッセージ形式:**

```
<type>: <description>

[optional body]
```

| Type | 用途 |
|------|------|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `refactor` | リファクタリング |
| `test` | テスト追加・修正 |
| `docs` | ドキュメント |
| `chore` | その他 |

## Step 4: プッシュ

```bash
git push -u origin <branch-name>
```

## Step 5: PR 作成

GitHub MCP を使用:

```
mcp__github__create_pull_request({
  owner: "owner",
  repo: "repo",
  title: "PR title",
  body: "## Summary\n\n## Test Plan",
  head: "feature-branch",
  base: "main"
})
```

## Step 6: マージ後

```bash
# Worktree 削除
git worktree remove .worktrees/<branch-name>

# ブランチ削除（オプション）
git branch -d <branch-name>
```

## クイックリファレンス

### Worktree コマンド

| 操作 | コマンド |
|------|----------|
| 一覧 | `git worktree list` |
| 作成 | `git worktree add .worktrees/<name> -b <name>` |
| 削除 | `git worktree remove .worktrees/<name>` |
| 強制削除 | `git worktree remove --force .worktrees/<name>` |

### ブランチ命名早見表

| タイプ | パターン | 例 |
|--------|----------|-----|
| Feature | `feature/<name>` | `feature/user-auth` |
| Bugfix | `fix/<name>` | `fix/login-error` |
| Test | `test/<name>` | `test/api-coverage` |
| Refactor | `refactor/<name>` | `refactor/cleanup` |
| Hotfix | `hotfix/<name>` | `hotfix/critical-bug` |

### コミットタイプ早見表

| Type | 用途 | 例 |
|------|------|-----|
| `feat` | 新機能 | `feat: add user registration` |
| `fix` | バグ修正 | `fix: resolve login timeout` |
| `refactor` | リファクタ | `refactor: simplify auth logic` |
| `test` | テスト | `test: add unit tests for Cart` |
| `docs` | ドキュメント | `docs: update API reference` |
| `chore` | その他 | `chore: update dependencies` |

### GitHub MCP 操作

| 操作 | ツール |
|------|--------|
| PR 作成 | `mcp__github__create_pull_request` |
| PR 一覧 | `mcp__github__list_pull_requests` |
| Issue 作成 | `mcp__github__create_issue` |
| ブランチ作成 | `mcp__github__create_branch` |

## 検証チェックリスト

### コミット前チェック

- [ ] テストが全て通過
- [ ] Lint エラーなし
- [ ] 型チェック通過
- [ ] ビルド成功
- [ ] 意図した変更のみステージング

### プッシュ前チェック

- [ ] コミットメッセージが適切
- [ ] 機密情報（.env等）を含まない
- [ ] 大きなバイナリファイルを含まない
- [ ] ブランチ名が規則に従っている

### PR 作成前チェック

- [ ] ローカルでテスト通過
- [ ] 変更内容を説明できる
- [ ] テストプラン記載

### 安全性チェック

- [ ] `main`/`master` への直接プッシュなし
- [ ] `--force` を使っていない（または明示的許可あり）
- [ ] 破壊的変更は事前に報告
- [ ] CI が通過してからマージ

## 禁止事項

| 操作 | 理由 |
|------|------|
| `main`/`master` 直接プッシュ | レビューなしの変更を防ぐ |
| `git push --force` | 履歴破壊を防ぐ |
| `git reset --hard` | 作業内容の消失を防ぐ |
| `git checkout .` | 未コミット変更の消失を防ぐ |

**例外:** ユーザーが明示的に許可した場合のみ

## 重要事項

- **Worktree 必須**: 作業開始時に必ず Worktree を作成
- **GitHub MCP 使用**: GitHub 操作は MCP ツールを使用
- **安全第一**: 破壊的コマンドは確認なしに実行しない
- **CI 必須**: マージ前に CI 通過を確認
