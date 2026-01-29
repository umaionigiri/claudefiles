# Serena Search Patterns

## Architecture Analysis

```
# Layer structure
mcp__serena__get_symbols_overview({ relative_path: "src/controllers" })
mcp__serena__get_symbols_overview({ relative_path: "src/services" })
mcp__serena__get_symbols_overview({ relative_path: "src/repositories" })
```

## Dependency Tracing

```
# Find all usages of a symbol
mcp__serena__find_references({ symbol_name: "UserService" })

# Find implementations
mcp__serena__find_implementations({ symbol_name: "IRepository" })
```

## Change Impact Analysis

Before refactoring:

1. `find_symbol` で対象を特定
2. `find_references` で参照箇所を列挙
3. 影響範囲を確認

## Token Budget Guidelines

| Operation | Typical Tokens |
|-----------|---------------|
| symbols_overview | 200-500 |
| find_symbol | 100-300 |
| get_definition | 300-1000 |
| search_pattern | 500-2000 |

## Anti-Patterns

❌ 広範囲のパターン検索
❌ 再帰的ディレクトリスキャン
❌ 大きなファイルの全体読み込み

✅ シンボル検索優先
✅ パス範囲を限定
✅ 段階的な詳細化
