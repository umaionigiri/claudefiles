# 回答一貫性の改善（Temperature・ソート・優先度ルール）

## 背景・問題

### 現象
- 同じ質問に対して異なる回答が返される
- 例：「大阪市で競技は実施されますか」→ 3回とも異なる回答

### 根本原因
1. **Temperature設定の不一致**
   - `src/server/lib/gemini/gateway.ts:24`で`temperature: 0.5`に設定
   - CLAUDE.mdでは「FAQには低Temperature（0.2）推奨」と明記
   - コメント「0.2 → 0.5 for response format diversity」で意図的に変更されている

2. **検索結果の順位付け非決定性**
   - `src/server/lib/gemini/file-search/parser.ts:32`でrelevanceスコアによるソートなし
   - 同等スコアの結果順序が毎回異なる可能性

3. **複数ドキュメント時の優先度ルール不備**
   - `src/server/lib/prompts/template-engine.ts:84-87`で複数参考情報を提示
   - どれを優先するかの指示がない

## 解決方針

**3段階の修正で回答の一貫性を95%以上に向上**

| Step | 対応内容 | 効果 |
|------|---------|------|
| P1-1 | Temperature を 0.5 → 0.2 に変更 | 回答生成の多様性を抑制 |
| P1-2 | 検索結果をrelevanceスコア順にソート | コンテキスト順序の安定化 |
| P2 | プロンプトに優先度ルール追加 | 矛盾情報への対応明確化 |

## 変更対象ファイル

| # | ファイル | 変更内容 | 変更行 |
|---|----------|----------|--------|
| 1 | `src/server/lib/gemini/gateway.ts` | `temperature: 0.5` → `0.2` | 24 |
| 2 | `src/server/lib/gemini/file-search/parser.ts` | `sortByRelevance()`関数追加 | 32 |
| 3 | `src/server/lib/prompts/template-engine.ts` | 優先度ルール文言追加 | 84-87 |
| 4 | `tests/unit/server/lib/prompts/template-engine.test.ts` | アサーション更新 | - |

## 詳細変更内容

### Step 1: Temperature修正

**ファイル**: `src/server/lib/gemini/gateway.ts:24`

```typescript
// 変更前
temperature: 0.5, // 0.2 → 0.5 for response format diversity

// 変更後
temperature: 0.2, // FAQ向け低Temperature（回答の一貫性を優先）
```

### Step 2: 検索結果スコアソート追加

**ファイル**: `src/server/lib/gemini/file-search/parser.ts:32`

```typescript
// 変更前
return results.map(r => mapToFileSearchResult(r, categoryToUrl));

// 変更後
const mapped = results.map(r => mapToFileSearchResult(r, categoryToUrl));
return sortByRelevance(mapped);
```

**追加関数**:
```typescript
/**
 * Sort results by relevance score (high > medium > low > undefined)
 */
function sortByRelevance(results: FileSearchResult[]): FileSearchResult[] {
  const order: Record<string, number> = { high: 0, medium: 1, low: 2 };
  return [...results].sort((a, b) => {
    const aScore = a.relevance ? order[a.relevance] ?? 3 : 3;
    const bScore = b.relevance ? order[b.relevance] ?? 3 : 3;
    return aScore - bScore;
  });
}
```

### Step 3: プロンプト優先度ルール追加

**ファイル**: `src/server/lib/prompts/template-engine.ts:84-87`

```typescript
// 変更前
return `## 参考情報
以下の情報を参考に回答してください：

${contextText}`;

// 変更後
return `## 参考情報
以下の情報を参考に回答してください。
**重要: 参考情報は関連度が高い順に並んでいます。矛盾する情報がある場合は、最初の情報を優先してください。**

${contextText}`;
```

## 影響範囲

| コンポーネント | 影響 |
|---------------|------|
| チャットAPI | ○ 変更あり（回答生成の一貫性向上） |
| RAG検索 | ○ 変更あり（結果ソート追加） |
| プロンプト | ○ 変更あり（優先度ルール追加） |
| 管理画面 | × 影響なし |
| アップロード機能 | × 影響なし |

## 工数見積（AI実施）

| 項目 | 工数 |
|------|------|
| P1-1: Temperature修正 | 0.1h |
| P1-2: スコアソート追加 | 0.25h |
| P2: プロンプト優先度 | 0.25h |
| テスト更新 | 0.3h |
| **AI作業小計** | **0.9h** |
| リスクバッファ（25%） | 0.2h |
| 人間による最終確認 | 1.0h |
| **合計工数** | **2.1h** |
| **合計費用** | **¥50,000** |

## リスク・注意事項

| リスク | 影響度 | 対策 |
|--------|--------|------|
| 回答の表現パターン減少 | 低 | Temperature 0.2でも十分な表現バリエーションあり |
| relevance未設定時のソート | 低 | undefined を最低優先度として処理 |
| テストアサーション変更 | 低 | プロンプト文言に合わせて更新 |

## 実装順序

1. **Phase 1**: `gateway.ts` の Temperature 修正（最も効果が高い）
2. **Phase 2**: `parser.ts` の sortByRelevance 追加
3. **Phase 3**: `template-engine.ts` の優先度ルール追加 + テスト更新
4. **Phase 4**: 手動確認（同じ質問を3回以上投げて一貫性確認）

## 前提条件
- 既存テストが正常にパスする状態
- CI/CDパイプラインが正常稼働

## スコープ外
- File Search Storeの設定変更
- RAG検索ロジックの大幅変更
- プロンプト全体の再設計

## クライアント向け説明

> AIの回答生成設定において、「回答の多様性」を重視する値になっておりました。
> FAQ用途では「一貫性・正確性」を重視すべきであり、設定値を調整することで
> 同じ質問に対して同じ回答を返すよう改善いたします。
