---
name: reserve-space
description: Accenture Places (support-places.accenture.com/places) の会議室・作業席を自動予約するスキル。「会議室を予約して」「部屋を取って」「meeting room を booking して」「作業席を確保して」「グループワーク席を予約して」などと依頼されたときに使用する。Playwright で Edge プロファイルを一時コピーして SSO 認証し、自然言語の指示から会議室を検索・予約する。
---

# reserve-space — Accenture Places スペース予約スキル

## Overview

Accenture Places で会議室（Meeting Room）または作業席（Open Workspace）を自動予約する。
SSO 認証は **LOGIN_ESO スキル** を使用（Edge を開いたまま実行可能）。

---

## SSO 認証について

**LOGIN_ESO** スキルの Edge プロファイルコピー方式を使用。

- Edge を開いたまま実行できる（プロファイルを一時コピーするためロック競合なし）
- `msedge` チャンネル使用のためマネージドデバイス認証 OK
- Edge の既存 SSO セッション（Cookie）を引き継ぐため再ログイン不要
- セッション切れの場合はブラウザでそのままログイン → 自動で続行

**Edge を閉じる必要はありません。**

---

## 実行コマンド

Windows 上で直接実行する（Claude Code は Windows ターミナルから起動すること）。

```powershell
# 会議室を検索
python "$env:USERPROFILE\.claude\skills\reserve-space\scripts\reserve_space.py" --action search --date 2026-03-05 --from-time 14:00 --to-time 16:00

# 会議室を予約（Meeting Room）
python "$env:USERPROFILE\.claude\skills\reserve-space\scripts\reserve_space.py" --action book --room-id A040048 --date 2026-03-05 --from-time 14:00 --to-time 16:00 --room-type "Meeting Room" --subject "週次チームMTG"

# 作業席を予約（Open Workspace）
python "$env:USERPROFILE\.claude\skills\reserve-space\scripts\reserve_space.py" --action book --room-id A04G019 --date 2026-03-05 --from-time 13:00 --to-time 14:00 --room-type "Open Workspace" --charge-code "JP-XXXXXXXX"
```

スクリプトは JSON を stdout に出力する（検索結果 or 予約結果）。

---

## 実行フロー

### STEP 0: 個人設定ルール
- チャージコード：
- AICの有線フロア順は13→14→12→4
- 自分の座席ID：

### STEP 1: 入力パース

ユーザーの指示から以下を抽出する:

| パラメータ | 必須 | 抽出例 |
|----------|------|--------|
| room_type | ★ | 「会議室」→ `Meeting Room` / 「作業席」「席」→ `Open Workspace` |
| date | ★ | 「明日」→ tomorrow の日付 / 「3月5日」→ `2026-03-05` |
| from_time | ★ | 「14時」「午後2時」→ `14:00` |
| to_time | ★ | 「16時まで」「2時間」→ `16:00` |
| min_capacity | ★ | 「8人」「8名」→ `8` |
| building | 任意 | 「AIR」→ `Tokyo, Akasaka Intercity AIR` / AIC → `Tokyo, Akasaka Intercity` |
| floor | 任意 | 「5階」「S4F」→ `S4` / 指定なし → `All Floors` |
| equipment | 任意 | 「プロジェクター」→ `Monitor` |
| subject | 後で確認 | Meeting Room のみ必須 |
| charge_code | 後で確認 | Open Workspace のみ必須。「WBS」「WBSe」もチャージコードと同じ意味 |

不明な項目（特に end_time）があればユーザーに確認する。
部屋IDが直接指定された場合も、book 実行前に必ず以下を確認すること：
  - Open Workspace: charge_code が未指定なら必ず聞く
  - Meeting Room: subject が未指定なら必ず聞く


#### room_type の判定ルール

| ユーザーの表現 | 選択するタブ |
|-------------|------------|
| 「会議室」「ミーティングルーム」「Meeting Room」 | `Meeting Room` |
| 「作業席」「席」「座席」「グループワーク席」「Open Workspace」 | `Open Workspace` |
| 指定なし | `Meeting Room`（デフォルト） |

#### building の解決ルール

頻出略称を下記に示す。全ビル略称は末尾の **Building 略称マスタ** を参照。

| ユーザーの表現 | building 引数 |
|-------------|--------------|
| 「AIC」/ 指定なし | `Tokyo, Akasaka Intercity` |
| 「AIR」 | `Tokyo, Akasaka Intercity AIR` |
| それ以外 | Building 略称マスタ を参照 → 該当なければユーザーに確認 |

### STEP 2: 空き室検索（search コマンド）

`--action search` でスクリプトを実行し、利用可能な部屋リストを取得する。

出力形式（JSON）:
```json
{
  "rooms": [
    {"id": "A040030", "floor": "S4", "capacity": 10, "equipment": ["Monitor"]},
    {"id": "A040048", "floor": "5F", "capacity": 8, "equipment": []}
  ],
  "screenshot": "C:\\Users\\...\\spacersv_screenshots\\search_results.png"
}
```

`"error"` キーが含まれる場合はエラーハンドリングを参照。
`"no_availability": true` が含まれる場合は **STEP 2.9** へ直行する（空き部屋なし）。

#### 検索結果から自動除外されるスペース

以下のキーワードを**部屋名またはカードのタグ行**に含むスペースはスクリプトが自動的に除外する（大文字小文字不問）:

| キーワード | 検出元 | 除外理由 |
|-----------|--------|---------|
| `Strategy Only` | 部屋名 | 特定チーム専用 |
| `CF Only` | 部屋名 | 特定チーム専用 |
| `Approval Required` | 部屋名 | 事前承認が必要 |
| `External` | 部屋名 | 外部向け専用 |
| `Client Room` | カードタグ行（🏷️） | External専用会議室 |
| `Strategy & Consulting` | カードタグ行（🏷️） | Strategy専用 |
| `Corporate Function` | カードタグ行（🏷️） | CF専用（推定） |

> カードタグ行とは、容量（Seats N）・設備（Monitor...）に続く3行目以降のメタ行（🏷️アイコン付き）を指す。

### STEP 2.5: オフィスチェアフィルタリング（Open Workspace のみ）

明示的にプロンプトで許容された場合を除き、Open Workspace 検索時は、オフィスチェアのある席のみを予約対象とし、ソファ席は対象としない。
検索結果の各 room には `thumbnail` キーにカードのスクリーンショットパスが含まれる。

#### Layer 1: 静的リスト（最優先）

allowlist に含まれる部屋は無条件で OK。blocklist に含まれる部屋は除外。

| 種別 | Room ID | フロア | ビル |
|------|---------|-------|------|
| ✅ OK | A04G037 | S4 | AIC |
| ✅ OK | A04G038 | S4 | AIC |
| ✅ OK | A12G018 | 12F | AIC |
| ✅ OK | A13G045 | 13F | AIC |
| ✅ OK | A13G046 | 13F | AIC |
| ✅ OK | A13G047 | 13F | AIC |
| ❌ NG | A04G035 | S4 | AIC |
| ❌ NG | A04G058 | S4 | AIC |
| ❌ NG | A04G059 | S4 | AIC |
| ❌ NG | A12G010 | 12F | AIC |
| ❌ NG | A12G011 | 12F | AIC |
| ❌ NG | A12G012 | 12F | AIC |

#### Layer 2: Vision スクリーニング（フォールバック）

allowlist にも blocklist にもない未知の部屋がある場合、
`thumbnail` パスを Read ツールで開いて画像を判定する。

| 判定 | 基準 |
|------|------|
| ✅ OK（オフィスチェア） | 高い背もたれ、キャスター付き、メッシュ素材のエルゴノミクスチェア |
| ❌ NG（ソファ等） | 低い背もたれ固定脚、クッション座面、ソファ、スツール、木製椅子 |

#### 判定フロー

1. 検索結果を allowlist / blocklist で分類
2. **allowlist に該当する部屋がある** → その中から STEP 3 の優先ルールで選択
3. **allowlist に該当なし・未知の部屋あり** → サムネイルを Vision で判定 → OK 部屋から選択
4. **いずれも該当なし** → 「オフィスチェアの席が見つかりませんでした。条件（時間帯・フロア）を変えますか？」と報告

---

### STEP 2.9: 空き部屋なし時のユーザー通知

検索結果が **0件** の場合（`"no_availability": true` または `"rooms": []`）、**エラー解析やデバッグは行わず、即座にユーザーに空きがないことを通知する。**

> **重要**: スクリーンショット確認・DOM解析・再検索のリトライなどは一切不要。「空いていない」という事実をそのまま伝える。

#### 通知テンプレート

```
指定の条件では空き部屋がありませんでした。

検索条件: AIC / 2026-03-11 13:30-14:00 / 4人部屋

別の条件で検索しますか？
- 時間帯を変更（例: 14:00-14:30、13:00-13:30）
- 別ビルで検索（AIR など）
- 定員を変更
- 別フロアで検索
```

#### ルール

- **再検索しない** — 同じ条件での自動リトライは禁止
- **エラー扱いしない** — `no_availability` はエラーではなく正常な検索結果
- **ユーザーの指示を待つ** — 代替条件はユーザーが決定する
- **候補0件のまま予約を実行してはならない**

> 複数日程の一括予約時は、候補なしの日程をまとめて報告し、1回の問い合わせで方針を決定する。個別に中断しない。

---

### STEP 3: 会議室選択（優先ルール）

#### 部屋ID命名規則

部屋IDの4文字目はスペースタイプを示す:

| 4文字目 | 種別 | 例 |
|--------|------|----|
| `C` | Closed Room（個室） | `A13C015` ✅ |
| `O` | Open Space（オープン） | `A13O015` ❌ |

#### Closed Room フィルタ（Meeting Room のみ）

**Meeting Room 予約時は、部屋IDの4文字目が `C` の部屋のみを対象とする。`O`（Open Space）は除外する。**

- フィルタ後に候補が0件の場合のみ、`O` 部屋も含めて再選択しユーザーに旨を伝える。

#### 優先順位スコアリング

フィルタ後の候補から最適な部屋を以下の優先順位で選ぶ:

| 優先度 | 条件 | 判定ロジック |
|--------|------|------------|
| **1** | 人数適合 | `capacity >= attendees AND capacity <= attendees + 2` |
| **2** | フロア一致 | ユーザーの所属フロアと同一フロア |
| **3** | 座席近接 | 同一フロアの場合、`abs(int(room_id[-3:]) - int(seat_id[-3:]))` が小さいほど優先（seat_id = A13G046） |
| **4** | 設備保有 | 指定設備（Monitor 等）を保有 |
| **5** | 時間帯 | 午前（〜12時）: やや広め / 午後（12時〜）: コンパクト優先 |

スコア1位の部屋を自動的に予約対象として決定する（候補リストをユーザーに見せない）。

### STEP 4: 不足情報の確認（1回のみ）

自動選択した部屋を伝え、不足情報のみ1回の質問で確認する:

**Meeting Room の場合:**
```
「A040048（5F・定員10名）を 2026-03-05 14:00-16:00 で予約します。
 件名を教えてください（例: 週次チームミーティング）」
```

**Open Workspace の場合:**
```
「A04G019（S4F）を 2026-03-05 13:00-14:00 で予約します。
 Charge Code を教えてください（例: JP-XXXXXXXX）」
```

ユーザーが「やめる」「キャンセル」と返答した場合のみ中断する。

| room_type | 確認する項目 | 自動入力 |
|-----------|------------|---------|
| Meeting Room | 件名（subject）のみ | 部屋・日時・Reservation Type=Business Development |
| Open Workspace | Charge Code のみ | 部屋・日時・Reservation Type=Business Development |

### STEP 5: 予約実行（book コマンド）

`--action book` でスクリプトを実行する。

出力形式（JSON）:
```json
{
  "booking_id": "WRE040432",
  "status": "Confirmed",
  "room_id": "A040048",
  "date": "2026-03-05",
  "start_time": "14:00",
  "end_time": "16:00",
  "subject": "週次チームミーティング",
  "screenshot": "C:\\Users\\...\\spacersv_screenshots\\booking_confirmed.png"
}
```

### STEP 6: 完了報告

予約完了後、以下の形式でユーザーに報告する:

```
✅ 会議室の予約が完了しました！

予約番号: WRE040432
会議室: A040048（Tokyo, Akasaka Intercity 5F）
日時: 2026-03-05 14:00 〜 16:00
件名: 週次チームミーティング

⚠️ 重要: 開始時刻（14:00）に Accenture Places で手動チェックインが必要です。
チェックアウトも1時間以内に行ってください。
チェックインしないと予約が自動キャンセルされる場合があります。
```

---

## Building 略称マスタ

スペース検索・予約時の `--building` 引数に使用するビル正式名称の対応表。

| ユーザーの表現 | building 引数（正式名称） |
|-------------|------------------------|
| 「AIC」/ 指定なし | `Tokyo, Akasaka Intercity` |
| 「AIR」 | `Tokyo, Akasaka Intercity AIR` |
| 「AIビル」 | `Fukuoka, Hakata FD Business Center` |
| 「FD」「FD博多」 | `Fukuoka, A.I. Building` |
| 「4PLA」 | `Sapporo, Sapporo 4-Chome Place, Sapporo` |
| 「白石」 | `Sapporo, Shiroishi Garden Place, Sapporo` |
| 「Z」「トリトンZ」「Z棟」 | `Harumi Triton Square Tower Z` |
| 「W」「トリトンW」「W棟」 | `Tokyo, Harumi Triton Square Tower W` |
| 「イヌイ」「inui」 | `Tokyo, Inui Building Kachidoki` |
| それ以外 | ユーザーに確認してから実行 |

---

## デバッグ用スクリーンショット

各ステップ後のスクリーンショットが自動保存される。
保存先: `%TEMP%\spacersv_screenshots\`

| ファイル名 | タイミング |
|-----------|----------|
| `search_results.png` | 検索結果表示後 |
| `reservation_details.png` | 予約詳細フォーム表示後 |
| `before_submit.png` | Submit 前 |
| `booking_confirmed.png` | 予約完了後 |

---

## エラーハンドリング

| エラー（`error` キー） | 原因 | 対処 |
|----------------------|------|------|
| `SSO ログインがタイムアウトしました` | 5分以内にログインが完了しなかった | 再実行してブラウザでログイン |
| `Edge のユーザーデータが見つかりません` | Edge がインストールされていない | Edge をインストール |
| `Room {id} の Add ボタンが見つかりません` | UI変更の可能性 | `search_results.png` を確認してセレクター修正を提案 |
| `rooms` が空リスト | 条件に合う部屋なし | 別の時間帯・フロアを提案 |

---

## 前提条件

```bash
pip install playwright
python -m playwright install chromium
```
