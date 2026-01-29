# Vercel Runtime ログ保管機能 実装計画

## 概要

Vercel Log Drains + 自作エンドポイントでRuntimeログを保管する最小実装。

## 推奨アプローチ

**Log Drains + 自作受信エンドポイント**

| 観点 | 理由 |
|------|------|
| 外部依存 | 低（Vercel内完結） |
| コスト | 無料（Pro/Enterpriseで利用可能） |
| 拡張性 | 提案書オプションC（Neon + Metabase）への移行パス確保 |

## 実装ステップ

### Step 0: Worktree作成

```bash
git worktree add .worktrees/feature/log-drains -b feature/log-drains develop
cd .worktrees/feature/log-drains
```

### Step 1: 型定義作成

**新規ファイル**: `src/types/vercel-logs.d.ts`

Vercel Log Drainsのログエントリ型（source, timestamp, level, proxy等）

### Step 2: 受信エンドポイント作成

**新規ファイル**: `src/app/api/logs/drain/route.ts`

- POST: NDJSONでログを受信、認証検証後に処理
- GET: Vercel検証リクエストに応答
- Runtime: `nodejs`（Edge不可）

### Step 3: ログ処理ハンドラ

**新規ファイル**: `src/server/lib/logs/drain-handler.ts`

- `/api/chat`関連のlambda/edgeログのみフィルタ
- 必要フィールドのみ抽出（id, timestamp, level, path, statusCode等）

### Step 4: ストレージ層

**新規ファイル**: `src/server/lib/logs/storage.ts`

最小実装: Vercel Blob Storage（JSONL形式、日付別ファイル）

> **注意**: Blob Storageは追記不可。代替案: Vercel KVバッファ or Neon PostgreSQL

### Step 5: 設定更新

**vercel.json**: drain用エンドポイントのmaxDuration追加

### Step 6: 環境変数

```bash
LOG_DRAIN_SECRET=<generated-secret>
BLOB_READ_WRITE_TOKEN=<blob-token>  # Blob使用時
```

### Step 7: Vercel Dashboard設定

1. Settings → Drains → Add Drain
2. URL: `https://wmg2027-ai-chatbot.vercel.app/api/logs/drain`
3. Format: NDJSON
4. Sources: lambda, edge
5. Secret生成 → 環境変数に設定

## 新規ファイル一覧

| ファイル | 用途 |
|----------|------|
| `src/types/vercel-logs.d.ts` | Vercelログ型定義 |
| `src/app/api/logs/drain/route.ts` | 受信エンドポイント |
| `src/server/lib/logs/drain-handler.ts` | ログ処理ロジック |
| `src/server/lib/logs/storage.ts` | 保存先抽象化 |
| `tests/unit/server/lib/logs/drain-handler.test.ts` | ユニットテスト |

## 関連ファイル（変更）

| ファイル | 変更内容 |
|----------|----------|
| `vercel.json` | drain用runtime設定追加 |
| `.env.example` | 環境変数追記 |

## 検証方法

### ローカルテスト

```bash
curl -X POST http://localhost:3000/api/logs/drain \
  -H "Content-Type: application/x-ndjson" \
  -H "x-vercel-verify: secret" \
  -d '{"id":"test1","source":"lambda","timestamp":1706140800000,"level":"info","proxy":{"path":"/api/chat","method":"POST"}}'
```

### 本番確認

1. チャットAPIにリクエスト送信
2. Vercel Dashboard → Drains で配信状況確認
3. Blob Storage / DB でログ保存確認

## 制約・注意点

| 項目 | 内容 |
|------|------|
| Edge Runtime | `/tmp`書き込み不可 → Node.js Runtime使用 |
| Vercel Blob | 追記不可 → KVバッファ or DB検討 |
| Log Drains | Pro/Enterprise限定（現行プラン対応済み） |
| PII | 既存pii.tsを参照し、個人情報はマスク |

## 将来の拡張

フェーズ1（本実装）→ フェーズ2（Neon PostgreSQL + Metabase）への移行時は`storage.ts`の実装変更のみで対応可能。

参照: `docs/specifications/proposals/wmg2027-log-analysis-proposal.md`
