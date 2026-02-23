---
name: document-converter
description: |
  ドキュメントフォーマット変換を標準スタイルで実行。
  Markdown から Word/Excel/PDF への変換、JSON から Excel への変換をサポート。
  トリガー: 「Markdownを Word に変換」「Excel に出力」「PDF を作成」「JSON をスプレッドシートに変換」「DOCX/XLSX/PDF を生成」
allowed-tools: Read, Write, Bash
version: 1.0.0
---

# ドキュメント変換スキル

## サポート形式

| From | To | ツール |
|------|-----|--------|
| Markdown | DOCX | pandoc + python-docx |
| Markdown | XLSX | Python (openpyxl) |
| Markdown | PDF | pandoc + LaTeX |
| JSON | XLSX | Python (openpyxl) |
| CSV | XLSX | Python (openpyxl) |

## 標準スタイル

| 要素 | フォント | サイズ |
|------|----------|--------|
| 見出し1 | Meiryo UI | 14pt |
| 見出し2-4 | Meiryo UI | 12pt |
| 本文 | Meiryo UI | 10.5pt |
| 表 | Meiryo UI | 10pt |
| ヘッダー行 | 背景色 #F0F0F0 | - |

## 変換手順

### Markdown → DOCX
```bash
pandoc input.md -o output.docx \
  --from markdown+pipe_tables+yaml_metadata_block
python3 scripts/format_docx.py output.docx
```

### Markdown → XLSX
```bash
python3 scripts/md_to_xlsx.py input.md output.xlsx
```

### JSON → XLSX
```bash
python3 scripts/json_to_xlsx.py input.json output.xlsx
```

### Markdown → PDF
```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V mainfont="Hiragino Kaku Gothic Pro"
```

## 依存関係

| パッケージ | インストール |
|------------|--------------|
| pandoc | `brew install pandoc` |
| python-docx | `pip install python-docx` |
| openpyxl | `pip install openpyxl` |
| LaTeX | `brew install --cask mactex` |

## スクリプト

| スクリプト | 用途 |
|------------|------|
| `scripts/format_docx.py` | DOCX フォーマット適用 |
| `scripts/md_to_xlsx.py` | Markdown テーブル → Excel |
| `scripts/json_to_xlsx.py` | JSON → Excel |

## トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 日本語文字化け | フォント未指定 | Meiryo UI を明示的に指定 |
| 表が崩れる | pipe_tables 未有効 | `+pipe_tables` を追加 |
| PDF で日本語不可 | 日本語フォント未指定 | xelatex + 日本語フォント指定 |
| Excel セルが空 | パース失敗 | Markdown 形式を確認 |

## 詳細ルール参照

| 形式 | 参照ファイル |
|------|--------------|
| DOCX | @docx-rules.md |
| XLSX | @xlsx-rules.md |

## 検証チェックリスト

**変換前:**
- [ ] 入力ファイルが存在し、形式がサポートされている
- [ ] 必要な依存関係がインストール済み

**変換後:**
- [ ] 出力ファイルが生成された（0バイトでない）
- [ ] テキスト欠落なし、テーブル正しく変換
- [ ] フォント・見出しサイズ・表スタイルが適用済み
