---
name: gemini-research
description: |
  Gemini MCPを通じて外部リサーチを効率的に実行。
  ベストプラクティス、最新技術トレンド、設計パターンの調査に使用。
  トリガー: 「ベストプラクティスを調査」「最新技術トレンド」「ライブラリを比較」「設計パターンを調査」「外部情報を検索」
allowed-tools: mcp__gemini__*
version: 1.0.0
---

# Gemini リサーチスキル

## いつ使うか

| 判断基準 | 対応 |
|----------|------|
| 既知の基本情報 | 内部知識で回答（Gemini 不要） |
| 最新情報が必要 | Gemini でリサーチ |
| 比較検討が必要 | Gemini でリサーチ |
| ベストプラクティス | Gemini でリサーチ |

## リサーチ実行

```
mcp__gemini__task({
  task: "具体的なリサーチ内容",
  cwd: "/path/to/project"
})
```

## ユースケース別プロンプト例

| ユースケース | プロンプト構成 |
|--------------|---------------|
| 技術選定 | `Compare X vs Y for [use case]. Consider: performance, learning curve, ecosystem` |
| 設計パターン | `Best practices for [pattern] in [language/framework]. Include code examples` |
| セキュリティ | `Security considerations for [implementation]. Include OWASP guidelines` |
| パフォーマンス | `Performance optimization for [scenario]. Include benchmarks if available` |
| アーキテクチャ | `Architecture patterns for [requirement]. Compare trade-offs` |

## 効果的なプロンプト構成

| 要素 | 内容 |
|------|------|
| 目的 | 何を知りたいか（`Compare...`, `Best practices for...`） |
| コンテキスト | 技術スタック（`in TypeScript`, `for React app`） |
| 制約 | 条件・要件（`for high-traffic`, `with limited budget`） |
| 観点 | 評価軸（`Consider: X, Y, Z`） |
| 出力形式 | 期待する形式（`Include code examples`, `with pros/cons table`） |

## 検証チェックリスト

**リサーチ前:**
- [ ] 質問が具体的で、コンテキスト・評価軸が明確

**リサーチ後:**
- [ ] 結果をプロジェクトに適用可能か評価
- [ ] 推奨事項が明確
- [ ] 追加調査の必要性を判断
