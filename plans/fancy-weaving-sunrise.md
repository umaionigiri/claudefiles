# RAG検索のマニフェスト依存削除計画

## 背景・問題

### 現象
- 管理画面からアップロードしたPDF（競技別実施要項等）がRAG検索で参照されない
- 競技に関する質問に正しく回答できない

### 根本原因
1. **Vercel環境でマニフェストが更新されない**
   - `src/app/api/admin/upload/route.ts:46-49`でVercel環境ではファイル書き込みをスキップ
   - File Search Storeにはアップロードされるが、`data/file-store-manifest.json`は更新されない

2. **RAG検索がマニフェストに依存**
   - Store名の取得
   - 検索プロンプトのカテゴリ抽出
   - マニフェストにないファイルのカテゴリが検索対象から漏れる

## 解決方針

**マニフェスト依存を削除し、File Search Storeのmetadataフィールドを活用する**

- Store名は環境変数 `FILE_SEARCH_STORE_NAME` から取得（既存）
- カテゴリはStore APIの `customMetadata` から取得（既に`source_type`で実装済み）
- 管理画面は既にStore APIを直接使用しており影響なし

### O3レビューによる改善ポイント

| 指摘事項 | 対応方針 |
|----------|----------|
| 検索品質劣化リスク | `customMetadata` のフィルタ機能を活用、必要に応じてカテゴリ絞り込み維持 |
| URLマッピング喪失 | `customMetadata` に `sourceUrl` を追加（将来対応、今回スコープ外） |
| セキュリティリスク | 現状は公開ドキュメントのみのため影響なし |
| eventual consistency | 既存UI/UXで対応済み（アップロード完了表示） |
| Rollbackプラン | Feature Flag `USE_MANIFEST_SEARCH` を追加し段階的移行 |

## 変更対象ファイル

### 1. `src/server/lib/gemini/file-search/index.ts`
- `loadManifest()` の呼び出しを削除
- Store名を環境変数から直接取得

```typescript
// Before
const manifest = await loadManifest();
const results = await performFileSearchStoreSearch(apiKey, query, numResults, manifest);

// After
const storeName = process.env.FILE_SEARCH_STORE_NAME;
if (!storeName) {
  logger.error('[File Search] FILE_SEARCH_STORE_NAME is not set');
  return { success: true, results: getFallbackContext() };
}
const results = await performFileSearchStoreSearch(apiKey, query, numResults, storeName);
```

### 2. `src/server/lib/gemini/file-search/file-search-store.ts`
- 関数シグネチャを変更（`manifest: Manifest` → `storeName: string`）
- カテゴリ抽出を削除

```typescript
// Before
export async function performFileSearchStoreSearch(
  apiKey: string,
  query: string,
  numResults: number,
  manifest: Manifest
): Promise<FileSearchResult[]>

// After
export async function performFileSearchStoreSearch(
  apiKey: string,
  query: string,
  numResults: number,
  storeName: string
): Promise<FileSearchResult[]>
```

### 3. `src/server/lib/gemini/file-search/prompts.ts`
- `buildFileSearchPrompt` からカテゴリパラメータを削除
- シンプルな検索プロンプトに変更

```typescript
// Before
export function buildFileSearchPrompt(
  query: string,
  availableCategories: string[],
  numResults: number
): string

// After
export function buildFileSearchPrompt(
  query: string,
  numResults: number
): string
```

### 4. `src/server/lib/gemini/file-search/parser.ts`
- `parseSearchResults` からマニフェスト依存を削除
- URLマッピングを固定値または削除

### 5. `src/server/lib/gemini/file-search/manifest.ts`
- 削除可能（RAG検索では不要に）
- ただし他で使用していないか確認が必要

### 6. `src/server/lib/gemini/file-search/types.ts`
- `SearchOptions` から不要な型を削除（必要に応じて）

## テスト対象

- `tests/unit/server/lib/gemini/file-search-service.test.ts`
- 変更に合わせてモックとアサーションを更新

## 実装順序

1. `prompts.ts` - カテゴリ依存を削除
2. `parser.ts` - マニフェスト依存を削除
3. `file-search-store.ts` - シグネチャ変更
4. `index.ts` - マニフェスト読み込みを削除
5. テスト更新
6. `manifest.ts` の削除判断

## 影響範囲

| コンポーネント | 影響 |
|---------------|------|
| RAG検索 | ○ 変更あり（マニフェスト不要に） |
| 管理画面（一覧表示） | × 影響なし（Store APIのcustomMetadataで切り分け） |
| 管理画面（アップロード中表示） | △ ローカル環境のみ影響あり（後述） |
| アップロードスクリプト | × 影響なし |
| データファイル | △ `data/file-store-manifest.json` は不要に |

### 管理画面の詳細調査結果

**一覧表示のデータソース:**
- メイン: File Search Store API直接（`source_type` customMetadataで qa/web を切り分け）
- サブ: manifest（ローカル環境のみ、アップロード中ファイル表示用）

**書き込み時のmanifest更新:**
- Vercel（本番）: 全てスキップ（ファイルシステム書き込み不可）
- ローカル: アップロード/削除時に更新

**結論:**
- URL管理タブ/ファイル管理タブの切り分けは**manifest不要**（Store APIで実現済み）
- ローカル環境で「アップロード中」ファイルが一覧に表示されなくなる（本番は既に非表示）

## 工数見積（AI実施）

### 作業内訳

| # | タスク | 詳細 | AI工数 |
|---|--------|------|--------|
| 1 | Feature Flag追加 | `USE_MANIFEST_SEARCH` 環境変数でRollback可能に | 0.1h |
| 2 | index.ts 修正 | `loadManifest()` 削除、Store名を環境変数から直接取得 | 0.1h |
| 3 | file-search-store.ts 修正 | 関数シグネチャ変更、カテゴリ抽出ロジック削除 | 0.2h |
| 4 | prompts.ts 修正 | カテゴリパラメータ削除、プロンプト簡素化 | 0.1h |
| 5 | parser.ts 修正 | マニフェスト依存削除、URLマッピング簡素化 | 0.2h |
| 6 | legacy-search.ts 対応判断 | 削除 or フォールバック維持の検討・実装 | 0.2h |
| 7 | manifest.ts 削除 | ファイル削除、import参照の整理 | 0.1h |
| 8 | types.ts 修正 | 不要になった型定義の削除・整理 | 0.1h |
| 9 | テストファイル更新 | モック修正、アサーション更新 | 0.5h |
| 10 | 統合テスト・動作確認 | テスト実行、エラー修正 | 0.3h |
| 11 | PR作成・レビュー対応 | PR作成、軽微な修正対応 | 0.2h |
| | **AI作業小計** | | **2.1h** |
| | リスクバッファ（25%） | 予期せぬ依存関係・エラー対応 | 0.5h |
| 12 | 人間による最終確認 | PR確認・マージ承認・本番動作確認 | 1.0h |
| | **合計** | | **3.6h** |

### 費用計算

| 項目 | 計算式 | 金額 |
|------|--------|------|
| 工数 | 3.6時間 | - |
| 基本時給 | ¥15,000/h | - |
| 利益率 | 1.5倍 | - |
| 時給単価 | ¥15,000 × 1.5 | ¥22,500/h |
| **合計費用** | 3.6h × ¥22,500 | **¥81,000** |

### 備考

- コード変更・テスト実行はAIが自動実行
- 人間による最終確認（PR確認・マージ承認・本番動作確認）を1h含む
- Vercel Preview環境での動作確認はAIがブラウザテストで実施可能

### リスク・注意事項（O3レビュー反映）

| リスク | 影響度 | 対策 |
|--------|--------|------|
| legacy-search.ts の扱い | 中 | File Search Store未設定時のフォールバック動作要確認 |
| URLマッピング喪失 | 低 | 固定URL（wmg2027.jp）への統一。将来的に`sourceUrl`メタデータ追加 |
| テストカバレッジ低下 | 低 | 新しいテストケースで補完 |
| 検索品質劣化 | 中 | `customMetadata`フィルタ活用、k件数調整で対応 |
| Rollback困難 | 中 | Feature Flag `USE_MANIFEST_SEARCH` で段階的移行 |
| Indexing lag | 低 | 既存UI/UXで対応済み（アップロード後の表示遅延は許容範囲） |

### 前提条件
- `FILE_SEARCH_STORE_NAME` 環境変数が全環境で設定済み
- マニフェストJSONファイルは削除可能

### スコープ外
- Vercelデプロイ設定変更
- File Search Store自体の設定変更
- ドキュメント更新

## 推奨実装順序

1. **Phase 1**: `file-search-store.ts` と `prompts.ts` の修正
2. **Phase 2**: `parser.ts` の簡素化
3. **Phase 3**: `manifest.ts` 削除、テスト更新
4. **Phase 4**: `legacy-search.ts` 削除判断（別Issue推奨）

## 今後の検討事項（本計画の範囲外）

- 検索結果の優先順位付け（競技別実施要項を優先等）
- source_typeの拡張（pdf, document等の追加）
