---
name: git-workflow
description: |
  ブランチ管理とコミットのためのGitワークフロールールを適用。
  Worktree必須、安全なブランチ操作、GitHub MCPとの連携。
  トリガー: 「ブランチ作成」「git workflow」「コミット」「PR作成」「worktree」
---

# Git ワークフロー

## Step 1: Worktree 作成（必須）

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
cd .worktrees/<branch-name>
```

## Step 2: ブランチ命名

| タイプ | パターン | 例 |
|--------|----------|-----|
| Feature | `feature/<name>` | `feature/user-auth` |
| Bugfix | `fix/<name>` | `fix/login-error` |
| Test | `test/<name>` | `test/api-coverage` |
| Refactor | `refactor/<name>` | `refactor/cleanup` |

## Step 3: コミット（Conventional Commits）

```
<type>: <description>
```

| Type | 用途 |
|------|------|
| `feat` | 新機能 |
| `fix` | バグ修正 |
| `refactor` | リファクタリング |
| `test` | テスト追加・修正 |
| `docs` | ドキュメント |
| `chore` | その他 |

## Step 4: PR 作成（GitHub MCP 使用）

```
mcp__github__create_pull_request({
  owner, repo, title, body, head, base: "main"
})
```

## Step 5: マージ後クリーンアップ

```bash
git worktree remove .worktrees/<branch-name>
git branch -d <branch-name>
```

## 禁止事項

| 操作 | 理由 |
|------|------|
| `main`/`master` 直接プッシュ | レビューなしの変更を防ぐ |
| `git push --force` | 履歴破壊を防ぐ |
| `git reset --hard` | 作業内容の消失を防ぐ |

**例外:** ユーザーが明示的に許可した場合のみ

## 検証チェックリスト

**コミット前:**
- [ ] テスト全通過・Lint・型チェック・ビルド成功
- [ ] 意図した変更のみステージング
- [ ] 機密情報を含まない

**PR 作成前:**
- [ ] ローカルでテスト通過
- [ ] CI が通過してからマージ
