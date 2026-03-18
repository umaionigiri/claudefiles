# Pattern Specifications — Accenture Brand Patterns

39 patterns (A–AN) + cover/section. Choose the best fit for your content.
All patterns use native shapes only (SVG is not used).

## Layout Constants (inches)
```
ML=0.42  MR=0.42  CW=12.50  CY=1.50  BY=6.85  AH=5.35
Slide: 13.333" × 7.500"
Breadcrumb: idx=11, y=0.08, h=0.27
Title:       idx=0,  y=0.42, h=0.48  (bottom=0.90)
Message line:        y=0.95, h=0.45  (bottom=1.40)
Content area:        y=1.50 → BY=6.85
```

**Typography rules (apply to ALL patterns):**
- Titles: 28pt bold, BLACK (#000000), sentence case
- Message line: **18pt** bold, DARK_PURPLE (#7500C0) — mandatory on all content slides except cover/section/agenda
- Lead/intro: 18pt regular, TEXT_BODY (#333333)
- Body/bullets: 14pt regular, TEXT_BODY (#333333)
- Label on colored bg: 14pt regular/bold, WHITE (#FFFFFF)
- Box sub-info: 14pt regular, TEXT_BODY (#333333)
- Caption/note: **12pt** regular, MID_GRAY (#818180)  ← 13pt is FORBIDDEN
- Breadcrumb: **12pt** MID_GRAY
- Footer: 8pt TEXT_SUB (#666666)

**Font size rule: only 8 / 12 / 14 / 18 / 28 / 36–44pt allowed. 11pt and 13pt are forbidden.**

**Container minimum rule: text inside any box, card, panel, or table cell must be ≥14pt. 12pt is reserved for captions/notes *outside* containers only.**

**Message line placement (all patterns):**
```
Breadcrumb  (y=0.08, idx=11, 12pt MID_GRAY)
Title       (y=0.42, idx=0,  28pt bold BLACK)
────────────────────────────────── ← add_message_line() at y=MSG_Y=0.95
Message line (y=0.95, 18pt bold DARK_PURPLE)
──────────────────────────────────
Content area starts at CY=1.50
```


---

## Cover slide template

**必須**: `add_cover_slide()` を使うこと。`add_slide()` は禁止。背景矩形を追加しない（マスターが背景・ロゴ・GTを自動提供）。

**背景色と文字色のルール:**
- `cover_text_color: "BLACK"` → 全プレースホルダーを BLACK / MID_GRAY
- 紫背景 → WHITE 文字、白背景 → BLACK / TEXT_BODY 文字（WHITE は不可視になる）

```python
# ── パターン1: idx=0/1 のテーマ（紫背景デフォルト） ──────────────────────
slide = add_cover_slide()
for ph in slide.placeholders:
    idx = ph.placeholder_format.idx
    ph.text_frame.clear()
    p = ph.text_frame.paragraphs[0]
    if idx == 0:        # Main title
        p.text = "プレゼンテーションタイトル"
        p.font.size = Pt(40); p.font.bold = True
        p.font.color.rgb = WHITE; p.font.name = FONT   # 白背景なら BLACK に変更
    elif idx == 1:      # Subtitle
        p.text = "FY2025最新動向 / AI時代の成長戦略"
        p.font.size = Pt(22)
        p.font.color.rgb = WHITE; p.font.name = FONT   # 白背景なら TEXT_BODY に変更
    else:               # Date / author
        p.text = "2026年3月"
        p.font.size = Pt(16)
        p.font.color.rgb = LIGHT_PURPLE; p.font.name = FONT  # 白背景なら MID_GRAY に変更

# ── パターン2: idx が異なるテーマ（theme JSON の layout_notes.cover.placeholders を参照） ──
# 例: sample_sha → idx=10 (組織名), idx=11 (タイトル), idx=12 (日付)
slide = prs.slides.add_slide(prs.slide_layouts[LAYOUT_COVER])
ph_map = {
    10: ("組織名 / 部署名",           18, False, BLACK),
    11: ("プレゼンテーションタイトル", 36, True,  BLACK),
    12: ("2026年3月",                 14, False, MID_GRAY),
}
for ph in slide.placeholders:
    idx = ph.placeholder_format.idx
    if idx in ph_map:
        text, size, bold, color = ph_map[idx]
        ph.text_frame.clear()
        p = ph.text_frame.paragraphs[0]
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size); run.font.bold = bold
        run.font.color.rgb = color; run.font.name = FONT
```
---

## Pattern A — Title + Body (Standard)
**Use**: Text-heavy explanations, reports, meeting content

```
Title (28pt bold, BLACK)
─────────────────────────
Lead sentence (18pt)

• Bullet 1 (14pt)
• Bullet 2
• Bullet 3
```

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Title | ML | CY | CW | 0.60 | NONE | 28pt bold BLACK |
| Lead | ML | 2.40 | CW | 0.55 | NONE | 18pt TEXT_BODY |
| Body | ML | 3.10 | CW | 3.20 | NONE | 14pt TEXT_BODY |

GT symbol and logo are provided by the slide master — do NOT add them manually.

```python
slide = add_slide()
add_breadcrumb(slide, "Section > Topic")
add_title(slide, "スライドタイトル")
add_message_line(slide, "スライドの主張を常体で。60字以内。")

body = slide.shapes.add_textbox(Inches(ML), Inches(CY), Inches(CW), Inches(AH))
tf = body.text_frame; tf.word_wrap = True
for i, line in enumerate(["ポイント1", "ポイント2", "ポイント3"]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = f"• {line}"; p.font.size = Pt(14)
    p.font.color.rgb = TEXT_BODY; p.font.name = FONT

set_footer(slide)
```

---

## Pattern B — Two Column
**Use**: Comparisons, before/after, two parallel concepts

Each panel has a 0.08" CORE_PURPLE accent bar at top.

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Title | ML | CY | CW | 0.55 | NONE |
| Left panel | ML | 2.35 | 6.00 | 4.00 | OFF_WHITE |
| Left accent bar | ML | 2.35 | 6.00 | 0.08 | CORE_PURPLE |
| Left header | ML+0.15 | 2.50 | 5.70 | 0.35 | NONE, 16pt bold |
| Left body | ML+0.15 | 2.95 | 5.70 | 3.20 | NONE, 14pt |
| Right panel | 6.92 | 2.35 | 6.00 | 4.00 | OFF_WHITE |
| Right accent bar | 6.92 | 2.35 | 6.00 | 0.08 | CORE_PURPLE |
| Right header | 7.07 | 2.50 | 5.70 | 0.35 | NONE, 16pt bold |
| Right body | 7.07 | 2.95 | 5.70 | 3.20 | NONE, 14pt |

---

## Pattern C — Section Divider (Dark)
**Use**: Chapter breaks, agenda transitions

Full-slide DARKEST_PURPLE (#460073) background.
Title: 36pt bold WHITE, placed via `add_title(slide, "...", size_pt=36)`.
Subtitle: **28pt** LIGHT_PURPLE (#C2A3FF), added as textbox below title.

Logo and GT symbol are embedded in the slide master layout — do NOT add them manually.

**Breadcrumb must not be empty.** Passing `""` renders as "テキストを入力" in thumbnails. Always pass the section name/number.

```python
slide = add_slide()

# Full-slide dark background
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
bg = slide.shapes.add_shape(MSO.RECTANGLE,
    Inches(0), Inches(0), prs.slide_width, prs.slide_height)
bg.fill.solid(); bg.fill.fore_color.rgb = DARKEST_PURPLE
bg.line.fill.background()

# Breadcrumb — always provide section name (never empty string)
add_breadcrumb(slide, "Section 02")   # ← use actual section number/name

# Title
add_title(slide, "セクションタイトル", size_pt=36)

# Optional subtitle textbox
tb = slide.shapes.add_textbox(Inches(ML), Inches(3.90), Inches(CW), Inches(0.60))
p = tb.text_frame.paragraphs[0]
p.text = "セクションのサブタイトルや概要説明文"
p.font.size = Pt(28); p.font.color.rgb = LIGHT_PURPLE; p.font.name = FONT

set_footer(slide)
```

---

## Pattern D — Key Message (Impact)
**Use**: Single bold statement, key insight, executive summary opener

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Title (small) | ML | CY | CW | 0.50 | NONE | 20pt bold BLACK |
| Accent bar | ML | 2.40 | 1.20 | 0.06 | CORE_PURPLE | — |
| Key message | ML | 2.55 | CW | 1.80 | NONE | 32pt bold BLACK |
| Supporting | ML | 5.20 | CW | 1.30 | NONE | 14pt TEXT_BODY |

---

## Pattern E — Bullet with Accent Mark
**Use**: Key findings, recommendations, executive readout

3–4 items max. Each row: small CORE_PURPLE accent rectangle (0.06"×0.28") + headline (18pt bold) + detail (14pt).

```python
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO

row_h = 1.35  # per item
for i, (headline, detail) in enumerate(items):
    row_y = CY + 0.60 + i * row_h
    # Accent mark (thin vertical rectangle instead of GT image)
    acc = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(ML), Inches(row_y + 0.05), Inches(0.06), Inches(0.28))
    acc.fill.solid(); acc.fill.fore_color.rgb = CORE_PURPLE
    acc.line.fill.background()
    # Headline text at x=ML+0.18, font 18pt bold
    tb_h = slide.shapes.add_textbox(Inches(ML + 0.18), Inches(row_y),
        Inches(CW - 0.18), Inches(0.42))
    p_h = tb_h.text_frame.paragraphs[0]
    p_h.text = headline; p_h.font.size = Pt(18)
    p_h.font.bold = True; p_h.font.color.rgb = TEXT_BODY; p_h.font.name = FONT
    # Detail text
    tb_d = slide.shapes.add_textbox(Inches(ML + 0.18), Inches(row_y + 0.45),
        Inches(CW - 0.18), Inches(0.85))
    p_d = tb_d.text_frame.paragraphs[0]
    p_d.text = detail; p_d.font.size = Pt(14)
    p_d.font.color.rgb = TEXT_BODY; p_d.font.name = FONT
```

---

## Pattern F — Card Grid (2×2)
**Use**: 4-item comparison, quadrant frameworks

Card: w=5.90", h=2.30", gap=0.35". Top accent bar: CORE_PURPLE, 0.06" tall.

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Card TL | ML | 2.35 | 5.90 | 2.30 | OFF_WHITE |
| Card TL bar | ML | 2.35 | 5.90 | 0.06 | CORE_PURPLE |
| Card TR | 6.92 | 2.35 | 5.90 | 2.30 | OFF_WHITE |
| Card TR bar | 6.92 | 2.35 | 5.90 | 0.06 | CORE_PURPLE |
| Card BL | ML | 4.80 | 5.90 | 2.30 | OFF_WHITE |
| Card BL bar | ML | 4.80 | 5.90 | 0.06 | CORE_PURPLE |
| Card BR | 6.92 | 4.80 | 5.90 | 2.30 | OFF_WHITE |
| Card BR bar | 6.92 | 4.80 | 5.90 | 0.06 | CORE_PURPLE |

Card title: 14pt bold BLACK inside card (y offset +0.20 from bar)
Card body: 14pt TEXT_BODY (y offset +0.55 from bar)

---

## Pattern G — Table
**Use**: Data tables, structured information

Header row: DARKEST_PURPLE fill + WHITE 14pt bold text
Data rows: WHITE（単色）, 14pt TEXT_BODY — **交互色禁止**

```python
table = slide.shapes.add_table(
    rows, cols, Inches(ML), Inches(2.30), Inches(CW), Inches(4.00)
).table

# Header
for c, h in enumerate(headers):
    cell = table.cell(0, c)
    cell.text = h
    cell.fill.solid(); cell.fill.fore_color.rgb = DARKEST_PURPLE
    for para in cell.text_frame.paragraphs:
        para.font.bold = True; para.font.size = Pt(14)
        para.font.color.rgb = WHITE; para.font.name = FONT

# Data rows（全行 WHITE — 交互色禁止）
for r, row in enumerate(data, 1):
    for c, val in enumerate(row):
        cell = table.cell(r, c); cell.text = str(val)
        cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
        for para in cell.text_frame.paragraphs:
            para.font.size = Pt(14)
            para.font.color.rgb = TEXT_BODY; para.font.name = FONT
```

---

## Pattern I — Agenda (目次)
**Use**: Table of contents, section overview (typically 4–7 items)

Numbered boxes on left + section text on right. Active section highlighted.

```
[01]  背景・課題
[02]  ソリューション概要
[03]  効果と実績
[04]  まとめ・Q&A
```

アジェンダにはメッセージラインが不要。アイテムを CY から開始し、アイテム数に応じてスペーシングを動的に計算する。

**⚠ バッジ色は DARKEST_PURPLE 単色。i の奇偶や index で色を変えることは絶対禁止。**
active なアイテムのみ CORE_PURPLE に変える（active_idx=None の場合は全て DARKEST_PURPLE）。

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Title | ML | CY | CW | 0.55 | NONE | 28pt bold BLACK |
| Number box [n] | ML | ITEM_Y + n*gap | 0.55 | 0.65 | DARKEST_PURPLE（全バッジ統一） | 20pt bold WHITE |
| Item text | ML+0.70 | ITEM_Y + n*gap + 0.08 | 11.30 | 0.50 | NONE | 18pt TEXT_BODY |
| Active bar | ML | ITEM_Y + active*gap | 0.06 | 0.65 | CORE_PURPLE（active のみ） | — |

`ITEM_Y = CY + 0.10`（タイトル直下から開始）
`gap = min(0.90, (BY - ITEM_Y - 0.65) / max(len(items) - 1, 1))`（4〜7アイテム対応）

```python
items = ["背景・課題", "ソリューション", "効果と実績", "まとめ"]
active_idx = None  # or 0,1,2... to highlight current section

ITEM_Y = CY + 0.10   # タイトル直下から開始（2.35" は下すぎる）
gap = min(0.90, (BY - ITEM_Y - 0.65) / max(len(items) - 1, 1))

for i, item in enumerate(items):
    iy = ITEM_Y + i * gap
    # Number badge
    num_box = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(iy), Inches(0.55), Inches(0.65))
    num_box.fill.solid()
    num_box.fill.fore_color.rgb = (CORE_PURPLE if i == active_idx
                                   else DARKEST_PURPLE)
    num_box.line.fill.background()
    tf = num_box.text_frame
    tf.word_wrap = False   # ← 必須: "01" が "0\n1" と縦割れするのを防ぐ
    from pptx.oxml.ns import qn as _qn
    _bp = tf._txBody.find(_qn('a:bodyPr'))
    for _attr in ('lIns', 'rIns', 'tIns', 'bIns'):
        _bp.set(_attr, '0')   # 内部余白ゼロで折り返しを完全排除
    _bp.set('anchor', 'ctr')  # 垂直中央
    tf.paragraphs[0].text = f"{i+1:02d}"
    tf.paragraphs[0].font.size = Pt(18)   # 20→18pt: 0.55" 幅で安全に収まるサイズ
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.color.rgb = WHITE
    tf.paragraphs[0].font.name = FONT
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Item text
    tb = slide.shapes.add_textbox(
        Inches(ML + 0.70), Inches(iy + 0.08),
        Inches(11.30), Inches(0.50))
    p = tb.text_frame.paragraphs[0]
    p.text = item
    p.font.size = Pt(18)
    p.font.color.rgb = (BLACK if i == active_idx else TEXT_BODY)
    p.font.bold = (i == active_idx)
    p.font.name = FONT
```

---

## Pattern J — KPI / Metrics
**Use**: Key numbers, performance results (2–4 KPIs side by side)

Large value (48–60pt) + label (14pt) + detail (12pt), evenly spaced.

```
┌────────┐  ┌────────┐  ┌────────┐
│  82%   │  │  1.8x  │  │  60日  │
│KPI達成率│  │ 生産性  │  │ 削減期間│
│前年比+12%│  │AI導入後 │  │リード短縮│
└────────┘  └────────┘  └────────┘
```

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Title | ML | CY | CW | 0.55 | NONE | 28pt bold BLACK |
| Accent bar (full) | ML | 2.35 | CW | 0.06 | CORE_PURPLE | — |
| KPI card [n] | ML + n*(CW/N) | 2.60 | CW/N - 0.20 | 3.50 | OFF_WHITE | — |
| KPI card bar | same x | 2.60 | same w | 0.06 | DARKEST_PURPLE | — |
| Value text | inside card | +0.50 | — | 0.80 | NONE | 52pt bold DARKEST_PURPLE |
| Label text | inside card | +1.50 | — | 0.40 | NONE | 14pt bold BLACK |
| Detail text | inside card | +2.00 | — | 0.35 | NONE | 12pt MID_GRAY |

```python
kpis = [
    {"value": "82%", "label": "KPI達成率", "detail": "前年比+12%"},
    {"value": "1.8x", "label": "生産性向上", "detail": "AI導入後"},
    {"value": "60日", "label": "リード削減", "detail": "期間短縮"},
]
n = len(kpis)
card_w = (CW - 0.20 * (n - 1)) / n

for i, kpi in enumerate(kpis):
    cx = ML + i * (card_w + 0.20)
    cy = 2.60
    # Card background
    card = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(cx), Inches(cy), Inches(card_w), Inches(3.50))
    card.fill.solid(); card.fill.fore_color.rgb = OFF_WHITE
    card.line.fill.background()
    # Top accent bar
    bar = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(cx), Inches(cy), Inches(card_w), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = DARKEST_PURPLE
    bar.line.fill.background()
    # Value
    def _add_tb(text, x, y, w, h, size, bold, color):
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        p = tb.text_frame.paragraphs[0]
        p.text = text; p.font.size = Pt(size); p.font.bold = bold
        p.font.color.rgb = color; p.font.name = FONT
        p.alignment = PP_ALIGN.CENTER
        return tb
    _add_tb(kpi["value"], cx, cy + 0.40, card_w, 0.80, 52, True, DARKEST_PURPLE)
    _add_tb(kpi["label"], cx, cy + 1.40, card_w, 0.40, 14, True, BLACK)
    _add_tb(kpi.get("detail", ""), cx, cy + 1.90, card_w, 0.35, 12, False, MID_GRAY)
```

**Variant: Hero Stat + Supporting Stats（1大統計＋3小統計）**

1つの主要指標を大きく、残りをその下に並べるレイアウト（Slide 52 タイプ）。

```python
# Hero stat (full-width card, prominent)
hero = {"value": "94%", "label": "顧客満足度", "detail": "過去最高水準を記録"}
hero_h = 2.60
hero_card = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
    Inches(ML), Inches(CY), Inches(CW), Inches(hero_h))
hero_card.fill.solid(); hero_card.fill.fore_color.rgb = OFF_WHITE
hero_card.line.fill.background()
bar = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
    Inches(ML), Inches(CY), Inches(CW), Inches(0.06))
bar.fill.solid(); bar.fill.fore_color.rgb = DARKEST_PURPLE; bar.line.fill.background()
_add_tb(hero["value"],  ML, CY + 0.30, CW, 1.00, 64, True,  DARKEST_PURPLE)
_add_tb(hero["label"],  ML, CY + 1.40, CW, 0.40, 18, True,  BLACK)
_add_tb(hero["detail"], ML, CY + 1.90, CW, 0.40, 14, False, MID_GRAY)

# Supporting stats (3 equal cards below hero)
sub_kpis = [
    {"value": "1.8x", "label": "生産性向上",  "detail": "AI導入後"},
    {"value": "60日", "label": "リード削減",  "detail": "期間短縮"},
    {"value": "¥2.4B","label": "コスト削減額","detail": "累計"},
]
sub_y   = CY + hero_h + 0.20
sub_h   = BY - sub_y - 0.10
sub_n   = len(sub_kpis)
sub_w   = (CW - 0.20 * (sub_n - 1)) / sub_n
for i, kpi in enumerate(sub_kpis):
    cx = ML + i * (sub_w + 0.20)
    sc = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(cx), Inches(sub_y), Inches(sub_w), Inches(sub_h))
    sc.fill.solid(); sc.fill.fore_color.rgb = OFF_WHITE; sc.line.fill.background()
    sb = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(cx), Inches(sub_y), Inches(sub_w), Inches(0.06))
    sb.fill.solid(); sb.fill.fore_color.rgb = CORE_PURPLE; sb.line.fill.background()
    _add_tb(kpi["value"],  cx, sub_y + 0.25, sub_w, 0.65, 36, True,  DARKEST_PURPLE)
    _add_tb(kpi["label"],  cx, sub_y + 0.95, sub_w, 0.35, 14, True,  BLACK)
    _add_tb(kpi["detail"], cx, sub_y + 1.35, sub_w, 0.30, 12, False, MID_GRAY)
```

---

## Pattern K — Three Column
**Use**: Three pillars, three principles, three workstreams

Same structure as B but with 3 equal panels (w≈3.90").

**⚠ 全パネルの背景色は OFF_WHITE 単色で統一。CORE_PURPLE / DARKEST_PURPLE 等の紫系を交互・混在で使うことは絶対禁止。上部アクセントバーのみ CORE_PURPLE。**

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Title | ML | CY | CW | 0.55 | NONE |
| Panel 1 | ML | 2.35 | 3.90 | 4.00 | OFF_WHITE（全パネル統一） |
| Panel 1 bar | ML | 2.35 | 3.90 | 0.08 | CORE_PURPLE |
| Panel 2 | 4.62 | 2.35 | 3.90 | 4.00 | OFF_WHITE（全パネル統一） |
| Panel 2 bar | 4.62 | 2.35 | 3.90 | 0.08 | CORE_PURPLE |
| Panel 3 | 8.82 | 2.35 | 3.90 | 4.00 | OFF_WHITE（全パネル統一） |
| Panel 3 bar | 8.82 | 2.35 | 3.90 | 0.08 | CORE_PURPLE |

Panel header: 14pt bold BLACK, y offset +0.20 from bar
Panel body: 14pt TEXT_BODY, y offset +0.65 from bar
Gap between panels: 0.30"

**Variant: Numbered Badge Header（番号付き3〜4列、Slide 50-51 タイプ）**

各パネルの上部に番号バッジ（DARKEST_PURPLE 円 + 白数字）を置くレイアウト。
列数 `N_COLS = 3` または `4` を変えるだけで 3列・4列どちらも対応。

```python
N_COLS   = 3           # 3 or 4
PANEL_W  = (CW - 0.20 * (N_COLS - 1)) / N_COLS
PANEL_H  = BY - CY - 0.30
BADGE_D  = 0.48        # badge circle diameter

panels = [
    {"num": 1, "title": "第1の柱",  "body": "・ 施策A\n・ 施策B\n・ 施策C"},
    {"num": 2, "title": "第2の柱",  "body": "・ 施策D\n・ 施策E\n・ 施策F"},
    {"num": 3, "title": "第3の柱",  "body": "・ 施策G\n・ 施策H\n・ 施策I"},
]

for i, panel in enumerate(panels):
    px = ML + i * (PANEL_W + 0.20)
    py = CY + 0.55   # leave room for badge above panel

    # Panel background
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(px), Inches(py), Inches(PANEL_W), Inches(PANEL_H))
    bg.fill.solid(); bg.fill.fore_color.rgb = OFF_WHITE; bg.line.fill.background()

    # Top accent bar
    bar = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(px), Inches(py), Inches(PANEL_W), Inches(0.06))
    bar.fill.solid(); bar.fill.fore_color.rgb = CORE_PURPLE; bar.line.fill.background()

    # Number badge (circle, overlapping top of panel)
    bx = px + (PANEL_W - BADGE_D) / 2
    badge = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(bx), Inches(py - BADGE_D / 2), Inches(BADGE_D), Inches(BADGE_D))
    badge.fill.solid(); badge.fill.fore_color.rgb = DARKEST_PURPLE; badge.line.fill.background()
    tf = badge.text_frame
    p = tf.paragraphs[0]; p.text = str(panel["num"])
    p.font.size = Pt(18); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    # Panel title
    tb_t = slide.shapes.add_textbox(Inches(px + 0.15), Inches(py + 0.20),
        Inches(PANEL_W - 0.30), Inches(0.50))
    p = tb_t.text_frame.paragraphs[0]; p.text = panel["title"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = BLACK; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER

    # Panel body
    tb_b = slide.shapes.add_textbox(Inches(px + 0.15), Inches(py + 0.80),
        Inches(PANEL_W - 0.30), Inches(PANEL_H - 1.00))
    tf = tb_b.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = panel["body"]
    p.font.size = Pt(14); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
```

---

## Pattern L — Do / Don't
**Use**: Best practices, recommendations vs. anti-patterns

Left panel = Do (green check indicator), Right = Don't (red X indicator).
Indicator: small colored accent bar at top (CORE_PURPLE for Do, DARK_PURPLE for Don't).

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Title | ML | CY | CW | 0.55 | NONE |
| Do panel | ML | 2.35 | 6.00 | 4.20 | OFF_WHITE |
| Do bar | ML | 2.35 | 6.00 | 0.08 | CORE_PURPLE |
| Do label | ML+0.15 | 2.50 | 2.50 | 0.35 | NONE | 16pt bold CORE_PURPLE |
| Do body | ML+0.15 | 2.95 | 5.70 | 3.40 | NONE | 14pt TEXT_BODY |
| Don't panel | 6.92 | 2.35 | 6.00 | 4.20 | OFF_WHITE |
| Don't bar | 6.92 | 2.35 | 6.00 | 0.08 | DARK_PURPLE |
| Don't label | 7.07 | 2.50 | 2.50 | 0.35 | NONE | 16pt bold DARK_PURPLE |
| Don't body | 7.07 | 2.95 | 5.70 | 3.40 | NONE | 14pt TEXT_BODY |

"✓ Do" label uses CORE_PURPLE; "✗ Don't" label uses DARK_PURPLE.

> ⚠ **ラベル textbox には必ず `tf.word_wrap = False` を設定すること。** デフォルトは True なので設定しないと「✓ Do（推奨）」が途中で折り返す。ラベル幅は 2.50" を使うこと（1.50" は Japanese 混在で折り返しが発生する）。
>
> ```python
> tb = slide.shapes.add_textbox(Inches(ML+0.15), Inches(2.50), Inches(2.50), Inches(0.35))
> tf = tb.text_frame
> tf.word_wrap = False   # ← 必須
> p = tf.paragraphs[0]
> p.text = "✓ Do（推奨）"
> p.font.size = Pt(16); p.font.bold = True
> p.font.color.rgb = CORE_PURPLE; p.font.name = FONT
> ```

---

## Pattern M — Chart
**Use**: Data visualization (bar, column, line, pie charts)

Use `scripts/charts.py` helpers. Chart occupies CX=9" H=4.20" area.
Optional description text on left (w=3.50") or below the chart.

```python
from charts import add_column_chart, add_bar_chart, add_line_chart, add_pie_chart

# Full-width chart (title + chart + footer)
chart = add_column_chart(
    slide,
    title="グラフタイトル",   # displayed inside chart area
    categories=["Q1", "Q2", "Q3", "Q4"],
    series_data=[
        {"name": "2025", "values": [100, 120, 130, 150]},
        {"name": "2026", "values": [110, 135, 145, 170]},
    ],
    x=ML, y=2.30, w=CW, h=4.20,
    font_name=FONT,
)

# Left description + right chart layout
# Description: x=ML, y=2.30, w=3.50, h=4.00
# Chart:       x=4.20, y=2.30, w=8.60, h=4.00
```

**Chart type selection guide:**
- Column (vertical bars): comparisons across categories, time series
- Bar (horizontal): rankings, comparisons with long labels
- Line: trends over time, continuous data
- Pie: composition/breakdown (max 5–6 slices)
- Stacked column: part-to-whole across categories

---

## Pattern N — Team Introduction
**Use**: Team member showcase (2–6 people)

Photo placeholder + name + title + optional description.

```
[Photo]    [Photo]    [Photo]
 Name       Name       Name
 Title      Title      Title
 Detail     Detail     Detail
```

| Shape | x (for 3-up) | y | w | h | Fill |
|-------|-------------|---|---|---|------|
| Photo box [n] | ML + n*4.25 | 2.35 | 3.50 | 2.50 | OFF_WHITE |
| Photo bar [n] | same x | 2.35 | 3.50 | 0.06 | CORE_PURPLE |
| Name [n] | same x | 4.95 | 3.50 | 0.35 | NONE | 14pt bold BLACK |
| Title [n] | same x | 5.35 | 3.50 | 0.30 | NONE | 12pt MID_GRAY |
| Detail [n] | same x | 5.70 | 3.50 | 0.55 | NONE | 12pt TEXT_BODY |

Photo box shows "[ 写真 ]" placeholder text (14pt MID_GRAY, centered).
If an image path is provided, use `add_image_fit()` instead.

---

### Variant: Org Chart（組織図）
**Use**: 報告体制・プロジェクト体制の階層可視化（2〜3層、部門間の上下関係を矩形＋コネクターで表現）。Slides 41-43 タイプ。「チーム紹介カード」（Base）と違い縦方向の階層を示す。

```
          ┌──────────────────┐
          │  Project Sponsor │
          └────────┬─────────┘
         ┌─────────┼─────────┐
         ▼         ▼         ▼
   ┌──────────┐ ┌──────────┐ ┌──────────┐
   │  Lead A  │ │  Lead B  │ │  Lead C  │
   └──────────┘ └──────────┘ └──────────┘
```

| Element | Shape | Fill | Text |
|---------|-------|------|------|
| L0 box  | RECTANGLE | DARKEST_PURPLE | WHITE 12pt bold |
| L1 box  | RECTANGLE | DARK_PURPLE    | WHITE 12pt |
| L2+ box | RECTANGLE | OFF_WHITE      | TEXT_BODY 12pt |
| Connector | add_connector_arrow | LIGHT_GRAY 1pt | arrow_end=False |

```python
from native_shapes import add_connector_arrow
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

BOX_W = 2.20
BOX_H = 0.65
H_GAP = 0.25   # sibling 間の水平間隔
V_GAP = 0.85   # 階層間の垂直間隔

# Tree: {"name", "title", "children": [...]}
org = {
    "name": "山田 太郎", "title": "Project Sponsor",
    "children": [
        {"name": "佐藤 花子", "title": "PMO Lead",
         "children": [
             {"name": "田中 一郎", "title": "Analyst"},
             {"name": "鈴木 美咲", "title": "Analyst"},
         ]},
        {"name": "高橋 健",  "title": "Tech Lead",
         "children": [
             {"name": "渡辺 涼",  "title": "Engineer"},
         ]},
        {"name": "伊藤 誠",  "title": "Change Lead", "children": []},
    ]
}

FILLS   = [DARKEST_PURPLE, DARK_PURPLE, OFF_WHITE]
TCOLORS = [WHITE,          WHITE,       TEXT_BODY]

def _leaves(node):
    if not node.get("children"):
        return 1
    return sum(_leaves(c) for c in node["children"])

def _draw_org(slide, node, level, x_left, y_top):
    lc   = _leaves(node)
    span = lc * BOX_W + max(lc - 1, 0) * H_GAP
    x_c  = x_left + span / 2
    y    = y_top + level * (BOX_H + V_GAP)

    fill = FILLS[min(level, len(FILLS) - 1)]
    tcol = TCOLORS[min(level, len(TCOLORS) - 1)]

    box = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(x_c - BOX_W / 2), Inches(y), Inches(BOX_W), Inches(BOX_H))
    box.fill.solid(); box.fill.fore_color.rgb = fill; box.line.fill.background()
    tf = box.text_frame; tf.word_wrap = False
    p1 = tf.paragraphs[0]; p1.text = node["name"]
    p1.font.size = Pt(12); p1.font.bold = True
    p1.font.color.rgb = tcol; p1.font.name = FONT; p1.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph(); p2.text = node.get("title", "")
    p2.font.size = Pt(12); p2.font.color.rgb = tcol; p2.font.name = FONT
    p2.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    if node.get("children"):
        child_y = y_top + (level + 1) * (BOX_H + V_GAP)
        cx = x_left
        for child in node["children"]:
            cl      = _leaves(child)
            child_w = cl * BOX_W + max(cl - 1, 0) * H_GAP
            child_c = cx + child_w / 2
            add_connector_arrow(slide,
                x_c,       y + BOX_H,
                child_c,   child_y,
                LIGHT_GRAY, width_pt=1, arrow_end=False)
            _draw_org(slide, child, level + 1, cx, y_top)
            cx += child_w + H_GAP

total_w = _leaves(org) * BOX_W + max(_leaves(org) - 1, 0) * H_GAP
_draw_org(slide, org, 0, ML + (CW - total_w) / 2, CY + 0.10)
```

**Tips:**
- 全体幅が CW を超える場合: `H_GAP=0.15`、`BOX_W=1.80` に縮小する
- 役職テキストが長い場合: `BOX_H=0.80`、`tf.word_wrap=True` に変更する
- 2層のみ（フラット組織）の場合: `org["children"]` にメンバーを並べ `"children": []` とする
- 部門アイコンを入れたい場合: `add_icon()` で BOX の左上に重ねる（`icon_utils.py` 参照）
- チーム紹介（写真付きカード）が必要な場合は Pattern N Base を使うこと

---


## Pattern P — Process Flow
**Use**: Multi-step process with visual flow direction (4–6 steps)

Uses `add_chevron_flow()` from `native_shapes.py`.

**標準スタイル（必須）: `shape_style='chevron'` + `use_pentagon_first=True`**

```
[▷ Step1][▷ Step2][▷ Step3][▷ Step4][▷ Step5]
 homePlate  chevron  chevron  chevron  chevron
```
- **左端のみ homePlate**（OOXML: `homePlate`、左辺が直線・右が尖る）← `pentagon` は使わない
- **残り全て chevron**（OOXML: `chevron`、左がへこんで・右が尖る）
- **全アイテムを必ず1行に収めること。2段組み・複数行分割は絶対禁止**
- `use_pentagon_first=False` 禁止

補助スタイル: `shape_style='box_triangle'` — 矩形 + ▷ 三角形セパレーター
三角形は **高さ:幅 = 1:3**（unrotated cy:cx = 1:3）。90° CW 回転後: 画面上の高さ = ボックス全高 h、幅 = h/3 のスリムな ▷。
**⚠ box_triangle ルール:**
- セパレーター三角形は **常に右向き ▷**。左向き ◁ は絶対禁止。内部で `rotation_deg=-90`（OOXML 90° CW）を使用（`rotation_deg=+90` は ◀ 左向きになるので使わない）
- `gap` は **0.10" 以上** を設定し、Box と ▷ の間に明確な余白を確保すること

```
[Step 1]  ▷  [Step 2]  ▷  [Step 3]  ▷  [Step 4]
  Detail         Detail         Detail         Detail
```

**⚠ y 座標ルール（垂直中央寄せ必須）:**
- **詳細テキストあり**: chevron + 詳細テキスト グループ全体を垂直中央に配置する
  ```python
  FLOW_H   = 0.80   # chevron の高さ
  GAP      = 0.25   # chevron と詳細テキストの間隔
  DETAIL_H = 3.00   # 詳細テキストエリアの高さ（コンテンツ量で調整）
  # グループ全体を垂直中央寄せ（AH=5.35、CY=1.50 に対して）
  FLOW_Y   = CY + (AH - FLOW_H - GAP - DETAIL_H) / 2   # ≈ 1.65"
  DETAIL_Y = FLOW_Y + FLOW_H + GAP
  ```
- **詳細テキストなし（フローのみ）**: `FLOW_Y = CY + (AH - FLOW_H) / 2`（垂直中央）
- 図形と詳細テキストが重なっていないか thumbnail で必ず確認すること

```python
from native_shapes import add_chevron_flow

steps = ["計画", "設計", "開発", "テスト", "リリース"]
details = [
    "• 要件定義・スコープ確定\n• ステークホルダー整合：全部門合意取得",
    "• アーキテクチャ設計\n• 技術選定：クラウドネイティブ採用",
    "• 実装・単体テスト\n• コードレビュー：PR承認必須",
    "• 結合テスト・UAT\n• 品質ゲート確認：不具吂0件",
    "• 本番デプロイ\n• 移行・引き渡し：SLA締結",
]


FLOW_H   = 0.80   # chevron の高さ
GAP      = 0.25   # chevron と詳細テキストの間隔
DETAIL_H = 3.00   # 詳細テキストエリアの高さ（内容量に応じて調整）
# グループ全体を垂直中央寄せ
FLOW_Y   = CY + (AH - FLOW_H - GAP - DETAIL_H) / 2
DETAIL_Y = FLOW_Y + FLOW_H + GAP

# 標準 chevron style — use_pentagon_first=True 必須（左端=pentagon、残り=chevron）
add_chevron_flow(
    slide, steps,
    x=ML, y=FLOW_Y, total_w=CW, h=FLOW_H,
    gap=0.05,
    fill_color=DARKEST_PURPLE,
    text_color=WHITE,
    font_name=FONT,
    font_size_pt=14,
    shape_style='chevron',              # ← 標準スタイル（必須）
    use_pentagon_first=True,            # ← 必須: 左端=pentagon、残り=chevron
)

# box_triangle style（補助）: gap=0.10 以上必須、三角形は右向き ▷ のみ
# add_chevron_flow(..., shape_style='box_triangle', gap=0.10, use_pentagon_first=True)

# Detail text boxes — 垂直中央寄せした DETAIL_Y から開始
n = len(steps)
flow_box_w = CW / n
for i, detail in enumerate(details):
    tb = slide.shapes.add_textbox(
        Inches(ML + i * flow_box_w), Inches(DETAIL_Y),
        Inches(flow_box_w - 0.10), Inches(DETAIL_H))
    tf = tb.text_frame; tf.word_wrap = True
    for j, line in enumerate(detail.split("
")):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(14)
        p.font.color.rgb = TEXT_BODY; p.font.name = FONT
```

**Tip**: To bold a keyword inside the subtitle (e.g., "要塞化"), use text runs:
```python
from pptx.oxml.ns import qn as _qn
tf = tb_sub.text_frame; tf.clear()
p = tf.paragraphs[0]
r1 = p.add_run(); r1.text = "基盤の"
r1.font.size = Pt(18); r1.font.color.rgb = TEXT_BODY; r1.font.name = FONT
r2 = p.add_run(); r2.text = "要塞化"
r2.font.size = Pt(18); r2.font.bold = True; r2.font.color.rgb = DARK_PURPLE; r2.font.name = FONT
```

---

### Variant: Multi-row Process Flow（7+ ステップ・複数行）
**Use**: ステップが7以上で1行に収まらない場合。行を分割し、行間に `▼` 矢印で接続。（`add_chevron_flow` は1行一方向のみのため2行に分割する）

```
[▷ S1][▷ S2][▷ S3][▷ S4][▷ S5]  ← 行1 (DARKEST_PURPLE)
                                  ▼
[▷ S6][▷ S7][▷ S8][▷ S9][▷ S10] ← 行2 (DARK_PURPLE)
```

```python
from native_shapes import add_chevron_flow, add_arrow_down
import math

steps = [
    "現状分析", "課題設定", "仮説立案", "情報収集", "データ分析",
    "施策評価", "施策策定", "プロトタイプ", "実装計画", "実行",
]

ROW_H    = 0.70   # chevron の高さ
GAP_H    = 0.55   # 行間（矢印スペース含む）
ROW_SIZE = math.ceil(len(steps) / 2)   # 均等分割
ROW_W    = CW - 0.55   # 右端に矢印スペースを確保

row1 = steps[:ROW_SIZE]
row2 = steps[ROW_SIZE:]

# 行1（左→右）
add_chevron_flow(
    slide, row1,
    x=ML, y=CY, total_w=ROW_W, h=ROW_H,
    gap=0.05, fill_color=DARKEST_PURPLE, text_color=WHITE,
    font_name=FONT, font_size_pt=12,
    shape_style='chevron', use_pentagon_first=True,
)

# 行間 ▼ 矢印（行1の右端）
add_arrow_down(slide, ML + ROW_W + 0.05, CY + ROW_H * 0.2, 0.40, GAP_H * 0.8, DARKEST_PURPLE)

# 行2（左→右。色を変えてフェーズ変化を示す）
ROW2_Y = CY + ROW_H + GAP_H
add_chevron_flow(
    slide, row2,
    x=ML, y=ROW2_Y, total_w=ROW_W, h=ROW_H,
    gap=0.05, fill_color=DARK_PURPLE, text_color=WHITE,
    font_name=FONT, font_size_pt=12,
    shape_style='chevron', use_pentagon_first=True,
)

# 詳細テキスト（行ごとに DETAIL_Y を計算）
DETAIL1_Y = CY + ROW_H + 0.10
DETAIL2_Y = ROW2_Y + ROW_H + 0.10
col_w = ROW_W / ROW_SIZE
details1 = ["• 詳細\n• 詳細"] * len(row1)
details2 = ["• 詳細\n• 詳細"] * len(row2)

for i, detail in enumerate(details1):
    tb = slide.shapes.add_textbox(
        Inches(ML + i * col_w), Inches(DETAIL1_Y),
        Inches(col_w - 0.08), Inches(GAP_H - 0.20))
    tf = tb.text_frame; tf.word_wrap = True
    for j, line in enumerate(detail.split("\n")):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
```

**Tips:**
- `ROW_SIZE = ceil(len(steps) / 2)` で均等分割。奇数の場合は行1が1つ多くなる
- 行1と行2で `fill_color` を変えるとフェーズ区分が視覚的になる（DARKEST_PURPLE / DARK_PURPLE）
- 詳細テキストの `h` は `GAP_H - 0.20` が目安。ただし `DETAIL_Y + h < ROW2_Y` を必ず守ること

---

### Variant: Iterative Loop（フィードバック付き反復フロー）
**Use**: 設計→実装→テスト→フィードバックなどのスプリントサイクル、反復改善プロセス（Slides 18-20 タイプ）。前進フローと折り返しフィードバック矢印を組み合わせる。

```
[▷ Discover][▷ Design][▷ Build][▷ Validate]
◁─────────── フィードバック ──────────────────
```

```python
from native_shapes import add_chevron_flow, add_connector_arrow

STEPS   = ["Discover", "Design", "Build", "Validate"]
FLOW_H  = 0.80

add_chevron_flow(
    slide, STEPS,
    x=ML, y=CY, total_w=CW, h=FLOW_H,
    gap=0.05, fill_color=DARKEST_PURPLE, text_color=WHITE,
    font_name=FONT, font_size_pt=14,
    shape_style='chevron', use_pentagon_first=True,
)

# 各ステップの詳細テキスト（chevron の直下）
DETAIL_Y = CY + FLOW_H + 0.12
n = len(STEPS)
col_w = CW / n
details = [
    "• ユーザーインタビュー\n• 課題定義",
    "• ワイヤーフレーム\n• プロトタイプ",
    "• スプリント開発\n• 単体テスト",
    "• UAT・ユーザー検証\n• 改善点集約",
]
for i, detail in enumerate(details):
    tb = slide.shapes.add_textbox(
        Inches(ML + i * col_w), Inches(DETAIL_Y),
        Inches(col_w - 0.10), Inches(0.70))
    tf = tb.text_frame; tf.word_wrap = True
    for j, line in enumerate(detail.split("\n")):
        p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.font.name = FONT

# フィードバック矢印（右端 → 左端、右→左 = arrow_end=True で左向き矢印）
LOOP_Y = DETAIL_Y + 0.80   # 詳細テキストの下
add_connector_arrow(slide,
    ML + CW, LOOP_Y,   # start: 右端
    ML,      LOOP_Y,   # end:   左端
    CORE_PURPLE, width_pt=2.5, arrow_end=True)

# フィードバックラベル
fb = slide.shapes.add_textbox(
    Inches(ML + CW / 2 - 1.20), Inches(LOOP_Y + 0.06),
    Inches(2.40), Inches(0.30))
p = fb.text_frame.paragraphs[0]; p.text = "フィードバック / Iteration"
p.font.size = Pt(12); p.font.color.rgb = MID_GRAY; p.font.name = FONT
p.alignment = PP_ALIGN.CENTER
```

**Tips:**
- 多層反復（Iterative Flow 3/4: Slides 19-20）の場合: 各レイヤーを独立した chevron 行として `y` を変えて積み上げ、各行に右→左のフィードバック矢印を追加する
- `LOOP_Y` は詳細テキストの下に置き、`BY - 0.30` を超えないように調整する
- `connector_type="elbow"` にすると下から回り込む L字コネクターになる（`add_connector_arrow` の `connector_type` 引数を参照）

---

## Pattern Q — Icon Grid
**Use**: Service catalog, feature overview, category listing (4–9 icons)

Icon (0.50") + label below. 3-column default, can use 2 or 4 columns.
Uses `icon_utils.add_icon_grid()`.

```
[☁️]  [🤝]  [📊]
Cloud  Deal  Chart

[💡]  [🛡️]  [🌍]
Idea  Safety Global
```

```python
from icon_utils import add_icon_grid

items = [
    ("cloud", "クラウド"),
    ("handshake", "パートナー"),
    ("chart", "分析"),
    ("bulb", "イノベーション"),
    ("security", "セキュリティ"),   # "shield" は存在しない場合あり → "security" / "lock" を試す
    ("globe", "グローバル"),
]

add_icon_grid(
    slide, prs,
    items=items,
    x=ML, y=2.40,
    total_w=CW, total_h=3.80,
    cols=3,
    icon_size=0.55,
    font_name=FONT,
    font_size_pt=12,
)
```

Without icon_index.json (first run), add_icon falls back to a labeled placeholder box.

> ⚠ **キーワードは必ず `find_icons(keyword)` で事前検証すること。** 存在しないキーワードを指定するとアイコンなし（ラベルのみ）になる。スクリプト生成前に以下で確認：
> ```python
> from icon_utils import find_icons
> for kw in ["cloud", "handshake", "chart", "bulb", "security", "lock", "globe"]:
>     print(kw, find_icons(kw)[:1])
> ```
> 代替キーワード例：セキュリティ → `"security"` / `"lock"` / `"shield"`、AI → `"robot"` / `"brain"` / `"ai"`、人・チーム → `"person"` / `"team"` / `"people"`

---

## Pattern R — Split Visual
**Use**: Image or diagram (left 40%) + text explanation (right 60%)

Useful when you have a screenshot, diagram, or photo to anchor the narrative.

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Title | ML | CY | CW | 0.55 | NONE | 28pt bold BLACK |
| Visual box | ML | 2.35 | 5.10 | 4.20 | OFF_WHITE |
| Visual bar | ML | 2.35 | 5.10 | 0.06 | CORE_PURPLE |
| Text area | 5.80 | 2.35 | 6.90 | 4.20 | NONE |
| Lead | 5.80 | 2.40 | 6.90 | 0.55 | NONE | 18pt TEXT_BODY |
| Body | 5.80 | 3.05 | 6.90 | 3.40 | NONE | 14pt TEXT_BODY |

Visual box shows "[ 図・画像 ]" placeholder or use `add_image_fit()`.

---

---

## Pattern S — Framework Matrix (枠組み比較表)
**Use**: Comparison frameworks, diagnostic rubrics, evaluation tables with labeled rows

Left column = purple row labels, right 1–2 columns = content. Use a python-pptx table for automatic row height handling.

```
┌──────────┬──────────────────────┬──────────────────────┐
│          │ 列ヘッダー A          │ 列ヘッダー B          │
├──────────┼──────────────────────┼──────────────────────┤
│ ラベル1   │ • 課題の説明          │ 対応策/要諦           │
├──────────┼──────────────────────┼──────────────────────┤
│ ラベル2   │ • 内容               │ 内容                  │
└──────────┴──────────────────────┴──────────────────────┘
```

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Table | ML | CY | CW | BY-CY-0.20 | — | — |
| Header row cells | — | — | — | — | DARKEST_PURPLE | 14pt bold WHITE center |
| Label col cells | — | — | 1.80 | — | DARKEST_PURPLE | 14pt bold WHITE center |
| Content cells | — | — | auto | — | WHITE | 14pt TEXT_BODY |

```python
labels   = ["戦略・方針", "業務", "データ", "アプリケーション"]
col_a    = ["• 全社方針なく各部門が個別PoC...", "• 個別部署優先で部分最適...", "• ボトムアップ型でモデル検討...", "• 要件考慮せずアプリを選定..."]
col_b    = ["KGI/KPIの見極めと優先順位付け", "部署横断・全体最適な業務のありたい姿の明確化", "ありたい業務からデータモデルを整理", "データモデルを整理した上でアプリを選択"]

n_rows = len(labels)
table = slide.shapes.add_table(
    n_rows + 1, 3,
    Inches(ML), Inches(CY), Inches(CW), Inches(BY - CY - 0.20)
).table

table.columns[0].width = Inches(1.80)   # label
table.columns[1].width = Inches(5.20)   # col A
table.columns[2].width = Inches(5.50)   # col B

# Header row
for c, hdr in enumerate(["", "推進上の一般的な課題", "成功の要諦"]):
    cell = table.cell(0, c)
    cell.fill.solid(); cell.fill.fore_color.rgb = DARKEST_PURPLE
    p = cell.text_frame.paragraphs[0]
    p.text = hdr; p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT
    p.alignment = PP_ALIGN.CENTER

# Data rows
from pptx.oxml.ns import qn as _qn
for r, (lbl, ca, cb) in enumerate(zip(labels, col_a, col_b), 1):
    # Label cell
    lc = table.cell(r, 0)
    lc.fill.solid(); lc.fill.fore_color.rgb = DARKEST_PURPLE
    lp = lc.text_frame.paragraphs[0]
    lp.text = lbl; lp.font.size = Pt(14); lp.font.bold = True
    lp.font.color.rgb = WHITE; lp.font.name = FONT
    lp.alignment = PP_ALIGN.CENTER
    lc.text_frame._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')
    # Content cells
    for col, text in [(1, ca), (2, cb)]:
        cc = table.cell(r, col)
        cc.fill.solid(); cc.fill.fore_color.rgb = WHITE
        cp = cc.text_frame.paragraphs[0]
        cp.text = text; cp.font.size = Pt(14)
        cp.font.color.rgb = TEXT_BODY; cp.font.name = FONT
```

**Tips:**
- Multi-line bullets in a cell: `cell.text_frame.add_paragraph()` for each line
- Emphasize specific text in a cell using runs with `run.font.bold = True` or `run.font.color.rgb = DARK_PURPLE`
- For a narrow single-column variant (no col B), set `table.columns[1].width = Inches(10.70)` and omit column 2

---

## Pattern T — Two-Section with Arrow (課題と提案)
**Use**: Problem → solution, background → proposal, as-is → to-be (2 stacked sections)

Two panels stacked vertically, each with a narrow purple label on the left and white body on the right. A filled arrow connects them.

```
┌─────────────────────────────────────────────┐
│ ラベルA │ 背景・課題の説明（箇条書き）         │
│        │ • 点1                               │
│        │ • 点2                               │
└─────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────┐
│ ラベルB │ ご提案内容（箇条書き）               │
│        │ • 点1                               │
│        │ ※ 補足事項                           │
└─────────────────────────────────────────────┘
```

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Section A bg | ML | CY | CW | section_h | OFF_WHITE, border LIGHT_GRAY |
| Section A label | ML | CY | LABEL_W | section_h | DARKEST_PURPLE |
| Section A content | ML+LABEL_W+0.10 | CY+0.15 | CW-LABEL_W-0.15 | section_h-0.30 | NONE |
| Arrow (down) | center, ~6.17 | CY+section_h+0.08 | 1.0 | 0.40 | DARKEST_PURPLE |
| Section B bg | ML | CY+section_h+0.55 | CW | section_h | OFF_WHITE, border LIGHT_GRAY |
| Section B label | ML | CY+section_h+0.55 | LABEL_W | section_h | DARKEST_PURPLE |
| Section B content | ML+LABEL_W+0.10 | … | CW-LABEL_W-0.15 | section_h-0.30 | NONE |

```python
from native_shapes import add_arrow_down
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

LABEL_W  = 1.60
ARROW_H  = 0.45
GAP      = 0.10
section_h = (BY - CY - ARROW_H - GAP * 3) / 2   # ~2.10" each

sections = [
    {"label": "ご提案の\n背景", "body": "• 背景説明1\n• 背景説明2\n• 背景説明3"},
    {"label": "ご提案\n内容",  "body": "• 提案内容1\n• 提案内容2\n※ 補足事項"},
]

for i, sec in enumerate(sections):
    sy = CY + i * (section_h + ARROW_H + GAP)

    # Panel background with border
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(sy), Inches(CW), Inches(section_h))
    bg.fill.solid(); bg.fill.fore_color.rgb = OFF_WHITE
    bg.line.color.rgb = LIGHT_GRAY; bg.line.width = Pt(0.75)

    # Left label box
    lbl = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(sy), Inches(LABEL_W), Inches(section_h))
    lbl.fill.solid(); lbl.fill.fore_color.rgb = DARKEST_PURPLE
    lbl.line.fill.background()
    tf = lbl.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = sec["label"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT
    p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    # Content area
    cx = ML + LABEL_W + 0.10
    cw = CW - LABEL_W - 0.15
    tb = slide.shapes.add_textbox(Inches(cx), Inches(sy + 0.15), Inches(cw), Inches(section_h - 0.30))
    tf2 = tb.text_frame; tf2.word_wrap = True
    for j, line in enumerate(sec["body"].split("\n")):
        p2 = tf2.paragraphs[0] if j == 0 else tf2.add_paragraph()
        p2.text = line; p2.font.size = Pt(14)
        p2.font.color.rgb = TEXT_BODY; p2.font.name = FONT

    # Arrow between sections
    if i < len(sections) - 1:
        ax = (13.333 / 2) - 0.50   # centered
        add_arrow_down(slide, ax, sy + section_h + GAP, 1.0, ARROW_H, DARKEST_PURPLE)
```

**Tips:**
- For 3+ sections, reduce `section_h` and `ARROW_H` proportionally
- Highlight key words inside body text using `run.font.bold = True` on a text run
- To widen the label column for longer labels, increase `LABEL_W` and adjust `cx`/`cw`

---

### Variant: 3-Section Cascade（3セクション以上）
**Use**: 背景→課題→提案、問題→原因→解決策など3段以上の論理構成（Slides 26-32 タイプ）。`sections` リストの要素数を変えるだけで2〜4セクションに対応。

```
┌───────────────────────────────────────┐
│ 背景   │ 外部環境の変化（市場縮小・…） │
└───────────────────────────────────────┘
                    ▼
┌───────────────────────────────────────┐
│ 課題   │ 顧客接点デジタル化の遅れ…    │
└───────────────────────────────────────┘
                    ▼
┌───────────────────────────────────────┐
│ 提案   │ CRM 統合プラットフォーム導入  │
└───────────────────────────────────────┘
```

```python
from native_shapes import add_arrow_down
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

sections = [
    {"label": "背景",   "body": "• 外部環境の変化（市場縮小・競合激化）\n• デジタル化の加速で従来モデルの限界"},
    {"label": "課題",   "body": "• 顧客接点のデジタル化が遅れ、CX が低下\n• 組織内サイロによる情報連携の断絶"},
    {"label": "提案",   "body": "• CRM 統合プラットフォームの導入\n• 横断組織体制と KPI ガバナンスの整備\n• 3ヶ月で PoC → 12ヶ月でロールアウト"},
]

LABEL_W  = 1.60
ARROW_H  = 0.38
GAP      = 0.08
n        = len(sections)   # 2〜4 対応

# セクション高さを可用領域から均等計算
section_h = (BY - CY - ARROW_H * (n - 1) - GAP * n * 2) / n

for i, sec in enumerate(sections):
    sy = CY + i * (section_h + ARROW_H + GAP * 2)

    # パネル背景
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(sy), Inches(CW), Inches(section_h))
    bg.fill.solid(); bg.fill.fore_color.rgb = OFF_WHITE
    bg.line.color.rgb = LIGHT_GRAY; bg.line.width = Pt(0.75)

    # 左ラベル
    lbl = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(sy), Inches(LABEL_W), Inches(section_h))
    lbl.fill.solid(); lbl.fill.fore_color.rgb = DARKEST_PURPLE; lbl.line.fill.background()
    tf = lbl.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = sec["label"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    # コンテンツ
    cx = ML + LABEL_W + 0.10
    cw = CW - LABEL_W - 0.15
    tb = slide.shapes.add_textbox(Inches(cx), Inches(sy + 0.15), Inches(cw), Inches(section_h - 0.30))
    tf2 = tb.text_frame; tf2.word_wrap = True
    for j, line in enumerate(sec["body"].split("\n")):
        p2 = tf2.paragraphs[0] if j == 0 else tf2.add_paragraph()
        p2.text = line; p2.font.size = Pt(14)
        p2.font.color.rgb = TEXT_BODY; p2.font.name = FONT

    # 矢印（最終セクション以外）
    if i < n - 1:
        ax = (13.333 / 2) - 0.50
        add_arrow_down(slide, ax, sy + section_h + GAP, 1.0, ARROW_H, DARKEST_PURPLE)
```

**Tips:**
- `n=2`: `section_h ≈ 2.10"` で余裕あり（Base と同等）。`n=4`: `section_h ≈ 1.10"` 程度で狭いため bullet を2〜3行に絞る
- ラベル列を右側にしたい場合: `bg.x=ML`、`lbl.x=ML+CW-LABEL_W`、`cx=ML`、`cw=CW-LABEL_W-0.15` に変更
- 各セクションで異なるラベル色を使う場合: `lbl.fill.fore_color.rgb` を `[DARKEST_PURPLE, DARK_PURPLE, CORE_PURPLE]` のリストから取る

---

## Pattern U — Three Column with Icons and Summary Bar (アイコン付き3列＋まとめ)
**Use**: Service pillars, value propositions with icons, benefit overview with footer tagline

Three equal columns (no background fill), each with an icon, a CORE_PURPLE accent line, bold header, and bullet list. A LIGHTEST_PURPLE summary bar spans the bottom.

```
[ icon ]          [ icon ]          [ icon ]
─────────         ─────────         ─────────
ヘッダー1          ヘッダー2          ヘッダー3
• 箇条書き        • 箇条書き        • 箇条書き
• 詳細            • 詳細            • 詳細
┌─────────────── まとめ文 ──────────────────┐
└───────────────────────────────────────────┘
```

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Icon [n] | col center | CY | icon_size | icon_size | image | — |
| Accent line [n] | col x | CY+icon+0.12 | col_w | 0.05 | CORE_PURPLE | — |
| Header [n] | col x | CY+icon+0.25 | col_w | 0.45 | NONE | 14pt bold DARKEST_PURPLE |
| Body [n] | col x+0.10 | CY+icon+0.78 | col_w-0.10 | body_h | NONE | 14pt TEXT_BODY |
| Footer bar | ML | BY-footer_h-0.10 | CW | footer_h | LIGHTEST_PURPLE | — |
| Footer text | ML+0.20 | footer bar y | CW-0.40 | footer_h | NONE | 14pt bold DARKEST_PURPLE center |

```python
from icon_utils import add_icon
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

ICON_SIZE = 0.55
FOOTER_H  = 0.55
N_COLS    = 3
GAP       = 0.30
col_w     = (CW - GAP * (N_COLS - 1)) / N_COLS   # ≈3.97"
footer_y  = BY - FOOTER_H - 0.10
body_h    = footer_y - (CY + ICON_SIZE + 0.78) - 0.10

columns = [
    {"icon": "chart",    "header": "設計情報を用いた生産性向上",      "body": ["DB設計情報からコード自動生成", "ソースコードを自動分析して整合性チェック"]},
    {"icon": "chat",     "header": "開発チーム内コラボレーション向上", "body": ["チャット連携でリマインド自動化", "ワークフロー化で手続きを効率化"]},
    {"icon": "dashboard","header": "プロジェクト管理の向上",           "body": ["状況を正確に示すレポートを自動生成", "データに基づく予兆分析"]},
]

for i, col in enumerate(columns):
    cx = ML + i * (col_w + GAP)

    # Icon (centered in column)
    add_icon(slide, prs, col["icon"], cx + (col_w - ICON_SIZE) / 2, CY, ICON_SIZE)

    # Accent line below icon
    line_y = CY + ICON_SIZE + 0.12
    bar = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(cx), Inches(line_y), Inches(col_w), Inches(0.05))
    bar.fill.solid(); bar.fill.fore_color.rgb = CORE_PURPLE
    bar.line.fill.background()

    # Header
    hdr = slide.shapes.add_textbox(Inches(cx), Inches(line_y + 0.12), Inches(col_w), Inches(0.45))
    hp = hdr.text_frame; hp.word_wrap = True
    p = hp.paragraphs[0]; p.text = col["header"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = DARKEST_PURPLE; p.font.name = FONT

    # Body bullets
    body = slide.shapes.add_textbox(Inches(cx + 0.10), Inches(line_y + 0.65), Inches(col_w - 0.10), Inches(body_h))
    bt = body.text_frame; bt.word_wrap = True
    for j, bullet in enumerate(col["body"]):
        p2 = bt.paragraphs[0] if j == 0 else bt.add_paragraph()
        p2.text = f"• {bullet}"; p2.font.size = Pt(14)
        p2.font.color.rgb = TEXT_BODY; p2.font.name = FONT

# Footer summary bar
fbar = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
    Inches(ML), Inches(footer_y), Inches(CW), Inches(FOOTER_H))
fbar.fill.solid(); fbar.fill.fore_color.rgb = LIGHTEST_PURPLE
fbar.line.fill.background()

ft = slide.shapes.add_textbox(Inches(ML + 0.20), Inches(footer_y + 0.08), Inches(CW - 0.40), Inches(FOOTER_H - 0.10))
fp = ft.text_frame.paragraphs[0]
fp.text = "まとめメッセージをここに記載する"
fp.font.size = Pt(14); fp.font.bold = True
fp.font.color.rgb = DARKEST_PURPLE; fp.font.name = FONT
fp.alignment = PP_ALIGN.CENTER
```

**Tips:**
- If no icons are available, replace the icon area with a large number badge (DARKEST_PURPLE box, 28pt WHITE bold, centered)
- For 4 columns, set `N_COLS = 4` and reduce `GAP = 0.20`
- The footer bar is optional — omit it if the slide has no single-sentence conclusion

---

## Pattern V — Numbered Card Grid
**Use**: 5–12 equal-weight concepts each with a short explanation (e.g., 8 reasons, 6 principles)

This extends Pattern F (2×2) to larger N×M grids. Each card has a numbered circle badge,
a tinted header area with a bold title, and body text below.

```
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ ① タイトル1          │  │ ② タイトル2          │  │ ③ タイトル3          │  │ ④ タイトル4          │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ • 説明テキスト        │  │ • 説明テキスト        │  │ • 説明テキスト        │  │ • 説明テキスト        │
│                      │  │                      │  │                      │  │                      │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ ⑤ タイトル5          │  │ ⑥ タイトル6          │  │ ⑦ タイトル7          │  │ ⑧ タイトル8          │
├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤  ├──────────────────────┤
│ • 説明テキスト        │  │ • 説明テキスト        │  │ • 説明テキスト        │  │ • 説明テキスト        │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

Reference dimensions (2 rows × 4 cols, total grid = CW × AH):
Card grid starts at **y = 1.61" (4.1cm)** from the top of the slide — leaves room for title + 2-line message.

| Shape | x | y | w | h | Fill |
|-------|---|---|---|---|------|
| Card background | col×(card_w+gap) | row×(card_h+gap) | 2.975" | 2.475" | OFF_WHITE, **no border** |
| Header band | same x | same y | card_w | 0.65" | LIGHTEST_PURPLE |
| Badge (circle) | card_x+0.10 | card_y+(band-0.32)/2 | 0.32" | 0.32" | DARK_PURPLE |
| Badge number | inside badge | — | — | — | 12pt bold WHITE center |
| Title | card_x+0.50 | card_y+0.06 | card_w-0.58 | band | 14pt bold DARK_PURPLE |
| Body | card_x+0.10 | card_y+0.73 | card_w-0.20 | card_h-0.77 | 14pt TEXT_BODY |

> ⚠ **カード枠線は使用禁止。** `highlight_indices` は渡さないこと。全カードは `bg.line.fill.background()`（枠線なし）のみ。

Card dimensions for n_cols=4, n_rows=2 (y_start=1.61"):
- gap_h = 0.20", gap_v = 0.20"
- card_w = (12.50 - 0.20×3) / 4 = 2.975"
- card_h = (BY - 1.61 - 0.20×1) / 2 ≈ 2.475"

```python
import sys, os
_SKILL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SKILL)
from helpers import *
from pattern_v import add_numbered_card_grid

cards = [
    {"title": "DXに特化した\nリーダーシップの確保",
     "body": "• 貴社のDXの旗振り役を務めつつ、技術スタッフの強力な巻き込みを果たすリーダーシップを確保"},
    {"title": "DX人材に特化した\n報酬体系・人事制度による人材の確保",
     "body": "• 他社と比べても競争力のある報酬水準の設定や柔軟な働き方など、DX人材のニーズに合わせた制度の整備"},
    {"title": "効果的な人事交流・\n育成プログラムの推進",
     "body": "• DX組織外の協業先も巻き込んだ人事交流、人材育成プログラムの提供を通じて、貴社人材の強化を強力に推進"},
    {"title": "エコシステムパートナーとの\nコラボレーション促進",
     "body": "• 国内外の民間企業、大学、NPO、個人などと幅広いエコシステムを形成し、貴社のDXを協働して推進"},
    # ... 4 more cards ...
]

# 2×4 grid (default) — no colored borders
add_numbered_card_grid(
    slide, cards,
    n_cols=4,
    # highlight_indices は使用禁止（枠線なし）
)
```

**Tips:**
- **`highlight_indices` は使用禁止**（枠線に色を使わない）。省略すると全カード枠線なし
- Y 開始位置はデフォルト 1.61"（4.1cm）。メッセージライン2行分の下にグリッドが来る
- For 2×3 (6 cards): `n_cols=3` — card dimensions auto-calculated
- For 2×2 (4 cards with badges): `n_cols=2` — similar to F but with numbered badges
- Body text should have 1–3 bullets per card; more than 4 bullets causes overflow at 14pt
- The badge circle uses MSO_AUTO_SHAPE_TYPE.OVAL — this is correctly rounded, not a rectangle
- Import: `from pattern_v import add_numbered_card_grid`

---

## Pattern W — Open-Canvas KPI (大数値統計)
**Use**: 2–4 large statistics that must make an immediate visual impact — without card backgrounds.
Contrast with Pattern J (which uses OFF_WHITE card panels): Pattern W uses the white slide canvas
with thin gray dividers, letting the typography itself carry the weight.

```
         │                    │
  > 50%  │    6.4 hours       │   52%
         │                    │
 説明テキスト  │   説明テキスト      │   説明テキスト
         │                    │
出典: ...  │   出典: ...         │   出典: ...
```

| Shape | x | y | w | h | Fill | Font |
|-------|---|---|---|---|------|------|
| Divider line [n] | ML + (n+1)×col_w | CY | 0.02" | BY-CY-0.20 | LIGHT_GRAY | — |
| Stat value | col center | CY+0.30 | col_w-0.20 | 1.20 | NONE | 64pt bold DARKEST_PURPLE center |
| Stat label | col center | CY+1.60 | col_w-0.20 | 0.50 | NONE | 18pt bold TEXT_BODY center |
| Stat detail | col center | CY+2.20 | col_w-0.20 | 1.40 | NONE | 14pt TEXT_BODY center |
| Source text | col center | BY-0.55 | col_w-0.20 | 0.45 | NONE | 12pt MID_GRAY center |

```python
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

stats = [
    {
        "value":  "> 50%",
        "label":  "インターネット普及率",
        "detail": "世界の人口の半分以上、45億人がインターネットにアクセスしている",
        "source": "出典: Internet World Stats: Usage and Population Statistics.",
    },
    {
        "value":  "6.4 hours",
        "label":  "1日のオンライン時間",
        "detail": "人々はあらゆるタイプのデバイスに常時接続しており、世界中で平均6.4時間/日をオンラインで過ごしている",
        "source": "出典: Salim, S. (2019, February 4). More Than Six Hours of Our Day Is Spent Online.",
    },
    {
        "value":  "52%",
        "label":  "テクノロジーへの依存度",
        "detail": "52%の生活者が「テクノロジーが日々の生活において重要な役割を果たしている」と回答",
        "source": "出典: Technology Vision 2020 research 調査対象は中国、インド、英国、米国の生活者2,000人",
    },
]

n = len(stats)
col_w = CW / n

# Vertical divider lines (n-1 lines between columns)
for i in range(1, n):
    lx = ML + i * col_w
    div = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(lx), Inches(CY), Inches(0.02), Inches(BY - CY - 0.20))
    div.fill.solid(); div.fill.fore_color.rgb = LIGHT_GRAY
    div.line.fill.background()

# Stat columns
def _stat_tb(slide, text, x, y, w, h, size, bold, color, font):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text; p.font.size = Pt(size); p.font.bold = bold
    p.font.color.rgb = color; p.font.name = font
    p.alignment = PP_ALIGN.CENTER
    return tb

for i, stat in enumerate(stats):
    cx  = ML + i * col_w
    cxp = cx + 0.15         # padded x
    cw  = col_w - 0.30      # padded width

    _stat_tb(slide, stat["value"],  cxp, CY + 0.30, cw, 1.20, 64, True,  DARKEST_PURPLE, FONT)
    _stat_tb(slide, stat["label"],  cxp, CY + 1.60, cw, 0.50, 18, True,  TEXT_BODY,      FONT)
    _stat_tb(slide, stat["detail"], cxp, CY + 2.20, cw, 1.40, 14, False, TEXT_BODY,      FONT)
    _stat_tb(slide, stat.get("source", ""), cxp, BY - 0.55, cw, 0.45, 12, False, MID_GRAY, FONT)
```

**When to use W vs J:**
- **W** — when the numbers ARE the message; minimal chrome, maximum typographic impact
- **J** — when each KPI needs structured context (card panel, label, detail line in a contained box)

**Tips:**
- 64pt is the default value size; for very long strings (e.g., "6.4 hours") reduce to 48pt
- Divider lines are optional — omit them for a fully open canvas
- Source citations are optional per stat; omit `"source"` key or pass empty string

**Variant: 2×2 グリッド（4統計値、Slide 53 タイプ）**

4つの統計を2行2列に配置する。縦ディバイダーに加え、横ディバイダーを追加する。

```python
stats_2x2 = [
    {"value": "> 50%",   "label": "普及率",     "detail": "世界人口の半数以上"},
    {"value": "6.4h",    "label": "オンライン時間", "detail": "1日平均（全デバイス）"},
    {"value": "52%",     "label": "依存度",     "detail": "テクノロジーへの依存"},
    {"value": "¥12.4T",  "label": "市場規模",   "detail": "2030年デジタル市場予測"},
]
# 2×2: 2 columns, 2 rows
COLS, ROWS = 2, 2
col_w = CW / COLS
row_h = (BY - CY - 0.10) / ROWS

# Dividers
for c in range(1, COLS):
    div = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML + c * col_w), Inches(CY), Inches(0.02), Inches(BY - CY - 0.10))
    div.fill.solid(); div.fill.fore_color.rgb = LIGHT_GRAY; div.line.fill.background()
for r in range(1, ROWS):
    hdiv = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(CY + r * row_h), Inches(CW), Inches(0.02))
    hdiv.fill.solid(); hdiv.fill.fore_color.rgb = LIGHT_GRAY; hdiv.line.fill.background()

for idx, stat in enumerate(stats_2x2):
    col = idx % COLS
    row = idx // COLS
    cx  = ML + col * col_w + 0.15
    cw  = col_w - 0.30
    cy  = CY + row * row_h
    _stat_tb(slide, stat["value"],  cx, cy + 0.20, cw, 0.90, 48, True,  DARKEST_PURPLE, FONT)
    _stat_tb(slide, stat["label"],  cx, cy + 1.15, cw, 0.40, 18, True,  TEXT_BODY,      FONT)
    _stat_tb(slide, stat["detail"], cx, cy + 1.60, cw, 0.80, 14, False, TEXT_BODY,      FONT)
```

---

## Pattern X — Step Chart (フェーズ付きステップチャート)
**Use**: Multi-phase process with grouped steps — each phase spans multiple columns, each step has detailed content (3–7 total steps across 2–4 phases)

Uses `add_step_chart()` from `pattern_x.py`.

Unlike Pattern P (chevron flow), Pattern X shows **phase grouping headers** spanning multiple steps and provides a **detail area** with bullets below each step. Best for roadmaps, transformation plans, and phased implementation processes.

```
[    分析    ][       構築       ][       運用       ]  <-- phase header (DARKEST_PURPLE)
[ 1.市場分析 ][ 2.システム構築 ][ 3.セキュリティ ][ 4.運用改善 ][ 5.エコシステム ]  <-- step header (LIGHTEST_PURPLE)
┌────────────┐┌────────────────┐┌────────────────┐┌────────────┐┌──────────────┐
│●市場ニーズ  ││●設備投資      ││●リスク管理    ││●テスト運用  ││●協業体制    │  <-- detail (OFF_WHITE)
│・調査      ││・設備選定      ││・リスク評価    ││・テスト実行  ││・エコシステム│
│・規制確認  ││・人材育成      ││・研修実施      ││・改善サイクル││・共同研究    │
│●技術選択  ││●プロセス設計  ││                ││●改善サイクル││              │
│・技術選定  ││・デジタル化    ││                ││・フレームワーク││            │
└────────────┘└────────────────┘└────────────────┘└────────────┘└──────────────┘
```

**3つの垂直ゾーン:**

| Zone | y | h | Fill | Font |
|------|---|---|------|------|
| Phase header | CY | 0.45" | DARKEST_PURPLE | 14pt bold WHITE center |
| Step header | CY+0.45 | 0.50" | LIGHTEST_PURPLE | 14pt bold DARK_PURPLE center |
| Detail area | CY+0.95 | remaining | OFF_WHITE + LIGHT_GRAY border | 14pt TEXT_BODY |

| Shape | Fill | Notes |
|-------|------|-------|
| Phase bar | DARKEST_PURPLE | Spans multiple step columns |
| Step header box | LIGHTEST_PURPLE | 1 per step, numbered "1. Title" |
| Detail panel | OFF_WHITE, 0.5pt LIGHT_GRAY border | Bullet content |
| Subtitle (optional) | — | ●bold BLACK inside detail |
| Bullets | — | ・14pt TEXT_BODY |

```python
from pattern_x import add_step_chart

phases = [
    {
        "label": "分析",
        "steps": [
            {"title": "市場分析", "subtitle": "市場ニーズ",
             "bullets": [
                 "市場のニーズを徹底的に調査し、スマートファクトリー化に必要な要素を抽出する",
                 "関連する規制や法律を調査し、遵守すべき点を明確にする",
             ]},
        ],
    },
    {
        "label": "構築",
        "steps": [
            {"title": "システム構築", "subtitle": "設備投資",
             "bullets": [
                 "必要な設備を選定し、投資計画を立てる",
                 "新しい設備の導入に伴う人材育成プログラムを策定する",
             ]},
            {"title": "セキュリティ", "subtitle": "リスク管理",
             "bullets": [
                 "サイバーセキュリティのリスクを評価し、対策を講じる",
                 "セキュリティ強化のための研修を実施し、従業員の意識を高める",
             ]},
        ],
    },
    {
        "label": "運用",
        "steps": [
            {"title": "運用改善", "subtitle": "テスト運用",
             "bullets": [
                 "新システムの運用テストを行い、問題点を洗い出す",
                 "フィードバックを基にシステムの改善を図る",
             ]},
            {"title": "エコシステム", "subtitle": "協業体制",
             "bullets": [
                 "関連企業とのエコシステムを構築し、相互に有益な関係を築く",
                 "共同研究や共同開発を通じて、イノベーションを促進する",
             ]},
        ],
    },
]

add_step_chart(slide, phases)
```

**Tips:**
- Phase header color can be customized per phase: `{"label": "分析", "color": CORE_PURPLE, "steps": [...]}`
- `subtitle` is optional — omit for simpler layouts with only bullets
- Recommended: 3–7 total steps across 2–4 phases
- Each step should have 2–5 bullets for balanced density
- Pattern P (chevron) is better for simple linear flows; Pattern X is better when you need phase grouping and detailed content per step
- Import: `from pattern_x import add_step_chart`

---

## Pattern H — Circular Flow / Cycle Diagram (循環フロー)
**Use**: PDCA サイクル、反復プロセス、継続的改善ループ（3〜5 ステップ）

ボックスを円上に配置し、時計回りの矢印で接続する。Pattern P（直線フロー）の循環版。

```
              [計画]
             /      \
        [改善]        [実行]
             \      /
              [評価]
```

**座標計算の考え方（4 items = PDCA 例）:**

| 位置 | 時計方向 | box 左上 x | box 左上 y |
|------|---------|-----------|-----------|
| Top (12時) | ステップ1 | CX_CENTER - BOX_W/2 | CY_CENTER - RADIUS - BOX_H/2 |
| Right (3時) | ステップ2 | CX_CENTER + RADIUS - BOX_W/2 | CY_CENTER - BOX_H/2 |
| Bottom (6時) | ステップ3 | CX_CENTER - BOX_W/2 | CY_CENTER + RADIUS - BOX_H/2 |
| Left (9時) | ステップ4 | CX_CENTER - RADIUS - BOX_W/2 | CY_CENTER - BOX_H/2 |

定数: `CX_CENTER=6.667"`, `CY_CENTER=4.175"`（コンテンツ領域中心）, `RADIUS=1.80"`, `BOX_W=2.20"`, `BOX_H=0.75"`

```python
import math
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn
from native_shapes import add_connector_arrow

items = [
    {"label": "計画",  "detail": "• 目標・KPI 設定\n• 施策立案・スコープ確定"},
    {"label": "実行",  "detail": "• 施策展開・リソース配置\n• 進捗モニタリング"},
    {"label": "評価",  "detail": "• KPI 測定・効果分析\n• ギャップ特定"},
    {"label": "改善",  "detail": "• 課題整理・打ち手策定\n• 次サイクルへ反映"},
]
n = len(items)

CX_CENTER = 13.333 / 2              # 6.667"
CY_CENTER = CY + (BY - CY) * 0.44  # 3.854" — 上寄せ（上下にdetailスペース確保）
RADIUS    = 1.50
BOX_W     = 2.00
BOX_H     = 0.60
DETAIL_W  = 2.00

# ① 12 時スタート、時計回りで angle を設定（math の角度は反時計方向）
angles = [90 - i * (360 / n) for i in range(n)]

box_positions = []
for a in angles:
    rad = math.radians(a)
    bx = CX_CENTER + RADIUS * math.cos(rad) - BOX_W / 2
    by = CY_CENTER - RADIUS * math.sin(rad) - BOX_H / 2
    box_positions.append((bx, by))

box_centers = [(bx + BOX_W / 2, by + BOX_H / 2) for bx, by in box_positions]

# ② ボックスを描画
for i, (item, (bx, by)) in enumerate(zip(items, box_positions)):
    box = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(bx), Inches(by), Inches(BOX_W), Inches(BOX_H))
    box.fill.solid(); box.fill.fore_color.rgb = DARKEST_PURPLE
    box.line.fill.background()
    tf = box.text_frame
    p = tf.paragraphs[0]; p.text = item["label"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

# ③ 接続矢印（時計回り）
half_diag = math.sqrt((BOX_W / 2) ** 2 + (BOX_H / 2) ** 2)
for i in range(n):
    cx1, cy1 = box_centers[i]
    cx2, cy2 = box_centers[(i + 1) % n]
    dx = cx2 - cx1; dy = cy2 - cy1
    d  = math.sqrt(dx ** 2 + dy ** 2)
    sx = cx1 + (dx / d) * half_diag
    sy = cy1 + (dy / d) * half_diag
    ex = cx2 - (dx / d) * half_diag
    ey = cy2 - (dy / d) * half_diag
    add_connector_arrow(slide, sx, sy, ex, ey, CORE_PURPLE, width_pt=2)

# ④ 詳細テキスト（ボックスの外側に方向別配置）
# 各ボックスの角度に応じて、ボックスから離れた位置にテキストを配置する。
# 極座標の半径ではなく、ボックス辺から固定オフセットで外側に配置することで
# ボックスとの重なりを確実に防ぐ。
DETAIL_H = 0.50   # テキストボックスの高さ
PAD = 0.10         # ボックスとテキスト間のパディング
for i, (item, (bx, by)) in enumerate(zip(items, box_positions)):
    a = angles[i]
    # 方向判定: 上(45<a<=135), 右(-45<a<=45), 下(-135<a<=-45), 左(残り)
    if 45 < a <= 135:       # 上 → テキストはボックスの上
        tx = bx + (BOX_W - DETAIL_W) / 2
        ty = by - DETAIL_H - PAD
    elif -45 < a <= 45:     # 右 → テキストはボックスの右
        tx = bx + BOX_W + PAD
        ty = by + (BOX_H - DETAIL_H) / 2
    elif -135 < a <= -45:   # 下 → テキストはボックスの下
        tx = bx + (BOX_W - DETAIL_W) / 2
        ty = by + BOX_H + PAD
    else:                    # 左 → テキストはボックスの左
        tx = bx - DETAIL_W - PAD
        ty = by + (BOX_H - DETAIL_H) / 2
    # スライド範囲内にクランプ
    tx = max(ML, min(tx, ML + CW - DETAIL_W))
    ty = max(CY, min(ty, BY - DETAIL_H - 0.10))
    tb = slide.shapes.add_textbox(Inches(tx), Inches(ty), Inches(DETAIL_W), Inches(DETAIL_H))
    tf2 = tb.text_frame; tf2.word_wrap = True
    for j, line in enumerate(item["detail"].split("\n")):
        p2 = tf2.paragraphs[0] if j == 0 else tf2.add_paragraph()
        p2.text = line; p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_BODY; p2.font.name = FONT
```

**Tips:**
- 3 ステップ: `RADIUS=1.40`, `BOX_W=2.20`
- 5 ステップ: `RADIUS=1.80`, `BOX_W=1.60`, `BOX_H=0.55` に縮小
- **CY_CENTER は上寄せ**にすること（`CY + AH * 0.42` が推奨）。`(CY + BY) / 2` だと下のボックスの詳細テキストがスライド下端を超えてクランプされ、ボックスと重なる
- 詳細テキスト不要の場合はステップ④を省略し、ボックスを大きくして詳細を内包する
- 中心に円（CORE_PURPLE）を置いてテーマを示す場合:
  ```python
  c = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
      Inches(CX_CENTER - 0.85), Inches(CY_CENTER - 0.85), Inches(1.70), Inches(1.70))
  c.fill.solid(); c.fill.fore_color.rgb = CORE_PURPLE; c.line.fill.background()
  ```

---

### Variant: Large Cycle（6〜9 ステップ）
**Use**: ステップ数が多い循環プロセス（6〜9ステップ）。詳細テキストは省略してラベルのみで表現。ボックスを小さくしてオーバーラップを防ぐ。

| N | RADIUS | BOX_W | BOX_H | font_size_pt |
|---|--------|-------|-------|-------------|
| 6 | 2.10   | 1.80  | 0.60  | 12 |
| 7 | 2.20   | 1.60  | 0.55  | 12 |
| 8 | 2.20   | 1.50  | 0.50  | 12 |
| 9 | 2.30   | 1.40  | 0.48  | 12 |

```python
import math
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn
from native_shapes import add_connector_arrow

items = [
    {"label": "Discovery"},
    {"label": "Ideation"},
    {"label": "Prototype"},
    {"label": "Test"},
    {"label": "Implement"},
    {"label": "Evaluate"},
]
n = len(items)   # 6〜9 に変更可

CX_CENTER = 13.333 / 2
CY_CENTER = (CY + BY) / 2
RADIUS  = 2.10   # n に合わせて上表を参照
BOX_W   = 1.80
BOX_H   = 0.60
FONT_PT = 12     # 全サイズ共通 12pt（ブランドルール準拠）

angles = [90 - i * (360 / n) for i in range(n)]
box_positions = []
for a in angles:
    rad = math.radians(a)
    bx = CX_CENTER + RADIUS * math.cos(rad) - BOX_W / 2
    by = CY_CENTER - RADIUS * math.sin(rad) - BOX_H / 2
    box_positions.append((bx, by))
box_centers = [(bx + BOX_W / 2, by + BOX_H / 2) for bx, by in box_positions]

for item, (bx, by) in zip(items, box_positions):
    box = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(bx), Inches(by), Inches(BOX_W), Inches(BOX_H))
    box.fill.solid(); box.fill.fore_color.rgb = DARKEST_PURPLE; box.line.fill.background()
    tf = box.text_frame
    p = tf.paragraphs[0]; p.text = item["label"]
    p.font.size = Pt(FONT_PT); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

half_diag = math.sqrt((BOX_W / 2) ** 2 + (BOX_H / 2) ** 2)
for i in range(n):
    cx1, cy1 = box_centers[i]
    cx2, cy2 = box_centers[(i + 1) % n]
    dx = cx2 - cx1; dy = cy2 - cy1
    d  = math.sqrt(dx ** 2 + dy ** 2)
    add_connector_arrow(slide,
        cx1 + (dx / d) * half_diag, cy1 + (dy / d) * half_diag,
        cx2 - (dx / d) * half_diag, cy2 - (dy / d) * half_diag,
        CORE_PURPLE, width_pt=2)

# オプション: 中心にテーマラベル（中心円）を追加
# center = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
#     Inches(CX_CENTER - 1.00), Inches(CY_CENTER - 0.45),
#     Inches(2.00), Inches(0.90))
# center.fill.solid(); center.fill.fore_color.rgb = CORE_PURPLE; center.line.fill.background()
# tf = center.text_frame
# p = tf.paragraphs[0]; p.text = "テーマ名"
# p.font.size = Pt(14); p.font.bold = True
# p.font.color.rgb = WHITE; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
# tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')
```

**⚠ 中心円を使う場合の RADIUS 計算（必須）:**
中心円を追加すると、左右（3時/9時）のボックスが中心円と重なるリスクがある。以下の公式で最小 RADIUS を算出し、**必ずこれ以上の値を設定すること:**
```
最小 RADIUS = BOX_W / 2 + center_circle_W / 2 + 0.15
```
例: BOX_W=2.00, center_W=1.70 → 最小 RADIUS = 1.00 + 0.85 + 0.15 = **2.00"**
RADIUS=1.50 では左右ボックスと中心円が 0.35" ずつ重なり、図形がくっついて見える。

**Tips:**
- 詳細テキストが必要な場合: `BOX_H=0.80` に拡大して2行テキスト（ラベル + 詳細）をボックス内に収める。外側の `DETAIL_RADIUS` は使わない
- 中心円（CORE_PURPLE）でサイクルのテーマを示すと視認性が高い（コメントアウト部分を参照）
- ボックス間隔が詰まりすぎる場合: `RADIUS` を増やすか `BOX_W` を縮小する（両方試して小さいほうを選ぶ）
- **中心円なし**: RADIUS=1.50〜1.80 で問題ない。**中心円あり**: 上記公式で最小 RADIUS を確認すること

---

## Pattern Y — Arrow Roadmap (矢印ロードマップ)
**Use**: プロジェクトスケジュール・フェーズ別ロードマップ（3〜6 行、最大 12 列）。HOME_PLATE 矢印タスクを時間軸グリッド上に配置する。完了タスクは濃色（DARK_PURPLE）、予定・未実施は薄色（LIGHTEST_PURPLE）で区別。

```
         |4月   |5月   |6月   |7月   |8月   |9月   |10月  |11月  |12月  |
─────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
         |[◇市場調査──→]                                                |
フェーズ1|      [◇KPI設定→]                                            |
─────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
         |            [◇基本設計──→]                                    |
フェーズ2|                  [◇詳細設計→]                                |
─────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
         |                        [◇開発────→]                         |
フェーズ3|                                    [◇テスト→]               |
─────────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
フェーズ4|                                          [◇UAT──→]         |
```
- 全月の左右に縦線 → 月は必ず枠線で閉じる
- 同一行の複数タスクは sub_row で上下段に分割 → 矢印が重ならない

```python
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
from pptx.oxml.ns import qn as _qn

# ── レイアウト定数 ──────────────────────────────────────────────────────
LABEL_W = 1.50          # 行ラベル幅（インチ）
CHART_X = ML + LABEL_W  # タイムライン開始 x
CHART_W = CW - LABEL_W  # タイムライン幅
HDR_H   = 0.42          # ヘッダー行（月名）の高さ

# ── 時間軸・行定義 ──────────────────────────────────────────────────────
periods = ["4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
rows    = ["フェーズ1: 企画", "フェーズ2: 設計", "フェーズ3: 実装", "フェーズ4: 展開"]
N_COLS  = len(periods)
N_ROWS  = len(rows)

DATA_H  = AH - HDR_H
ROW_H   = DATA_H / N_ROWS   # 行高さ
COL_W   = CHART_W / N_COLS

def _cx(c):  return CHART_X + c * COL_W           # 列 c の左端 x（インチ）

# ── タスク定義: (row, sub_row, max_sub, start_col, span_cols, label, completed)
# - row: フェーズ行 (0-indexed)
# - sub_row: 行内の段 (0-indexed)。同一行に複数タスクがある場合に上下段で分ける
# - max_sub: その行の最大段数（1=1段、2=上下2段、3=3段）
# - completed: True=完了（DARK_PURPLE）/ False=予定（LIGHTEST_PURPLE）
tasks = [
    (0, 0, 2, 0, 2, "市場調査・要件整理",  True),
    (0, 1, 2, 1, 2, "KPI 設定",           True),
    (1, 0, 2, 2, 3, "基本設計",           True),
    (1, 1, 2, 3, 2, "詳細設計・レビュー", False),
    (2, 0, 2, 3, 3, "開発・単体テスト",   False),
    (2, 1, 2, 5, 2, "結合テスト",         False),
    (3, 0, 1, 6, 3, "UAT・本番移行",      False),
]

# sub_row に応じたタスク矢印の y / 高さを計算
PAD = 0.06  # 上下パディング
def _ty(r, sub, max_sub):
    """行 r 内の sub 段目のタスク上端 y"""
    row_top = CY + HDR_H + r * ROW_H
    sub_h = (ROW_H - PAD * 2) / max_sub  # 1段あたりの高さ
    return row_top + PAD + sub * sub_h

def _task_h(max_sub):
    """段数に応じたタスク矢印の高さ"""
    sub_h = (ROW_H - PAD * 2) / max_sub
    return sub_h - 0.04  # 段間に少し隙間

# ── (オプション) 今日線: today_col 列の左端に赤縦線 ──────────────────
today_col  = 2    # 0-indexed。None にすると非表示

# ── (オプション) マイルストーン: (col, label) ──────────────────────────
milestones = [(4, "中間報告"), (8, "最終報告")]  # col: 0-indexed

# ──────────────────────────────────────────────────────────────────────
# ── 描画コード ─────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────

# ヘッダー背景バー（DARKEST_PURPLE・全幅）
_hbg = slide.shapes.add_shape(MSO.RECTANGLE,
    Inches(ML), Inches(CY), Inches(CW), Inches(HDR_H))
_hbg.fill.solid(); _hbg.fill.fore_color.rgb = DARKEST_PURPLE
_hbg.line.fill.background()

# 月名テキスト（各列）
for ci, period in enumerate(periods):
    tb = slide.shapes.add_textbox(
        Inches(_cx(ci)), Inches(CY), Inches(COL_W), Inches(HDR_H))
    tf = tb.text_frame; p = tf.paragraphs[0]
    p.text = period; p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

# 行背景（WHITE 統一）+ 行ラベル（左列）
for ri, row_label in enumerate(rows):
    ry = CY + HDR_H + ri * ROW_H
    bg = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(ML), Inches(ry), Inches(CW), Inches(ROW_H))
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE
    bg.line.color.rgb = LIGHT_GRAY

    lb = slide.shapes.add_textbox(
        Inches(ML + 0.08), Inches(ry), Inches(LABEL_W - 0.12), Inches(ROW_H))
    tf = lb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = row_label; p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = TEXT_BODY; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

# 縦区切り線（全月の左右境界 — 月は必ず枠線で閉じる）
for ci in range(N_COLS + 1):  # 0〜N_COLS: 左端〜右端の全境界線
    vl = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(_cx(ci) - 0.005), Inches(CY + HDR_H),
        Inches(0.01), Inches(DATA_H))
    vl.fill.solid(); vl.fill.fore_color.rgb = LIGHT_GRAY
    vl.line.fill.background()

# タスク矢印（HOME_PLATE = 右向きの五角形、sub_row で段分け）
for (ri, sub, max_sub, sc, span, label, completed) in tasks:
    tx  = _cx(sc)
    ty  = _ty(ri, sub, max_sub)
    tw  = span * COL_W - 0.06   # 右端に 0.06" マージン
    th  = _task_h(max_sub)
    col = DARK_PURPLE     if completed else LIGHTEST_PURPLE
    fg  = WHITE           if completed else TEXT_BODY

    sh = slide.shapes.add_shape(MSO.PENTAGON,
        Inches(tx), Inches(ty), Inches(tw), Inches(th))
    sh.fill.solid(); sh.fill.fore_color.rgb = col
    sh.line.fill.background()

    tf = sh.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    p.text = label
    # 2段以上の場合はフォントを小さくする
    _fsz = Pt(12) if max_sub <= 1 else Pt(11)
    p.font.size = _fsz; p.font.bold = False
    p.font.color.rgb = fg; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

# 今日線（オプション）
if today_col is not None:
    _tlx = _cx(today_col)
    _tl = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(_tlx - 0.01), Inches(CY),
        Inches(0.02), Inches(AH))
    _tl.fill.solid(); _tl.fill.fore_color.rgb = RGBColor(0xFF, 0x00, 0x00)
    _tl.line.fill.background()
    _ttb = slide.shapes.add_textbox(
        Inches(_tlx - 0.25), Inches(CY - 0.20),
        Inches(0.50), Inches(0.20))
    _tp = _ttb.text_frame.paragraphs[0]
    _tp.text = "本日"; _tp.alignment = PP_ALIGN.CENTER
    _tp.font.size = Pt(10); _tp.font.bold = True
    _tp.font.color.rgb = RGBColor(0xFF, 0x00, 0x00); _tp.font.name = FONT

# マイルストーン（オプション: ▼ マーカー + ラベル）
for (mc, mlabel) in milestones:
    _mtb = slide.shapes.add_textbox(
        Inches(_cx(mc) - 0.30), Inches(CY + HDR_H - 0.28),
        Inches(1.20), Inches(0.28))
    _mp = _mtb.text_frame.paragraphs[0]
    _mp.text = f"▼{mlabel}"; _mp.alignment = PP_ALIGN.LEFT
    _mp.font.size = Pt(10); _mp.font.bold = False
    _mp.font.color.rgb = CORE_PURPLE; _mp.font.name = FONT
```

**Tips:**
- **sub_row の決め方**: 同一 row にタスクが複数ある場合、`max_sub` をその行のタスク数に設定し、各タスクに `sub_row=0, 1, ...` を振る。タスクが1つなら `sub_row=0, max_sub=1`
- **3段の場合**: `max_sub=3` にすれば3段分割。フォントは `Pt(11)` に自動縮小される
- 行数が多い場合（5行以上）: `ROW_H` が狭くなるため `PAD = 0.04` に調整
- 週粒度にする場合: `periods` を週番号リスト（例: `["1w","2w","3w","4w","5w","6w","7w","8w"]`）に変更
- 凡例（右上）: 完了・未実施の小さな HOME_PLATE + テキストを右上隅（`x≈ML+CW-2.00, y≈CY+0.05`）に追加する
- グループ行（カテゴリ区切り）: `is_category=True` な行の背景を `OFF_WHITE` + `DARKEST_PURPLE` の左端アクセントバー（幅 0.06"）にすると視覚的に区別できる
- **枠線**: 縦区切り線は `range(N_COLS + 1)` で全月の左右に配置。月が必ず枠線で閉じられる

---

## Pattern Z — Maturity Model (成熟度評価)
**Use**: 現状 vs. 目標の成熟度評価、ケイパビリティアセスメント（5〜8 次元）

横軸に成熟度レベル（Basic → Leading）、縦に評価対象。現在地（●）と目標（○）をバーで接続。

```
           Basic  Advanced  Leading  Emerging
戦略・方針   ●──────────────○
業務         ●────○
データ              ●──────────────○
アプリ              ●────○
テクノロジー  ●──────────────────────○
```

```python
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

LEVELS = ["基本", "発展途上", "先進的", "リーディング"]
N_LEVELS = len(LEVELS)

# current/target: LEVELS の 0-based index
capabilities = [
    {"name": "戦略・方針",       "current": 0, "target": 2},
    {"name": "業務プロセス",     "current": 0, "target": 1},
    {"name": "データ管理",       "current": 1, "target": 3},
    {"name": "アプリケーション", "current": 1, "target": 2},
    {"name": "テクノロジー",     "current": 0, "target": 3},
    {"name": "人材・組織",       "current": 0, "target": 2},
]
N_CAPS = len(capabilities)

LABEL_W  = 2.10
SCALE_W  = CW - LABEL_W
COL_W    = SCALE_W / N_LEVELS
HEADER_H = 0.45
ROW_H    = (BY - CY - HEADER_H - 0.60) / N_CAPS
GRID_Y   = CY + HEADER_H + 0.10
DOT_R    = 0.14

# スケールヘッダー
for i, level in enumerate(LEVELS):
    lx = ML + LABEL_W + i * COL_W
    hbg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(lx), Inches(CY), Inches(COL_W - 0.03), Inches(HEADER_H))
    hbg.fill.solid(); hbg.fill.fore_color.rgb = DARKEST_PURPLE; hbg.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(lx), Inches(CY), Inches(COL_W), Inches(HEADER_H))
    tf = tb.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; p.text = level; p.alignment = PP_ALIGN.CENTER
    p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

def level_cx(idx):
    return ML + LABEL_W + (idx + 0.5) * COL_W

# 能力行
for r, cap in enumerate(capabilities):
    ry  = GRID_Y + r * ROW_H
    rcy = ry + ROW_H / 2

    # ラベル
    lbl = slide.shapes.add_textbox(
        Inches(ML), Inches(ry + 0.05), Inches(LABEL_W - 0.15), Inches(ROW_H - 0.10))
    tf = lbl.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; p.text = cap["name"]
    p.font.size = Pt(14); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    # 行背景（単色 — 交互色禁止）
    rbg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML + LABEL_W), Inches(ry),
        Inches(SCALE_W), Inches(ROW_H - 0.04))
    rbg.fill.solid(); rbg.fill.fore_color.rgb = OFF_WHITE
    rbg.line.color.rgb = LIGHT_GRAY; rbg.line.width = Pt(0.5)

    cur_x = level_cx(cap["current"])
    tgt_x = level_cx(cap["target"])

    # 接続バー（current → target）
    if cap["current"] != cap["target"]:
        bar = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
            Inches(min(cur_x, tgt_x) + DOT_R),
            Inches(rcy - 0.04),
            Inches(abs(tgt_x - cur_x) - DOT_R * 2), Inches(0.08))
        bar.fill.solid(); bar.fill.fore_color.rgb = CORE_PURPLE; bar.line.fill.background()

    # ● 現在地（塗りつぶし）
    dc = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(cur_x - DOT_R), Inches(rcy - DOT_R),
        Inches(DOT_R * 2), Inches(DOT_R * 2))
    dc.fill.solid(); dc.fill.fore_color.rgb = DARKEST_PURPLE; dc.line.fill.background()

    # ○ 目標（枠線のみ）
    dt = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(tgt_x - DOT_R), Inches(rcy - DOT_R),
        Inches(DOT_R * 2), Inches(DOT_R * 2))
    dt.fill.background(); dt.line.color.rgb = CORE_PURPLE; dt.line.width = Pt(2.0)

# 凡例
legend_y = GRID_Y + N_CAPS * ROW_H + 0.12
for dot_fill, dot_line, label, ox in [
    (DARKEST_PURPLE, None,        "現在", ML),
    (None,           CORE_PURPLE, "目標", ML + 1.70),
]:
    d = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(ox), Inches(legend_y), Inches(0.20), Inches(0.20))
    if dot_fill: d.fill.solid(); d.fill.fore_color.rgb = dot_fill
    else:        d.fill.background()
    if dot_line: d.line.color.rgb = dot_line; d.line.width = Pt(2.0)
    else:        d.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(ox + 0.28), Inches(legend_y - 0.03), Inches(1.20), Inches(0.28))
    p = tb.text_frame.paragraphs[0]; p.text = label
    p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
```

**Tips:**
- スケールラベルを変える場合: `LEVELS = ["レベル1", ..., "レベル5"]`
- 現在地 == 目標の場合: 接続バーを省略し、`dot_tgt` を DARKEST_PURPLE 塗りにする
- グループで行を分けたい場合: 間に区切り行（DARKEST_PURPLE ラベル行）を挿入

---

## Pattern AA — 2×2 Quadrant Matrix (優先度・ポートフォリオマトリクス)
**Use**: 優先度評価、Quick Win 特定、ポートフォリオ分析（縦軸: 価値/インパクト、横軸: 難易度/コスト）

4 象限を色分けし、各象限にアイテムを番号付き円で配置。

```
     高インパクト
  ┌──────────┬──────────┐
  │ Quick Win│ Strategic│
  │ (2)(5)   │   (1)(8) │
  ├──────────┼──────────┤
  │  Avoid   │ Big Bet  │
  │  (4)     │  (3)(6)  │
  └──────────┴──────────┘
     低インパクト   高難易度
```

```python
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

QUAD_W    = CW / 2
AXIS_H    = 0.45
GRID_Y    = CY + AXIS_H
QUAD_H    = (BY - GRID_Y - 0.45) / 2
DOT_SIZE  = 0.32

quadrants = [
    {"label": "Quick Win",  "desc": "優先着手",  "x": ML,          "y": GRID_Y,          "fill": LIGHTEST_PURPLE,              "text": DARKEST_PURPLE},
    {"label": "Strategic",  "desc": "戦略的投資", "x": ML + QUAD_W, "y": GRID_Y,          "fill": RGBColor(0xE0, 0xCC, 0xFF),   "text": DARKEST_PURPLE},
    {"label": "Avoid",      "desc": "優先度低",  "x": ML,          "y": GRID_Y + QUAD_H, "fill": RGBColor(0xF5, 0xF5, 0xF5),   "text": MID_GRAY},
    {"label": "Big Bet",    "desc": "長期投資",  "x": ML + QUAD_W, "y": GRID_Y + QUAD_H, "fill": OFF_WHITE,                    "text": TEXT_BODY},
]

# 象限描画
for q in quadrants:
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(q["x"]), Inches(q["y"]),
        Inches(QUAD_W - 0.05), Inches(QUAD_H - 0.05))
    bg.fill.solid(); bg.fill.fore_color.rgb = q["fill"]
    bg.line.color.rgb = LIGHT_GRAY; bg.line.width = Pt(0.75)

    ql = slide.shapes.add_textbox(
        Inches(q["x"] + 0.12), Inches(q["y"] + 0.10),
        Inches(QUAD_W - 0.24), Inches(0.55))
    tf = ql.text_frame; tf.word_wrap = False
    p1 = tf.paragraphs[0]; p1.text = q["label"]
    p1.font.size = Pt(14); p1.font.bold = True
    p1.font.color.rgb = q["text"]; p1.font.name = FONT
    p2 = tf.add_paragraph(); p2.text = q["desc"]
    p2.font.size = Pt(12); p2.font.color.rgb = MID_GRAY; p2.font.name = FONT

# 軸ラベル
for text, x, y, align in [
    ("▲ 高インパクト", ML,          GRID_Y - 0.40, PP_ALIGN.LEFT),
    ("低インパクト ▼", ML,          GRID_Y + QUAD_H * 2 + 0.05, PP_ALIGN.LEFT),
    ("難易度 低 ◀",   ML,          GRID_Y - 0.40, PP_ALIGN.LEFT),
    ("▶ 難易度 高",   ML + QUAD_W, GRID_Y - 0.40, PP_ALIGN.RIGHT),
]:
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(QUAD_W), Inches(0.35))
    p = tb.text_frame.paragraphs[0]; p.text = text; p.alignment = align
    p.font.size = Pt(12); p.font.color.rgb = MID_GRAY; p.font.name = FONT

# アイテム（番号付き円）
# x_ratio / y_ratio: 0.0〜1.0 で象限内の位置を指定
items = [
    {"num": 1, "name": "CRM 統合",        "q": 1, "x_ratio": 0.65, "y_ratio": 0.35},
    {"num": 2, "name": "レポート自動化",  "q": 0, "x_ratio": 0.35, "y_ratio": 0.30},
    {"num": 3, "name": "基幹システム刷新","q": 3, "x_ratio": 0.55, "y_ratio": 0.50},
    {"num": 4, "name": "旧帳票移行",      "q": 2, "x_ratio": 0.45, "y_ratio": 0.55},
    {"num": 5, "name": "モバイル対応",    "q": 0, "x_ratio": 0.60, "y_ratio": 0.60},
    {"num": 6, "name": "AI 予測分析",     "q": 3, "x_ratio": 0.30, "y_ratio": 0.35},
]

qx_list = [ML, ML + QUAD_W, ML, ML + QUAD_W]
qy_list = [GRID_Y, GRID_Y, GRID_Y + QUAD_H, GRID_Y + QUAD_H]

for item in items:
    qx = qx_list[item["q"]]
    qy = qy_list[item["q"]]
    ix = qx + item["x_ratio"] * (QUAD_W - 0.05) - DOT_SIZE / 2
    iy = qy + item["y_ratio"] * (QUAD_H - 0.05) - DOT_SIZE / 2

    dot = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(ix), Inches(iy), Inches(DOT_SIZE), Inches(DOT_SIZE))
    dot.fill.solid(); dot.fill.fore_color.rgb = DARKEST_PURPLE; dot.line.fill.background()
    tf = dot.text_frame
    p = tf.paragraphs[0]; p.text = str(item["num"])
    p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

# 凡例（番号 → 名称）
legend_y = GRID_Y + QUAD_H * 2 - len(items) * 0.28 - 0.10
for j, item in enumerate(items):
    tb = slide.shapes.add_textbox(
        Inches(ML + CW * 0.52), Inches(legend_y + j * 0.28),
        Inches(CW * 0.46), Inches(0.26))
    p = tb.text_frame.paragraphs[0]
    p.text = f"{item['num']}. {item['name']}"
    p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
```

**Tips:**
- 軸ラベルを変える場合: `"▲ 高インパクト"` / `"難易度 低 ◀"` 等を変更するだけ
- 象限名を変えたい場合: `quadrants[i]["label"]` / `["desc"]` を更新する
- `x_ratio` / `y_ratio` は 0.05〜0.95 内に収めること（端に貼り付くと視認性が悪い）
- アイテムが多い場合は凡例を 2 列に分割する（`ML + CW * 0.0` と `ML + CW * 0.52` の 2 カラム）

**Variant: Shaded Area Only（ゾーン可視化のみ、Slides 47-48 タイプ）**

アイテムを配置せず、4ゾーンの色分けと軸ラベルだけで「空の評価フレーム」を作るバリアント。
`items = []` にするだけでなく、軸ラベルを X/Y クライテリア形式に変更する。

```python
# AA の quadrants 描画ブロックはそのまま使用
# items = [] にしてアイテム描画ループをスキップ
# 軸ラベルを4本（上下左右）に変更

AXIS_H  = 0.45
GRID_Y  = CY + AXIS_H
QUAD_W  = CW / 2
QUAD_H  = (BY - GRID_Y - 0.45) / 2

# 象限ラベルと色（用途に合わせて変更可）
quadrants = [
    {"label": "Area 1", "x": ML,          "y": GRID_Y,          "fill": LIGHTEST_PURPLE},
    {"label": "Area 2", "x": ML + QUAD_W, "y": GRID_Y,          "fill": RGBColor(0xE0, 0xCC, 0xFF)},
    {"label": "Area 3", "x": ML,          "y": GRID_Y + QUAD_H, "fill": OFF_WHITE},
    {"label": "Area 4", "x": ML + QUAD_W, "y": GRID_Y + QUAD_H, "fill": RGBColor(0xF5, 0xF5, 0xF5)},
]
for q in quadrants:
    bg = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(q["x"]), Inches(q["y"]),
        Inches(QUAD_W - 0.05), Inches(QUAD_H - 0.05))
    bg.fill.solid(); bg.fill.fore_color.rgb = q["fill"]
    bg.line.color.rgb = LIGHT_GRAY; bg.line.width = Pt(0.75)
    tb = slide.shapes.add_textbox(Inches(q["x"] + 0.15), Inches(q["y"] + 0.15),
        Inches(QUAD_W - 0.30), Inches(0.40))
    p = tb.text_frame.paragraphs[0]; p.text = q["label"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = TEXT_BODY; p.font.name = FONT

# 4方向の軸ラベル（X/Y クライテリア形式）
for text, x, y, align in [
    ("▲ Y-Criteria High", ML,          GRID_Y - 0.40, PP_ALIGN.LEFT),
    ("Y-Criteria Low ▼",  ML,          GRID_Y + QUAD_H * 2 + 0.05, PP_ALIGN.LEFT),
    ("◀ X-Criteria Low",  ML,          GRID_Y - 0.40, PP_ALIGN.LEFT),
    ("X-Criteria High ▶", ML + QUAD_W, GRID_Y - 0.40, PP_ALIGN.RIGHT),
]:
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(QUAD_W), Inches(0.35))
    p = tb.text_frame.paragraphs[0]; p.text = text; p.alignment = align
    p.font.size = Pt(12); p.font.color.rgb = MID_GRAY; p.font.name = FONT
```

---

## Pattern AB — Issue Tree / Logic Tree (論点ツリー・ロジックツリー)
**Use**: MECE分解、課題の構造化、根本原因分析（ロジックツリー、イシューツリー）

ルートノード（左）から葉（右）へ展開する横方向ツリー。再帰関数でノードを自動配置。

```
 ┌──────────────┐
 │   根本課題    │──▶ 要因 A ──▶ A-1: …
 │              │         └──▶ A-2: …
 │              │──▶ 要因 B ──▶ B-1: …
 │              │         └──▶ B-2: …
 │              │              B-3: …
 │              │──▶ 要因 C ──▶ C-1: …
 └──────────────┘         └──▶ C-2: …
```

| Element | Shape | Fill | Text |
|---------|-------|------|------|
| Root node | RECTANGLE | DARKEST_PURPLE | WHITE 14pt bold |
| Level 1 nodes | RECTANGLE | DARK_PURPLE | WHITE 12pt |
| Level 2 nodes | RECTANGLE | CORE_PURPLE | WHITE 12pt |
| Level 3+ nodes | RECTANGLE | OFF_WHITE | TEXT_BODY 12pt |
| Connectors | Straight line | LIGHT_GRAY 1pt | — |

```python
from native_shapes import add_connector_arrow
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

NODE_W = 1.90   # width of each node box (in)
NODE_H = 0.50   # height of each node box (in)
H_GAP  = 0.50   # horizontal space between levels
V_GAP  = 0.22   # vertical space between siblings
LEVEL_FILLS = [DARKEST_PURPLE, DARK_PURPLE, CORE_PURPLE, OFF_WHITE]
LEVEL_TEXTS = [WHITE,          WHITE,       WHITE,       TEXT_BODY]

# Tree structure: nested dicts with "label" and optional "children"
tree = {
    "label": "根本課題",
    "children": [
        {"label": "要因 A",
         "children": [{"label": "A-1: サブ要因"}, {"label": "A-2: サブ要因"}]},
        {"label": "要因 B",
         "children": [{"label": "B-1: サブ要因"}, {"label": "B-2: サブ要因"},
                      {"label": "B-3: サブ要因"}]},
        {"label": "要因 C",
         "children": [{"label": "C-1: サブ要因"}, {"label": "C-2: サブ要因"}]},
    ]
}

def _leaf_count(n):
    if not n.get("children"):
        return 1
    return sum(_leaf_count(c) for c in n["children"])

def _draw_tree(slide, node, level, x, y_top):
    lc      = _leaf_count(node)
    total_h = lc * NODE_H + (lc - 1) * V_GAP
    y_c     = y_top + total_h / 2   # vertical center of this subtree

    fill = LEVEL_FILLS[min(level, len(LEVEL_FILLS) - 1)]
    tcol = LEVEL_TEXTS[min(level, len(LEVEL_TEXTS) - 1)]

    rect = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(x), Inches(y_c - NODE_H / 2), Inches(NODE_W), Inches(NODE_H))
    rect.fill.solid(); rect.fill.fore_color.rgb = fill; rect.line.fill.background()
    tf = rect.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = node["label"]
    p.font.size  = Pt(12 if level > 0 else 13)
    p.font.bold  = (level == 0)
    p.font.color.rgb = tcol; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    if node.get("children"):
        child_x = x + NODE_W + H_GAP
        cy = y_top
        for child in node["children"]:
            clc     = _leaf_count(child)
            child_h = clc * NODE_H + (clc - 1) * V_GAP
            child_c = cy + child_h / 2
            # Straight connector: parent right-center → child left-center
            add_connector_arrow(slide,
                x + NODE_W, y_c,
                child_x,    child_c,
                LIGHT_GRAY, width_pt=1, arrow_end=False)
            _draw_tree(slide, child, level + 1, child_x, cy)
            cy += child_h + V_GAP

_draw_tree(slide, tree, 0, ML, CY + 0.20)
```

**Tips:**
- ツリー全体の高さ = `_leaf_count(tree) * NODE_H + (_leaf_count(tree) - 1) * V_GAP` で計算。`CY + 0.20` を調整してセンタリングする
- 階層が深い（4層以上）場合: `NODE_W` を 1.50 以下に縮小、フォントを 12pt に下げる（ブランドルール最小値）
- 縦ツリー（トップ→ボトム）に変換したい場合: x/y を入れ替えて `H_GAP` を `V_GAP` として使う

---

### Variant: Vertical Tree（縦ツリー・上→下）
**Use**: 戦略→施策、KGI→KPI→アクションなど「上位概念から下位実施事項へ」の展開（Slide 24 タイプ）。横ツリーより「トップダウン意思決定」の流れを直感的に示す。

```
              ┌──────────┐
              │ 戦略目標  │
              └──┬────┬──┘
                 ▼    ▼
         ┌───────┐  ┌───────┐
         │テーマA│  │テーマB│
         └──┬────┘  └───────┘
            ▼
     ┌───────┐ ┌───────┐
     │施策A-1│ │施策A-2│
     └───────┘ └───────┘
```

横ツリー（Pattern AB Base）の `_draw_tree` 関数を「X↔Y 入れ替え + 幅スパン計算」で縦方向に変換。

```python
from native_shapes import add_connector_arrow
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

NODE_W  = 2.00
NODE_H  = 0.50
H_GAP   = 0.25   # sibling 間の水平間隔
V_GAP   = 0.65   # 階層間の垂直間隔

LEVEL_FILLS = [DARKEST_PURPLE, DARK_PURPLE, CORE_PURPLE, OFF_WHITE]
LEVEL_TEXTS = [WHITE,          WHITE,       WHITE,       TEXT_BODY]

tree = {
    "label": "戦略目標",
    "children": [
        {"label": "テーマ A",
         "children": [{"label": "施策 A-1"}, {"label": "施策 A-2"}]},
        {"label": "テーマ B",
         "children": [{"label": "施策 B-1"}]},
        {"label": "テーマ C",
         "children": [{"label": "施策 C-1"}, {"label": "施策 C-2"}]},
    ]
}

def _leaf_count_v(n):
    if not n.get("children"):
        return 1
    return sum(_leaf_count_v(c) for c in n["children"])

def _draw_vtree(slide, node, level, x_left, y_top):
    # 縦ツリー: x_left はこのサブツリーの水平スパン左端
    lc    = _leaf_count_v(node)
    span  = lc * NODE_W + max(lc - 1, 0) * H_GAP
    x_c   = x_left + span / 2   # このノードの水平中心
    y     = y_top + level * (NODE_H + V_GAP)

    fill = LEVEL_FILLS[min(level, len(LEVEL_FILLS) - 1)]
    tcol = LEVEL_TEXTS[min(level, len(LEVEL_TEXTS) - 1)]

    rect = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(x_c - NODE_W / 2), Inches(y), Inches(NODE_W), Inches(NODE_H))
    rect.fill.solid(); rect.fill.fore_color.rgb = fill; rect.line.fill.background()
    tf = rect.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = node["label"]
    p.font.size  = Pt(12 if level > 0 else 14)
    p.font.bold  = (level == 0)
    p.font.color.rgb = tcol; p.font.name = FONT; p.alignment = PP_ALIGN.CENTER
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

    if node.get("children"):
        child_y = y_top + (level + 1) * (NODE_H + V_GAP)
        cx = x_left
        for child in node["children"]:
            cl      = _leaf_count_v(child)
            child_w = cl * NODE_W + max(cl - 1, 0) * H_GAP
            child_c = cx + child_w / 2
            add_connector_arrow(slide,
                x_c,      y + NODE_H,
                child_c,  child_y,
                LIGHT_GRAY, width_pt=1, arrow_end=False)
            _draw_vtree(slide, child, level + 1, cx, y_top)
            cx += child_w + H_GAP

total_leaves = _leaf_count_v(tree)
total_tree_w = total_leaves * NODE_W + max(total_leaves - 1, 0) * H_GAP
start_x      = ML + (CW - total_tree_w) / 2   # 水平センタリング
_draw_vtree(slide, tree, 0, start_x, CY + 0.10)
```

**Tips:**
- 葉ノードが多い（8+）場合: `NODE_W=1.50`、`H_GAP=0.15` に縮小。全体幅 `total_tree_w` を CW 以内に収めること
- 4層以上: `V_GAP=0.50` に縮小し、フォントを 12pt に下げる（ブランドルール最小値）
- 横ツリー（Base）との使い分け: 「原因→結果」「問題→解決策」は横が自然。「戦略→施策」「KGI→KPI→アクション」は縦が自然
- 非対称ツリー（Slide 23 タイプ）: 横ツリー（Base）の `tree` データに子ノード数が異なる構造を入れるだけで自動対応する（再帰ロジックに手を加える必要なし）

---

## Pattern AC — Stacked Pyramid (積み上げピラミッド)
**Use**: 階層構造の可視化（基盤→価値、下位→上位）、前提条件の積み上げ、マズロー型モデル。3〜5層が最適。

```
          ┌────┐
         /  L4  \
        /─────────\
       /    L3      \
      /───────────────\
     /       L2         \
    /─────────────────────\
   /          L1             \
  └───────────────────────────┘
```

| Element | Shape | Fill | Text |
|---------|-------|------|------|
| Pyramid layer | Custom trapezoid (custGeom) | Level color | WHITE 14pt bold / 12pt |
| Sub-label | textbox (centered in trapezoid) | — | Same as fill text color 12pt |

```python
from lxml import etree
from pptx.oxml.ns import qn as _qn
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

LAYERS = [  # Bottom → Top order
    {"label": "Infrastructure",  "sub": "基盤・プロセス・データ",    "fill": DARKEST_PURPLE, "text": WHITE},
    {"label": "Capability",      "sub": "スキル・ツール・ガバナンス", "fill": DARK_PURPLE,   "text": WHITE},
    {"label": "Enablement",      "sub": "標準化・リスク管理",        "fill": CORE_PURPLE,   "text": WHITE},
    {"label": "Value",           "sub": "ビジネス価値・顧客体験",     "fill": LIGHT_PURPLE,  "text": DARKEST_PURPLE},
]

PYR_W   = CW          # total base width (in)
PYR_H   = AH - 0.30  # total pyramid height (in)
PYR_Y   = CY + 0.15  # top of pyramid in slide

def _add_trapezoid(slide, x, y, bottom_w, top_w, h, fill_color):
    """Draw a centered isoceles trapezoid using custom geometry."""
    EMU = 914400
    bw  = int(bottom_w * EMU)
    tw  = int(top_w    * EMU)
    off = int((bottom_w - top_w) / 2 * EMU)
    h_e = int(h * EMU)
    sh  = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(x), Inches(y), Inches(bottom_w), Inches(h))
    spPr = sh._element.find(_qn('p:spPr'))
    prstGeom = spPr.find(_qn('a:prstGeom'))
    if prstGeom is not None:
        spPr.remove(prstGeom)
    custGeom_xml = (
        '<a:custGeom xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
        f'<a:rect l="0" t="0" r="{bw}" b="{h_e}"/>'
        '<a:pathLst>'
        f'<a:path w="{bw}" h="{h_e}">'
        f'<a:moveTo><a:pt x="{off}" y="0"/></a:moveTo>'
        f'<a:lnTo><a:pt x="{bw - off}" y="0"/></a:lnTo>'
        f'<a:lnTo><a:pt x="{bw}" y="{h_e}"/></a:lnTo>'
        f'<a:lnTo><a:pt x="0" y="{h_e}"/></a:lnTo>'
        '<a:close/></a:path></a:pathLst>'
        '</a:custGeom>'
    )
    # xfrm の直後に挿入（index 0 に入れると xfrm の前になり図形が壊れる）
    xfrm = spPr.find(_qn('a:xfrm'))
    ins_idx = list(spPr).index(xfrm) + 1 if xfrm is not None else 0
    spPr.insert(ins_idx, etree.fromstring(custGeom_xml))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill_color; sh.line.fill.background()
    return sh

n       = len(LAYERS)
layer_h = PYR_H / n
for i, layer in enumerate(LAYERS):          # i=0 = bottom
    row   = n - 1 - i                       # row 0 = top in drawing
    b_w   = PYR_W * (row + 1) / n          # trapezoid bottom width（下層ほど広い）
    t_w   = PYR_W * row / n  # top width（row=0 で幅0 → 頂点が尖る）
    x     = ML + (PYR_W - b_w) / 2
    y     = PYR_Y + row * layer_h
    _add_trapezoid(slide, x, y, b_w, t_w, layer_h - 0.04, layer["fill"])

    # Text inside trapezoid (horizontally centered)
    mid_w = (b_w + t_w) / 2
    mid_x = x + (b_w - mid_w) / 2
    tb = slide.shapes.add_textbox(
        Inches(mid_x + 0.10), Inches(y + 0.06),
        Inches(mid_w - 0.20), Inches(layer_h - 0.16))
    tf = tb.text_frame; tf.word_wrap = True
    p1 = tf.paragraphs[0]; p1.text = layer["label"]
    p1.font.size = Pt(14); p1.font.bold = True
    p1.font.color.rgb = layer["text"]; p1.font.name = FONT
    p1.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph(); p2.text = layer["sub"]
    p2.font.size = Pt(12); p2.font.color.rgb = layer["text"]; p2.font.name = FONT
    p2.alignment = PP_ALIGN.CENTER
```

**Tips:**
- 3層: `layer_h ≈ 1.78"` で余裕あり。5層は `layer_h ≈ 1.07"` でやや狭い → フォントを 12pt に（ブランドルール最小値）
- ラベルを右サイドに出したい場合: textbox を `x = ML + PYR_W + 0.15` に配置し `add_connector_arrow` で接続
- 色を反転させたい（薄い色が下）: `LAYERS` リストの順序を逆にするか `fill` 色を入れ替える

---

## Pattern AD — Program Status Dashboard (プログラムステータス / RAG ダッシュボード)
**Use**: プロジェクト状況報告、課題・リスク管理、RAG（赤/黄/緑）ステータスの一覧可視化

ステータス表（時間・品質・予算など）＋ 課題・アクションテーブルの2段構成。

```
 ┌──────────────────────────────────────────────┐
 │ Overall Status   ● GREEN   コメント           │
 │ Time             ● AMBER   コメント           │
 │ Budget           ● RED     コメント           │
 ├──────────────────────────────────────────────┤
 │ Issues / Risks        Responsible   Due Date │
 │ 課題の内容            担当者        MM/DD    │
 ├──────────────────────────────────────────────┤
 │ Next Steps            Responsible   Due Date │
 │ アクション内容        担当者        MM/DD    │
 └──────────────────────────────────────────────┘
```

| Element | Shape | Fill | Notes |
|---------|-------|------|-------|
| Section header row | RECTANGLE | DARKEST_PURPLE | WHITE 14pt bold |
| Status rows | RECTANGLE | WHITE | RAG indicator (OVAL) + text |
| RAG indicator | OVAL | GREEN / AMBER / RED | 0.22" × 0.22" |
| Issues/Actions table | add_table | DARKEST_PURPLE header | 3 columns |

```python
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE

# ── RAG color constants ─────────────────────────────────────────────────
RAG_GREEN = RGBColor(0x00, 0x70, 0x00)
RAG_AMBER = RGBColor(0xFF, 0xA5, 0x00)
RAG_RED   = RGBColor(0xCC, 0x00, 0x00)

# ── Status items ────────────────────────────────────────────────────────
STATUS_ITEMS = [
    {"label": "Time",    "rag": RAG_GREEN, "comment": "スケジュール通りに進行中。マイルストーン達成。"},
    {"label": "Budget",  "rag": RAG_AMBER, "comment": "予算超過リスクあり。月末に再見積もり予定。"},
    {"label": "Quality", "rag": RAG_GREEN, "comment": "品質指標は全て基準値内。テスト完了率 92%。"},
    {"label": "Scope",   "rag": RAG_RED,   "comment": "スコープ追加要求 3件。変更管理プロセス中。"},
]

DOT_SIZE  = 0.22
ROW_H     = 0.55
LABEL_W   = 1.30
DOT_COL_W = 0.40
COMMENT_W = CW - LABEL_W - DOT_COL_W

def _sec_header(slide, y, text):
    hdr = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(y), Inches(CW), Inches(0.38))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = DARKEST_PURPLE; hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; p.text = text
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT
    tf._txBody.find(_qn('a:bodyPr')).set('anchor', 'ctr')

# ── RAG status section ──────────────────────────────────────────────────
_sec_header(slide, CY, "Overall Status")
ry = CY + 0.40
for item in STATUS_ITEMS:
    rb = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(ML), Inches(ry), Inches(CW), Inches(ROW_H - 0.04))
    rb.fill.solid(); rb.fill.fore_color.rgb = WHITE
    rb.line.color.rgb = LIGHT_GRAY; rb.line.width = Pt(0.5)

    lb = slide.shapes.add_textbox(Inches(ML + 0.10), Inches(ry + 0.06),
        Inches(LABEL_W - 0.10), Inches(ROW_H - 0.10))
    p = lb.text_frame.paragraphs[0]; p.text = item["label"]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = TEXT_BODY; p.font.name = FONT

    dot = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(ML + LABEL_W + (DOT_COL_W - DOT_SIZE) / 2),
        Inches(ry + (ROW_H - DOT_SIZE) / 2 - 0.04),
        Inches(DOT_SIZE), Inches(DOT_SIZE))
    dot.fill.solid(); dot.fill.fore_color.rgb = item["rag"]; dot.line.fill.background()

    cb = slide.shapes.add_textbox(
        Inches(ML + LABEL_W + DOT_COL_W + 0.10), Inches(ry + 0.07),
        Inches(COMMENT_W - 0.20), Inches(ROW_H - 0.10))
    tf = cb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = item["comment"]
    p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
    ry += ROW_H

# ── Issues / Risks table ────────────────────────────────────────────────
_sec_header(slide, ry + 0.10, "Issues / Risks")
ISSUES = [
    {"issue": "外部ベンダーの納期遅延（API 連携部品）",        "owner": "山田 太郎", "due": "03/20"},
    {"issue": "本番環境のメモリ容量不足（16GB → 32GB 必要）", "owner": "鈴木 花子", "due": "03/25"},
]
issues_y = ry + 0.50
tbl_h    = len(ISSUES) * ROW_H + 0.05
tbl = slide.shapes.add_table(
    len(ISSUES) + 1, 3,
    Inches(ML), Inches(issues_y), Inches(CW), Inches(tbl_h)).table
tbl.columns[0].width = Inches(CW * 0.60)
tbl.columns[1].width = Inches(CW * 0.25)
tbl.columns[2].width = Inches(CW * 0.15)

for j, hdr_text in enumerate(["Issue / Risk", "Responsible", "Due Date"]):
    c = tbl.cell(0, j)
    c.text = hdr_text
    c.fill.solid(); c.fill.fore_color.rgb = DARKEST_PURPLE
    p = c.text_frame.paragraphs[0]
    p.font.size = Pt(12); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT

for i, issue in enumerate(ISSUES):
    for j, val in enumerate([issue["issue"], issue["owner"], issue["due"]]):
        c = tbl.cell(i + 1, j)
        c.text = val
        c.fill.solid(); c.fill.fore_color.rgb = WHITE
        p = c.text_frame.paragraphs[0]
        p.font.size = Pt(12); p.font.color.rgb = TEXT_BODY; p.font.name = FONT
```

**Tips:**
- ステータス行は全て WHITE で統一すること（交互色禁止）
- RAG 色は Python 定数として保持。スライドの目的に応じて GREEN/AMBER/RED/GRAY(未開始) を使い分ける
- セクションヘッダー間の間隔: 前セクション最終行 y + 0.10" → ヘッダー → + 0.40" → コンテンツ
- Next Steps セクションを追加する場合: Issues テーブルの下に同じパターンを繰り返す
- テーブルヘッダー上に水平線を追加しないこと（禁止ルール準拠）

---

## Pattern AE — Venn Diagram (ベン図)
**Use**: 3つの概念の重複・交差関係の可視化（経済・社会・環境の交差、スキル×ビジネス×テクノロジーなど）

3つの半透明円を三角形配置で重ね合わせる。中央交差点にラベルを置く。

```
         ╭─────╮
        /  L1   \
       /    ╭────┼──╮
      │  ╭──┼────╯  │
       \  │  ╰──╮  /
        ╰─┼──╮  ╰─╯
          │ L3│
     L2   ╰───╯
```

| Element | Shape | Fill | Notes |
|---------|-------|------|-------|
| Circle 1 (top) | OVAL | DARKEST_PURPLE 55% alpha | 3.20" diameter |
| Circle 2 (bottom-left) | OVAL | DARK_PURPLE 55% alpha | 3.20" diameter |
| Circle 3 (bottom-right) | OVAL | CORE_PURPLE 55% alpha | 3.20" diameter |
| Outer labels | textbox | — | 14pt bold DARKEST_PURPLE |
| Center overlap label | textbox | — | 14pt bold WHITE |

```python
from lxml import etree
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.oxml.ns import qn as _qn

CIRCLE_D = 3.20   # circle diameter (in)
CX_C = ML + CW / 2   # diagram center X
CY_C = CY + AH / 2   # diagram center Y
R    = CIRCLE_D * 0.40  # triangle arrangement radius

# Three circle centers (top, bottom-left, bottom-right)
positions = [
    (CX_C,             CY_C - R * 0.65),  # top
    (CX_C - R * 0.85,  CY_C + R * 0.50),  # bottom-left
    (CX_C + R * 0.85,  CY_C + R * 0.50),  # bottom-right
]
circle_colors = [DARKEST_PURPLE, DARK_PURPLE, CORE_PURPLE]
labels        = ["経済的成長", "社会的責任", "環境保護"]

def _oval_with_alpha(slide, cx, cy, d, rgb_color, alpha_pct=55):
    # Draw an oval with alpha transparency via XML.
    shape = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
        Inches(cx - d / 2), Inches(cy - d / 2), Inches(d), Inches(d))
    shape.line.fill.background()
    spPr = shape._element.find(_qn('p:spPr'))
    solidFill = spPr.find(_qn('a:solidFill'))
    if solidFill is not None:
        spPr.remove(solidFill)
    r, g, b = rgb_color.r, rgb_color.g, rgb_color.b
    fill_xml = (
        '<a:solidFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<a:srgbClr val="{r:02X}{g:02X}{b:02X}">'
        f'<a:alpha val="{int(alpha_pct * 1000)}"/>'
        '</a:srgbClr></a:solidFill>'
    )
    # xfrm・prstGeom の直後に挿入（index 0 だと xfrm の前になり図形が壊れる）
    xfrm = spPr.find(_qn('a:xfrm'))
    prstGeom = spPr.find(_qn('a:prstGeom'))
    ref = prstGeom if prstGeom is not None else xfrm
    ins_idx = list(spPr).index(ref) + 1 if ref is not None else 0
    spPr.insert(ins_idx, etree.fromstring(fill_xml))
    return shape

# Draw circles (back to front for Z-order)
for (cx, cy), color in zip(reversed(positions), reversed(circle_colors)):
    _oval_with_alpha(slide, cx, cy, CIRCLE_D, color, alpha_pct=55)

# Outer labels (at non-overlapping portion of each circle)
label_offsets = [
    (0.00, -0.65),   # top circle: above center
    (-0.75, 0.55),   # bottom-left: lower-left
    (0.75,  0.55),   # bottom-right: lower-right
]
for (cx, cy), (dx, dy), label in zip(positions, label_offsets, labels):
    tb = slide.shapes.add_textbox(
        Inches(cx + dx - 1.10), Inches(cy + dy - 0.22),
        Inches(2.20), Inches(0.50))
    tf = tb.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; p.text = label
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = DARKEST_PURPLE; p.font.name = FONT
    p.alignment = PP_ALIGN.CENTER

# Center overlap label
tb_c = slide.shapes.add_textbox(
    Inches(CX_C - 1.00), Inches(CY_C - 0.25),
    Inches(2.00), Inches(0.55))
tf = tb_c.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "共通の誓約"
p.font.size = Pt(14); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = FONT
p.alignment = PP_ALIGN.CENTER
```

**Tips:**
- `alpha_pct=55` で自然な半透明重なりになる。70以上は不透明感が強くなり交差が見にくい
- 2円ベン図にする場合: `positions` を 2つに減らし、配置を左右に変更する
- 各円に補足テキストを入れる場合: `label_offsets` の位置にテキストボックスを追加
- アルファ値は OOXML の `val` 属性で `alpha_pct * 1000`（55% = 55000）

---

## Pattern AF — Pull Quote (プルクォート / 引用スライド)
**Use**: 重要な発言・調査結果の引用、エグゼクティブへのインパクト強調、キービジョンの宣言（Slide 54 タイプ）

大型の装飾引用符と中央揃えテキストで視覚的インパクトを最大化。Pattern D（Key Message）との違い: D はメッセージ主張型、AF は引用・発言の明示が目的。

```
          ❝
    重要なメッセージや引用文をここに
    2〜3行、大きく中央揃えで表示する。
                                    ❞
        — 発言者名、肩書き / 出典
```

| Element | Shape | Fill | Font |
|---------|-------|------|------|
| Opening quote ❝ | textbox | — | 96pt LIGHTEST_PURPLE |
| Closing quote ❞ | textbox | — | 96pt LIGHTEST_PURPLE |
| Quote text | textbox | — | 28pt bold DARKEST_PURPLE center |
| Accent line | RECTANGLE | CORE_PURPLE | w=1.50" h=0.05" centered |
| Attribution | textbox | — | 14pt MID_GRAY center |

```python
QUOTE_TEXT  = "技術と人間の力を組み合わせることで、より良い未来を共に創り上げることができる。私たちはその可能性を信じる。"
ATTRIBUTION = "— Jane Smith, CEO of ExampleCorp（出典: FY2025 Annual Report）"

# Opening quote mark (top-left, decorative)
qm_open = slide.shapes.add_textbox(
    Inches(ML), Inches(CY + 0.05), Inches(1.00), Inches(1.20))
p = qm_open.text_frame.paragraphs[0]; p.text = "\u201C"
p.font.size = Pt(96); p.font.color.rgb = LIGHTEST_PURPLE; p.font.name = FONT

# Quote text (centered, large)
QUOTE_Y = CY + 0.65
QUOTE_H = 3.20
qt = slide.shapes.add_textbox(
    Inches(ML + 0.70), Inches(QUOTE_Y),
    Inches(CW - 1.40), Inches(QUOTE_H))
tf = qt.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = QUOTE_TEXT
p.font.size = Pt(28); p.font.bold = True
p.font.color.rgb = DARKEST_PURPLE; p.font.name = FONT
p.alignment = PP_ALIGN.CENTER

# Closing quote mark (bottom-right)
qm_close = slide.shapes.add_textbox(
    Inches(ML + CW - 1.00), Inches(QUOTE_Y + QUOTE_H - 0.90),
    Inches(1.00), Inches(1.20))
p = qm_close.text_frame.paragraphs[0]; p.text = "\u201D"
p.font.size = Pt(96); p.font.color.rgb = LIGHTEST_PURPLE; p.font.name = FONT

# Accent divider line
div_y = QUOTE_Y + QUOTE_H + 0.15
div = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE,
    Inches(ML + CW / 2 - 0.75), Inches(div_y), Inches(1.50), Inches(0.05))
div.fill.solid(); div.fill.fore_color.rgb = CORE_PURPLE; div.line.fill.background()

# Attribution
at = slide.shapes.add_textbox(
    Inches(ML), Inches(div_y + 0.20), Inches(CW), Inches(0.45))
p = at.text_frame.paragraphs[0]; p.text = ATTRIBUTION
p.font.size = Pt(14); p.font.color.rgb = MID_GRAY; p.font.name = FONT
p.alignment = PP_ALIGN.CENTER
```

**Tips:**
- 引用文が短い（1行）場合: `QUOTE_H = 1.80` に縮小し `QUOTE_Y` を調整
- 引用符なし・シンプル版（Pattern D との中間）: `qm_open` / `qm_close` を省略
- 日本語引用符: `\u201C` / `\u201D` の代わりに `\u300C` / `\u300D`（「」）も可
- アクセント下線は引用と帰属の視覚的セパレーターとして機能する

---

## Pattern AG — Architecture / Connector Diagram (アーキテクチャ図・システム構成図)
**Use**: システム構成図・フロー図・アーキテクチャ図など、ボックスを線（矢印）でつなぐ図解スライド。全てのシェイプ・コネクタが PowerPoint ネイティブオブジェクトとして編集可能（PNG なし）。

```
┌──────────┐               ┌──────────┐
│  Box A   │ ────────────► │  Box B   │
└──────────┘               └──────────┘
      │ (elbow)
      ▼
┌──────────┐               ┌──────────┐
│  Box C   │ ◄────────────►│  Box D   │
└──────────┘               └──────────┘
```

| Element | Shape | Fill | Font |
|---------|-------|------|------|
| 通常ボックス | RECTANGLE | OFF_WHITE | 14pt TEXT_BODY |
| 強調ボックス | RECTANGLE | LIGHTEST_PURPLE | 14pt bold DARKEST_PURPLE |
| ヘッダーボックス | RECTANGLE | DARKEST_PURPLE | 14pt bold WHITE |
| コネクタ（矢印） | add_connector_arrow | — | 線色: CORE_PURPLE, 1.5pt |
| ボックスラベル | textbox | — | 12pt MID_GRAY（サブラベル） |

```python
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
from native_shapes import add_connector_arrow

# ── ボックス作成ヘルパー ───────────────────────────────────────────
def make_box(slide, x, y, w, h, label,
             fill=OFF_WHITE, border=LIGHT_GRAY,
             font_size=14, bold=False, text_color=None):
    """ネイティブ矩形 + テキストボックスのボックスを作成する"""
    if text_color is None:
        text_color = TEXT_BODY
    shape = slide.shapes.add_shape(
        MSO.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid(); shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = border
    tb = slide.shapes.add_textbox(
        Inches(x + 0.08), Inches(y + 0.08),
        Inches(w - 0.16), Inches(h - 0.16))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run(); run.text = label
    run.font.size = Pt(font_size); run.font.bold = bold
    run.font.color.rgb = text_color; run.font.name = FONT
    return shape

# ── レイアウト定数 ────────────────────────────────────────────────
BOX_W, BOX_H = 2.40, 0.72   # 標準ボックスサイズ
COL_GAP = 1.60               # 列間（コネクタ + 余白）
ROW_GAP = 0.80               # 行間
COL1_X = ML                  # 左列 X
COL2_X = ML + BOX_W + COL_GAP  # 右列 X
ROW1_Y = CY + 0.20
ROW2_Y = ROW1_Y + BOX_H + ROW_GAP

# ── ボックス配置 ──────────────────────────────────────────────────
make_box(slide, COL1_X, ROW1_Y, BOX_W, BOX_H, "フロントエンド")
make_box(slide, COL2_X, ROW1_Y, BOX_W, BOX_H, "バックエンド API",
         fill=LIGHTEST_PURPLE, text_color=DARKEST_PURPLE)
make_box(slide, COL1_X, ROW2_Y, BOX_W, BOX_H, "ユーザー DB")
make_box(slide, COL2_X, ROW2_Y, BOX_W, BOX_H, "分析基盤",
         fill=DARKEST_PURPLE, text_color=WHITE, bold=True)

# ── コネクタ ─────────────────────────────────────────────────────
# A → B（水平・直線）
add_connector_arrow(
    slide,
    x1=COL1_X + BOX_W, y1=ROW1_Y + BOX_H / 2,
    x2=COL2_X,          y2=ROW1_Y + BOX_H / 2,
    color=CORE_PURPLE, width_pt=1.5)

# A → C（垂直 elbow）
add_connector_arrow(
    slide,
    x1=COL1_X + BOX_W / 2, y1=ROW1_Y + BOX_H,
    x2=COL1_X + BOX_W / 2, y2=ROW2_Y,
    color=DARK_PURPLE, width_pt=1.5, connector_type="elbow")

# C ↔ D（双方向）
add_connector_arrow(
    slide,
    x1=COL1_X + BOX_W, y1=ROW2_Y + BOX_H / 2,
    x2=COL2_X,          y2=ROW2_Y + BOX_H / 2,
    color=CORE_PURPLE, width_pt=1.5, arrow_end=True, arrow_start=True)
```

**Sizing mode:** ボックス数・列数に応じて `BOX_W` / `COL_GAP` / `ROW_GAP` を調整。全ボックスが `ML`〜`ML+CW` に収まること（右端 = `ML + CW = 12.92"`）。

**Tips:**
- `connector_type='elbow'` → L字ルーティング（PPT が自動ルーティング）
- `connector_type='curved'` → 有機的な弧線
- `connector_type='straight'` → 直線（デフォルト）
- ラベル付きコネクタ: 矢印の中点付近にテキストボックスを追加（12pt MID_GRAY）
- 強調ボックス: `fill=LIGHTEST_PURPLE` + `text_color=DARKEST_PURPLE`（通常）または `fill=DARKEST_PURPLE` + `text_color=WHITE`（最強調）
- ボックスが多い（6個以上）場合: `BOX_W=2.00, BOX_H=0.60` に縮小し `font_size=12` を使用
- 垂直フロー（上→下のみ）: `add_arrow_down()` の組み合わせも可
- 矩形の線は `shape.line.color.rgb = LIGHT_GRAY`（通常）または `shape.line.fill.background()`（枠線なし）

---

## Pattern AH — Decision Matrix（意思決定マトリクス）

複数の選択肢を複数の評価軸で評価し、◎○△×記号で可視化する。Pattern S（Framework Matrix）と構造は近いが、セル内が記号テキスト中心になる点が異なる。

```
┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ 選択肢 ╲ 評価軸 │   コスト    │  実現可能性  │   スピード   │    リスク   │  ← DARKEST_PURPLE
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ 選択肢A （強調） │      ○     │      △      │      ◎      │      △      │  ← CORE_PURPLE BG
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ 選択肢B          │      ◎     │      ○      │      △      │      ○      │
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ 選択肢C          │      △     │      ◎      │      ○      │      ▲      │
└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

| Shape | x | y | w | h | Fill | Text |
|-------|---|---|---|---|------|------|
| Table header row | ML | CY | CW | 0.55 | DARKEST_PURPLE | WHITE 14pt bold center |
| Row label (推奨行) | ML | — | 1.80 | 0.80 | CORE_PURPLE | WHITE 14pt bold |
| Row label (通常行) | ML | — | 1.80 | 0.80 | OFF_WHITE | TEXT_BODY 14pt |
| Symbol cell | — | — | vary | 0.80 | WHITE | Symbol 18pt center BLACK |

**記号と意味:**
| 記号 | 意味 | フォント色 |
|------|------|-----------|
| ◎ | 優秀・最適 | BLACK |
| ○ | 良好 | BLACK |
| △ | 要検討 | BLACK |
| × | 不適 | BLACK |
| ▲ | 警告 | BLACK |

```python
# ── Pattern AH — Decision Matrix ──────────────────────────────────────────
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

criteria  = ["コスト効率", "実現可能性", "スピード", "リスク"]
options   = ["選択肢A", "選択肢B", "選択肢C"]
ratings   = [
    ["○", "△", "◎", "△"],   # 選択肢A（推奨 → 強調行）
    ["◎", "○", "△", "○"],
    ["△", "◎", "○", "▲"],
]
highlight_row = 0  # 推奨候補の行インデックス（0始まり）

LABEL_W = 1.80
CELL_W  = (CW - LABEL_W) / len(criteria)
ROW_H   = 0.80
HDR_H   = 0.55

tbl_y = CY

# ── ヘッダー行（評価軸） ──────────────────────────────────────────────────
hdr = slide.shapes.add_table(1, len(criteria) + 1,
    Inches(ML), Inches(tbl_y),
    Inches(CW), Inches(HDR_H)).table
hdr.columns[0].width = Inches(LABEL_W)
for ci in range(len(criteria)):
    hdr.columns[ci + 1].width = Inches(CELL_W)

# 角ラベル（空欄）
c = hdr.cell(0, 0)
c.fill.solid(); c.fill.fore_color.rgb = DARKEST_PURPLE
c.text = "選択肢 ╲ 評価軸"
p = c.text_frame.paragraphs[0]
p.font.size = Pt(12); p.font.bold = True
p.font.color.rgb = WHITE; p.font.name = FONT
p.alignment = PP_ALIGN.CENTER

for ci, crit in enumerate(criteria):
    c = hdr.cell(0, ci + 1)
    c.fill.solid(); c.fill.fore_color.rgb = DARKEST_PURPLE
    c.text = crit
    p = c.text_frame.paragraphs[0]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = WHITE; p.font.name = FONT
    p.alignment = PP_ALIGN.CENTER

# ── データ行 ──────────────────────────────────────────────────────────────
for ri, (opt, row_ratings) in enumerate(zip(options, ratings)):
    is_highlight = (ri == highlight_row)
    row_y = tbl_y + HDR_H + ri * ROW_H

    data_tbl = slide.shapes.add_table(1, len(criteria) + 1,
        Inches(ML), Inches(row_y),
        Inches(CW), Inches(ROW_H)).table
    data_tbl.columns[0].width = Inches(LABEL_W)
    for ci in range(len(criteria)):
        data_tbl.columns[ci + 1].width = Inches(CELL_W)

    # 行ラベル
    c = data_tbl.cell(0, 0)
    lbl_fill = CORE_PURPLE if is_highlight else OFF_WHITE
    lbl_text_color = WHITE if is_highlight else TEXT_BODY
    c.fill.solid(); c.fill.fore_color.rgb = lbl_fill
    c.text = opt
    p = c.text_frame.paragraphs[0]
    p.font.size = Pt(14); p.font.bold = True
    p.font.color.rgb = lbl_text_color; p.font.name = FONT

    # 記号セル
    for ci, sym in enumerate(row_ratings):
        c = data_tbl.cell(0, ci + 1)
        c.fill.solid(); c.fill.fore_color.rgb = WHITE
        c.text = sym
        p = c.text_frame.paragraphs[0]
        p.font.size = Pt(18); p.font.bold = False
        p.font.color.rgb = BLACK; p.font.name = FONT
        p.alignment = PP_ALIGN.CENTER
```

**Sizing mode:** 評価軸数に応じて `LABEL_W` と `CELL_W` を調整。全幅 CW に収めること。

**Tips:**
- 推奨行（`highlight_row`）は行ラベルを CORE_PURPLE にして視覚的に強調する
- 列数が多い（5列以上）場合: `LABEL_W=1.40`、ヘッダーテキストを 12pt に縮小
- 記号の代わりに数値スコア（1-5）を使う場合: `p.font.size = Pt(18)` のまま中央揃えで数字を入れる

---

## Pattern AI — Evaluation Scorecard（評価スコアカード）

複数の選択肢を多軸で評価し、推奨候補をハイライト行で示す。最終列に推奨理由テキスト（→ 形式）を追加。

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────────────────┐
│  評価項目 │  評価軸1  │  評価軸2  │  評価軸3  │  評価軸4  │     総評            │  ← DARKEST_PURPLE
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────────────┤
│  選択肢A  │    ◎    │    ◎    │    ◎    │    —    │→ ベストチョイス      │  ← LIGHTEST_PURPLE BG
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────────────┤
│  選択肢B  │    △    │    △    │    △    │    △    │→ 限定的              │
├──────────┼──────────┼──────────┼──────────┼──────────┼──────────────────────┤
│  選択肢C  │    △    │    △    │    ×    │    ×    │→ 要再検討            │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────────────────┘
```

| Shape | Fill | Text |
|-------|------|------|
| Header row | DARKEST_PURPLE | WHITE 14pt bold center |
| Highlight row (推奨) | LIGHTEST_PURPLE | CORE_PURPLE 14pt bold（ラベル列）|
| Normal row | WHITE | TEXT_BODY 14pt |
| 総評 cell | same as row | 14pt regular「→ …」|

```python
# ── Pattern AI — Evaluation Scorecard ────────────────────────────────────
criteria = ["開発速度", "エコシステム", "学習コスト", "総評"]
options  = [
    ("Python",  ["◎", "◎", "◎", "→ 成熟したエコシステム"],  True),   # True = highlight
    ("R",       ["△", "△", "△", "→ 人材市場は限定的"],       False),
    ("Julia",   ["△", "△", "×", "→ 学習コスト要検討"],       False),
]

LABEL_W  = 1.80
EVAL_W   = (CW - LABEL_W - 2.80) / (len(criteria) - 1)  # 最終列は幅広
LAST_W   = 2.80
ROW_H    = 0.90
HDR_H    = 0.55

# ヘッダー行（テーブル1）、データ行（テーブル N 行）のパターンで実装
# 評価記号（◎○△×）は中央揃え 18pt / 総評は左揃え 14pt
```

**Tips:**
- ハイライト行の行ラベルは CORE_PURPLE 太字で推奨を明示
- 総評列は → + 短いテキスト（16文字以内）で収める
- 記号サイズは 18pt（セル内視認性確保）

---

## Pattern AJ — Radar Chart（レーダーチャート）

多軸評価を蜘蛛の巣形で俯瞰する。**線のみ（塗りなし）**で複数系列の比較に使う。

```
         技術
          ↑
  創造性 ━━ ━━ コミュニケーション
          ↓
   分析  ←   → リーダーシップ
```

```python
# ── Pattern AJ — Radar Chart（線のみ・塗りなし） ──────────────────────────
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Pt
from pptx.oxml.ns import qn as _qn
from lxml import etree

chart_data = ChartData()
chart_data.categories = ["技術", "コミュニケーション", "リーダーシップ", "分析", "創造性"]
chart_data.add_series("現状", (4, 3, 4, 3, 3))
chart_data.add_series("目標", (5, 4, 5, 4, 4))

# スライド中央に正方形レイアウト
CHART_W = CW * 0.65   # 8.125"
CHART_H = AH * 0.90   # 4.815"
CHART_X = ML + (CW - CHART_W) / 2
CHART_Y = CY + (AH - CHART_H) / 2

chart_obj = slide.shapes.add_chart(
    XL_CHART_TYPE.RADAR,       # 線のみ（塗りなし）
    Inches(CHART_X), Inches(CHART_Y),
    Inches(CHART_W), Inches(CHART_H),
    chart_data,
)
chart = chart_obj.chart

# ── 軸ラベルのフォントサイズ設定（XML 操作） ──────────────────────────────
for series in chart.series:
    sp = series._element
    # 系列線幅を 2pt に設定
    spPr = sp.find(_qn("c:spPr"))
    if spPr is None:
        spPr = etree.SubElement(sp, _qn("c:spPr"))
    ln = spPr.find(_qn("a:ln"))
    if ln is None:
        ln = etree.SubElement(spPr, _qn("a:ln"))
    ln.set("w", str(int(Pt(2).pt * 12700)))   # EMU

# 凡例をチャート下部に配置
chart.has_legend = True
from pptx.enum.chart import XL_LEGEND_POSITION
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.include_in_layout = False

# 凡例テキスト 12pt
leg_txPr = chart.legend._element.find(_qn("c:txPr"))
# （オプション）凡例フォントサイズは デフォルトのまま（12pt 程度）で問題なければスキップ可
```

**Sizing mode:** チャートを中央配置。縦横比が崩れると蜘蛛の巣が楕円になるため、`CHART_W : CHART_H ≈ 1.7 : 1` を維持する。

**Tips:**
- `XL_CHART_TYPE.RADAR` = 線のみ（塗りなし）。`RADAR_FILLED` は使わない
- 系列色の変更は XML 操作（`a:ln > a:solidFill > a:srgbClr`）が必要
- 軸の最大値は `chart.value_axis.maximum_scale = 5` で固定できる（python-pptx の radar では利用不可の場合あり）
- カテゴリ数（軸数）は 4〜8 が実用的。3 だと三角形になる

---

## Pattern AK — Calendar（カレンダー）

3ヶ月分のカレンダーを横並びで表示。イベント・祝日を小さな矩形バッジで入れる。

```
┌────────────┬────────────┬────────────┐
│  2026-03   │  2026-04   │  2026-05   │  ← DARKEST_PURPLE ヘッダー
├─┬─┬─┬─┬─  ├─┬─┬─┬─┬─  ├─┬─┬─┬─┬─  │
│月│火│水│木│金 │月│火│水│木│金 │月│火│水│木│金 │  ← CORE_PURPLE, WHITE 14pt
│  │  │ 1│ 2│ 3 │  │  │  │  │  │  │  │  │  │ 1 │
│ …                                        │
└────────────┴────────────┴────────────┘
```

| Shape | Fill | Text |
|-------|------|------|
| 月ヘッダー | DARKEST_PURPLE | WHITE 18pt bold center |
| 曜日行 | CORE_PURPLE | WHITE 12pt bold center |
| 日付セル | WHITE / OFF_WHITE (交互) | 14pt center |
| イベントバッジ | CORE_PURPLE | WHITE 8pt |
| 祝日テキスト | NONE | CORE_PURPLE 8pt |

```python
# ── Pattern AK — Calendar（3ヶ月）──────────────────────────────────────────
import calendar
from datetime import date

YEAR, START_MONTH = 2026, 3   # 開始年月
NUM_MONTHS = 3

# イベント定義: {date(Y, M, D): "イベント名"}
EVENTS = {
    date(2026, 3, 20): "春分の日",
    date(2026, 4, 16): "中間報告",
    date(2026, 4, 29): "昭和の日",
}

WEEKS_DISP = ["月", "火", "水", "木", "金"]   # 月〜金のみ（土日省略）
CAL_X      = ML
CAL_Y      = CY
CAL_W      = CW / NUM_MONTHS - 0.20          # 各月の幅（月間ギャップ 0.20"）
HDR_H      = 0.45
DOW_H      = 0.30
CELL_H     = 0.65                            # 日付セル高さ
CELL_W     = CAL_W / len(WEEKS_DISP)

for mi in range(NUM_MONTHS):
    month = START_MONTH + mi
    year  = YEAR + (month - 1) // 12
    month = (month - 1) % 12 + 1
    ox    = CAL_X + mi * (CAL_W + 0.20)

    # 月ヘッダー
    from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
    bg = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(ox), Inches(CAL_Y), Inches(CAL_W), Inches(HDR_H))
    bg.fill.solid(); bg.fill.fore_color.rgb = DARKEST_PURPLE
    bg.line.fill.background()
    tf = bg.text_frame; tf.word_wrap = False
    p = tf.paragraphs[0]; run = p.add_run()
    run.text = f"{year:04d}-{month:02d}"; run.font.size = Pt(18)
    run.font.bold = True; run.font.color.rgb = WHITE; run.font.name = FONT
    from pptx.enum.text import PP_ALIGN; p.alignment = PP_ALIGN.CENTER

    # 曜日ヘッダー
    for di, dow in enumerate(WEEKS_DISP):
        cx = ox + di * CELL_W
        dh = slide.shapes.add_shape(MSO.RECTANGLE,
            Inches(cx), Inches(CAL_Y + HDR_H), Inches(CELL_W), Inches(DOW_H))
        dh.fill.solid(); dh.fill.fore_color.rgb = CORE_PURPLE
        dh.line.fill.background()
        tf = dh.text_frame; tf.word_wrap = False
        p = tf.paragraphs[0]; run = p.add_run()
        run.text = dow; run.font.size = Pt(12)
        run.font.bold = True; run.font.color.rgb = WHITE; run.font.name = FONT
        p.alignment = PP_ALIGN.CENTER

    # 日付セル（月〜金のみ）
    cal = calendar.monthcalendar(year, month)
    for wk_idx, week in enumerate(cal):
        for di, day_num in enumerate(week[:5]):   # 0=月, 4=金
            if day_num == 0:
                continue
            cx = ox + di * CELL_W
            cy = CAL_Y + HDR_H + DOW_H + wk_idx * CELL_H
            d  = date(year, month, day_num)

            cell_fill = OFF_WHITE if wk_idx % 2 == 0 else WHITE
            ds = slide.shapes.add_shape(MSO.RECTANGLE,
                Inches(cx), Inches(cy), Inches(CELL_W), Inches(CELL_H))
            ds.fill.solid(); ds.fill.fore_color.rgb = cell_fill
            ds.line.color.rgb = LIGHT_GRAY

            # 日付数字
            tb = slide.shapes.add_textbox(
                Inches(cx + 0.04), Inches(cy + 0.04),
                Inches(CELL_W - 0.08), Inches(0.28))
            tf = tb.text_frame; tf.word_wrap = False
            p = tf.paragraphs[0]; run = p.add_run()
            run.text = str(day_num); run.font.size = Pt(14)
            run.font.color.rgb = TEXT_BODY; run.font.name = FONT
            p.alignment = PP_ALIGN.CENTER

            # イベントバッジ
            if d in EVENTS:
                ev_name = EVENTS[d]
                eb = slide.shapes.add_shape(MSO.RECTANGLE,
                    Inches(cx + 0.04), Inches(cy + 0.32),
                    Inches(CELL_W - 0.08), Inches(0.22))
                eb.fill.solid(); eb.fill.fore_color.rgb = CORE_PURPLE
                eb.line.fill.background()
                tf2 = eb.text_frame; tf2.word_wrap = False
                p2 = tf2.paragraphs[0]; run2 = p2.add_run()
                run2.text = ev_name; run2.font.size = Pt(8)
                run2.font.color.rgb = WHITE; run2.font.name = FONT
                p2.alignment = PP_ALIGN.CENTER
```

**Sizing mode:** 月数・曜日数（月〜金 vs 月〜土）に応じて `CAL_W` と `CELL_W` を調整。

**Tips:**
- 土日を含める場合: `WEEKS_DISP = ["月","火","水","木","金","土","日"]` + `week[:7]`
- 祝日テキストのみ（バッジなし）で軽くする場合: バッジ矩形を削除してフォント色を CORE_PURPLE にする
- 月の高さは週数（4〜5週）によって変わる。`len(cal) * CELL_H` で計算して BY を超えないか確認

---

## Pattern AL — Business Model Canvas（ビジネスモデルキャンバス）

9 つのブロックでビジネスモデルを俯瞰する。Osterwalder の BMC を pptx ネイティブ矩形で実装する。

```
┌──────────┬─────────┬────────────────┬──────────────────┬──────────────┐
│  Key     │ Key     │                │ Customer Relat.  │ Customer     │
│ Partners │ Activ.  │ Value          │                  │ Segments     │
│          ├─────────┤ Propositions   ├──────────────────┤              │
│          │ Key     │                │ Channels         │              │
│          │ Resou.  │                │                  │              │
├──────────┴─────────┴────────────────┴──────────────────┴──────────────┤
│ Cost Structure                      │ Revenue Streams                  │
└─────────────────────────────────────┴──────────────────────────────────┘
```

**9 ブロックの定義:**

| ブロック | 列 | 行 | 幅(CW比) | 高さ |
|---------|---|---|---------|------|
| Key Partners | 1 | 1-2 | 0.20 | 上段全高 |
| Key Activities | 2 | 1 | 0.18 | 上段/2 |
| Key Resources | 2 | 2 | 0.18 | 上段/2 |
| Value Propositions | 3 | 1-2 | 0.22 | 上段全高 |
| Customer Relationships | 4 | 1 | 0.22 | 上段/2 |
| Channels | 4 | 2 | 0.22 | 上段/2 |
| Customer Segments | 5 | 1-2 | 0.18 | 上段全高 |
| Cost Structure | 1-3 | 下段 | 0.50 | 1.20 |
| Revenue Streams | 4-5 | 下段 | 0.50 | 1.20 |

```python
# ── Pattern AL — Business Model Canvas ───────────────────────────────────
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
from pptx.enum.text import PP_ALIGN

UPPER_H = 3.60    # 上段（7ブロック）の高さ
LOWER_H = 1.20    # 下段（Cost/Revenue）の高さ
TOP_Y   = CY

# 列幅定義（CW に対する比率）
# Key Partners | Key Activities+Resources | Value Props | Cust.Rel+Channels | Cust.Segments
COL_RATIOS = [0.20, 0.18, 0.22, 0.22, 0.18]
col_widths  = [CW * r for r in COL_RATIOS]
col_xs      = [ML + sum(col_widths[:i]) for i in range(len(col_widths))]

BORDER = LIGHT_GRAY

def _bmc_box(slide, x, y, w, h, title, content="", title_bold=True):
    """BMC 1ブロック：ヘッダータイトル（上端 DARKEST_PURPLE）+ 本文テキスト"""
    # 外枠
    box = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = WHITE
    box.line.color.rgb = BORDER

    # ヘッダーラベル（紫バー）
    hdr_h = 0.36
    hdr = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(hdr_h))
    hdr.fill.solid(); hdr.fill.fore_color.rgb = DARKEST_PURPLE
    hdr.line.fill.background()
    tf = hdr.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; run = p.add_run()
    run.text = title; run.font.size = Pt(12)
    run.font.bold = title_bold; run.font.color.rgb = WHITE; run.font.name = FONT
    p.alignment = PP_ALIGN.CENTER

    # 本文テキスト
    if content:
        tb = slide.shapes.add_textbox(
            Inches(x + 0.10), Inches(y + hdr_h + 0.08),
            Inches(w - 0.20), Inches(h - hdr_h - 0.16))
        tf2 = tb.text_frame; tf2.word_wrap = True
        for line in content.split("\n"):
            p2 = tf2.add_paragraph() if tf2.paragraphs[0].text else tf2.paragraphs[0]
            if p2.text:
                p2 = tf2.add_paragraph()
            run2 = p2.add_run()
            run2.text = line; run2.font.size = Pt(14)
            run2.font.color.rgb = TEXT_BODY; run2.font.name = FONT

# ── 上段 7 ブロック ───────────────────────────────────────────────────────
_bmc_box(slide, col_xs[0], TOP_Y,    col_widths[0], UPPER_H,
         "Key Partners",       "クラウドベンダー\nSIパートナー")
_bmc_box(slide, col_xs[1], TOP_Y,    col_widths[1], UPPER_H / 2,
         "Key Activities",     "プロダクト開発\nカスタマーサクセス")
_bmc_box(slide, col_xs[1], TOP_Y + UPPER_H / 2, col_widths[1], UPPER_H / 2,
         "Key Resources",      "開発チーム\nデータ基盤")
_bmc_box(slide, col_xs[2], TOP_Y,    col_widths[2], UPPER_H,
         "Value Propositions", "業務効率化\nコスト削減")
_bmc_box(slide, col_xs[3], TOP_Y,    col_widths[3], UPPER_H / 2,
         "Customer Relationships", "専任サポート\nコミュニティ")
_bmc_box(slide, col_xs[3], TOP_Y + UPPER_H / 2, col_widths[3], UPPER_H / 2,
         "Channels",           "直販\nパートナー経由")
_bmc_box(slide, col_xs[4], TOP_Y,    col_widths[4], UPPER_H,
         "Customer Segments",  "中堅企業\n大企業")

# ── 下段 2 ブロック ───────────────────────────────────────────────────────
lower_y = TOP_Y + UPPER_H
_bmc_box(slide, ML,            lower_y, CW * 0.50, LOWER_H,
         "Cost Structure",     "人件費\nインフラ費用")
_bmc_box(slide, ML + CW * 0.50, lower_y, CW * 0.50, LOWER_H,
         "Revenue Streams",    "サブスクリプション\n導入支援")
```

**Tips:**
- 上段の高さ（`UPPER_H`）は内容量に応じて 3.20〜4.00" で調整
- ヘッダーラベルを小さく（12pt）することでセル内の本文スペースを確保
- 本文テキストが多い場合は 14pt → 12pt に下げて可（12pt はキャプション扱い）

---

## Pattern AM — Interview Card（インタビューカード）

ペルソナ情報（左サイドバー）と Q&A リスト（右メインエリア）を構造化して提示する。

```
┌────────────────┬──────────────────────────────────────────────────────┐
│                │ Q. 現在の最大の課題は？                             │← CORE_PURPLE 14pt bold
│   [イニシャル] │ ─────────────────────────────────────────           │← LIGHT_GRAY 区切り線
│                │ A. データ入力の二重作業が多く、月末の集計に3日かかる │← TEXT_BODY 14pt
│   氏名（太字） │                                                      │
│   役職         ├──────────────────────────────────────────────────────┤
│   部署         │ Q. 理想の業務フローは？                             │
│   経験 X年     ├──────────────────────────────────────────────────────┤
│                │ Q. 導入時の懸念点は？                               │
└────────────────┴──────────────────────────────────────────────────────┘
```

| Shape | x | y | w | h | Fill | Text |
|-------|---|---|---|---|------|------|
| Left sidebar | ML | CY | 2.20 | AH | LIGHTEST_PURPLE | — |
| Left accent bar | ML | CY | 0.06 | AH | CORE_PURPLE | — |
| Avatar circle | ML+0.35 | CY+0.20 | 0.80 | 0.80 | NONE（枠: CORE_PURPLE 2pt） | イニシャル 18pt bold CORE_PURPLE center |
| Name | ML+0.11 | CY+1.10 | 2.00 | 0.35 | NONE | 14pt bold TEXT_BODY center |
| Sub-info lines | ML+0.11 | CY+1.50 | 2.00 | vary | NONE | 12pt MID_GRAY center |
| Q label | ML+2.40 | vary | CW-2.20 | 0.40 | NONE | CORE_PURPLE 14pt bold |
| Divider | ML+2.40 | vary | CW-2.20 | 0 | — | LIGHT_GRAY 0.5pt |
| A text | ML+2.40 | vary | CW-2.20 | vary | NONE | TEXT_BODY 14pt |

```python
# ── Pattern AM — Interview Card ───────────────────────────────────────────
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn as _qn
from lxml import etree

SIDEBAR_W = 2.20
CONTENT_X = ML + SIDEBAR_W + 0.20   # 右エリア開始X
CONTENT_W = CW - SIDEBAR_W - 0.20

persona = {
    "name":    "田中太郎",
    "role":    "営業部長",
    "dept":    "営業本部",
    "exp":     "経験 15年",
    "initial": "田",
}
qa_list = [
    ("現在の最大の課題は？",
     "データ入力の二重作業が多く、月末の集計に3日かかる"),
    ("理想の業務フローは？",
     "自動連携により入力作業を半減、リアルタイムでダッシュボード確認"),
    ("導入時の懸念点は？",
     "現場の抵抗感とトレーニング期間の確保"),
]

# ── 左サイドバー背景 ──────────────────────────────────────────────────────
sb_bg = slide.shapes.add_shape(MSO.RECTANGLE,
    Inches(ML), Inches(CY), Inches(SIDEBAR_W), Inches(AH))
sb_bg.fill.solid(); sb_bg.fill.fore_color.rgb = LIGHTEST_PURPLE
sb_bg.line.fill.background()

# アクセントバー（左端の細い CORE_PURPLE）
accent = slide.shapes.add_shape(MSO.RECTANGLE,
    Inches(ML), Inches(CY), Inches(0.06), Inches(AH))
accent.fill.solid(); accent.fill.fore_color.rgb = CORE_PURPLE
accent.line.fill.background()

# アバター（楕円で円形を模す）
av_x, av_y, av_s = ML + 0.70, CY + 0.25, 0.80
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
oval = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL,
    Inches(av_x), Inches(av_y), Inches(av_s), Inches(av_s))
oval.fill.solid(); oval.fill.fore_color.rgb = LIGHTEST_PURPLE
oval.line.color.rgb = CORE_PURPLE
# 線幅を 2pt に設定
oval.line.width = Pt(2).pt * 12700   # EMU
tb_av = slide.shapes.add_textbox(
    Inches(av_x), Inches(av_y), Inches(av_s), Inches(av_s))
tf_av = tb_av.text_frame
p_av = tf_av.paragraphs[0]; run_av = p_av.add_run()
run_av.text = persona["initial"]
run_av.font.size = Pt(18); run_av.font.bold = True
run_av.font.color.rgb = CORE_PURPLE; run_av.font.name = FONT
p_av.alignment = PP_ALIGN.CENTER
tf_av.word_wrap = False

# 氏名
nm_tb = slide.shapes.add_textbox(
    Inches(ML + 0.11), Inches(CY + 1.20), Inches(SIDEBAR_W - 0.22), Inches(0.40))
tf_nm = nm_tb.text_frame
p_nm = tf_nm.paragraphs[0]; run_nm = p_nm.add_run()
run_nm.text = persona["name"]
run_nm.font.size = Pt(14); run_nm.font.bold = True
run_nm.font.color.rgb = TEXT_BODY; run_nm.font.name = FONT
p_nm.alignment = PP_ALIGN.CENTER

# サブ情報（役職・部署・経験）
for si, info_key in enumerate(["role", "dept", "exp"]):
    si_tb = slide.shapes.add_textbox(
        Inches(ML + 0.11), Inches(CY + 1.65 + si * 0.32),
        Inches(SIDEBAR_W - 0.22), Inches(0.30))
    tf_si = si_tb.text_frame
    p_si = tf_si.paragraphs[0]; run_si = p_si.add_run()
    run_si.text = persona[info_key]
    run_si.font.size = Pt(12); run_si.font.color.rgb = MID_GRAY
    run_si.font.name = FONT
    p_si.alignment = PP_ALIGN.CENTER

# ── 右エリア Q&A リスト ──────────────────────────────────────────────────
qa_cur_y = CY + 0.10
QA_H     = AH / len(qa_list)

for qi, (question, answer) in enumerate(qa_list):
    # Q ラベル
    q_tb = slide.shapes.add_textbox(
        Inches(CONTENT_X), Inches(qa_cur_y),
        Inches(CONTENT_W), Inches(0.40))
    tf_q = q_tb.text_frame; tf_q.word_wrap = False
    p_q  = tf_q.paragraphs[0]; run_q = p_q.add_run()
    run_q.text = f"Q. {question}"
    run_q.font.size = Pt(14); run_q.font.bold = True
    run_q.font.color.rgb = CORE_PURPLE; run_q.font.name = FONT
    qa_cur_y += 0.40

    # 区切り線
    from native_shapes import add_divider_line
    add_divider_line(slide, CONTENT_X, qa_cur_y, CONTENT_W, LIGHT_GRAY)
    qa_cur_y += 0.10

    # A テキスト
    a_tb = slide.shapes.add_textbox(
        Inches(CONTENT_X), Inches(qa_cur_y),
        Inches(CONTENT_W), Inches(QA_H - 0.65))
    tf_a = a_tb.text_frame; tf_a.word_wrap = True
    p_a  = tf_a.paragraphs[0]; run_a = p_a.add_run()
    run_a.text = f"A. {answer}"
    run_a.font.size = Pt(14); run_a.font.color.rgb = TEXT_BODY; run_a.font.name = FONT
    qa_cur_y += QA_H - 0.55

    # 仕切り矩形（Q&A 間の区切り：薄いグレーバックの帯）
    if qi < len(qa_list) - 1:
        sep = slide.shapes.add_shape(MSO.RECTANGLE,
            Inches(CONTENT_X), Inches(qa_cur_y),
            Inches(CONTENT_W), Inches(0.06))
        sep.fill.solid(); sep.fill.fore_color.rgb = LIGHT_GRAY
        sep.line.fill.background()
        qa_cur_y += 0.10
```

**Sizing mode:** Q&A の件数に応じて `QA_H = AH / len(qa_list)` で自動分割。3〜4件が適切。

**Tips:**
- アバターの楕円はブランドルール上「丸角矩形（roundRect）禁止」の例外。円（OVAL）は使用可
- サイドバー幅 `SIDEBAR_W` は 2.00〜2.40" の範囲で調整
- Q が長い場合は `tf_q.word_wrap = True` にしてテキストボックスの高さを増やす

---

## Pattern AN — Layer Diagram（レイヤー図・積み上げ形式）

システムの各レイヤーを積み上げ形式で示す。左列にレイヤー名（強調）、右列に説明テキスト（簡潔）を横並びにする。

```
┌────────────────────┬──────────────────────────────────────────────┐
│  プレゼンテーション層 │  UI/UX                                      │  ← CORE_PURPLE BG
├────────────────────┼──────────────────────────────────────────────┤
│  ビジネスロジック層   │  API/ルール                                  │  ← DARK_PURPLE BG
├────────────────────┼──────────────────────────────────────────────┤
│  データアクセス層    │  ORM/DB                                      │  ← 別アクセントカラー
├────────────────────┼──────────────────────────────────────────────┤
│  インフラ層          │  クラウド                                    │  ← DARKEST_PURPLE BG
└────────────────────┴──────────────────────────────────────────────┘
```

**⚠ ブランドルール注意**: 画像例では丸角矩形が使われているが、ブランドルール（Rectangles only — no rounded corners）に従い、**RECTANGLE（四角形）のみ**で実装すること。

| Shape | x | y | w | h | Fill | Text |
|-------|---|---|---|---|------|------|
| Layer label box | ML | CY + row * LAYER_H | LABEL_W=3.20 | LAYER_H | accent_color(i) | WHITE 14pt bold center |
| Description box | ML+3.30 | CY + row * LAYER_H | CW-3.30 | LAYER_H | OFF_WHITE | TEXT_BODY 14pt left |
| Connector line（オプション）| ML+3.20 | center_y | 0.10 | 0.02 | LIGHT_GRAY | — |

```python
# ── Pattern AN — Layer Diagram（積み上げレイヤー図） ─────────────────────
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as MSO
from pptx.enum.text import PP_ALIGN

layers = [
    ("プレゼンテーション層", "UI/UX — ユーザーインターフェース"),
    ("ビジネスロジック層",   "API/ルール — 業務ロジック処理"),
    ("データアクセス層",     "ORM/DB — データ永続化"),
    ("インフラ層",           "クラウド — AWS/Azure/GCP"),
]

LABEL_W = 3.20
DESC_W  = CW - LABEL_W - 0.10
LAYER_H = AH / len(layers)

# レイヤーカラー（上から順に明→暗）
LAYER_COLORS = [CORE_PURPLE, DARK_PURPLE, DARKEST_PURPLE, DARKEST_PURPLE]
# ※ layers が 4 件を超える場合は accent_color(i) を使う

for i, (name, desc) in enumerate(layers):
    ly = CY + i * LAYER_H
    fill_color = LAYER_COLORS[i] if i < len(LAYER_COLORS) else accent_color(i)

    # ラベルボックス（左・カラー）
    lbl = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(ML), Inches(ly), Inches(LABEL_W), Inches(LAYER_H))
    lbl.fill.solid(); lbl.fill.fore_color.rgb = fill_color
    lbl.line.fill.background()
    tf_l = lbl.text_frame; tf_l.word_wrap = True
    p_l = tf_l.paragraphs[0]; run_l = p_l.add_run()
    run_l.text = name
    run_l.font.size = Pt(14); run_l.font.bold = True
    run_l.font.color.rgb = WHITE; run_l.font.name = FONT
    p_l.alignment = PP_ALIGN.CENTER

    # 説明ボックス（右・OFF_WHITE）
    desc_x = ML + LABEL_W + 0.10
    desc_box = slide.shapes.add_shape(MSO.RECTANGLE,
        Inches(desc_x), Inches(ly), Inches(DESC_W), Inches(LAYER_H))
    desc_box.fill.solid(); desc_box.fill.fore_color.rgb = OFF_WHITE
    desc_box.line.color.rgb = LIGHT_GRAY
    tb_d = slide.shapes.add_textbox(
        Inches(desc_x + 0.15), Inches(ly + 0.12),
        Inches(DESC_W - 0.30), Inches(LAYER_H - 0.24))
    tf_d = tb_d.text_frame; tf_d.word_wrap = True
    p_d = tf_d.paragraphs[0]; run_d = p_d.add_run()
    run_d.text = desc
    run_d.font.size = Pt(14); run_d.font.color.rgb = TEXT_BODY; run_d.font.name = FONT
```

**Sizing mode:** レイヤー数に応じて `LAYER_H = AH / len(layers)` で自動等分。4〜6層が視認性のベスト。

**Tips:**
- 各レイヤーのカラーを `accent_color(i)` で自動サイクルすると、テーマ変更時に自動対応する
- ラベルボックスとの間（`LABEL_W` 右端）にコネクタ点線を追加する場合: `add_connector_arrow(..., color=LIGHT_GRAY)` を使う
- 詳細テキスト（説明）が複数行の場合: `LAYER_H` を増やすか、テキストを短くして 1 行に収める
- レイヤー間の境界を明示したい場合: `desc_box.line.color.rgb = LIGHT_GRAY` で枠線を設定する

---

## Choosing a Pattern

| Situation | Pattern |
|-----------|---------|
| Explaining a concept with text | A |
| Comparing two things | B or L |
| Chapter/section break | C |
| Single bold statement | D |
| 3–4 recommendations | E |
| 4 equal-weight concepts | F |
| Data in rows/columns | G |
| Sequential steps (arrows / chevron) | P |
| Iterative / cyclical process (PDCA, continuous improvement) | H |
| Table of contents | I |
| Key numbers/KPIs (with card panels) | J |
| Three pillars/workstreams | K |
| Best practices vs. pitfalls | L |
| Charts and graphs | M |
| Team/people intro | N |
| Process with visual flow | P |
| Service/feature catalog | Q |
| Image + text explanation | R |
| Framework / evaluation matrix with row labels | S |
| Problem → solution / background → proposal | T |
| Service pillars with icons and footer message | U |
| 5–12 numbered concepts (e.g., 8 reasons, 6 principles) | V |
| 2–4 large stats for maximum visual impact (no card panels) | W |
| Phased process with grouped steps and detailed content | X |
| Project schedule / roadmap (Gantt chart) | Y |
| Capability / maturity assessment (current vs. target) | Z |
| Priority / portfolio quadrant (value vs. effort) | AA |
| MECE decomposition / logic tree / issue tree | AB |
| Layered hierarchy / prerequisite build-up (pyramid) | AC |
| Project status report with RAG indicators | AD |
| 3-circle Venn diagram (concept overlap / intersection) | AE |
| Key quote / pull quote with attribution | AF |
| Architecture diagram / system map with connectors | AG |
| Decision matrix with ◎○△× symbols (選択肢 × 評価軸) | AH |
| Evaluation scorecard with highlighted winner row | AI |
| Radar / spider chart (multi-axis, line only) | AJ |
| Calendar (3-month grid with event badges) | AK |
| Business Model Canvas (9-block BMC) | AL |
| Interview card (persona sidebar + Q&A list) | AM |
| Layer / stack diagram (system architecture layers) | AN |
