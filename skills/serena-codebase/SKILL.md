---
name: serena-codebase
description: |
  コードベース探索・分析にSerena MCPを使用。トークン効率を最優先。
  シンボル検索を優先し、パターン検索は最終手段として使用。
  トリガー: 「シンボルを探す」「コードベースを検索」「アーキテクチャを分析」「Xの仕組みを調査」「プロジェクト構造を探索」
allowed-tools: mcp__serena__*
version: 1.0.0
---

# Serena コードベース分析スキル

## Step 1: セッション初期化

```
mcp__serena__check_onboarding_performed()
mcp__serena__list_memories()
mcp__serena__list_dir({ relative_path: ".", recursive: false })
```

## Step 2: 概要把握

```
mcp__serena__get_symbols_overview({ relative_path: "src" })
```

## Step 3: シンボル検索（優先）

```
mcp__serena__find_symbol({ symbol_name: "ClassName", include_body: false, depth: 1 })
```

## Step 4: 詳細取得

```
mcp__serena__find_symbol({ symbol_name: "ClassName/methodName", include_body: true })
```

## Step 5: 参照検索

```
mcp__serena__find_referencing_symbols({ symbol_name: "targetSymbol" })
```

## Step 6: シンボル編集（必要時）

```
mcp__serena__replace_symbol_body({ symbol_name: "ClassName/methodName", new_body: "..." })
```

## 検索優先度

| 優先度 | ツール | 用途 |
|--------|--------|------|
| 1 | `find_symbol` | シンボル名が分かる場合 |
| 2 | `find_file` | ファイル名が分かる場合 |
| 3 | `search_for_pattern` | 上記で見つからない場合（最終手段） |

## トークン最適化

| 手法 | 効果 |
|------|------|
| 検索パスを絞る | `src/services/` > `src/` |
| `include_body: false` 先行 | 概要把握後に詳細取得 |
| 500行以上のファイルは分割取得 | 必要部分のみ取得 |
| 目標: 2000トークン以下/検索 | 大量結果を回避 |

## シンボル操作一覧

| 操作 | ツール |
|------|--------|
| 概要取得 | `get_symbols_overview` |
| シンボル検索 | `find_symbol` |
| 参照検索 | `find_referencing_symbols` |
| 本体置換 | `replace_symbol_body` |
| 前に挿入 | `insert_before_symbol` |
| 後に挿入 | `insert_after_symbol` |
| リネーム | `rename_symbol` |

## name_path パターン

| パターン | 説明 |
|----------|------|
| `ClassName` | クラス全体 |
| `ClassName/method` | クラス内メソッド |
| `ClassName/__init__` | コンストラクタ（Python） |
| `function_name` | トップレベル関数 |

## 検証チェックリスト

- [ ] オンボーディング完了確認
- [ ] メモリに関連情報がないか確認
- [ ] シンボル検索を優先している
- [ ] 編集前に参照シンボルを確認（後方互換性）
