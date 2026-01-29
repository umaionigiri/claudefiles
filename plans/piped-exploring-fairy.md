# チャットボットアクセス制御変更計画

## 概要
WMG2027 AIチャットボットの `ALLOWED_ORIGINS` に新しいドメインを追加する。

## 追加するURL
| ドメイン | 用途 |
|---------|------|
| `https://form.wmg2027.jp` | 本番環境のフォームサイト |
| `https://dev.wmg2027.jp` | 開発環境サイト |

## 変更対象ファイル
- `src/app/api/chat/route.ts` (行20-30付近の `ALLOWED_ORIGINS` 配列)

## 実装手順

### 1. Worktree作成
```bash
git worktree add .worktrees/feature-access-control -b feature/add-allowed-origins develop
```

### 2. コード変更
`ALLOWED_ORIGINS` 配列に2つのドメインを追加：

```typescript
const ALLOWED_ORIGINS: string[] = [
  // 本番環境
  'https://wmg2027.jp',
  'https://www.wmg2027.jp',
  'https://form.wmg2027.jp',  // ← 追加
  // ステージング・開発環境
  'https://develop.wmg2027.jp',
  'https://dev.wmg2027.jp',   // ← 追加
  // チャットボット自身（直接アクセス用）
  'https://wmg2027-ai-chatbot.vercel.app',
  // Preview環境
  'https://wmg2027-chatbot-preview.vercel.app',
];
```

### 3. テスト実行
```bash
pnpm test
```

### 4. コミット・PR作成
- ブランチ: `feature/add-allowed-origins`
- ベースブランチ: `develop`
- コミットメッセージ: `feat: form.wmg2027.jp と dev.wmg2027.jp をアクセス許可リストに追加`

## 検証方法
1. ユニットテストがパスすることを確認
2. Preview環境でCORS設定が正しく動作することを確認（手動）
   - `https://form.wmg2027.jp` からのリクエストが許可される
   - `https://dev.wmg2027.jp` からのリクエストが許可される

## リスク
- 低：既存の許可リストへの追加のみ
- セキュリティ上の新しいドメインは信頼できるWMG公式ドメイン
