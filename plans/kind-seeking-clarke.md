# チャットボット注意文言の文字サイズ修正

## 要件

注意文言の文字サイズを **14px → 12px** に変更する。

## 作業手順

1. Worktree作成: `fix/disclaimer-font-size`
2. `src/client/components/chat/ChatInput.tsx` を修正
3. テスト実行・ビルド確認
4. コミット・プッシュ
5. develop へ PR 作成

## 対象ファイル

- `src/client/components/chat/ChatInput.tsx` (行120)

## 修正内容

```tsx
// Before
<p className="text-[14px] text-[#373737] text-left leading-relaxed">

// After
<p className="text-[12px] text-[#373737] text-left leading-relaxed">
```
