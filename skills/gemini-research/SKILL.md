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

## When to Use

| Criteria | Action |
|----------|--------|
| Known basic information | Answer from internal knowledge (no Gemini needed) |
| Latest information needed | Research with Gemini |
| Comparison needed | Research with Gemini |
| Best practices | Research with Gemini |

## Research Execution

```
mcp__gemini__task({
  task: "Specific research content",
  cwd: "/path/to/project"
})
```

## Prompt Examples by Use Case

| Use Case | Prompt Structure |
|----------|-----------------|
| Technology selection | `Compare X vs Y for [use case]. Consider: performance, learning curve, ecosystem` |
| Design patterns | `Best practices for [pattern] in [language/framework]. Include code examples` |
| Security | `Security considerations for [implementation]. Include OWASP guidelines` |
| Performance | `Performance optimization for [scenario]. Include benchmarks if available` |
| Architecture | `Architecture patterns for [requirement]. Compare trade-offs` |

## Effective Prompt Structure

| Element | Content |
|---------|---------|
| Purpose | What you want to know (`Compare...`, `Best practices for...`) |
| Context | Tech stack (`in TypeScript`, `for React app`) |
| Constraints | Conditions/requirements (`for high-traffic`, `with limited budget`) |
| Perspectives | Evaluation axes (`Consider: X, Y, Z`) |
| Output format | Expected format (`Include code examples`, `with pros/cons table`) |

## Verification Checklist

**Pre-research:**
- [ ] Question is specific with clear context and evaluation axes

**Post-research:**
- [ ] Results evaluated for project applicability
- [ ] Recommendations are clear
- [ ] Need for additional research assessed
