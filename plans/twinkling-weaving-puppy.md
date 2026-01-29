# i18n対応計画: UIテキストの多言語化

## 概要
WMG2027 AIチャットボットのUI上の日本語文章をロケール情報によって英語表記に自動切り替え可能にする。

## 要件
- **日本語（ja）**: 日本語表記
- **それ以外のロケール**: 英語表記

## 工数・費用見積もり（AI実行）

### 作業項目別工数

| No. | 作業項目 | 工数 |
|-----|----------|------|
| 1 | i18n.ts拡張（7キー×4言語） | 0.25h |
| 2 | ChatWindow.tsx修正（3箇所） | 0.25h |
| 3 | ChatInput.tsx修正（4箇所） | 0.25h |
| 4 | ChatButton.tsx修正（ロケール検出追加） | 0.25h |
| 5 | ユニットテスト更新（3ファイル） | 0.5h |
| 6 | 動作確認・調整 | 1.0h |
| **合計** | | **2.5h** |

### 費用計算

| 項目 | 金額 |
|------|------|
| 内部コスト（2.5h × ¥15,000） | ¥37,500 |
| 税抜金額（×1.5） | ¥56,250 |
| 消費税（10%） | ¥5,750 |
| **合計（税込）** | **¥62,000** |

### 納期
発注後 **2営業日以内**

### 参考：人間実行との比較

| 項目 | 人間実行 | AI実行 | 削減率 |
|------|---------|--------|--------|
| 工数 | 8.0h | 2.5h | 68.8%削減 |
| 請求額（税込） | ¥198,000 | ¥62,000 | 68.7%削減 |

## 対象ファイル

### 修正対象
1. `src/client/lib/theme/i18n.ts` - 翻訳キー追加
2. `src/client/components/chat/ChatWindow.tsx` - ヘッダー部分
3. `src/client/components/chat/ChatInput.tsx` - 入力欄・注意文言
4. `src/client/components/chat/ChatButton.tsx` - チャットボタン
5. `tests/unit/client/lib/theme/i18n.test.ts` - テスト更新

### 追加する翻訳キー（7キー）

| キー | 日本語 | 英語 |
|------|--------|------|
| headerTitle | WMG2027 サポートチャット | WMG2027 Support Chat |
| headerSubtitle | お気軽にご質問ください | Feel free to ask |
| closeChat | チャットを閉じる | Close Chat |
| openChat | チャットを開く | Open Chat |
| disclaimer1 | お申込みのヒントとして、AIが皆さまをサポートいたします。 | Our AI assistant is here to help with your registration. |
| disclaimer2 | まだ勉強中のため、たまに間違ったお答えをしてしまうことがあるかもしれません。 | It's still learning, so it may sometimes give incorrect answers. |
| disclaimer3 | 大切なルールや締切については、念のため大会要項もチェックしながら進めていただけると安心です！ | For critical rules or deadlines, always refer to the official competition guidelines. |

## 実装手順

### Step 1: Worktree作成
```bash
git worktree add .worktrees/feature-i18n-ui -b feature/i18n-ui-texts develop
cd .worktrees/feature-i18n-ui
```

### Step 2: GitHub Issue起票
GitHub MCPを使ってIssueを作成:
- タイトル: `feat: UIテキストの多言語対応（i18n）`
- 本文: 見積もり・作業内容・対象箇所を記載
- ラベル: `enhancement`

### Step 3: i18n.ts拡張
- `I18nMessages`インターフェースに9キー追加
- `messages`オブジェクトにja/en翻訳追加
- zh/koは英語と同じ値を設定

### Step 4: コンポーネント修正
1. **ChatWindow.tsx**: `messages_i18n`から翻訳取得
2. **ChatInput.tsx**: props経由で翻訳受け取り
3. **ChatButton.tsx**: 内部で`detectBrowserLocale()`呼び出し

### Step 5: テスト更新
- 新キーの存在確認テスト追加
- 各言語での取得テスト

### Step 6: PR作成
- developブランチへPR作成

## 検証方法

### 自動テスト
```bash
pnpm test
pnpm run type-check
pnpm build
```

### 人間による確認手順

1. **ローカルサーバー起動**
   ```bash
   pnpm dev
   ```

2. **日本語表示確認**
   - ブラウザの言語設定を日本語（ja）に設定
   - http://localhost:3000 にアクセス
   - 以下を確認：
     - ヘッダー: 「WMG2027 サポートチャット」「お気軽にご質問ください」
     - チャットボタン: 「チャットを開く」
     - 閉じるボタン: 「チャットを閉じる」
     - 注意文言3行が日本語で表示

3. **英語設定での確認**
   - ブラウザの言語設定を英語（en）に変更
   - ページをリロード
   - 以下を確認：
     - ヘッダー: 「WMG2027 Support Chat」「Feel free to ask」
     - チャットボタン: 「Open Chat」
     - 閉じるボタン: 「Close Chat」
     - 注意文言3行が英語で表示

4. **韓国語設定での確認（英語表示になることを確認）**
   - ブラウザの言語設定を韓国語（ko）に変更
   - ページをリロード
   - 以下を確認：
     - 日本語以外のロケールでは英語表示になること
     - 英語設定時と同じテキストが表示されること

5. **レイアウト確認**
   - 英語表示時にテキストがはみ出していないか
   - ボタンサイズが適切か
   - モバイル表示でも問題ないか

6. **Preview環境確認**
   - developブランチへマージ後、Vercel Preview環境で同様の確認を実施
