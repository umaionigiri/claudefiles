---
name: gemini-research
description: |
  Gemini MCPを通じて外部リサーチを効率的に実行。
  ベストプラクティス、最新技術トレンド、設計パターンの調査に使用。
  トリガー: 「ベストプラクティスを調査」「最新技術トレンド」「ライブラリを比較」「設計パターンを調査」「外部情報を検索」
allowed-tools: mcp__gemini__*
version: 1.0.0
---

# Gemini Research Skill

Gemini MCP を活用した外部リサーチスキル。

## ワークフロー

```mermaid
flowchart TD
    A[リサーチ要求] --> B[タスク分析]
    B --> C{内部情報で解決?}
    C -->|Yes| D[内部情報で回答]
    C -->|No| E[リサーチ質問作成]
    E --> F[コンテキスト追加]
    F --> G[Gemini タスク実行]
    G --> H[結果分析]
    H --> I{追加調査必要?}
    I -->|Yes| J[深掘り質問作成]
    J --> G
    I -->|No| K[結果統合]
    K --> L[回答作成]
    L --> M[完了]
```

## Step 1: タスク分析

リサーチが必要かどうかを判断:

| 判断基準 | 対応 |
|----------|------|
| 既知の基本情報 | 内部知識で回答 |
| 最新情報が必要 | Gemini でリサーチ |
| 比較検討が必要 | Gemini でリサーチ |
| ベストプラクティス | Gemini でリサーチ |

## Step 2: リサーチ質問作成

効果的な質問の要素:

- **具体性**: 曖昧さを排除
- **コンテキスト**: 言語、フレームワーク、バージョン
- **観点**: 比較軸、評価基準を明示

## Step 3: Gemini タスク実行

```
mcp__gemini__task({
  task: "具体的なリサーチ内容",
  cwd: "/path/to/project"
})
```

## Step 4: 結果統合

- 複数の情報源を統合
- プロジェクトへの適用可能性を評価
- 推奨事項をまとめる

## クイックリファレンス

### ユースケース別プロンプト

| ユースケース | プロンプト例 |
|--------------|--------------|
| 技術選定 | `Compare X vs Y vs Z for [use case]. Consider: performance, learning curve, ecosystem` |
| 設計パターン | `Best practices for implementing [pattern] in [language/framework]. Include code examples` |
| セキュリティ | `Security considerations for [implementation]. Include OWASP guidelines` |
| パフォーマンス | `Performance optimization strategies for [scenario]. Include benchmarks if available` |
| アーキテクチャ | `Architecture patterns for [requirement]. Compare trade-offs` |

### 効果的なプロンプト構成

| 要素 | 内容 | 例 |
|------|------|-----|
| 目的 | 何を知りたいか | `Compare...`, `Best practices for...` |
| コンテキスト | 技術スタック | `in TypeScript`, `for React app` |
| 制約 | 条件・要件 | `for high-traffic`, `with limited budget` |
| 観点 | 評価軸 | `Consider: X, Y, Z` |
| 出力形式 | 期待する形式 | `Include code examples`, `with pros/cons table` |

### リサーチカテゴリ

| カテゴリ | 説明 |
|----------|------|
| ベストプラクティス | 推奨される実装方法 |
| 技術トレンド | 最新の技術動向 |
| 設計パターン | アーキテクチャ・コードパターン |
| セキュリティ | セキュリティ考慮事項 |
| パフォーマンス | 最適化手法 |
| ライブラリ比較 | 選定の判断材料 |

## プロンプトテンプレート

### 技術選定

```
Compare [Technology A] vs [Technology B] vs [Technology C] for [specific use case].

Context:
- Application type: [web app / mobile / API / etc.]
- Scale: [small / medium / large]
- Team experience: [beginner / intermediate / expert]

Evaluation criteria:
- Performance
- Learning curve
- Ecosystem and community support
- Long-term maintenance
- Cost (licensing, infrastructure)

Provide a comparison table and recommendation.
```

### 設計パターン

```
What are the best practices for implementing [pattern/feature] in [language/framework]?

Requirements:
- [Requirement 1]
- [Requirement 2]

Include:
- Code examples
- Common pitfalls to avoid
- Testing strategies
```

### セキュリティレビュー

```
Review security considerations for implementing [feature] in [technology].

Focus areas:
- Authentication/Authorization
- Input validation
- Data protection
- OWASP Top 10 relevance

Provide specific recommendations and code examples.
```

## 検証チェックリスト

### リサーチ前チェック

- [ ] 質問が具体的である
- [ ] 必要なコンテキストを含む
- [ ] 評価軸が明確

### リサーチ中チェック

- [ ] 結果が質問に対応している
- [ ] 複数の観点をカバー
- [ ] 具体例を含む

### リサーチ後チェック

- [ ] 結果をプロジェクトに適用可能
- [ ] 推奨事項が明確
- [ ] 追加調査の必要性を評価

## 統合フロー

```mermaid
flowchart LR
    A[Claude] -->|タスク分析| B[リサーチ必要性判断]
    B -->|外部情報必要| C[Gemini]
    C -->|結果| D[Claude]
    D -->|統合・適用| E[最終回答]
```

## 重要事項

- **具体的な質問**: 曖昧な質問は曖昧な回答を生む
- **コンテキスト提供**: 言語・フレームワーク・バージョンを明記
- **複数観点**: 単一の観点ではなく多角的に評価
- **結果の検証**: リサーチ結果は批判的に評価
