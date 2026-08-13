# git-pull-safe

未コミット・未ステージの変更がある状態でも安全にリモートの最新を取り込むスキル。
stash → pull (rebase) → unstash の手順を自動化する。

## トリガー

- 「最新を pull して」「リポジトリを同期して」「pull して」「リモートの更新を取り込んで」
- 英語: "pull latest", "sync repo", "fetch and pull", "update branch"

## 手順

### Step 1: 状態確認

```bash
git status --short
```

変更なし（出力が空） → Step 3 へスキップ  
変更あり → Step 2 へ

### Step 2: stash に退避

```bash
git stash push --include-untracked -m "auto-stash before pull $(date +%Y%m%d-%H%M%S)"
```

- `--include-untracked` で追跡されていないファイルも含める
- stash 名にタイムスタンプを入れて後から特定しやすくする

失敗した場合 → ユーザーに報告して中断

### Step 3: リモートの最新を取得

```bash
git fetch origin
git rebase origin/$(git branch --show-current)
```

- `git pull --rebase` はリモート ref のキャッシュがない場合に失敗することがあるため
  `fetch` + `rebase` の 2ステップを使う

コンフリクトが発生した場合:
```bash
git rebase --abort
git stash pop   # stash した場合のみ
```
→ コンフリクトファイルを列挙してユーザーに報告

### Step 4: stash を戻す（Step 2 を実行した場合のみ）

```bash
git stash pop
```

`already exists` 系のエラーが出た場合は Windows の Zone.Identifier ファイルによる
衝突であることが多い。変更ファイルが復元されていれば実害なし。
残った stash エントリは `git stash drop stash@{0}` で削除する。

### Step 5: 結果の確認・報告

```bash
git log -5 --oneline
git status --short
```

取り込んだコミット一覧と、ワーキングツリーの状態をユーザーへ伝える。
「ブランチはすでに最新です」の場合もその旨を明示する。

## 注意事項

- stash pop でコンフリクトが起きた場合は、ユーザーに手動解決を依頼する
- stash エントリが残った場合は必ず `git stash drop` で清掃する
- このスキルはブランチ切り替えや rebase -i などの複雑な操作は行わない  
  → ブランチ管理全体は `git-workflow` スキルを参照
