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

## Supported Formats

| From | To | Tool |
|------|-----|------|
| Markdown | DOCX | pandoc + python-docx |
| Markdown | XLSX | Python (openpyxl) |
| Markdown | PDF | pandoc + LaTeX |
| JSON | XLSX | Python (openpyxl) |
| CSV | XLSX | Python (openpyxl) |

## Standard Style

| Element | Font | Size |
|---------|------|------|
| Heading 1 | Meiryo UI | 14pt |
| Heading 2-4 | Meiryo UI | 12pt |
| Body | Meiryo UI | 10.5pt |
| Table | Meiryo UI | 10pt |
| Header row | Background #F0F0F0 | - |

## Conversion Steps

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

## Dependencies

| Package | Installation |
|---------|-------------|
| pandoc | `brew install pandoc` |
| python-docx | `pip install python-docx` |
| openpyxl | `pip install openpyxl` |
| LaTeX | `brew install --cask mactex` |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/format_docx.py` | Apply DOCX formatting |
| `scripts/md_to_xlsx.py` | Markdown table → Excel |
| `scripts/json_to_xlsx.py` | JSON → Excel |

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Japanese character corruption | Font not specified | Explicitly specify Meiryo UI |
| Broken tables | pipe_tables not enabled | Add `+pipe_tables` |
| Japanese not rendering in PDF | Japanese font not specified | Use xelatex + Japanese font |
| Empty Excel cells | Parse failure | Check Markdown format |

## Detailed Rules Reference

| Format | Reference File |
|--------|---------------|
| DOCX | @docx-rules.md |
| XLSX | @xlsx-rules.md |

## Verification Checklist

**Pre-conversion:**
- [ ] Input file exists and format is supported
- [ ] Required dependencies installed

**Post-conversion:**
- [ ] Output file generated (non-zero bytes)
- [ ] No text loss, tables properly converted
- [ ] Font, heading sizes, and table styles applied
