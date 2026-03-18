# theme-setup-guide.md — テーマ選択・設定の詳細ガイド

## ⚠ 必須ゲート — スクリプトを1行も書く前に完了すること

- テーマが複数ある場合は **AskUserQuestion** でユーザーに選ばせてから boilerplate を書く
- **`theme_selector.py` / `select_theme()` をスクリプト内で呼ぶことは絶対禁止**（Tkinter ダイアログは Claude Code から結果を取得できない）
- **`set_lang` → `load_theme` の順序厳守**（逆にすると `set_lang` が `TEMPLATE_PATH` を上書きしてしまう）
- **カラーテーマとスライドマスターは1つの質問で同時に選ばせること**

---

## 確認手順（5ステップ）

1. `~/.claude/skills/acnpptx/assets/themes/` の `*.json`（`_` 除外）を読んで利用可能テーマをリストアップ
2. 各テーマ JSON の `name`・`tokens.primary`・`tokens.background`・`template`・`layout_notes` を読み取る
3. テーマの `layout_notes.content` にブレッドクラム・タイトル・メッセージラインの placeholder が揃っているか確認。揃っていないマスターは除外またはユーザーに説明する
4. テーマが複数あれば **AskUserQuestion** でテーマを選ばせる（以下フォーマット参照）
5. テーマが1つだけなら AskUserQuestion 不要 — 自動適用

---

## AskUserQuestion フォーマット例

各テーマ JSON から実際の値を読んで使うこと（この例をそのままコピーしない）:

```
使用するテーマ（カラー＋スライドマスター）を選んでください。
※ テーマを選ぶとカラーとスライドマスターが同時に確定します。

🎨 Accenture
   アクセント: #A100FF ████  背景: #FFFFFF ░░░░
   マスター: accenture.pptx（白背景 — 文字は BLACK）

🎨 Sample社
   アクセント: #FF50AA ████  背景: #FFFFFF ░░░░
   マスター: sample_sha.pptx

🎨 Fiori
   アクセント: #21B7C4 ████  背景: #FFFFFF ░░░░
   マスター: fiori.pptx（SAP Fiori テンプレート）
```

回答を受け取ったら、その `name` フィールドを `load_theme()` にハードコードしてから boilerplate を書く。

---

## 新規 .pptx テンプレートを登録する手順

1. **AskUserQuestion** で「このテーマの名前を教えてください（例: "ClientXYZ"）」と確認
2. `master_to_theme.py` を実行してカラートークンを抽出:
   ```bash
   PYTHONUTF8=1 python ~/.claude/skills/acnpptx/scripts/master_to_theme.py <path/to/file.pptx> "テーマ名"
   ```
3. 抽出結果（カラートークン一覧）が stdout に出力される — 色がおかしい場合はユーザーに確認
4. 保存後は再度 AskUserQuestion で選択肢に含める

**`master_to_theme.py` の仕組み:**

| 項目 | 内容 |
|------|------|
| 走査方式 | `fill.fore_color.rgb`（python-pptx API）は使わない — `schemeClr` 参照で AttributeError を silently raise するため Fiori・SAP 系では色が1件も拾えない |
| schemeClr 解決 | `_build_theme_map` でマスターテーマ XML から slot → hex を構築し、`lumMod`/`lumOff`/`shade`/`tint` モディファイアを HLS 色空間で適用して実際の表示色を算出 |
| Namespace 非依存 | `element.iter(f"{NS_A}solidFill")` で全 solidFill を取得 |
| text_body/text_muted | 彩度 < 0.20 のグレー系のみ選択 — アクセント色は混入しない |

---

## テーマ JSON の `layout_notes` を使ったレイアウト設定

theme JSON に以下のフィールドがある場合、スクリプト冒頭で必ず参照して定数を設定:

| JSON フィールド | 設定例 |
|----------------|--------|
| `layout_indices.cover` | `LAYOUT_COVER = theme_data["layout_indices"]["cover"]` |
| `layout_indices.content` | `LAYOUT_CONTENT = theme_data["layout_indices"]["content"]` |
| `layout_notes.content.content_area_y` | `CONTENT_Y = layout_notes["content"]["content_area_y"]`（未定義なら `CY=1.50"` を使う）|
| `layout_notes.cover.placeholders` | 表紙プレースホルダーの idx 割り当てを確認してから埋める |
| `cover_text_color` | `"BLACK"` なら全プレースホルダーを BLACK/MID_GRAY で埋める（白背景テーマでは WHITE は不可視）|
| `layout_notes.content.message_line_idx` | null なら `add_message_line()` を使う。数値なら該当 idx に直接書き込む |

```python
import json as _json
_theme_path = os.path.join(_SKILL, "..", "assets", "themes", "テーマ名.json")
with open(_theme_path) as _f:
    _td = _json.load(_f)
LAYOUT_COVER   = _td["layout_indices"]["cover"]
LAYOUT_CONTENT = _td["layout_indices"]["content"]
CONTENT_Y      = _td.get("layout_notes", {}).get("content", {}).get("content_area_y", CY)
_MSG_IDX       = _td.get("layout_notes", {}).get("content", {}).get("message_line_idx")
```