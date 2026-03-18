---
name: common-mistakes
description: "PPTX スキルでよくあるミスとその修正方法。コード生成前に必ず確認すること。"
---

## Common Mistakes

| Issue | Fix |
|-------|-----|
| `select_theme()` / `theme_selector.py` をスクリプトで呼ぶ | **禁止。** Tkinter ダイアログは Claude Code から結果を取得できない。テーマ選択は **AskUserQuestion** で先に確認し、`load_theme("name")` にハードコードすること |
| `load_theme` を `set_lang` より先に呼ぶ | **禁止。** `set_lang()` は `TEMPLATE_PATH` を `slide-master.pptx` に上書きするため、`load_theme` の設定が消える。**必ず `set_lang → load_theme` の順**にすること |
| ロゴ・GTシンボルを手動追加 | **禁止。** スライドマスターに組み込み済み。`add_logo()` / `add_gt_symbol()` を呼ぶと二重配置・テキスト重なりが発生する |
| GT が文字に重なる | `add_gt_symbol()` を削除すること。スライドマスターが自動配置する |
| カバーに紫背景矩形を追加 | **禁止。** `add_cover_slide()` を使えばマスターが背景を提供する。矩形を追加するとロゴ・GTが隠れる |
| カバーで `add_slide()` を使用 | 禁止。カバーには必ず `add_cover_slide()` を使うこと |
| Rounded shapes | `MSO_AUTO_SHAPE_TYPE.RECTANGLE` only |
| Old purple color | Use `CORE_PURPLE` (#A100FF), not #7E00FF |
| SVG import | Not needed — use native shapes or brand asset PNGs |
| ALL CAPS headline | Use sentence case |
| GT used as arrow | GT symbol is brand decoration, not directional |
| No footer | `set_footer(slide)` on every content slide |
| Box内テキストが12pt/13pt | ボックス・カード・テーブルセル内は最小14pt。12ptは外部キャプションのみ |
| Placeholder text showing ("Place subtitle here" / "テキストを入力") | カバーの全プレースホルダーをループで埋めること。`add_breadcrumb(slide, "")` に空文字を渡すとヒントテキストが表示される。セクション区切りのブレッドクラムは必ずセクション名を渡す |
| タイトルを textbox で直接配置 | 禁止。`add_title(slide, "タイトル")` を使うこと |
| ブレッドクラムを textbox で直接配置 | 禁止。`add_breadcrumb(slide, "Section > Topic")` を使うこと |
| メッセージラインのフォントサイズを明示しない | `add_message_line()` は自動で 18pt を設定する。placeholder に書く場合は必ず `run.font.size = Pt(18)` を明示すること。省略するとレイアウト継承値（14pt など）になる |
| Message line in 敬体 | Write in 常体 (〜である/〜だ), never 〜です/〜ます |
| メッセージラインが長すぎる | 60字以内・1行。それを超えると折り返してコンテンツ領域と重なる |
| 図形がメッセージラインと重なる | 全コンテンツ要素の y 座標は CONTENT_Y 以上にすること（`layout_notes.content.content_area_y`、未定義なら `CY=1.50"`）。thumbnail で目視確認 |
| 13pt font | Forbidden. Use 12pt for notes/captions, 14pt for body |
| Font < 12pt | Minimum is 12pt for all visible text except footer (8pt) |
| Agenda badge wraps "01" | Set `tf.word_wrap = False` and zero out bodyPr insets (lIns/rIns/tIns/bIns="0") |
| Chevron で use_pentagon_first=False を使う | **禁止**。常に `use_pentagon_first=True`（デフォルト）を使うこと。左端=pentagon、残り=chevron が正しいスタイル |
| Chevron を複数行に分割する（2段組み）| **禁止**。`add_chevron_flow` は1行のみ。アイテムが多い場合はフォントを小さくするか項目を減らすこと |
| 矢印を三角形にしたい | `add_chevron_flow(..., shape_style='box_triangle')` で四角形＋三角形セパレーターになる |
| Chart wrong colors | Charts auto-apply theme palette via helpers.py; override via series.format.fill |
| Icon not found | Run `icon_utils.build_icon_index()` first, or check keyword spelling |
| Outline skipped | Always generate and confirm outline before writing slide code |
| タイトルが2行になる（カバー・コンテンツ共通） | フォントサイズを下げるのは禁止。**1行に収まる場合は文言を短くすること**（目安: 全角換算26文字以内）。**2行が避けられない場合は意味の切れ目で手動改行を入れること**（自動折り返しは語句の途中で切れる）。改行には `tf.add_paragraph()` で2段落目を追加し、font設定を1段落目と完全に揃えること。例: 「2026年3月 生成AI最新動向レポート」→ p1「2026年3月 生成AI最新動向」p2「レポート」 |
| 交互方向のChevron（← → ← →）を作ろうとする | 非サポート。`add_chevron_flow(..., shape_style='chevron', use_pentagon_first=True)` で全て右向きのフローを使うこと |
| box_triangle で◀左向き三角形になる | **絶対禁止**。セパレーターは常に右向き ▷。内部で `rotation_deg=-90`（OOXML 90° CW）を使用。`rotation_deg=+90` は 270° CW = 90° CCW = ◀ LEFT になるので使わない |
| box_triangle で Box と ▷ の間にスペースがない | `gap=0.10` 以上を指定すること。`max(gap, 0.10)` で最低値を保証する |
| box_triangle の三角形サイズを変えたい | セパレーターは自動的に「高さ:幅=1:3」（ボックス全高×1/3の幅）の細長い ▷ になる。`h` パラメーター（ボックス高さ）で自動スケールするため個別調整不要 |
| 白背景カバーで WHITE / LIGHT_PURPLE 文字を使う | **禁止**。白背景では全テキストを BLACK / TEXT_BODY にすること。WHITE 文字は不可視になる |
| 列ヘッダーラベルが 2 行に折り返す（"MCP" → "MC\nP"） | `tf.word_wrap = False` を設定し、ボックス幅を文字数 × 0.20" 以上にすること |
| Do/Don't ラベルが 2 行に折り返す | ラベル textbox に `tf.word_wrap = False` を設定すること。幅は 2.50" 以上（1.50" は Japanese 混在で折り返しが発生）|
| Icon Grid でアイコンが表示されず空ラベルのみ | キーワードが icon_index.json に存在しない。`find_icons(keyword)` で事前検証。代替：セキュリティ→"security"/"lock"、AI→"robot"/"ai"、チーム→"person"/"team" |
| Chevron フローの下の詳細テキストが図形と重なる / 上下に空白が多い | **垂直中央寄せ公式を使うこと**: `FLOW_Y = CY + (AH - FLOW_H - GAP - DETAIL_H) / 2`、`DETAIL_Y = FLOW_Y + FLOW_H + GAP`。`y=CY` 固定は上詰めになり下部に空白が残る。thumbnail で確認 |
| アジェンダがカバーの直後に来ない | **禁止**。アジェンダがある場合は必ずスライド順序 2 番目（カバーの直後）に配置すること |
| `remove_placeholder()` でプレースホルダーを削除した後「テキストを入力」が表示される | 削除すると layout 側 ghost が表示される。削除せず `ph.text = ""` で空クリアすること |
| `CY=1.50"` / `MSG_Y` をテンプレートに合わせず使う | これらはデフォルト値。`layout_notes.content.content_area_y` が定義されているテンプレートでは `CONTENT_Y` をその値に設定すること。メッセージラインも `layout_notes` に placeholder idx がある場合はそちらを使う |
| テーマ抽出の色が期待と異なる（Fiori で cyan でなく blue が出る） | python-pptx API の `fill.fore_color.rgb` は `schemeClr` で `AttributeError` を silently raise し色が拾えない。`master_to_theme.py`（lxml + `_resolve_color_el`）で再抽出すること。旧スクリプトを使っている場合は最新版に更新 |
| `text_body` / `text_muted` に赤紫・シアンなど彩度の高い色が入る | アクセント色・警告色がテキストに使われていても body/muted トークンは彩度 <0.20 のグレー系のみを選択するよう設計されている。混入する場合は `master_to_theme.py` を最新版に更新 |
| 白背景テンプレートのカバーでサブタイトル・日付が不可視 | `thumbnail.py` でカバーの背景色を確認してから文字色を決める。白背景では title / subtitle / date の**全て**を BLACK / TEXT_BODY / MID_GRAY にすること。WHITE や LIGHT_PURPLE は白背景で不可視になる（「色だけ変えた」つもりで日付を見落としやすい） |
| retheme 後にカバーが白紙・プレースホルダーヒントが残る | `retheme.py` はプレースホルダー構造（型）で移行先レイアウトを選択し、空 placeholder を自動削除する。発生する場合は `PYTHONUTF8=1` を付けて実行しているか確認。それでも残る場合は thumbnail.py で確認して手動修正 |
| retheme 後にメッセージラインがスライド上端に表示される | 旧テーマで idx=11 に message line が配置されている場合、移行先 idx=11（ブレッドクラム位置 y=0.08"）にマッピングされる古いバグ。最新 `retheme.py` は content スライドで idx=11 を free-floating として元の座標に移植するため発生しない。旧バージョンを使っている場合は更新すること |
| retheme でセクション区切りが content レイアウトになる | ソース PPTX のレイアウト名に "section" / "セクション" 等のキーワードが含まれていれば自動で section レイアウトへマッピングされる。キーワードが含まれない名前の場合は content 扱いになる。その場合は手動でスライドのレイアウトを変更するか、セクション区切りらしい背景矩形（DARKEST_PURPLE）が残っているので視覚的には問題ない |
| 色の交互使用（テーブル・カード・バッジ等） | **全面禁止**。index の奇偶や順番で色を変えることは一切禁止。同じ要素には同じ色を使う: テーブルデータ行は WHITE 単色、カード/パネル背景は OFF_WHITE 単色、アジェンダバッジは DARKEST_PURPLE 単色（active のみ CORE_PURPLE）。カード背景に CORE_PURPLE と DARKEST_PURPLE を交互に使うことも禁止 |
| リード↔ボディ間に水平線を引く | **禁止**。タイトル/メッセージラインとコンテンツの間の垂直ギャップが自然なセパレーター。`add_connector`, `add_divider_line`, `add_shape` による線は一切引かない |
| テーブルヘッダー上に水平線を引く | **禁止**。テーブルの紫ヘッダー行自体が視覚的境界。二重境界になるため線を追加しない |
| `make_closing_slide()` を呼ばない | 全デッキの最後に `make_closing_slide(prs)` → `strip_sections(prs)` → `prs.save()` が必須 |
| `strip_sections()` を呼ばない | `prs.save()` の前に必ず呼ぶ。PowerPoint セクションヘッダーが残ったまま納品される |
| `markitdown` でプレースホルダー残留チェックをしない | Step 9 で `markitdown output.pptx` を実行し、「タイトルを入力」等のヒントテキストが残っていないか確認必須 |
| テーブル/チャートの幅が CW 未満で右側に大きな空白 | **テーブル・チャートは常に `w=CW` で作成**。列が少ない場合は列幅を均等拡大して CW を埋める。`verify_pptx.py` が CW の 80% 未満を WARNING として検出する。**円グラフ（Pie）も例外なく `w=CW`** — `w=6.50` 等の狭い値は禁止。凡例はチャートエリア内に自動配置される |
| コンテンツがスライド左側に偏って右側が空白 | コンテンツ幅が CW の 70% 未満の場合、幅を拡大するかセンタリングすること。`verify_pptx.py` が自動検出する |
| セクション区切り（Pattern C）の多用 | **セクション区切りは後続のコンテンツスライドが3枚以上ある場合のみ使用する。** 1〜2枚しかない場合はブレッドクラムでセクションを示せば十分。12枚以下のデッキではセクション区切りは最大2枚まで。セクション区切りはタイトルとサブタイトルだけの「中身のないスライド」なので、多用するとデッキ全体の情報密度が下がり冗長になる |
| 同じパターンの繰り返し使用 | **同じパターンは原則1デッキに1回。** アウトライン段階で使用パターンの重複をチェックし、重複があれば別パターンに差し替える。テキスト系・図形系・データ系・グリッド系をバランスよく混ぜる。単調なデッキはコンサルタント品質に達しない |
| スライドの中身が薄い（bullet 3行＋汎用文言のみ） | **全スライドに固有名詞・数値・年号・金額を含めること。** 「ポイント1」「施策A」等の抽象的プレースホルダーは絶対禁止。コンテンツエリアに最低4つの情報要素（数値、事実、分析、具体例）を含める。トピックについて十分なリサーチを行ってからコンテンツを作成する |
| メッセージラインが事実の羅列 | **So What（だから何なのか）を常体で書く。** 「〜を行った」ではなく「〜により競争優位を構築した」のように示唆・結論・主張を書く |
| カバーに「Presenter 14pt」等のヒントテキストが残る | **カバーの全プレースホルダーを `for ph in slide.placeholders:` でイテレートし、使わないphは `ph.text_frame.clear(); p.text = ""` で空にすること。** idx=0, 1 以外にもプレースホルダーが存在するテンプレートがある。markitdownで残留チェック必須 |
| コンテンツエリアの下半分が空白 | **コンテンツ充填率70%以上を維持すること。** Pattern A でbullet 6行以下なら Pattern E/K に変更するか図形を追加。カード系パネルはコンテンツに合わせて高さを調整する。thumbnailで目視確認し「空白が目立つ」スライドは修正必須 |
| カード・パネル内のテキストが上部に集中し下半分が空白 | カード高さをコンテンツ量に合わせて縮小するか、コンテンツを追加して埋める。カードの高さは固定値ではなくコンテンツ量に応じて動的に決定する |
| Pattern V の `total_h` 未指定でカード下部が大量に空白 | `add_numbered_card_grid()` の `total_h` パラメータを必ず指定すること。デフォルトでは `AH=5.35"` が使われカードが縦に引き伸ばされる。5列1行なら `total_h=3.20` 程度、2行なら `total_h=4.50` 程度を目安に調整。thumbnailで確認 |
| カバーの idx=12（Presenter）や idx=2（Date）が未クリア | **テーマごとにカバーのph構造は異なる。** `for ph in slide.placeholders:` で全phをイテレートし、使わないphには `p.text = " "`（半角スペース1文字）を設定すること。空文字 `""` ではレイアウト側のヒントテキストが表示される場合がある |
| Two Column（Pattern B）でテキストだけ配置し下半分が空白 | **Pattern B は必ず OFF_WHITE パネル背景 + CORE_PURPLE アクセントバーを使うこと。** テキストだけの2列はPattern Bではない。パネルがコンテンツエリア全体（y=2.35〜BY付近）を埋めるため、余白問題が自然に解消される。テキスト量が少ない場合は行間を広げる（`p.space_after = Pt(8)`）か、パネル内でテキストを垂直中央揃えにする |
| コンテンツが上部に固まり下部が空白（全パターン共通） | **テキスト量が少ない場合の対処法（優先順）:** (1) コンテンツを追加して埋める (2) 行間・段落間スペースを広げる（`p.space_after = Pt(8)` 等） (3) コンテンツを垂直方向に中央配置する (4) パターンを変更する。いずれにしても下半分が空白のまま放置しないこと |
| bulletリストにspace_afterを設定していない | **全てのbulletリスト・複数行テキストに `p.space_after = Pt(8)` を設定すること。** デフォルト行間ではテキストが上部に密集し、下部に大量の空白ができる。ヘルパー関数 `_bullets()` を使う場合も内部で必ず設定する。行間を広げることでコンテンツが縦方向に自然に分散し、プロフェッショナルな見た目になる |
| テキストがボックス内で上に偏っている（全パターン共通） | **textbox/カード/パネル内のテキストは垂直中央揃え（`anchor=ctr`）を必須設定すること。** `tf._txBody.find(_qn("a:bodyPr")).set("anchor", "ctr")` を全てのtextboxに適用する。これによりテキストが少ない場合でもボックス内で上下中央に配置され、上に偏る問題を根本解消する |
| テーブルの項目番号カラムで数字が縦に折り返す（"2.\n1" や "1\n0"） | **テーブルで項目番号・連番を表示するカラムは、最長の番号テキストが1行に収まる幅を確保すること。** 目安: 1桁整数 → 最小 0.45"、2桁整数 → 最小 0.55"、"X.X" 形式 → 最小 0.65"、"QXX" 形式 → 最小 0.65"。加えてセルの `word_wrap = False` を設定するか、十分な幅を確保すること。列幅が足りないと "10" が "1\n0" や "2.1" が "2.\n1" のように縦に折れ、テーブルが崩壊する。**生成後は必ず2桁番号のスライドをサムネイルで確認** |
| テーブルの col_widths 合計が CW に満たず左寄りになる | **col_widths を指定する場合、全カラム幅の合計を必ず CW（12.50"）に一致させること。** 合計が CW 未満だとテーブルが左寄りになり右側に大きな空白が生じる。計算例: 4列なら `0.50 + 2.20 + 8.00 + 1.80 = 12.50`。生成前に `sum(col_widths) == CW` を検算すること |
| パネル内のヘッダーとコンテンツが重なる（Pattern B / K 等） | **パネル内にヘッダーtextboxとボディtextboxを配置する場合、y座標が重ならないようにすること。** ヘッダーの bottom（y + h）とボディの top（y）の間に最低 0.10" のギャップを確保する。ヘッダーテキストが長くて折り返す場合はヘッダーの h を大きくするか、テキストを短くする。ヘッダーの推定行数 = ceil(文字数 × 0.14 / textbox幅)。2行以上になる場合は h を 0.50" 以上にすること |
| Pattern H（Circular Flow）で中心円とボックスが重なる | **中心円を追加する場合、RADIUS を `BOX_W/2 + center_W/2 + 0.15` 以上に設定すること。** 例: BOX_W=2.00, center_W=1.70 → 最小 RADIUS=2.00"。RADIUS=1.50 では左右ボックスと中心円が 0.35" ずつ重なり、図形がくっついて見える。中心円なしなら RADIUS=1.50〜1.80 で問題ない |
| retheme 後にレイアウトが崩壊（Gray slice heading 等の装飾レイアウトになる） | **retheme.py の content レイアウト判定は段階的フォールバックを使用する。** TITLE+BODY+footer → TITLE のみ（"Title Only" 相当） → TITLE+BODY の順で探索する。BCG 等 BODY/footer プレースホルダーがないテンプレートでは "Title Only" が選ばれる。レイアウトが崩壊した場合は retheme-guide.md のフォールバック優先順位を確認すること |
| retheme 後に PowerPoint COM がファイルを開けない（`ERROR_FILE_CORRUPT`） | **ZIP 内の重複メディアエントリが原因。** `zipfile` 警告 `Duplicate name: 'ppt/media/imageXX.png'` が出た場合、retheme-guide.md の「ZIP 重複メディアエントリの修復」スクリプトを実行すること。retheme 実行後は必ず `thumbnail.py` でファイルが開けることを確認する |
| 新テーマ登録時にテンプレート PPTX にコンテンツスライドが残っている | **テーマ JSON の `template` フィールドは必ずコンテンツスライドを含まないクリーン版マスターを指すこと。** 外部プレゼンテーションをテーマとして取り込む場合、全スライドを削除したクリーン版を `assets/masters/<name>-clean.pptx` として保存する。retheme-guide.md の「テンプレート準備」を参照 |
