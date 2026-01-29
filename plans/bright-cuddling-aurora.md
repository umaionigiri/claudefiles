# EC BPaaS システム構成図 改善計画

## 目的
現在のMermaid形式の構成図を、経営層・非技術者向けにより分かりやすい視覚的なシステム構成図に改善する。

---

## 調査結果サマリ

### 経営層向け構成図のベストプラクティス
- **シンプルさ最優先**: 必要最低限の要素のみ表示
- **階層化・グルーピング**: データソース → 処理 → 出力の流れを明確に
- **配色**: 強調部分のみに色を限定使用
- **専門用語回避**: シンプルな言語で説明

### nano-banana-pro プロンプト設計
- キーワード羅列ではなく**シーンを描写**
- **3〜5文程度**の具体的な記述が最適
- スタイル（モダン、ミニマリスト等）を明示指定

---

## 実行計画

### Step 1: プロンプト作成

EC BPaaS 7ステップ自動戦略最適化の構成図用プロンプト:

```
A clean, professional system architecture diagram for "EC BPaaS - AI-powered E-commerce Strategy Optimization System".

The diagram shows a left-to-right data flow with four main layers:
1. DATA SOURCES (left): GA4 Analytics icon and Shopify icon connected to BigQuery data warehouse
2. AI ANALYSIS ENGINE (center): A large rounded rectangle containing "7-Step Auto Strategy Flow" with numbered steps: State Analysis → Bottleneck Detection → Strategy Generation → ROI Prediction → Priority Decision → Execution Parameters → Learning Loop
3. OUTPUT (right): Dashboard interface showing KPI metrics and recommended actions
4. FEEDBACK LOOP: A curved arrow from Output back to Data Sources

Style: Modern, minimalist corporate presentation style. Use a blue (#2563EB) and teal (#0D9488) gradient color scheme with white backgrounds. Rounded rectangles, clean sans-serif labels, subtle shadows. No technical jargon - labels should be business-friendly like "Data Collection", "AI Analysis", "Insights & Actions".
```

### Step 2: nano-banana-pro で画像生成

**使用ツール**: `mcp__nano-banana-pro__generate_image`

**パラメータ**:
- `prompt`: 上記プロンプト
- `aspectRatio`: "16:9"（プレゼン向け横長）
- `imageSize`: "2K"（高解像度）
- `outputPath`: `/Users/so/MyWorkSpace/scibit/petabit-bpaas/outputs/system-architecture-ec-bpaas.png`

### Step 3: 検証・調整

1. 生成された画像を確認
2. 必要に応じてプロンプトを調整して再生成
3. ラベル・テキストの正確性を確認（AI生成の弱点）

### Step 4: ドキュメント更新

- `estimate-ec-bpaas.md` の構成図セクションを画像参照に更新
- PDF再生成

---

## 代替案（必要に応じて）

nano-banana-proで期待通りの結果が得られない場合:

| 代替手法 | 特徴 |
|----------|------|
| Eraser DiagramGPT | テキスト→図変換AI、技術図に強い |
| Miro AI | フローチャート生成 |
| 手動Mermaid改善 | 現行の図を色・レイアウト調整 |

---

## 成果物

| ファイル | 説明 |
|----------|------|
| `outputs/system-architecture-ec-bpaas.png` | 新システム構成図（画像） |
| `outputs/estimate-ec-bpaas.md` | 更新版見積書 |
| `outputs/estimate-ec-bpaas.pdf` | 更新版PDF |

---

## 検証方法

1. 画像が正常に生成されたか確認
2. 構成図の要素（4層構造、7ステップ、データフロー）が含まれているか確認
3. 経営層向けに分かりやすいか（専門用語なし、シンプル）確認
