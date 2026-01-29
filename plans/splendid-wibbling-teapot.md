# Issue #148: 回答一貫性の改善（Temperature・ソート・優先度ルール）

## 概要
同じ質問に対して異なる回答が返される問題を解決するため、3つの修正を実施。

## 作業ディレクトリ
```
/Users/so/MyWorkSpace/scibit/wmg2027-ai-chatbot/.worktrees/issue-148
```

## 変更対象ファイル

| # | ファイル | 変更内容 |
|---|----------|----------|
| 1 | `src/server/lib/gemini/gateway.ts:24` | temperature: 0.5 → 0.3 |
| 2 | `src/server/lib/gemini/file-search/parser.ts:32` | sortByRelevance()関数追加 |
| 3 | `src/server/lib/prompts/template-engine.ts:75-87` | 優先度ルール文言追加 |
| 4 | `tests/unit/server/lib/prompts/template-engine.test.ts` | アサーション更新 |
| 5 | `tests/unit/server/lib/gemini/gateway-consistency.test.ts` | **新規作成** 一貫性テスト |

## 実装手順

### Step 1: Temperature修正 (gateway.ts)
```typescript
// 変更前
temperature: 0.5, // 0.2 → 0.5 for response format diversity

// 変更後
temperature: 0.3, // FAQ向け低Temperature（回答の一貫性と多少の表現バリエーションを両立）
```

### Step 2: 検索結果ソート追加 (parser.ts)
1. `sortByRelevance()`関数を追加
2. parseSearchResponse()の戻り値をソート

```typescript
function sortByRelevance(results: FileSearchResult[]): FileSearchResult[] {
  const order: Record<string, number> = { high: 0, medium: 1, low: 2 };
  return [...results].sort((a, b) => {
    const aScore = a.relevance ? order[a.relevance] ?? 3 : 3;
    const bScore = b.relevance ? order[b.relevance] ?? 3 : 3;
    return aScore - bScore;
  });
}
```

### Step 3: プロンプト優先度ルール追加 (template-engine.ts)
```typescript
// 変更後
return `## 参考情報
以下の情報を参考に回答してください。
**重要: 参考情報は関連度が高い順に並んでいます。矛盾する情報がある場合は、最初の情報を優先してください。**

${contextText}`;
```

### Step 4: テスト更新 (template-engine.test.ts)
- プロンプト文言変更に伴うアサーション更新

### Step 5: 一貫性テスト追加 (gateway-consistency.test.ts) **新規作成**
同じ問い合わせで同じような応答が返ってくることを検証するテストを追加。

```typescript
// tests/unit/server/lib/gemini/gateway-consistency.test.ts
describe('Response Consistency', () => {
  it('should return consistent output for identical inputs', async () => {
    // 同じメッセージで3回呼び出し
    // 全回呼び出しのstreamText()引数が一致することを検証
  });

  it('should use temperature=0.3 for FAQ consistency', () => {
    // streamText()がtemperature: 0.3で呼ばれることを確認
  });

  it('should maintain consistent context through message history', async () => {
    // 同じメッセージ履歴で複数回実行
    // streamText()呼び出しの引数が一貫していることを確認
  });
});
```

**テスト方針**:
- モックを固定してDeterminism検証
- 低temperature (0.3) での確定的応答を確認
- 会話履歴を含む場合のコンテキスト一貫性確認

## 確認事項
- [ ] テスト実行: `pnpm vitest run`
- [ ] 型チェック: `pnpm type-check`
- [ ] ビルド: `pnpm build`

## PRマージフロー
```
issue/148-answer-consistency → develop → main
```

**手順**:
1. PR作成: `issue/148-answer-consistency` → `develop`
2. CIパス確認
3. **承認を得てからマージ** （自動マージしない）
4. developで動作確認後、`develop` → `main` のPRを作成
5. 承認を得てからマージ
