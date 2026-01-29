# チャットボット免責文言追加計画

## 作業手順

### Step 1: Worktree作成
```bash
git worktree add .worktrees/feature/add-disclaimer -b feature/add-disclaimer develop
cd .worktrees/feature/add-disclaimer
```

### Step 2: コード修正
- `src/client/components/chat/ChatInput.tsx` を編集

### Step 3: 動作確認
- 開発サーバーで表示確認
- モバイル表示確認

### Step 4: コミット & PR作成
- コミットメッセージ: `feat: add disclaimer text below chat input`
- develop ブランチへPR作成

---

## 要件
- **場所**: チャットボット入力エリアの下
- **文言**: 「本サポートチャットは学習中のため、不正確な情報を回答することがあります。正確な回答内容は再確認いただくようお願いいたします。」
- **言語**: 日本語のみ（多言語対応なし）
- **スタイル**: 控えめ（グレー小文字、現在の「Powered by AI」と同様）

## 修正対象ファイル
- `src/client/components/chat/ChatInput.tsx`

## 実装内容

### ChatInput.tsx の修正

現在のフッター部分（L117-120）:
```tsx
<div className="mt-2 px-1">
  <p className="text-[10px] text-gray-400 text-right">Powered by AI</p>
</div>
```

修正後:
```tsx
<div className="mt-2 px-1">
  <p className="text-[10px] text-gray-400 text-center leading-relaxed">
    本サポートチャットは学習中のため、不正確な情報を回答することがあります。
    <br />
    正確な回答内容は再確認いただくようお願いいたします。
  </p>
  <p className="text-[10px] text-gray-400 text-right mt-1">Powered by AI</p>
</div>
```

### スタイル詳細
- フォントサイズ: `10px`（既存と統一）
- 文字色: `text-gray-400`（既存と統一）
- 配置: `text-center`（中央揃え）
- 行間: `leading-relaxed`（読みやすさ向上）
- 「Powered by AI」は右寄せのまま維持、上にマージン追加

## 確認事項
- [ ] 開発環境で表示確認
- [ ] モバイル表示での改行・レイアウト確認
- [ ] 埋め込み版（ChatWidgetFrame経由）でも同様に表示されることを確認
