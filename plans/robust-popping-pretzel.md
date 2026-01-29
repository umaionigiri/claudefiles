# PR #195のベースブランチ変更プラン

## 現状
- **PR #195**: `claude/fix-multilingual-language-switch-KJ0NF` → `main`
- CLAUDE.mdルールにより、mainへの直接マージは禁止（developを経由する必要がある）

## 修正内容
PR #195のbaseブランチを `main` から `develop` に変更する

## 実行手順

### 1. Bash経由でgh CLIを使用してPRのベースブランチを変更
```bash
gh pr edit 195 --base develop --repo kgkgzrtk/wmg2027-ai-chatbot
```

## 検証方法
- GitHub上でPR #195のベースブランチが `develop` になっていることを確認
- `gh pr view 195 --repo kgkgzrtk/wmg2027-ai-chatbot` で確認

## 影響範囲
- PR #195のみ
- 変更されたコード自体は変わらない（ベースブランチの変更のみ）
