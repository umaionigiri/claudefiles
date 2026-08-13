# Skill: excel-update

Excelファイルを openpyxl で生成・更新するときの手順。

## 手順

### 1. スクラッチパッドで生成

常にスクラッチパッドに一時ファイルを作成してから、宛先へコピーする。
直接宛先パスに書き込むとファイルが開かれている場合に失敗する。

```python
SCRATCH = "/tmp/claude-.../scratchpad/<filename>.xlsx"
DEST    = "<project_path>/<filename>.xlsx"

# openpyxl でブックを生成して SCRATCH に保存
wb.save(SCRATCH)
```

### 2. 宛先へ上書きコピー

```bash
cp "$SCRATCH" "$DEST"
```

- **既存ファイルは必ず上書き（`_new`, `_v2` など別名で作らない）**
- PermissionError が出た場合 → ユーザーに「Excel でファイルを閉じてから再実行してください」と伝え、待つ。別名で保存しない。

### 3. よくある破損原因と対策

| 問題 | 対策 |
|------|------|
| `merge_cells` 後に非アンカーセルへ border 設定 | merge 後は左上セル（アンカー）だけに border を設定する |
| フォント名に日本語（游ゴシック等） | `"Calibri"` など英語名フォントを使う |
| `Alignment(indent=...)` の型ミス | indent は整数のみ |

### 4. スタイルの定型

```python
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

FONT = "Calibri"
thin = Side(style="thin", color="BFBFBF")
full_border = Border(left=thin, right=thin, top=thin, bottom=thin)

fill_header = PatternFill("solid", fgColor="4472C4")
font_header = Font(bold=True, color="FFFFFF", name=FONT, size=11)

al_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
al_left   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
```

### 5. セクション見出し行パターン

カテゴリをカラム（列）ではなく、全列結合の見出し行として挿入する。

```python
def srow(ws, r, label, n_cols=5):
    ws.row_dimensions[r].height = 20
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=n_cols)
    cl = ws.cell(r, 1)
    cl.value = f"■ {label}"
    cl.font = Font(bold=True, name=FONT, size=10)
    cl.fill = PatternFill("solid", fgColor="D6DCE4")
    cl.alignment = Alignment(horizontal="left", vertical="center")
    cl.border = full_border  # アンカーセルのみ
```
