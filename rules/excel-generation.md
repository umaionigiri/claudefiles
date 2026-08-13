# Excel Generation Rules

Python で `.xlsx` を生成するときは必ず以下に従う。

## ライブラリ
- **xlsxwriter のみ使用**。openpyxl で生成しない
  - 理由: openpyxl + merge_cells はセル結合範囲の非先頭セルにスタイル情報が残り、Excelが「修復」ダイアログを出す

## フォント（必須）
- `font_name: 'Meiryo UI'`
- `font_size: 10.5`
- 全 `add_format()` 呼び出しに含める（ヘッダー・データ行・カテゴリ行すべて）

## 生成手順
1. `/tmp/<filename>.xlsx` に書き出す（OneDriveパスに直接書かない）
2. `shutil.copy2(TMP_PATH, DEST_PATH)` でコピー
3. `openpyxl.load_workbook(TMP_PATH)` で読み直し検証（行数アサートを含める）

## add_format() の注意
- `border_color` は無効プロパティ（xlsxwriterが認識しない）。使わない
- 罫線色を変えたい場合は `top_color` / `bottom_color` / `left_color` / `right_color` を個別指定

## テンプレート

```python
import xlsxwriter, shutil, openpyxl

TMP  = "/tmp/output.xlsx"
DEST = "/mnt/c/.../output.xlsx"

wb = xlsxwriter.Workbook(TMP)
ws = wb.add_worksheet("シート名")
ws.freeze_panes(1, 0)

base = {"font_name": "Meiryo UI", "font_size": 10.5, "valign": "vcenter", "text_wrap": True, "border": 1}

f_header = wb.add_format({**base, "bold": True, "bg_color": "#4472C4", "font_color": "#FFFFFF", "align": "center"})
f_normal = wb.add_format({**base, "align": "left"})

# ... データ書き込み ...

wb.close()

wb2 = openpyxl.load_workbook(TMP)
assert wb2.active.max_row == EXPECTED_ROWS
shutil.copy2(TMP, DEST)
```
