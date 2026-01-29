# XLSX Conversion Rules

## Excelスタイル設定

| 要素 | 設定 |
|------|------|
| フォント | Meiryo UI, 10pt |
| ヘッダー行 | 背景色 #F0F0F0, 太字 |
| 罫線 | 細線（thin） |
| 列幅 | 自動調整（最大50文字） |
| テキスト | 折り返し有効 |

## Markdown Table Format

```markdown
| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

## JSON Format

JSON配列形式を想定:

```json
[
  {"column_a": "value1", "column_b": "value2"},
  {"column_a": "value3", "column_b": "value4"}
]
```

## CSV Format

UTF-8エンコーディングのCSV:

```csv
column_a,column_b,column_c
value1,value2,value3
```

## Multiple Sheets

Markdownの見出し（##）ごとに別シートに分割可能。

## Troubleshooting

| 問題 | 原因 | 対処 |
|------|------|------|
| 列幅が狭い | 自動調整の上限 | 手動調整 |
| 文字化け | エンコーディング | UTF-8確認 |
| シート名エラー | 31文字制限 | 名前を短縮 |
