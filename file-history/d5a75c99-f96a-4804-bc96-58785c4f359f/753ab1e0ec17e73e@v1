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

トークン効率を重視したコードベース分析スキル。

## ワークフロー

```mermaid
flowchart TD
    A[分析開始] --> B{オンボーディング済み?}
    B -->|No| C[オンボーディング実行]
    B -->|Yes| D[メモリ確認]
    C --> D
    D --> E[概要取得]
    E --> F{対象特定済み?}
    F -->|No| G[シンボル検索]
    F -->|Yes| H[詳細取得]
    G --> I{見つかった?}
    I -->|No| J[パターン検索]
    I -->|Yes| H
    J --> K{見つかった?}
    K -->|No| L[検索範囲拡大]
    K -->|Yes| H
    L --> G
    H --> M[関連シンボル調査]
    M --> N{編集必要?}
    N -->|Yes| O[シンボル編集]
    N -->|No| P[完了]
    O --> P
```

## Step 1: セッション初期化

**初回実行時:**

```
mcp__serena__check_onboarding_performed()
mcp__serena__list_memories()
mcp__serena__list_dir({ relative_path: ".", recursive: false })
```

## Step 2: 概要把握

```
mcp__serena__get_symbols_overview({ relative_path: "src" })
```

- プロジェクト構造を理解
- 主要なモジュールを特定
- 依存関係を把握

## Step 3: シンボル検索（優先）

```
mcp__serena__find_symbol({
  symbol_name: "ClassName",
  include_body: false,
  depth: 1
})
```

## Step 4: 詳細取得

```
mcp__serena__find_symbol({
  symbol_name: "ClassName/methodName",
  include_body: true
})
```

## Step 5: 関連シンボル調査

```
mcp__serena__find_referencing_symbols({
  symbol_name: "targetSymbol"
})
```

## Step 6: シンボル編集（必要時）

```
mcp__serena__replace_symbol_body({
  symbol_name: "ClassName/methodName",
  new_body: "// new implementation"
})
```

## クイックリファレンス

### 検索優先度

| 優先度 | ツール | 用途 |
|--------|--------|------|
| 1 | `find_symbol` | シンボル名が分かる場合 |
| 2 | `find_file` | ファイル名が分かる場合 |
| 3 | `search_for_pattern` | 上記で見つからない場合 |

### トークン最適化

| 手法 | 効果 |
|------|------|
| 検索パスを絞る | `src/services/` > `src/` |
| 目標: 2000トークン以下/検索 | 大量結果を回避 |
| 500行以上のファイルは分割取得 | 必要部分のみ取得 |
| `include_body: false` 先行 | 概要把握後に詳細取得 |

### シンボル操作

| 操作 | ツール |
|------|--------|
| 概要取得 | `get_symbols_overview` |
| シンボル検索 | `find_symbol` |
| 参照検索 | `find_referencing_symbols` |
| 本体置換 | `replace_symbol_body` |
| 前に挿入 | `insert_before_symbol` |
| 後に挿入 | `insert_after_symbol` |
| リネーム | `rename_symbol` |

### name_path パターン

| パターン | 説明 |
|----------|------|
| `ClassName` | クラス全体 |
| `ClassName/method` | クラス内メソッド |
| `ClassName/__init__` | コンストラクタ（Python） |
| `function_name` | トップレベル関数 |

### よく使うパターン

**プロジェクト概要:**
```
mcp__serena__get_symbols_overview({ relative_path: "." })
mcp__serena__get_symbols_overview({ relative_path: "src" })
```

**特定シンボル調査:**
```
mcp__serena__find_symbol({ symbol_name: "ClassName", include_body: false, depth: 1 })
mcp__serena__find_symbol({ symbol_name: "ClassName/method", include_body: true })
```

**設定ファイル検索:**
```
mcp__serena__find_file({ file_mask: "*.config.*" })
mcp__serena__find_file({ file_mask: "package.json" })
```

## 検証チェックリスト

### 検索前チェック

- [ ] オンボーディング完了確認
- [ ] メモリに関連情報がないか確認
- [ ] 検索パスを最小範囲に絞る

### 検索中チェック

- [ ] シンボル検索を優先している
- [ ] `include_body: false` で概要を先に取得
- [ ] 結果が2000トークン以下

### 編集前チェック

- [ ] 対象シンボルを正確に特定
- [ ] 参照シンボルを確認（後方互換性）
- [ ] 最小限の変更に留める

## 段階的アプローチ

| フェーズ | 目的 | ツール |
|----------|------|--------|
| 概要 | 構造理解 | `get_symbols_overview`, `list_dir` |
| 特定 | 対象発見 | `find_symbol`, `find_file` |
| 詳細 | 内容取得 | `find_symbol` with `include_body: true` |
| 関連 | 影響調査 | `find_referencing_symbols` |
| 編集 | 変更適用 | `replace_symbol_body`, `insert_*` |

## 重要事項

- **シンボル優先**: ファイル全体読み込みより`find_symbol`
- **段階的取得**: `include_body: false` → `true`
- **パス限定**: 検索範囲は最小限に
- **メモリ活用**: 過去の調査結果を参照
