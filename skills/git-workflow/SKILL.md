---
name: git-workflow
description: |
  ブランチ管理とコミットのためのGitワークフロールールを適用。
  Worktree必須、安全なブランチ操作、GitHub MCPとの連携。
  トリガー: 「ブランチ作成」「git workflow」「コミット」「PR作成」「worktree」
---

# Git Workflow

## Step 1: Create Worktree (Required)

```bash
git worktree add .worktrees/<branch-name> -b <branch-name>
cd .worktrees/<branch-name>
```

## Step 2: Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<name>` | `feature/user-auth` |
| Bugfix | `fix/<name>` | `fix/login-error` |
| Test | `test/<name>` | `test/api-coverage` |
| Refactor | `refactor/<name>` | `refactor/cleanup` |

## Step 3: Commit (Conventional Commits)

```
<type>: <description>
```

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Refactoring |
| `test` | Add/modify tests |
| `docs` | Documentation |
| `chore` | Other |

## Step 4: Create PR (Using GitHub MCP)

```
mcp__github__create_pull_request({
  owner, repo, title, body, head, base: "main"
})
```

## Step 5: Post-Merge Cleanup

```bash
git worktree remove .worktrees/<branch-name>
git branch -d <branch-name>
```

## Prohibited Operations

| Operation | Reason |
|-----------|--------|
| Direct push to `main`/`master` | Prevents unreviewed changes |
| `git push --force` | Prevents history corruption |
| `git reset --hard` | Prevents work loss |

**Exception:** Only when user explicitly permits

## Verification Checklist

**Pre-commit:**
- [ ] All tests pass, lint, type check, build successful
- [ ] Only intended changes staged
- [ ] No secrets included

**Pre-PR:**
- [ ] Tests pass locally
- [ ] Merge only after CI passes
