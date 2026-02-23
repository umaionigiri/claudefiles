# Serena 検索パターン集

## アーキテクチャ分析

```
mcp__serena__get_symbols_overview({ relative_path: "src/controllers" })
mcp__serena__get_symbols_overview({ relative_path: "src/services" })
mcp__serena__get_symbols_overview({ relative_path: "src/repositories" })
```

## 依存関係トレース

```
# シンボルの全参照箇所を検索
mcp__serena__find_referencing_symbols({ symbol_name: "UserService" })

# 設定ファイル検索
mcp__serena__find_file({ file_mask: "*.config.*" })
mcp__serena__find_file({ file_mask: "package.json" })
```

## 変更影響分析

1. `find_symbol` で対象を特定
2. `find_referencing_symbols` で参照箇所を列挙
3. 影響範囲を確認してから編集

## トークン消費目安

| 操作 | 典型的なトークン数 |
|------|-------------------|
| symbols_overview | 200-500 |
| find_symbol | 100-300 |
| find_symbol (with body) | 300-1000 |
| search_for_pattern | 500-2000 |

## アンチパターン

- 広範囲のパターン検索は避ける
- 再帰的ディレクトリスキャンは避ける
- 大きなファイルの全体読み込みは避ける
- **常に**: シンボル検索優先、パス範囲限定、段階的詳細化
