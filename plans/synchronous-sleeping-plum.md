# モバイルメニュー背景色修正 + ブランチ戦略更新

## 問題
1. スマホでHPを開いた際、右上のメニューボタンを押すとメニューが表示されるが、画像と被って見えにくい
2. CLAUDE.mdのブランチ戦略がdevelop経由になっているが、main直接PRに変更

## 実装手順

### 1. Worktree再作成
現在のworktreeは古いコミットから作成されているため、再作成が必要。
```bash
git worktree remove .worktrees/feature/fix-mobile-menu-bg
git branch -D feature/fix-mobile-menu-bg
git fetch origin
git worktree add .worktrees/feature/fix-mobile-menu-bg -b feature/fix-mobile-menu-bg origin/main
```

### 2. CLAUDE.md ブランチ戦略更新
**ファイル**: `CLAUDE.md`

```markdown
## Gitワークフロー

### ブランチ戦略

# Before
main (本番) ← develop (開発統合) ← feature/* (作業)

# After
main (本番) ← feature/* (作業)
```

### 3. MobileMenu.tsx修正
**ファイル**: `src/components/common/MobileMenu.tsx`

メニューボタンのclassNameに背景色を追加:
```tsx
// Before
className="p-2 text-neutral-700 hover:text-sakura-600 transition-colors"

// After
className="p-2 text-neutral-700 hover:text-sakura-600 transition-colors bg-white/90 backdrop-blur-sm rounded-lg shadow-sm"
```

### 4. ビルド確認
```bash
cd .worktrees/feature/fix-mobile-menu-bg
npm install && npm run build
```

### 5. コミット・プッシュ
```bash
git add CLAUDE.md src/components/common/MobileMenu.tsx
git commit -m "fix: モバイルメニューボタンの視認性向上 / ブランチ戦略更新"
git push -u origin feature/fix-mobile-menu-bg
```

### 6. PR作成（mainへ直接）
```bash
gh pr create --base main --title "fix: モバイルメニューボタンの視認性向上 / ブランチ戦略更新" --body "..."
```

## 検証方法
1. 開発サーバー起動 (`npm run dev`)
2. ブラウザでモバイル表示に切り替え
3. トップページでメニューボタンが白い背景で見やすいことを確認
4. メニューを開いて正常に動作することを確認
