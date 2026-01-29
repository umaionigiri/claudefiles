---
name: document-converter
description: |
  ドキュメントフォーマット変換を標準スタイルで実行。
  Markdown から Word/Excel/PDF への変換、JSON から Excel への変換をサポート。
  トリガー: 「Markdownを Word に変換」「Excel に出力」「PDF を作成」「JSON をスプレッドシートに変換」「DOCX/XLSX/PDF を生成」
allowed-tools: Read, Write, Bash
version: 1.0.0
---

# Document Converter Skill

標準化されたルールでドキュメント形式変換を実行するスキル。

## ワークフロー

```mermaid
flowchart TD
    A[変換要求] --> B[入力ファイル確認]
    B --> C{ファイル存在?}
    C -->|No| D[エラー報告]
    C -->|Yes| E[出力形式特定]
    E --> F{サポート形式?}
    F -->|No| D
    F -->|Yes| G[依存関係確認]
    G --> H{依存関係OK?}
    H -->|No| I[依存インストール]
    I --> J[変換実行]
    H -->|Yes| J
    J --> K[スタイル適用]
    K --> L[出力確認]
    L --> M{変換成功?}
    M -->|No| N[エラー対処]
    N --> J
    M -->|Yes| O[完了]
```

## Step 1: 入力確認

- ソースファイルの存在確認
- ファイル形式の特定
- 出力形式の確認

## Step 2: 依存関係確認

```bash
# 確認コマンド
which pandoc
python3 -c "import docx; import openpyxl"
```

## Step 3: 変換実行

形式に応じた変換を実行。

## Step 4: スタイル適用

標準スタイルを適用。

## Step 5: 出力確認

- ファイルが生成されたか
- 内容が正しく変換されたか
- スタイルが適用されたか

## クイックリファレンス

### サポート形式

| From | To | ツール |
|------|-----|--------|
| Markdown | DOCX | pandoc + python-docx |
| Markdown | XLSX | Python (openpyxl) |
| Markdown | PDF | pandoc + LaTeX |
| JSON | XLSX | Python (openpyxl) |
| CSV | XLSX | Python (openpyxl) |

### 標準スタイル

| 要素 | フォント | サイズ |
|------|----------|--------|
| 見出し1 | Meiryo UI | 14pt |
| 見出し2-4 | Meiryo UI | 12pt |
| 本文 | Meiryo UI | 10.5pt |
| 表 | Meiryo UI | 10pt |
| ヘッダー行 | 背景色 #F0F0F0 | - |

### 変換コマンド

**Markdown → DOCX:**
```bash
# Step 1: pandoc 変換
pandoc input.md -o output.docx \
  --from markdown+pipe_tables+yaml_metadata_block

# Step 2: スタイル適用
python3 scripts/format_docx.py output.docx
```

**Markdown → XLSX:**
```bash
python3 scripts/md_to_xlsx.py input.md output.xlsx
```

**JSON → XLSX:**
```bash
python3 scripts/json_to_xlsx.py input.json output.xlsx
```

**Markdown → PDF:**
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Hiragino Kaku Gothic Pro"
```

### 依存関係

| パッケージ | インストール |
|------------|--------------|
| pandoc | `brew install pandoc` |
| python-docx | `pip install python-docx` |
| openpyxl | `pip install openpyxl` |
| LaTeX | `brew install --cask mactex` |

### スクリプト

| スクリプト | 用途 |
|------------|------|
| `scripts/format_docx.py` | DOCX フォーマット |
| `scripts/md_to_xlsx.py` | Markdown テーブル → Excel |
| `scripts/json_to_xlsx.py` | JSON → Excel |

## 検証チェックリスト

### 変換前チェック

- [ ] 入力ファイルが存在する
- [ ] 入力形式がサポートされている
- [ ] 出力形式がサポートされている
- [ ] 必要な依存関係がインストール済み

### 変換中チェック

- [ ] pandoc/Python スクリプトがエラーなく実行
- [ ] 中間ファイルが正しく生成

### 変換後チェック

- [ ] 出力ファイルが生成された
- [ ] ファイルサイズが適切（0バイトでない）
- [ ] 内容が正しく変換された
  - [ ] テキストが欠落していない
  - [ ] テーブルが正しく変換された
  - [ ] 画像が含まれている（該当する場合）
- [ ] スタイルが適用された
  - [ ] フォントが正しい
  - [ ] 見出しサイズが正しい
  - [ ] 表のスタイルが正しい

## トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 日本語が文字化け | フォント未指定 | Meiryo UI を明示的に指定 |
| 表が崩れる | pipe_tables 未有効 | `+pipe_tables` を追加 |
| PDF で日本語表示不可 | 日本語フォント未指定 | xelatex + 日本語フォント指定 |
| Excel セルが空 | パース失敗 | Markdown 形式を確認 |

## 詳細ルール参照

| 形式 | 参照ファイル |
|------|--------------|
| DOCX | @docx-rules.md |
| XLSX | @xlsx-rules.md |

## 重要事項

- **依存確認**: 変換前に必要なツールがインストールされているか確認
- **スタイル統一**: 常に標準スタイル（Meiryo UI）を適用
- **日本語対応**: フォント指定を忘れない
- **出力検証**: 変換後は必ず内容を確認
