---
name: serena-codebase
description: |
  コードベース探索・分析にSerena MCPを使用。トークン効率を最優先。
  シンボル検索を優先し、パターン検索は最終手段として使用。
  トリガー: 「シンボルを探す」「コードベースを検索」「アーキテクチャを分析」「Xの仕組みを調査」「プロジェクト構造を探索」
allowed-tools: mcp__serena__*
version: 1.0.0
---

# Serena Codebase Analysis Skill

## Step 1: Session Initialization

```
mcp__serena__check_onboarding_performed()
mcp__serena__list_memories()
mcp__serena__list_dir({ relative_path: ".", recursive: false })
```

## Step 2: Overview

```
mcp__serena__get_symbols_overview({ relative_path: "src" })
```

## Step 3: Symbol Search (Preferred)

```
mcp__serena__find_symbol({ symbol_name: "ClassName", include_body: false, depth: 1 })
```

## Step 4: Detailed Retrieval

```
mcp__serena__find_symbol({ symbol_name: "ClassName/methodName", include_body: true })
```

## Step 5: Reference Search

```
mcp__serena__find_referencing_symbols({ symbol_name: "targetSymbol" })
```

## Step 6: Symbol Editing (When Needed)

```
mcp__serena__replace_symbol_body({ symbol_name: "ClassName/methodName", new_body: "..." })
```

## Search Priority

| Priority | Tool | Use Case |
|----------|------|----------|
| 1 | `find_symbol` | When symbol name is known |
| 2 | `find_file` | When file name is known |
| 3 | `search_for_pattern` | When above methods fail (last resort) |

## Token Optimization

| Technique | Effect |
|-----------|--------|
| Narrow search path | `src/services/` > `src/` |
| `include_body: false` first | Get overview before details |
| Split retrieval for 500+ line files | Retrieve only needed parts |
| Target: <2000 tokens/search | Avoid large result sets |

## Symbol Operations

| Operation | Tool |
|-----------|------|
| Get overview | `get_symbols_overview` |
| Search symbol | `find_symbol` |
| Search references | `find_referencing_symbols` |
| Replace body | `replace_symbol_body` |
| Insert before | `insert_before_symbol` |
| Insert after | `insert_after_symbol` |
| Rename | `rename_symbol` |

## name_path Patterns

| Pattern | Description |
|---------|-------------|
| `ClassName` | Entire class |
| `ClassName/method` | Method within class |
| `ClassName/__init__` | Constructor (Python) |
| `function_name` | Top-level function |

## Verification Checklist

- [ ] Onboarding check completed
- [ ] Checked memories for relevant info
- [ ] Prioritizing symbol search
- [ ] Checked referencing symbols before editing (backward compatibility)
