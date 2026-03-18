---
name: acnpptx
description: "Generates, reads, edits, restyles, and rethemes Accenture-branded PowerPoint presentations (.pptx/.ppt) using python-pptx with official brand assets (logos, Greater Than symbol, Graphik/Meiryo UI fonts), slide masters, and structured layouts. Use when creating slide decks, pitch decks, PowerPoint, or presentations from scratch; reading or extracting content from .pptx/.ppt files; editing existing presentations; restyling/redesigning existing decks; or changing deck themes/templates. Trigger when user mentions PowerPoint, PPT, pptx, deck, slides, presentation, restyle, redesign, or uses Japanese terms: スライド, プレゼン, プレゼンテーション, デッキ, スライドデッキ, パワポ, パワーポイント. Do NOT trigger for Google Slides, Keynote, or web/CSS presentations."
---

compatibility: "Python 3.9+. Packages: python-pptx, Pillow, lxml, markitdown, pywin32 (Windows only, for thumbnails)"


# PPTX Skill — Multi-Theme Brand Edition

Five workflows: **Read**, **Edit** (template-based), **Create** (from scratch), **Restyle** (redesign existing deck), **Retheme** (change colors/template only).

References: [color-palette.md](references/color-palette.md) | [brand-guidelines.md](references/brand-guidelines.md) | [pattern-specs.md](references/pattern-specs.md) | [pattern-selection-guide.md](references/pattern-selection-guide.md) | [chart-specs.md](references/chart-specs.md) | [api-reference.md](references/api-reference.md) | [common-mistakes.md](references/common-mistakes.md)

## Setup

```bash
pip install python-pptx Pillow lxml "markitdown[pptx]" pywin32
```

## Language / Font / Assets

| Language | Font | Template |
|----------|------|----------|
| Japanese (default) | Meiryo UI | `assets/slide-master.pptx` |
| English | Graphik (Arial fallback) | `assets/slide-master.pptx` |

```python
import helpers as _h
_h.set_lang("ja")   # or "en"  ← load_theme() より先に呼ぶこと
from helpers import *
```

**Logo・GT symbol はスライドマスターが自動提供。`add_logo()` / `add_gt_symbol()` 呼び出し禁止。**

---

## Workflow: Reading Content

```bash
python -m markitdown presentation.pptx
```

---

## Workflow: Editing Existing Slides

See [editing-workflow.md](references/editing-workflow.md).

```
scripts/unpack.py → scripts/add_slide.py → edit XML → scripts/clean.py → scripts/pack.py
```

---

## Workflow: Modifying Existing Presentations (Restyle / Retheme)

ユーザーが既存 PPTX の変更を求めたら、まず **AskUserQuestion** で方向性を確認:

```
📐 Restyle（リスタイル）— レイアウト・構成・ビジュアルを一新（スライド数変更あり）
🎨 Retheme（リテーマ）— カラー・フォント・マスターのみ変更、構成はそのまま
```

次に **AskUserQuestion** でテーマを選ばせる（色スウォッチ付き）。詳細は [theme-setup-guide.md](references/theme-setup-guide.md) 参照。

- **Restyle** → [restyle-workflow.md](references/restyle-workflow.md) 参照
- **Retheme** → Step 8 (下記) を実行

---

## Workflow: Creating from Scratch

**FILE LOCATION RULES:** 生成スクリプト・出力 .pptx ともにユーザーの CWD に保存。`~/.claude/skills/acnpptx/` は READ-ONLY。

### Step 0 — Outline（骨子）先行

```python
import sys, os
_SKILL = os.path.join(os.path.expanduser("~"), ".claude", "skills", "acnpptx", "scripts")
sys.path.insert(0, _SKILL)
from outline import generate_outline, format_outline_md, save_outline, validate_outline
outline = generate_outline(title="タイトル", language="ja", sections=["背景","ソリューション","効果","まとめ"])
print(format_outline_md(outline))

valid, errors, warnings = validate_outline(outline)
if warnings:
    print("⚠️ 改善推奨:")
    for w in warnings:
        print(f"  {w}")
if not valid:
    print("❌ エラー:")
    for e in errors:
        print(f"  {e}")

save_outline(outline, "outline.json")
```

**パターン選択**: アウトラインの各スライドにパターンを割り当てる際は [pattern-selection-guide.md](references/pattern-selection-guide.md) を参照すること。Pattern A のデフォルト使用は禁止 — 必ずコンテンツ目的に応じたパターンを割り当てる。

ユーザーに確認してから続行。スキーマ詳細は [outline-schema.md](references/outline-schema.md)。

**スライド順序ルール:**
1. カバー（常に先頭）
2. アジェンダ（Pattern I）— **ある場合はカバーの直後に必ず配置。間に別スライドを挟まない**
3. 以降 — セクション区切り・コンテンツスライド

**スライド枚数カウントルール:**
- ユーザーが「N枚で作って」と指定した場合、N枚 = **カバー + アジェンダ（ある場合）+ コンテンツスライド**
- **枚数に含めるもの**: カバー（表紙）、アジェンダ（ある場合）、コンテンツスライド
- **枚数に含めないもの**: セクション区切り（Pattern C）、クロージング（Thank You）
- セクション区切りはページ番号は振るが、実質的な中身のないスライドであるため枚数にカウントしない

**セクション区切り使用ルール:**
- **10枚以下のデッキではセクション区切り不要**（ブレッドクラムでセクションを示す）
- 11枚以上でセクション区切りを使う場合は、**全セクションを区切る**こと。一部だけ区切りを入れて残りは省略、は禁止
- セクションが1つしかない（区切る意味がない）場合は使わなくてよい

**パターン多様性ルール（必須）:**
- **同じパターンを連続で使わない。** 直前のスライドと異なるパターンを選ぶこと
- **同じパターンは原則1デッキに1回。** 再利用が許されるのは内容上の必然性がある場合のみ（例: 別セクションの比較表が2枚必要）
- アウトライン作成時に使用パターンの重複チェックを行い、重複があれば別パターンに差し替える
- **パターン選択の優先度**: 未使用パターン（最優先） > 2回目だが内容的に必然性あり（許容） > 3回目以上（禁止）
- 多様なビジュアル体験のため、テキスト系（A, E）、図形系（P, H, T）、データ系（G, J, M, W）、グリッド系（B, F, K, Q）をバランスよく混ぜること
- **Pattern A の使用制限**: Pattern A は「他のどのパターンにも当てはまらない場合の最終手段」として扱う。アウトラインに Pattern A が2枚以上あれば、[pattern-selection-guide.md](references/pattern-selection-guide.md) を参照して適切なパターンに差し替えること
- **validate_outline() による自動チェック**: outline 保存前に `validate_outline()` を実行し、多様性の WARNING/ERROR を確認すること。連続使用・3回以上使用・カテゴリ偏りが検出される

**コンテンツ品質ルール（コンサルタント品質の必須要件）:**
- **具体性**: 全スライドに固有名詞・数値・年号・金額を含めること。「ポイント1」「施策A」等の抽象的なプレースホルダーは絶対禁止
- **情報密度**: 各スライドのコンテンツエリアに最低4つの情報要素（数値、事実、分析、具体例）を含める。bullet 3行 + 汎用文言だけのスライドは不可
- **So What**: 各スライドのメッセージラインは「だから何なのか（So What）」を常体で明示する。事実の羅列ではなく、示唆・結論・主張を書く
- **ストーリーライン**: スライド間の論理的つながりを意識する。前のスライドの結論が次のスライドの前提になるよう構成する
- **リサーチ**: トピックについて十分なリサーチを行ってからコンテンツを作成する。一般的な知識で書ける内容だけでなく、具体的なデータポイントを調べて盛り込む

**余白・レイアウト密度ルール（必須）:**
- **コンテンツ充填率**: コンテンツエリア（CY〜BY）の **70%以上** をコンテンツで埋めること。下半分が空白のスライドは不可
- **テキストボックスの高さ**: textbox の高さは常に **配置可能な残り領域いっぱい** に設定する（例: `h = BY - detail_y - 0.10`）。テキスト量に合わせて小さくしない
- **垂直中央揃え（anchor: middle）**: テキストが少なくボックスの上部に偏る場合は、bodyPr の `anchor` を `'ctr'` に設定してテキストを垂直方向の中央に配置すること。**これは全パターン共通の必須設定。** カード内テキスト、パネル内テキスト、フロー下の説明テキスト、全てに適用する
```python
# ✅ 正しい: テキストを垂直中央に配置
tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
tf = tb.text_frame; tf.word_wrap = True
tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')  # ← 垂直中央揃え
# テキスト追加...

# ❌ 間違い: anchor 未設定でテキストが上に偏る
```
- **行間（space_after）の必須設定**: bullet リストや複数行テキストには必ず **`p.space_after = Pt(8)`**（目安: 6〜12pt）を設定すること。デフォルト行間はテキストが詰まって見え、かつ下部に大量の余白ができる。行間を広げることでコンテンツが縦方向に自然に分散する
```python
# ✅ 正しい: 行間を設定してコンテンツを縦に分散
for j, line in enumerate(lines):
    p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
    p.text = line; p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY; p.font.name = FONT
    p.space_after = Pt(8)  # ← 必須: 行間を広げる

# ❌ 間違い: space_after なしでテキストが上に固まる
```
- **Chevron / Flow 系パターンの下部テキスト**: 詳細テキストボックスの高さを `BY - detail_y - 0.10` にし、`space_after = Pt(8)` を設定する。テキストが4行程度でも行間で縦に広がり、下部の空白を軽減できる
- **Pattern A（Title+Body）の禁止事項**: テキストだけを1つのtextboxに詰め込んで上部に配置し、下半分を空白にしてはならない。bulletが6行以下の場合は Pattern E（Accent Bullet）や Pattern K（3-Column）に変更するか、図形・カード等のビジュアル要素を追加して空間を活用すること
- **カード・パネル系**: OFF_WHITEパネルの内部テキストがパネル高さの50%未満の場合、コンテンツを追加すること。パネル背景があるため多少の余白は許容されるが、テキストにも `space_after` を設定して分散させる
- **余白最小化**: 全スライドで「この余白は意図的か？」を自問する。意図がなければコンテンツを拡大するかレイアウトを調整する
- **カバースライド**: 全プレースホルダーを必ずループで埋めるかクリアすること。「Presenter 14pt」「テキストを入力」等のヒントテキスト残留は絶対禁止。使わないphは `p.text = " "`（半角スペース）で埋める（空文字 `""` ではレイアウト側ヒントが表示される場合がある）

### Step 1 — テーマ選択（スクリプトを書く前に必ず実行）

> **🚨 絶対ゲート**: `theme_selector.py` / `select_theme()` をスクリプト内で呼ぶことは禁止。**AskUserQuestion** で確認してから `load_theme()` にハードコードする。
> 詳細フロー・AskUserQuestion フォーマット例・master_to_theme.py 内部詳細は [theme-setup-guide.md](references/theme-setup-guide.md) 参照。

確認手順（全ステップ完了後に boilerplate を書く）:
1. `~/.claude/skills/acnpptx/assets/themes/*.json`（`_` 除外）をリストアップ
2. 各テーマの `name`・`tokens.primary`・`tokens.background`・`layout_notes` を読み取る
3. `layout_notes.content` にブレッドクラム・タイトル・メッセージライン placeholder が揃っているか確認
4. テーマが複数なら **AskUserQuestion** でカラー＋マスターをセットで選ばせる（1問で両方確定）
5. テーマが1つなら自動適用
6. 新規 .pptx ファイルの場合は `master_to_theme.py` でトークン抽出してから登録

**テーマ JSON の `layout_notes` を使った定数設定:**
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

#### Script boilerplate

```python
import sys, os
_SKILL = os.path.join(os.path.expanduser("~"), ".claude", "skills", "acnpptx", "scripts")
sys.path.insert(0, _SKILL)

import helpers as _h
_h.set_lang("ja")               # ① 先に set_lang
_h.load_theme("★テーマ名★")    # ② 後に load_theme（AskUserQuestion で確認済みの名前）
from helpers import *           # ③ ここで全定数・関数が有効になる

from native_shapes import *
from charts import add_column_chart, add_bar_chart, add_line_chart, add_pie_chart
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

prs = Presentation(TEMPLATE_PATH)
while len(prs.slides) > 0:
    sldId = prs.slides._sldIdLst[0]
    prs.part.drop_rel(sldId.get(_qn("r:id")))
    del prs.slides._sldIdLst[0]
```

### Step 2 — スライド追加

```python
LAYOUT_COVER   = 0   # ← theme JSON の layout_indices.cover に従う
LAYOUT_CONTENT = 2   # ← theme JSON の layout_indices.content に従う
LAYOUT_SECTION = 6   # ← テンプレートにある場合

def add_slide(layout_idx=LAYOUT_CONTENT):
    slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
    clear_placeholders(slide)   # 未使用の idx=10 body placeholder を削除
    return slide

def add_cover_slide():
    return prs.slides.add_slide(prs.slide_layouts[LAYOUT_COVER])
    # clear_placeholders() を呼ばない
```

**Layout 2 の placeholder 構造:**

| Placeholder | idx | y (in) | 使い方 |
|-------------|-----|--------|--------|
| Breadcrumb  | 11  | 0.08   | `add_breadcrumb(slide, "Section > Topic")` — 空文字禁止 |
| Title       | 0   | 0.42   | `add_title(slide, "タイトル")` — textbox 直接配置禁止 |
| *(unused)*  | 10  | 0.87   | `clear_placeholders()` で自動削除 |
| Message line| ※   | 0.95※  | **全コンテンツスライドに必須**（カバー・アジェンダ除く） |
| Content     | —   | CY=1.50"| パターンごとに配置 |

### Step 3 — スライドコンテンツ

**必須ゾーン（コンテンツスライド）:**

| Zone | Notes |
|------|-------|
| Breadcrumb | `add_breadcrumb(slide, "Section > Topic")` — 12pt MID_GRAY |
| Title | `add_title(slide, "タイトル")` — 28pt bold BLACK |
| Message line | **全コンテンツスライドに必須**（カバー・アジェンダ除く）。`_MSG_IDX` が定義済みなら该当 placeholder へ書き込む（18pt bold DARK_PURPLE を明示）。未定義なら `add_message_line(slide, "…")`。60字以内・常体 |
| Body | Min **14pt**。CONTENT_Y から配置 |
| Footer | `set_footer(slide)` — 全コンテンツスライドに必須 |

詳細 API → [api-reference.md](references/api-reference.md)

**コンテンツ密度ルール:**
- 各カード/パネルに title + 3〜5行 bullet。数値・固有名詞を含む具体的な文にする
- 余白がコンテナ面積の 50% 超なら bullet を追加

**短いラベルのルール:** `tf.word_wrap = False`、幅 = 文字数 × 0.20" 以上

**アジェンダバッジのルール（"01" 縦割れ防止）:** バッジ textframe は必ず `tf.word_wrap = False` を設定し、bodyPr の lIns/rIns/tIns/bIns をすべて `"0"` にリセットすること。省略すると "0\n1" と縦に折り返す。

**Chevron フロー (Pattern P) の y 座標・垂直バランス:**
- **詳細テキストあり**: chevron + 詳細テキスト グループ全体を垂直中央寄せ
  ```python
  FLOW_H   = 0.80   # chevron 高さ
  GAP      = 0.25   # chevron↔詳細の間隔
  DETAIL_H = 3.00   # 詳細テキストエリア高さ（コンテンツ量に応じて調整）
  FLOW_Y   = CY + (AH - FLOW_H - GAP - DETAIL_H) / 2   # ≈ 1.65"
  DETAIL_Y = FLOW_Y + FLOW_H + GAP
  ```
- **詳細テキストなし（フローのみ）**: `FLOW_Y = CY + (AH - FLOW_H) / 2`（垂直中央）
- 図形と詳細テキストが重なっていないか thumbnail で必ず確認すること

### Step 4 — パターン選択

ASCII レイアウト・shape テーブル・コード例は [pattern-specs.md](references/pattern-specs.md) 参照。

| Pattern | Name | Use When |
|---------|------|----------|
| **A** | Title + Body | 長文説明・報告（5行以上 bullet）。3-4項目 → E、3列構成 → K を優先 |
| **B** | Two Column | 2概念の並列比較（パネル型）。因果関係あり → T、Do/Don't → L を検討 |
| **C** | Section Divider | Chapter break (dark background) |
| **D** | Key Message | 1文のインパクトメッセージ。長文が必要 → A。引用 → AF |
| **E** | Bullet with GT Icon | 発見事項・提言（3-4項目、各項目に見出し+詳細）。5項目以上 → V |
| **F** | Card Grid 2×2 | 4項目を均等に比較（2×2カード）。3項目 → K、5項目以上 → V |
| **G** | Table | 5行以上のデータ表。2-3行 → B/F。評価表 → AH/AI を検討 |
| **I** | Agenda | Table of contents (4–7 items) |
| **J** | KPI / Metrics | **Base**: 2〜4 KPIカード横並び。**Variant: Hero Stat**: 1大統計＋3小統計（Slide 52タイプ） |
| **K** | 3-Column | 3つの柱・原則・カテゴリ（3列パネル）。2列 → B、4項目 → F。**Variant: Numbered Badge**: 番号バッジ付き3〜4列（Slide 50-51タイプ、`N_COLS=3` or `4`） |
| **L** | Do / Don't | 推奨 vs 注意（Do/Don't）。中立比較 → B |
| **M** | Chart | **Basic**: column, bar, line, pie, stacked column, area — `charts.py` ヘルパー。**Advanced**: radar, doughnut, scatter, bubble, combination (column+line), range bar — `XL_CHART_TYPE` 直接使用。詳細は [chart-specs.md](references/chart-specs.md) |
| **N** | Team Intro / Org Chart | **Base**: 写真付きチーム紹介カード（2〜6人）。**Variant: Org Chart**: 階層型組織図（矩形＋コネクター） |
| **P** | Chevron Flow | **Base**: 4〜6ステップ1行フロー。**Variant: Labeled-Chevron**: ラベル＋サブタイトル＋本文3段構成。**Variant: Multi-row**: 7+ステップ2行。**Variant: Iterative Loop**: フィードバック矢印付き |
| **Q** | Icon Grid | サービス/機能カタログ（アイコン付き3-6項目）。3列+まとめ → U |
| **R** | Split Visual | 画像+テキスト説明（画像が主役）。画像なし → A |
| **S** | Framework Matrix | 行ラベル付き評価基準表。一般テーブル → G。◎○△×評価 → AH |
| **T** | Two-Section with Arrow | 2-3段の因果・変化（課題→提案、As-Is→To-Be）。4段以上 → P。Variant: 3-Section Cascade |
| **U** | Three Column with Icons + Footer | アイコン付き3列 + まとめバー |
| **V** | Numbered Card Grid | 番号付きカードリスト（5-8項目）。4項目 → F。3項目 → K。（`from pattern_v import add_numbered_card_grid`） |
| **W** | Open-Canvas KPI | 1-3個の大統計数値をインパクト表示。4個以上 → J。**Variant: 2×2 Grid**: 4統計値を2行2列に配置 |
| **X** | Step Chart | フェーズ付きステップチャート（`from pattern_x import add_step_chart`） |
| **H** | Circular Flow | 3〜5ステップ循環 / Variant: Large Cycle |
| **Y** | Arrow Roadmap | プロジェクトスケジュール（HOME_PLATE 矢印タスク、今日線・マイルストーン対応）|
| **Z** | Maturity Model | ケイパビリティ成熟度評価 |
| **AA** | 2×2 Quadrant Matrix | 優先度・ポートフォリオ分析 |
| **AB** | Issue Tree / Logic Tree | 横ツリー / Variant: Vertical Tree |
| **AC** | Stacked Pyramid | 積み上げピラミッド |
| **AD** | Program Status Dashboard | RAGステータスダッシュボード |
| **AE** | Venn Diagram | 3円ベン図（半透明 OVAL × 3） |
| **AF** | Pull Quote | 引用符付き大型引用 |
| **AG** | Architecture / Connector Diagram | システム構成図・フロー図・アーキテクチャ図（ボックス＋矢印、ネイティブ編集可） |
| **AH** | Decision Matrix | ◎○△×記号で選択肢×評価軸を評価（推奨行 CORE_PURPLE 強調） |
| **AI** | Evaluation Scorecard | 推奨候補ハイライト行付き評価表（最終列に→総評テキスト） |
| **AJ** | Radar Chart | 多軸評価を蜘蛛の巣形で俯瞰（**線のみ・塗りなし**） |
| **AK** | Calendar | 3ヶ月カレンダー（イベント・祝日バッジ付き） |
| **AL** | Business Model Canvas | BMC 9ブロック（Key Partners〜Revenue Streams） |
| **AM** | Interview Card | ペルソナサイドバー（LIGHTEST_PURPLE）+ Q&Aリスト |
| **AN** | Layer Diagram | システムレイヤー積み上げ図（左カラー帯 + 右説明エリア） |

**Brand rules（全パターン共通）:**
- 矩形のみ — 丸角(roundRect)禁止
- グラデーション禁止 — solid fill のみ
- **交互色全面禁止** — 同種の要素（テーブル行・カード・バッジ等）に index の奇偶や順番で異なる色を割り当てることは一切禁止。色は状態（active / header）によってのみ変える
- リード↔ボディ間の水平線禁止 / テーブルヘッダー上の水平線禁止
- テーブル・チャートは `w=CW` でフル幅配置
- **テーブルの col_widths 合計 = CW（必須）:** `col_widths` を指定する場合、全カラム幅の合計を必ず `CW`（12.50"）に一致させること。合計が CW 未満だとテーブルが左寄りになり右側に空白が生じる
- **テーブルの番号カラム幅ルール（必須）:** 項目番号・連番・Q番号を表示するカラムは、最長テキストが**1行に収まる幅**を必ず確保すること。目安: 1桁整数 → 0.45"、2桁整数 → 0.55"、"X.X" 形式 → 0.65"、"QXX" 形式 → 0.65"。幅不足で "10" が "1\n0" や "2.1" が "2.\n1" と縦折れするのは**致命的な表示崩れ**であり絶対禁止
- **パネル内ヘッダー/ボディの y 座標重なり禁止:** Pattern B / K 等でパネル内にヘッダーとボディを配置する場合、ヘッダー bottom（y+h）とボディ top の間に最低 0.10" のギャップを確保すること。ヘッダーテキストが折り返して2行になる場合は h を 0.50" 以上にする
- `add_logo()` / `add_gt_symbol()` 呼び出し禁止（マスターが自動提供）

### Image Handling

1. ユーザーが明示パスを指定 → そのパスを使用
2. 会話中に画像が提供されている → そのパスを使用
3. CWD の `assets/` に画像ファイルがある → 内容を読んでトピックに合う画像を選ぶ
4. 画像なし → ネイティブシェイプで代替

`add_image_fit(slide, img_path, x, y, max_w, max_h)` （helpers.py）

| 状況 | パターン |
|------|---------|
| 1画像 + テキスト | Pattern R (Split Visual) |
| 1画像がメイン | full-width `add_picture` |
| 複数画像 | 2×2 `add_picture` |

### Step 5 — カバースライド

**必須ルール:**
- `add_cover_slide()` を使うこと（`add_slide()` は禁止）。背景矩形は追加しない
- 背景が紫 → WHITE 文字。背景が白 → BLACK / TEXT_BODY 文字（WHITE は不可視）
- `cover_text_color: "BLACK"` なら全プレースホルダーを BLACK / MID_GRAY で埋める
- **全プレースホルダーを必ず埋める**（未入力のまま = ヒントテキストが表示される）
- テーマごとの placeholder idx は `layout_notes.cover.placeholders` で確認
- **タイトルが2行になる場合は意味の切れ目で手動改行すること**（自動折り返しは語句の途中で切れる）。`tf.add_paragraph()` で2段落目を追加し font 設定を揃える:
  ```python
  ph.text_frame.clear()
  p1 = ph.text_frame.paragraphs[0]
  p1.text = "2026年3月 生成AI最新動向"   # ← 意味の区切りで改行
  p1.font.size = Pt(40); p1.font.bold = True; p1.font.color.rgb = WHITE; p1.font.name = FONT
  p2 = ph.text_frame.add_paragraph()
  p2.text = "レポート"                   # ← 2行目
  p2.font.size = Pt(40); p2.font.bold = True; p2.font.color.rgb = WHITE; p2.font.name = FONT
  ```

→ コード例（紫背景/白背景バリアント・ph_map パターン）は [pattern-specs.md](references/pattern-specs.md) の `## Cover slide template` 参照

**セクション区切り (Pattern C):**
```python
slide = add_slide()
bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
    Inches(0), Inches(0), prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = DARKEST_PURPLE; bg.line.fill.background()
add_breadcrumb(slide, "Section 02")   # 空文字禁止
add_title(slide, "セクションタイトル", size_pt=36)
set_footer(slide)
```

### Step 6 — チャート (Pattern M)

**Basic charts（`charts.py` ヘルパー関数）:**

```python
from charts import add_column_chart, add_bar_chart, add_line_chart, add_pie_chart, add_stacked_column_chart, add_area_chart
chart = add_column_chart(slide, title="四半期別実績",
    categories=["Q1","Q2","Q3","Q4"],
    series_data=[{"name":"2025年","values":[100,120,130,150]}],
    x=ML, y=2.30, w=CW, h=4.20, font_name=FONT, show_data_labels=True)
```

**Advanced charts（`XL_CHART_TYPE` 直接使用 — 詳細コード例は [chart-specs.md](references/chart-specs.md)）:**

| チャート | 定数 | 用途 |
|---------|------|------|
| Radar | `RADAR` / `RADAR_FILLED` / `RADAR_MARKERS` | 多軸評価、スキルアセスメント |
| Doughnut | `DOUGHNUT` | Pie の変形、中央に大数値を重ねて表示 |
| Scatter | `XY_SCATTER` / `XY_SCATTER_LINES` | 2変数の相関・分布 |
| Bubble | `BUBBLE` | 3変数可視化（X, Y, サイズ） |
| Combination | Column + Line 重ね合わせ | 量（棒）とトレンド（線）の同時表示 |
| Range Bar | `BAR_STACKED` 透明オフセット | 工程開始〜終了範囲（Gantt的） |

```python
# Advanced chart imports
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import ChartData, XyChartData, BubbleChartData
```

### Step 7 — アイコン (Pattern Q)

```python
# 初回セットアップ: python ~/.claude/skills/acnpptx/scripts/icon_utils.py
from icon_utils import add_icon_grid, find_icons
find_icons("cloud")
add_icon_grid(slide, prs, [("cloud","クラウド"),("ai","AI")],
    x=ML, y=2.40, total_w=CW, total_h=3.80, cols=3, font_name=FONT)
```

### Step 8 — 既存 PPTX のテーマ移行（オプション）

```bash
PYTHONUTF8=1 python ~/.claude/skills/acnpptx/scripts/retheme.py deck.pptx <target>
PYTHONUTF8=1 python ~/.claude/skills/acnpptx/scripts/retheme.py deck.pptx <target> --from fiori
PYTHONUTF8=1 python ~/.claude/skills/acnpptx/scripts/retheme.py deck.pptx <target> --out deck_out.pptx
```

処理詳細（カラーマップ構築・schemeClr 解決・placeholder 移植・空 placeholder 除去）は [retheme-guide.md](references/retheme-guide.md) 参照。

### Step 8b — 必須クロージングシーケンス

```python
make_closing_slide(prs)          # デフォルト "Thank You"、左寄せ。ユーザーが別テキストを指定した場合のみ変更
# 白背景テーマ: make_closing_slide(prs, text_color=BLACK)
# 別テキストを指定する場合のみ: make_closing_slide(prs, "ありがとうございました")
strip_sections(prs)              # PowerPoint セクションヘッダーを削除
prs.save(output_path)
```

### Step 9 — 検証

```bash
python ~/.claude/skills/acnpptx/scripts/brand_check.py output.pptx
python ~/.claude/skills/acnpptx/scripts/verify_pptx.py output.pptx
python ~/.claude/skills/acnpptx/scripts/thumbnail.py output.pptx slides/
python -m markitdown output.pptx   # "タイトルを入力" 等のヒントテキスト残留チェック
```

全 ERROR を修正。WARNING を確認。詳細チェック内容・目視確認チェックリストは [verify-guide.md](references/verify-guide.md) 参照。

**🚨 目視確認必須チェックリスト（thumbnail生成後、全スライドを必ず確認）:**
1. **ヒントテキスト残留**: 「Presenter 14pt」「テキストを入力」「Place subtitle here」等が見えていないか（markitdownでも確認）
2. **余白過多**: コンテンツエリアの下半分が空白になっていないか。空白が目立つスライドはレイアウト変更またはコンテンツ追加
3. **テキスト重なり**: 図形とテキストが重なっていないか（特にChevron詳細、Circular Flow矢印）
4. **文字切れ**: テキストがボックスからはみ出していないか（特にKPI大数値、テーブルセル）
5. **矢印・コネクター**: 接続元と接続先が正しいか（Circular Flowの矢印が循環を形成しているか）
6. **カバー**: 全プレースホルダーが適切に埋められているか。未使用phにヒントテキストが残っていないか
7. **パターン品質**: 各パターンが「そのパターンらしく」見えているか。カードが空っぽ、パネルが歪等がないか

**問題を発見したら必ず修正してから納品すること。「自動チェックがパスした」だけでは不十分。目視確認が最終ゲート。**

---

## API Quick Reference

詳細パラメーター・コード例は [api-reference.md](references/api-reference.md) 参照。

**helpers.py:** `clear_placeholders` / `add_breadcrumb` / `add_title` / `add_message_line` / `set_footer` / `make_closing_slide` / `strip_sections` / `accent_color` / `accent_color_hex` / `make_dark_divider` / `add_title_accent_line`

**native_shapes.py:** `add_arrow_right/left/down/up` / `add_connector_arrow` / `add_divider_line` / `add_accent_corner` / `add_highlight_bar` / `add_chevron_flow`

**charts.py:** `add_column_chart` / `add_bar_chart` / `add_line_chart` / `add_pie_chart` / `add_stacked_column_chart` / `add_area_chart`

**icon_utils.py:** `build_icon_index` / `find_icons` / `add_icon` / `add_icon_grid`

**Layout constants:** `CY=1.50` / `BY=6.85` / `AH=5.35` / `ML=0.42` / `CW=12.50` / `MSG_Y=0.95`

---

## Colors & Typography

カラー定数 Python クイックリファレンス → [color-palette.md](references/color-palette.md) の "Python Quick Reference" セクション

フォントサイズ表（コンテンツ/カバー別）→ [brand-guidelines.md](references/brand-guidelines.md) の "Font sizes" セクション

**13pt 使用禁止。** 使用可能: 12 / 14 / 18 / 28 / 36〜44

---

## Common Mistakes

> ⚠ **コード生成前に必ず [references/common-mistakes.md](references/common-mistakes.md) を確認すること。**