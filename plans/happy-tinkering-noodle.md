# GCP Gemini API トークン使用量確認方法 調査結果

## 結論

**GCPコンソールの標準APIメトリクスではトークン数は表示されません。**

これはGoogleの仕様であり、リクエスト数やエラー率は見れますが、トークン消費量を見るには別の方法が必要です。

---

## トークン使用量を確認する方法

### 方法1: Google AI Studio（推奨・最も簡単）

**URL**: https://aistudio.google.com/apikey

1. 使用しているAPIキーでログイン
2. 「Usage」タブでトークン消費量を確認

**注意**: Vertex AI経由ではなく、Generative Language API（Google AI）を使用している場合に有効

### 方法2: Firebase AI Monitoring

Firebase ConsoleのAI Monitoringでは以下が確認可能：
- リクエスト数、レイテンシ、エラー
- **モダリティ別トークン使用量**
- リクエストの入出力内容

**セットアップが必要**

### 方法3: BigQuery Billing Export（詳細分析用）

1. GCPコンソール → Billing → Billing export → BigQuery連携を有効化
2. APIコール時にラベルを付与（コード変更必要）
3. BigQueryでSKU単位のトークン消費をクエリ

```sql
SELECT
  sku.description,
  SUM(usage.amount) as total_usage,
  SUM(cost) as total_cost
FROM `project.dataset.gcp_billing_export_v1_*`
WHERE service.description = 'Generative Language API'
  AND _PARTITIONTIME >= '2024-12-01'
GROUP BY sku.description
```

### 方法4: Billing Reports からの逆算（現実的な代替案）

GCPコンソール → Billing → Reports で費用が確認可能。

**12月実績 ¥2,048 からの推定**:

| モデル | 入力料金 | 出力料金 | 推定利用量 |
|--------|---------|---------|-----------|
| Gemini 2.0 Flash | $0.10/1M | $0.40/1M | 約20-30万トークン |
| Gemini 1.5 Flash | $0.075/1M | $0.30/1M | 約25-40万トークン |

※ 入出力比率により変動

---

## WMG2027プロジェクトの現状

- **使用API**: Generative Language API（Google AI経由）
- **アプリ側ログ**: トークン使用量のログ機能なし
- **確認可能な情報**: GCP Billing の費用のみ

---

## 推奨アクション

| 優先度 | アクション | 効果 |
|--------|-----------|------|
| 1 | Google AI Studio で確認 | 即座にトークン消費を確認可能 |
| 2 | アプリにログ機能追加 | 今後のリクエストごとのトークン追跡 |
| 3 | BigQuery Export設定 | 詳細な費用分析・予測 |

---

## 参考リンク

- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Billing](https://ai.google.dev/gemini-api/docs/billing)
- [Firebase AI Monitoring](https://firebase.google.com/docs/ai-logic/monitoring)
- [GCP Billing Export to BigQuery](https://cloud.google.com/billing/docs/how-to/export-data-bigquery)
