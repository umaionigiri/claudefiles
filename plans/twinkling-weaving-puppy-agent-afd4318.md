# WMG2027 AIチャットボット i18n対応 工数見積もり

## 概要
チャットUI上のハードコードされた日本語テキストを、ロケール情報に基づいて日本語/英語で切り替え可能にする。

## 現状分析

### 既存のi18n基盤
- **ファイル**: `src/client/lib/theme/i18n.ts`
- **対応ロケール**: ja, en, zh, ko（4言語）
- **既存キー**: placeholder, send, loading, error, retry, charLimitError, piiError, welcome（8キー）
- **検出方法**: `detectBrowserLocale()` でブラウザの言語設定を自動検出
- **取得方法**: `getMessages(locale)` で翻訳テキスト取得

### 追加が必要な翻訳キー（9キー）

| キー名 | 日本語 | 英語 |
|--------|--------|------|
| `headerTitle` | WMG2027 サポートチャット | WMG2027 Support Chat |
| `headerSubtitle` | お気軽にご質問ください | Feel free to ask questions |
| `closeChat` | チャットを閉じる | Close chat |
| `openChat` | チャットを開く | Open chat |
| `inputPlaceholder` | 質問を入力してください | Enter your question |
| `disclaimer1` | お申込みのヒントとして、AIが皆さまをサポートいたします。 | AI will assist you with application tips. |
| `disclaimer2` | まだ勉強中のため、たまに間違ったお答えをしてしまうことがあるかもしれません。 | As it's still learning, it may occasionally give incorrect answers. |
| `disclaimer3` | 大切なルールや締切については、念のため大会要項もチェックしながら進めていただけると安心です！ | For important rules and deadlines, please also check the competition guidelines. |

**注意**: 既存の `placeholder` キーは「メッセージを入力してください」で別用途のため、新規キー `inputPlaceholder` を追加。

### 修正対象ファイル

| ファイル | 変更内容 | 影響度 |
|----------|----------|--------|
| `src/client/lib/theme/i18n.ts` | I18nMessages に9キー追加、messages オブジェクトに4言語分の翻訳追加 | 中 |
| `src/client/components/chat/ChatWindow.tsx` | ハードコード文字列を i18n 対応に変更（3箇所） | 低 |
| `src/client/components/chat/ChatInput.tsx` | ハードコード文字列を i18n 対応に変更（4箇所）、props 経由で翻訳を受け取る | 中 |
| `src/client/components/chat/ChatButton.tsx` | ハードコード文字列を i18n 対応に変更（1箇所）、i18n hook の追加 | 低 |
| `tests/unit/client/lib/theme/i18n.test.ts` | 新キーの検証追加 | 低 |
| `tests/unit/client/components/chat/ChatInput.test.tsx` | i18n プロップス対応のテスト更新 | 中 |
| `tests/unit/client/components/chat/ChatWindow.test.tsx` | i18n モック更新、テストケース追加 | 中 |

## 作業項目と工数見積もり

### 1. i18n.ts の拡張
**作業内容**:
- I18nMessages インターフェースに9キー追加
- messages オブジェクトに日本語・英語の翻訳追加
- 中国語・韓国語の翻訳追加（要件外だが整合性のため）

**工数**: 0.5時間

### 2. ChatWindow.tsx の修正
**作業内容**:
- useChatUI から messages_i18n を取得（既存）
- ヘッダータイトル・サブタイトルを翻訳キーに置換
- 閉じるボタンの aria-label を翻訳キーに置換

**工数**: 0.5時間

### 3. ChatInput.tsx の修正
**作業内容**:
- props に messages_i18n を追加
- placeholder のデフォルト値を削除し、props 必須化
- 送信ボタンの aria-label を翻訳キーに置換
- 注意文言3行を翻訳キーに置換

**工数**: 0.5時間

### 4. ChatButton.tsx の修正
**作業内容**:
- i18n フックまたはコンテキストの導入検討
- aria-label を翻訳キーに置換

**工数**: 0.5時間

### 5. ユニットテスト更新
**作業内容**:
- i18n.test.ts に新キーの検証追加
- ChatInput.test.tsx の i18n プロップス対応
- ChatWindow.test.tsx のモック更新

**工数**: 1.5時間

### 6. 動作確認・調整
**作業内容**:
- ブラウザ言語設定切り替えで表示確認
- 日本語・英語それぞれの表示確認
- レイアウト崩れチェック（英語は日本語より長い傾向）

**工数**: 0.5時間

## 工数サマリー

| 作業項目 | 工数（時間） |
|----------|--------------|
| 1. i18n.ts の拡張 | 0.5 |
| 2. ChatWindow.tsx の修正 | 0.5 |
| 3. ChatInput.tsx の修正 | 0.5 |
| 4. ChatButton.tsx の修正 | 0.5 |
| 5. ユニットテスト更新 | 1.5 |
| 6. 動作確認・調整 | 0.5 |
| **合計** | **4.0時間** |

## 費用見積もり

| 項目 | 単価 | 数量 | 金額 |
|------|------|------|------|
| 開発工数 | ¥8,000/時間 | 4.0時間 | ¥32,000 |
| **合計** | | | **¥32,000** |

※ 単価は一般的なフリーランス開発者の時給目安です。実際の単価に応じて調整してください。

## 前提条件・リスク

### 前提条件
- 既存の i18n 基盤（detectBrowserLocale, getMessages）をそのまま活用
- 4言語（ja, en, zh, ko）すべてに翻訳を追加（ただし中韓は英語と同じでもOKなら工数減）
- ChatButton は単独で i18n 取得可能にする（useChatUI を使わない場合、別途フックが必要）

### リスク
1. **ChatButton の i18n 取得方法**: 現在 ChatButton は独立しており useChatUI を使っていない。i18n を取得するには以下のいずれかの対応が必要：
   - props で親から渡す
   - ChatButton 内で直接 detectBrowserLocale/getMessages を呼び出す
   - 共通の i18n Context を導入する

2. **中国語・韓国語の翻訳品質**: 機械翻訳を使う場合、品質確認が必要

## 設計メモ

### ChatButton の i18n 対応方針（推奨）
ChatButton 内で直接 i18n を取得する方法が最もシンプル：

```tsx
export function ChatButton({ onClick }: ChatButtonProps) {
  const locale = detectBrowserLocale();
  const messages = getMessages(locale);

  return (
    <button aria-label={messages.openChat}>
      ...
    </button>
  );
}
```

### ChatInput への翻訳渡し方法
ChatWindow から ChatInput に props で渡す：

```tsx
// ChatWindow.tsx
<ChatInput
  input={input}
  isLoading={isLoading}
  onInputChange={handleInputChange}
  onSubmit={handleFormSubmit}
  messages={messages_i18n}  // 追加
/>
```

```tsx
// ChatInput.tsx
interface ChatInputProps {
  input: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSubmit: () => void;
  messages: I18nMessages;  // 追加（placeholder 削除）
}
```
