# Git Workflow

Adapted from Everything Claude Code (`rules/common/git-workflow.md`).

## Commit Message Format (Conventional Commits)

```
<type>(<scope>): <description>

<optional body>

<optional footer>
```

Types: `feat` / `fix` / `refactor` / `docs` / `test` / `chore` / `perf` / `ci` / `style` / `build` / `revert`

Examples:
```
feat(auth): add OAuth2 PKCE flow for mobile clients
fix(api): handle empty pagination cursor without 500
refactor(db): extract migration helpers into shared module
```

## Pull Request Workflow

**MUST: PR は必ず `/create-pr` スキル経由で作成する。`gh pr create` を直接叩かない。**

理由: `/create-pr` はテンプレート(概要 / 関連タスク / やったこと / やらないこと / 影響範囲 / テスト / 備考)を強制し、レビュー観点の抜けを防ぐ。素の `gh pr create` を直接呼ぶと本文がアドホックになり、レビュアーが「なぜこの変更は無いのか」「影響範囲は」を毎回問い合わせる手戻りを生む。

例外:
- 緊急 hotfix で本文を最小限に留めたい場合のみ、ユーザーが明示的に「テンプレ不要」「直接作って」と指示したとき。

スキル本体は `~/.claude/commands/create-pr.md` (内容: 情報収集 → テンプレート記入 → `gh pr create` の流れ)。

スキル実行前のチェック:
1. `git branch --show-current` で作業ブランチを確認(main/master ではないこと)
2. `git log <base>..HEAD --oneline` で含まれるコミットを把握
3. `git diff <base>...HEAD --stat` で変更ファイルの規模を確認
4. `gh pr list --head <branch> --state open` で既存 PR の重複が無いか確認
5. ブランチがリモート未 push なら `git push -u origin <branch>`

## Pre-Commit Discipline

See `pre-commit.md` for the full checklist. In summary:
- Tests pass
- Lint/type checks pass
- `git diff --staged` shows only intended changes
- No secrets in staged files
- No debug code (`console.log`, `print`, `debugger`)

## Branching

- Never work directly on `main` / `master`
- Use feature/topic branches: `feat/<short-name>` / `fix/<short-name>`
- Use `git worktree` for parallel work: `git worktree add .git/worktrees/<name> <branch>`

## Forbidden Operations (Without Explicit User Approval)

- `git push --force` to shared branches (especially `main`)
- `git reset --hard` on commits already pushed
- `git rebase -i` while a PR is under review
- `git commit --no-verify` to skip hooks
- `git commit --no-gpg-sign` to bypass signing

If you encounter a hook failure or signing issue, fix the root cause rather than bypassing.

## Amending vs New Commit

- Default: **create a new commit**
- Amend only when:
  - The previous commit is not yet pushed
  - The user explicitly asks for `--amend`
  - Fixing a hook failure on an unpushed commit

After a hook failure, the commit did *not* happen — use a new commit, not `--amend`, or you risk modifying the wrong (previous) commit.
