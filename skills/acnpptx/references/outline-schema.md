# Outline Schema — JSON 骨子フォーマット

スライド生成前に JSON 骨子を作成してユーザーに確認する。
`scripts/outline.py` で生成・バリデーション・Markdown変換できる。

## 使い方

```python
from outline import generate_outline, format_outline_md, validate_outline, save_outline

# 1. 骨子を生成
outline = generate_outline(
    title="AIISプロジェクト概要",
    language="ja",
    sections=["背景", "ソリューション", "効果", "まとめ"]
)

# 2. Markdownで確認用表示
print(format_outline_md(outline))

# 3. バリデーション（多様性チェック含む）
valid, errors, warnings = validate_outline(outline)

# 4. ファイル保存
save_outline(outline, "outline.json")
```

---

## トップレベルフィールド

```json
{
  "title":    "プレゼンタイトル",
  "subtitle": "サブタイトル（任意）",
  "date":     "2026-03",
  "author":   "作成者名（任意）",
  "language": "ja",
  "slides":   [ ... ]
}
```

---

## スライド共通フィールド

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `pattern` | ○ | パターンID ("cover", "section", "A"–"R") |
| `title` | ○ | スライドタイトル |
| `breadcrumb` | × | パンくず "セクション > トピック" |

---

## パターン別フィールド

### cover（表紙）
```json
{
  "pattern": "cover",
  "title": "プレゼンタイトル",
  "subtitle": "2026年3月"
}
```

### section（セクション区切り）
```json
{
  "pattern": "section",
  "title": "セクション名",
  "subtitle": "任意のサブテキスト"
}
```

### A（タイトル＋本文）
```json
{
  "pattern": "A",
  "title": "スライドタイトル",
  "breadcrumb": "セクション > トピック",
  "lead": "リード文（任意）",
  "bullets": ["ポイント1", "ポイント2", "ポイント3"]
}
```

### B（2カラム）
```json
{
  "pattern": "B",
  "title": "スライドタイトル",
  "left":  { "header": "左見出し", "bullets": ["項目A", "項目B"] },
  "right": { "header": "右見出し", "bullets": ["項目C", "項目D"] }
}
```

### D（キーメッセージ）
```json
{
  "pattern": "D",
  "title": "スライドタイトル（小）",
  "message": "大きく伝えたい1文",
  "supporting": "補足説明。詳細や根拠を記載。"
}
```

### E（GTアイコン箇条書き）
```json
{
  "pattern": "E",
  "title": "スライドタイトル",
  "items": [
    { "headline": "見出し1", "detail": "詳細説明テキスト" },
    { "headline": "見出し2", "detail": "詳細説明テキスト" }
  ]
}
```

### F（カードグリッド 2×2）
```json
{
  "pattern": "F",
  "title": "スライドタイトル",
  "cards": [
    { "title": "カード1", "body": "説明テキスト" },
    { "title": "カード2", "body": "説明テキスト" },
    { "title": "カード3", "body": "説明テキスト" },
    { "title": "カード4", "body": "説明テキスト" }
  ]
}
```

### G（テーブル）
```json
{
  "pattern": "G",
  "title": "スライドタイトル",
  "headers": ["列1", "列2", "列3"],
  "rows": [
    ["データ1", "データ2", "データ3"],
    ["データ4", "データ5", "データ6"]
  ]
}
```

### H（タイムライン / プロセス）
```json
{
  "pattern": "H",
  "title": "スライドタイトル",
  "steps": [
    { "label": "フェーズ1", "detail": "説明" },
    { "label": "フェーズ2", "detail": "説明" },
    { "label": "フェーズ3", "detail": "説明" }
  ]
}
```

### I（アジェンダ）
```json
{
  "pattern": "I",
  "title": "アジェンダ",
  "items": ["1. 背景", "2. ソリューション", "3. まとめ"],
  "active": null
}
```
`active` は現在のセクション番号（0始まり）または `null`。

### J（KPI / 数値実績）
```json
{
  "pattern": "J",
  "title": "成果サマリー",
  "kpis": [
    { "value": "82%", "label": "KPI達成率", "detail": "前年比+12%" },
    { "value": "1.8x", "label": "生産性向上", "detail": "AI導入後" },
    { "value": "60日", "label": "リード削減", "detail": "期間短縮" }
  ]
}
```

### K（3カラム）
```json
{
  "pattern": "K",
  "title": "スライドタイトル",
  "columns": [
    { "header": "柱1", "bullets": ["点A", "点B"] },
    { "header": "柱2", "bullets": ["点C", "点D"] },
    { "header": "柱3", "bullets": ["点E", "点F"] }
  ]
}
```

### L（Do / Don't）
```json
{
  "pattern": "L",
  "title": "推奨事項と注意点",
  "do":   { "header": "✓ 推奨", "bullets": ["積極的にやること"] },
  "dont": { "header": "✗ 避けること", "bullets": ["やってはいけないこと"] }
}
```

### M（チャート）
```json
{
  "pattern": "M",
  "title": "スライドタイトル",
  "breadcrumb": "データ > 実績",
  "chart_type": "column",
  "chart_title": "グラフタイトル（任意）",
  "categories": ["Q1", "Q2", "Q3", "Q4"],
  "series": [
    { "name": "2025年", "values": [100, 120, 130, 150] },
    { "name": "2026年", "values": [110, 135, 145, 170] }
  ],
  "description": "左側に表示する補足テキスト（任意）"
}
```

`chart_type`: `"column"` | `"bar"` | `"line"` | `"pie"` | `"stacked_column"` | `"area"`

### N（チーム紹介）
```json
{
  "pattern": "N",
  "title": "チーム紹介",
  "members": [
    { "name": "山田 太郎", "title": "プロジェクトマネージャー", "detail": "10年以上の経験", "photo": null },
    { "name": "鈴木 花子", "title": "テクニカルリード", "detail": "AI/ML専門", "photo": null }
  ]
}
```

### P（シェブロンフロー）
```json
{
  "pattern": "P",
  "title": "導入プロセス",
  "steps": [
    { "label": "計画", "detail": "要件定義・スコープ設定" },
    { "label": "設計", "detail": "アーキテクチャ設計" },
    { "label": "開発", "detail": "実装・単体テスト" },
    { "label": "テスト", "detail": "結合テスト・UAT" },
    { "label": "リリース", "detail": "本番デプロイ" }
  ]
}
```

### Q（アイコングリッド）
```json
{
  "pattern": "Q",
  "title": "対応分野",
  "items": [
    { "keyword": "cloud", "label": "クラウド" },
    { "keyword": "ai", "label": "AI/ML" },
    { "keyword": "data", "label": "データ分析" },
    { "keyword": "security", "label": "セキュリティ" },
    { "keyword": "team", "label": "組織変革" },
    { "keyword": "chart", "label": "実績管理" }
  ],
  "cols": 3
}
```

### R（スプリットビジュアル）
```json
{
  "pattern": "R",
  "title": "スライドタイトル",
  "visual": null,
  "lead": "リード文",
  "bullets": ["ポイント1", "ポイント2"]
}
```

### S（フレームワークマトリクス）
```json
{
  "pattern": "S",
  "title": "スライドタイトル",
  "headers": ["", "列ヘッダーA", "列ヘッダーB"],
  "row_labels": ["行ラベル1", "行ラベル2"],
  "rows": [
    ["課題1の説明", "要諦1"],
    ["課題2の説明", "要諦2"]
  ]
}
```

### T（2セクション+矢印）
```json
{
  "pattern": "T",
  "title": "スライドタイトル",
  "sections": [
    { "label": "背景", "body": "• 背景説明1\n• 背景説明2" },
    { "label": "提案", "body": "• 提案内容1\n• 提案内容2" }
  ]
}
```
`sections` は2〜4個。3個以上で3-Section Cascadeバリアント。

### U（アイコン付き3列+フッター）
```json
{
  "pattern": "U",
  "title": "スライドタイトル",
  "columns": [
    { "icon": "cloud", "header": "柱1", "bullets": ["点A", "点B"] },
    { "icon": "ai", "header": "柱2", "bullets": ["点C", "点D"] },
    { "icon": "data", "header": "柱3", "bullets": ["点E", "点F"] }
  ],
  "footer": "まとめテキスト"
}
```

### V（番号付きカードグリッド）
```json
{
  "pattern": "V",
  "title": "スライドタイトル",
  "cards": [
    { "title": "カード1", "body": "• 説明" },
    { "title": "カード2", "body": "• 説明" }
  ],
  "n_cols": 3,
  "highlight_indices": [0, 3]
}
```

### W（大数値統計）
```json
{
  "pattern": "W",
  "title": "スライドタイトル",
  "stats": [
    { "value": "> 50%", "label": "ラベル", "detail": "説明", "source": "出典" }
  ]
}
```

### X（フェーズ付きステップチャート）
```json
{
  "pattern": "X",
  "title": "スライドタイトル",
  "phases": [
    { "label": "フェーズ1", "steps": [
      { "title": "ステップ1", "subtitle": "サブ", "bullets": ["内容1"] }
    ]}
  ]
}
```

### Y（ガントチャート）
```json
{
  "pattern": "Y",
  "title": "スライドタイトル",
  "months": ["1月", "2月", "3月"],
  "rows": [
    { "label": "フェーズ1", "is_phase": true, "bar": null },
    { "label": "  タスク1", "is_phase": false, "bar": [1, 2] }
  ]
}
```

### Z（成熟度評価）
```json
{
  "pattern": "Z",
  "title": "スライドタイトル",
  "levels": ["基本", "発展途上", "先進的", "リーディング"],
  "capabilities": [
    { "name": "戦略", "current": 0, "target": 2 }
  ]
}
```

### AA（2×2マトリクス）
```json
{
  "pattern": "AA",
  "title": "スライドタイトル",
  "quadrants": ["Quick Win", "Strategic", "Avoid", "Big Bet"],
  "x_axis": "難易度", "y_axis": "インパクト",
  "items": [
    { "num": 1, "name": "施策名", "q": 0, "x_ratio": 0.35, "y_ratio": 0.30 }
  ]
}
```

### AB（ロジックツリー）
```json
{
  "pattern": "AB",
  "title": "スライドタイトル",
  "variant": "horizontal",
  "tree": {
    "label": "根本課題",
    "children": [
      { "label": "要因A", "children": [{ "label": "サブ要因" }] }
    ]
  }
}
```
`variant`: `"horizontal"`（左→右）または `"vertical"`（上→下）

### AC（積み上げピラミッド）
```json
{
  "pattern": "AC",
  "title": "スライドタイトル",
  "layers": [
    { "label": "Infrastructure", "sub": "基盤", "fill": "darkest" },
    { "label": "Value", "sub": "価値", "fill": "lightest" }
  ]
}
```
`layers` は下→上の順。

### AD（RAGダッシュボード）
```json
{
  "pattern": "AD",
  "title": "スライドタイトル",
  "status_items": [
    { "label": "Time", "rag": "green", "comment": "コメント" }
  ],
  "issues": [
    { "issue": "課題内容", "owner": "担当者", "due": "MM/DD" }
  ]
}
```

### AE（ベン図）
```json
{
  "pattern": "AE",
  "title": "スライドタイトル",
  "circles": ["概念1", "概念2", "概念3"],
  "center_label": "交差点ラベル"
}
```

### AF（プルクォート）
```json
{
  "pattern": "AF",
  "title": "スライドタイトル",
  "quote": "引用テキスト",
  "attribution": "— 発言者名, 肩書き"
}
```

### AG（アーキテクチャ / コネクター図）
```json
{
  "pattern": "AG",
  "title": "システム構成図",
  "nodes": [
    { "id": "web", "label": "Web App", "x": 1, "y": 1, "w": 2, "h": 1 },
    { "id": "api", "label": "API Gateway", "x": 4, "y": 1, "w": 2, "h": 1 },
    { "id": "db",  "label": "Database", "x": 7, "y": 1, "w": 2, "h": 1 }
  ],
  "connectors": [
    { "from": "web", "to": "api", "label": "REST" },
    { "from": "api", "to": "db", "label": "SQL" }
  ]
}
```

### AH（デシジョンマトリクス — ◎○△×評価）
```json
{
  "pattern": "AH",
  "title": "ツール比較評価",
  "headers": ["", "コスト", "機能", "拡張性", "サポート"],
  "rows": [
    { "label": "Option A", "scores": ["◎", "○", "△", "○"], "recommended": true },
    { "label": "Option B", "scores": ["○", "◎", "○", "△"], "recommended": false },
    { "label": "Option C", "scores": ["△", "○", "◎", "○"], "recommended": false }
  ]
}
```
`recommended: true` の行は CORE_PURPLE で強調される。

### AI（評価スコアカード）
```json
{
  "pattern": "AI",
  "title": "ベンダー評価結果",
  "headers": ["ベンダー", "技術力", "価格", "実績", "総評"],
  "rows": [
    { "values": ["A社", "4.5", "3.0", "4.0", "技術力が突出。コスト面は要交渉"], "recommended": true },
    { "values": ["B社", "3.5", "4.5", "3.5", "コスパ重視なら最適"], "recommended": false }
  ]
}
```
`recommended: true` の行にハイライト。最終列は総評テキスト（→矢印付き）。

### AJ（レーダーチャート）
```json
{
  "pattern": "AJ",
  "title": "スキルアセスメント",
  "categories": ["戦略", "技術", "マネジメント", "コミュニケーション", "リーダーシップ"],
  "series": [
    { "name": "現状", "values": [3, 4, 2, 5, 3] },
    { "name": "目標", "values": [5, 5, 4, 5, 5] }
  ]
}
```
線のみ・塗りなし。`values` は 0〜5 スケール。

### AK（カレンダー — 3ヶ月）
```json
{
  "pattern": "AK",
  "title": "Q1 イベントカレンダー",
  "start_month": "2026-01",
  "months": 3,
  "events": [
    { "date": "2026-01-15", "label": "キックオフ", "color": "primary" },
    { "date": "2026-02-28", "label": "中間レビュー", "color": "accent" },
    { "date": "2026-03-31", "label": "最終報告", "color": "primary" }
  ],
  "holidays": ["2026-01-01", "2026-01-13", "2026-02-11", "2026-03-20"]
}
```

### AL（ビジネスモデルキャンバス）
```json
{
  "pattern": "AL",
  "title": "ビジネスモデル分析",
  "blocks": {
    "key_partners":    ["パートナー1", "パートナー2"],
    "key_activities":  ["活動1", "活動2"],
    "key_resources":   ["リソース1"],
    "value_propositions": ["提供価値1", "提供価値2"],
    "customer_relationships": ["関係性1"],
    "channels":        ["チャネル1", "チャネル2"],
    "customer_segments": ["セグメント1"],
    "cost_structure":  ["コスト1", "コスト2"],
    "revenue_streams": ["収益源1"]
  }
}
```
BMC 9ブロック標準レイアウト。

### AM（インタビューカード / ペルソナ）
```json
{
  "pattern": "AM",
  "title": "ユーザーインタビュー",
  "persona": {
    "name": "田中 一郎",
    "role": "事業部長",
    "department": "デジタル推進部",
    "photo": null
  },
  "qa": [
    { "q": "現在の課題は？", "a": "データ活用が属人化しており、組織的な意思決定に活かせていない" },
    { "q": "理想の状態は？", "a": "ダッシュボードで全部門がリアルタイムにKPIを確認できる状態" }
  ]
}
```
左サイドバー（LIGHTEST_PURPLE）にペルソナ情報、右側に Q&A リスト。

### AN（レイヤー図 — システム構成）
```json
{
  "pattern": "AN",
  "title": "アーキテクチャレイヤー",
  "layers": [
    { "label": "Presentation Layer", "detail": "React / Next.js フロントエンド", "color": "lightest" },
    { "label": "Application Layer", "detail": "Node.js API サーバー、認証・認可", "color": "light" },
    { "label": "Domain Layer", "detail": "ビジネスロジック、ルールエンジン", "color": "medium" },
    { "label": "Infrastructure Layer", "detail": "AWS, PostgreSQL, Redis", "color": "darkest" }
  ]
}
```
`layers` は上→下の順。`color`: `lightest` / `light` / `medium` / `darkest` でグラデーション。

---

## バリデーションルール

- `pattern` は定義済みパターンIDであること（cover, section, A〜AN。Oは欠番）
- パターン M: `chart_type`, `categories`, `series` 必須
- パターン B/L: `left`/`right` または `do`/`dont` 必須
- パターン D: `message` 必須
- パターン E: `items` 必須（1件以上）
- パターン F: `cards` は4個
- パターン G: `headers` と `rows` 必須
- パターン J: `kpis` は1件以上
- パターン K: `columns` は3個
- パターン P: `steps` は3個以上
- パターン T: `sections` は2〜4個
- パターン AB: `tree` にネスト構造、`variant` は `horizontal`/`vertical`
- パターン AC: `layers` は下→上の順（3〜5個）
- パターン AD: `rag` は `green`/`amber`/`red`
- パターン AH/AI: `headers` と `rows` 必須
- パターン AJ: `categories` と `series` 必須
- パターン AL: `blocks` 必須
- パターン AN: `layers` は上→下の順
- スライド全体: `title` 必須
- **多様性チェック**: 同一パターン3回以上 → ERROR、連続同一パターン → WARNING、2回使用 → WARNING

---

## ワークフロー

```
① outline.generate_outline() でスケルトン生成
② format_outline_md() でMarkdown変換 → ユーザーに表示
③ ユーザーが内容を修正・確認
④ validate_outline() でチェック
⑤ PPTX生成スクリプトを作成・実行
```
