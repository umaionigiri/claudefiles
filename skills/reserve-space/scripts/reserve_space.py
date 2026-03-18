#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Accenture Places スペース予約スクリプト。
LOGIN_ESO スキルを使って SSO 認証し、会議室・作業席を検索・予約する。

使い方:
    # 会議室を検索
    python reserve_space.py --action search --date 2026-03-05 --from-time 14:00 --to-time 16:00

    # 会議室を予約（Meeting Room）
    python reserve_space.py --action book --room-id A040048 --date 2026-03-05 --from-time 14:00 --to-time 16:00 --room-type "Meeting Room" --subject "週次チームMTG"

    # 作業席を予約（Open Workspace）
    python reserve_space.py --action book --room-id A04G019 --date 2026-03-05 --from-time 13:00 --to-time 14:00 --room-type "Open Workspace" --charge-code "JP-XXXXXXXX"

必要なパッケージ:
    pip install playwright
    python -m playwright install chromium
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Windows 環境でも日本語を正常に出力できるようにする
if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp932', 'shift_jis', 'mbcs'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() in ('cp932', 'shift_jis', 'mbcs'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# LOGIN_ESO スキルをインポート
_LOGIN_ESO = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "skills" / "login-eso" / "scripts"
sys.path.insert(0, str(_LOGIN_ESO))
from login_eso import get_browser_context, wait_for_login, check_auth, save_screenshot, SCREENSHOT_DIR  # noqa: E402

PLACES_URL = (
    "https://support-places.accenture.com/places"
    "?id=places_search&source=qkr"
    "&building=7f31978d87cb15108beba71e0ebb3562"
    "&floor="
)


# ---------------------------------------------------------------------------
# ナビゲーション
# ---------------------------------------------------------------------------

def navigate_to_places(page, context, cleanup):
    """Places 検索ページに遷移し、SSO 認証を通す。

    headless モードでセッション切れを検出した場合、wait_for_login が headed で
    ブラウザを再起動するため、返却された page/context/cleanup に差し替える。

    Returns:
        (page, context, cleanup): 認証済み状態の最新オブジェクト群
    """
    try:
        page.goto(PLACES_URL, timeout=30000)
    except Exception:
        page.goto(PLACES_URL, wait_until="load", timeout=30000)
    page.wait_for_timeout(3000)
    # login-eso: セッション切れならフォールバック、認証済みなら None を返す
    result = wait_for_login(page, PLACES_URL, cleanup=cleanup)
    if result:
        context, page, cleanup = result
    # SPA ロード完了待機（日付入力欄が表示されるまで）
    try:
        page.wait_for_selector("input[name='start_time']", timeout=15000)
    except Exception:
        page.wait_for_timeout(5000)
    save_screenshot(page, "00_form_loaded")
    return page, context, cleanup


# ---------------------------------------------------------------------------
# 検索フォーム入力
# ---------------------------------------------------------------------------

def fill_search_form(page, room_type, building, floor, date, start_time, end_time):
    """検索フォームに日時・フロアを入力して検索結果を待つ。

    UI 構造（2026年2月確認）:
    - タブ: Open Workspace / Enclosed Workspace / Meeting Room / Parking
    - Building: URL パラメータで事前設定済み（Tokyo, Akasaka Intercity）
    - Floor: カスタムドロップダウン（placeholder='All floors'）
    - From 日付: input[name='start_time']（YYYY-MM-DD）
    - From 時刻: input[aria-label='Hour'] + input[aria-label='Minute']（1番目ペア）
    - To 日付: input[name='end_time']（YYYY-MM-DD）
    - To 時刻: input[aria-label='Hour'] + input[aria-label='Minute']（2番目ペア）
    - 検索ボタン不要: 日時変更で結果は自動更新
    """
    # タブ選択
    tab_label = room_type if room_type else "Meeting Room"
    try:
        page.click(f"text={tab_label}", timeout=5000)
        page.wait_for_timeout(1000)
    except Exception as e:
        print(f"  タブ選択スキップ: {e}", flush=True)

    # Building 選択（デフォルト "Tokyo, Akasaka Intercity" は URL で設定済みのためスキップ）
    if building and building != "Tokyo, Akasaka Intercity":
        try:
            page.click(".select2-choice", timeout=5000)
            page.wait_for_timeout(500)
            search_keyword = building.split(",")[-1].strip()
            page.fill(".select2-input", search_keyword, timeout=3000)
            page.wait_for_timeout(1000)
            page.click(f".select2-result:has-text('{building}')", timeout=5000)
            page.wait_for_timeout(500)
        except Exception as e:
            print(f"  Building 選択スキップ: {e}", flush=True)

    # Floor 選択（select2 ウィジェット: input を直接クリックすると .select2-choice に遮られるため
    # aria-label="sn_wsd_core_floor" の input の祖先 select2-container 内の choice をクリックする）
    if floor and floor.lower() not in ("all floors",):
        try:
            page.locator(
                'input[aria-label="sn_wsd_core_floor"]'
            ).locator(
                'xpath=ancestor::div[contains(@class,"select2-container")]'
            ).locator('a.select2-choice').click(timeout=5000)
            page.wait_for_timeout(500)
            page.locator(f".select2-results li:has-text('{floor}')").first.click(timeout=5000)
            page.wait_for_timeout(500)
            print(f"  Floor 選択: {floor}", flush=True)
        except Exception as e:
            print(f"  Floor 選択スキップ: {e}", flush=True)

    # From 日付
    try:
        page.fill("input[name='start_time']", date, timeout=5000)
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)
    except Exception as e:
        print(f"  From 日付スキップ: {e}", flush=True)

    # From 時刻（visible な select 要素から選択 / 旧UIボタン式にもフォールバック）
    start_h, start_m = start_time.split(":")
    dropdown_start = f"{int(start_h)}:{start_m}"  # 先頭ゼロ除去: "23:00"
    try:
        time_selects = [s for s in page.locator("select").all() if s.is_visible()]
        if time_selects:
            time_selects[0].select_option(label=dropdown_start, timeout=3000)
            page.wait_for_timeout(300)
            print(f"  From 時刻 設定: {dropdown_start}", flush=True)
        else:
            # フォールバック: 旧UIのボタン式ドロップダウン
            toggles = page.locator("button.time-dropdown-toggle-btn").all()
            if toggles:
                toggles[0].click()
                page.wait_for_timeout(500)
                page.locator(
                    f".time-interval-dropdown:not(.ng-hide) "
                    f".time-interval-dropdown-item:has-text('{dropdown_start}')"
                ).first.click(timeout=5000)
                page.wait_for_timeout(300)
    except Exception as e:
        print(f"  From 時刻スキップ: {e}", flush=True)

    # To 日付
    try:
        page.fill("input[name='end_time']", date, timeout=5000)
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)
    except Exception as e:
        print(f"  To 日付スキップ: {e}", flush=True)

    # To 時刻（visible な select 要素から選択 / 旧UIボタン式にもフォールバック）
    end_h, end_m = end_time.split(":")
    dropdown_end = f"{int(end_h)}:{end_m}"  # 先頭ゼロ除去: "23:30"
    try:
        time_selects = [s for s in page.locator("select").all() if s.is_visible()]
        if len(time_selects) > 1:
            time_selects[1].select_option(label=dropdown_end, timeout=3000)
            page.wait_for_timeout(300)
            print(f"  To 時刻 設定: {dropdown_end}", flush=True)
        else:
            toggles = page.locator("button.time-dropdown-toggle-btn").all()
            if len(toggles) > 1:
                toggles[1].click()
                page.wait_for_timeout(500)
                page.locator(
                    f".time-interval-dropdown:not(.ng-hide) "
                    f".time-interval-dropdown-item:has-text('{dropdown_end}')"
                ).first.click(timeout=5000)
                page.wait_for_timeout(300)
    except Exception as e:
        print(f"  To 時刻スキップ: {e}", flush=True)

    # --- 結果ロード完了を待機（stale結果回避版） ---

    # Phase A: 新しい検索の開始を検知する
    page.evaluate("""() => {
        const card = document.querySelector('.horizontal-card');
        if (card) card.setAttribute('data-stale-marker', 'true');
    }""")
    try:
        page.wait_for_function(
            """() => {
                const spinner = document.querySelector('.loading-text-cards');
                if (spinner && spinner.offsetParent !== null) return true;
                if (!document.querySelector('.horizontal-card[data-stale-marker]')) return true;
                return false;
            }""",
            timeout=5000,
        )
    except Exception:
        page.wait_for_timeout(1500)

    # Phase B: 検索完了を待機（スピナー消滅 → カード出現）
    try:
        page.wait_for_selector(".loading-text-cards", state="hidden", timeout=20000)
    except Exception:
        pass
    try:
        page.wait_for_selector(".horizontal-card", timeout=15000)
    except Exception:
        page.wait_for_timeout(3000)

    # Phase C: DOM安定化待機
    page.wait_for_timeout(800)


# ---------------------------------------------------------------------------
# 会議室検索
# ---------------------------------------------------------------------------

def search_rooms(context, room_type, building, floor, date, start_time, end_time,
                 min_capacity=0, cleanup=None):
    """
    Accenture Places で会議室を検索し、利用可能な部屋リストを返す。

    Returns:
        (dict, context, cleanup):
            dict は {"rooms": [...], "screenshot": "path"}
            context/cleanup はフォールバック時に差し替わった最新オブジェクト
    """
    page = context.new_page()
    try:
        page, context, cleanup = navigate_to_places(page, context, cleanup)
        fill_search_form(page, room_type, building, floor, date, start_time, end_time)

        # Capacity フィルターをサイトのUIに適用（指定がある場合のみ）
        if min_capacity > 0:
            try:
                page.wait_for_selector("text=Capacity", timeout=10000)
                # 「+」ボタンを探す（非表示の Recurring#increment を避け、visible なものを使う）
                plus_btn = None
                for btn in page.locator("button:has-text('+')").all():
                    if btn.is_visible():
                        plus_btn = btn
                        break
                if plus_btn:
                    for _ in range(min_capacity):
                        plus_btn.click()
                        page.wait_for_timeout(100)
                    page.wait_for_timeout(300)
                    # "Capacity" セクション内の Apply をクリック
                    apply_btns = page.locator("text=Apply").all()
                    for ab in apply_btns:
                        if ab.is_visible():
                            ab.click(timeout=5000)
                            break
                    # Apply 後の結果リロードを待機
                    try:
                        page.wait_for_selector(".loading-text-cards", state="hidden", timeout=15000)
                    except Exception:
                        pass
                    try:
                        page.wait_for_selector(".horizontal-card", timeout=15000)
                    except Exception:
                        page.wait_for_timeout(3000)
                    page.wait_for_timeout(800)
                    print(f"  Capacity フィルター適用: {min_capacity}", flush=True)
                else:
                    print("  Capacity +ボタンが見つかりません", flush=True)
            except Exception as e:
                print(f"  Capacity フィルタースキップ: {e}", flush=True)

        screenshot = save_screenshot(page, "search_results")

        # 部屋カードが1枚もなければ空きなしと判定
        # （旧ロジック: "Find what's available for you" ヘッダーで判定していたが、
        #  Capacity フィルター適用後もヘッダーが残るケースがあるため、カード有無で判定に変更）
        if not page.query_selector_all(".horizontal-card"):
            return {"rooms": [], "no_availability": True, "screenshot": screenshot}, context, cleanup

        # カードパース内部関数
        def _parse_cards():
            _EXCLUDED = [
                "strategy only", "cf only", "approval required", "external",
                "client room", "strategy & consulting", "corporate function",
            ]
            parsed = []
            for el in page.query_selector_all(".horizontal-card"):
                try:
                    title_el = el.query_selector("h3.horizontal-card__title")
                    full_title = (title_el.inner_text() if title_el else "").strip()
                    rid = full_title.split("_")[0].split(" ")[0]
                    if not rid:
                        continue
                    if any(kw in full_title.lower() for kw in _EXCLUDED):
                        continue
                    subtitle_el = el.query_selector(".horizontal-card__subtitle")
                    floor_t = (subtitle_el.inner_text() if subtitle_el else "").strip()
                    cap = 0; equip = []; tgs = []
                    for i, meta_el in enumerate(el.query_selector_all(".horizontal-card__meta-row-text")):
                        mt = meta_el.inner_text().strip()
                        if i == 0:
                            try: cap = int(''.join(filter(str.isdigit, mt)))
                            except Exception: cap = 0
                        elif i == 1:
                            equip = [e.strip() for e in mt.split(",") if e.strip()]
                        else:
                            if mt: tgs.append(mt)
                    if any(kw in t.lower() for t in tgs for kw in _EXCLUDED):
                        continue
                    thumb = ""
                    if room_type == "Open Workspace":
                        try:
                            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
                            tf = SCREENSHOT_DIR / f"card_{rid}.png"
                            el.screenshot(path=str(tf)); thumb = str(tf)
                        except Exception: pass
                    parsed.append({"id": rid, "floor": floor_t, "capacity": cap,
                                   "equipment": equip, "tags": tgs, "thumbnail": thumb})
                except Exception:
                    continue
            return parsed

        # 初期カードをパース
        rooms = _parse_cards()

        if min_capacity > 0:
            rooms = [r for r in rooms if r["capacity"] >= min_capacity]

        return {"rooms": rooms, "screenshot": screenshot}, context, cleanup

    finally:
        page.close()


# ---------------------------------------------------------------------------
# 会議室予約
# ---------------------------------------------------------------------------

def book_room(context, room_id, date, start_time, end_time, room_type,
              building, floor, subject=None, charge_code=None, cleanup=None):
    """
    指定した会議室を予約する。

    Returns:
        (dict, context, cleanup):
            dict は {"booking_id": ..., "status": "Confirmed", ...}
            context/cleanup はフォールバック時に差し替わった最新オブジェクト
    """
    page = context.new_page()
    try:
        page, context, cleanup = navigate_to_places(page, context, cleanup)
        fill_search_form(page, room_type, building, floor, date, start_time, end_time)

        # 対象部屋の "Add" ボタンをクリック（UI 2026年2月確認）
        # カード: .horizontal-card、Add ボタン: button.btn-add-card
        add_sel = (
            f".horizontal-card:has(h3.horizontal-card__title:has-text('{room_id}'))"
            f" button.btn-add-card"
        )
        try:
            page.click(add_sel, timeout=10000)
        except Exception as e:
            return {"error": f"Room {room_id} の Add ボタンが見つかりませんでした: {e}"}

        page.wait_for_timeout(1000)

        # 画面下部の "Make A Reservation" ボタンをクリック → 予約フォームページへ遷移
        # Add 直後は disabled の場合があるため、有効化されるまで最大15秒待機する
        try:
            page.wait_for_selector("button.btn-next:not([disabled])", timeout=15000)
            page.click("button.btn-next", timeout=5000)
        except Exception as e:
            return {"error": f"'Make A Reservation' ボタンが見つかりませんでした: {e}"}

        # 予約フォームページのロード待機
        # input#reservation-subject の出現後、SP-VARIABLE-LAYOUT の非同期ロードを待つ
        try:
            page.wait_for_selector("input#reservation-subject", timeout=15000)
        except Exception:
            page.wait_for_timeout(3000)
        page.wait_for_timeout(2000)  # ServiceNow カタログセクションの非同期ロード待機
        save_screenshot(page, "reservation_details")

        # Reservation subject（全タイプ必須 - Open Workspace でも件名は入力が必要）
        effective_subject = subject or f"Reservation for {room_id}"
        try:
            page.fill("input#reservation-subject", effective_subject, timeout=5000)
            page.keyboard.press("Tab")  # blur して Angular validation を確定させる
            page.wait_for_timeout(300)
            print(f"  subject 入力: {effective_subject}", flush=True)
        except Exception as e:
            print(f"  subject 入力スキップ: {e}", flush=True)

        # Reservation Type = "Business Development"（固定）
        # SP-VARIABLE-LAYOUT セクションは TinyMCE の下に位置するためスクロールが必要
        # jQuery による値設定は Angular ng-model が更新されないため、ネイティブクリックで操作する
        try:
            page.evaluate("""
                () => {
                    const el = document.getElementById('s2id_sp_formfield_u_reservation_type');
                    if (el) el.scrollIntoView({behavior: 'instant', block: 'center'});
                }
            """)
            page.wait_for_timeout(800)
            page.locator("#s2id_sp_formfield_u_reservation_type .select2-choice").click(timeout=5000)
            page.wait_for_timeout(500)
            page.locator(".select2-results li:has-text('Business Development')").first.click(timeout=5000)
            page.wait_for_timeout(500)
            print("  Reservation Type 設定: OK", flush=True)
        except Exception as e:
            print(f"  Reservation Type 設定スキップ: {e}", flush=True)

        # Charge Code（Open Workspace のみ）
        if charge_code:
            try:
                charge_locator = page.locator("input[name='u_charge_code']")
                charge_locator.scroll_into_view_if_needed(timeout=5000)
                charge_locator.fill(charge_code, timeout=5000)
                charge_locator.press("Tab")  # locator 指定 Tab でオートコンプリートを経由せず blur
                page.wait_for_timeout(500)
                print(f"  Charge Code 入力: {charge_code}", flush=True)
            except Exception as e:
                print(f"  Charge Code 入力スキップ: {e}", flush=True)

        save_screenshot(page, "before_submit")

        # Submit ボタンが有効になるまで待機（最大10秒）
        for _ in range(20):
            if not page.evaluate("() => !!document.getElementById('submitReservation')?.disabled"):
                break
            page.wait_for_timeout(500)

        # Submit Reservation
        page.click("button#submitReservation", timeout=10000)
        try:
            page.wait_for_selector("text=submitted successfully", timeout=15000)
        except Exception:
            page.wait_for_timeout(3000)

        # 予約番号取得（確認画面: "Reservation Number" ラベル + WRES{数字}）
        booking_id = page.evaluate("""
            () => {
                // body テキストから WRES + 数字パターンを抽出
                const match = document.body.textContent.match(/WRES\\d+/);
                if (match) return match[0];
                // フォールバック: WRE + 数字
                const match2 = document.body.textContent.match(/WRE\\w+\\d{4,}/);
                return match2 ? match2[0] : '';
            }
        """)

        screenshot = save_screenshot(page, "booking_confirmed")

        return {
            "booking_id": booking_id,
            "status": "Confirmed",
            "room_id": room_id,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "subject": subject,
            "screenshot": screenshot,
        }, context, cleanup

    finally:
        page.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Accenture Places スペース予約スクリプト")
    parser.add_argument("--action", required=True, choices=["search", "book"],
                        help="実行するアクション")
    parser.add_argument("--date", help="日付（YYYY-MM-DD）")
    parser.add_argument("--from-time", dest="from_time", help="開始時刻（HH:MM）")
    parser.add_argument("--to-time", dest="to_time", help="終了時刻（HH:MM）")
    parser.add_argument("--room-type", dest="room_type", default="Meeting Room",
                        help="予約区分（Meeting Room / Open Workspace）")
    parser.add_argument("--building", default="Tokyo, Akasaka Intercity",
                        help="ビルディング名")
    parser.add_argument("--floor", default="All Floors", help="フロア")
    parser.add_argument("--room-id", dest="room_id", help="部屋ID（book アクション時に必須）")
    parser.add_argument("--min-capacity", dest="min_capacity", type=int, default=0,
                        help="最低定員（search 時にフィルタリング）")
    parser.add_argument("--subject", help="予約件名（Meeting Room は必須）")
    parser.add_argument("--charge-code", dest="charge_code",
                        help="チャージコード（Open Workspace は必須）")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(json.dumps({
            "error": "playwright がインストールされていません。pip install playwright を実行してください。"
        }, ensure_ascii=False))
        sys.exit(1)

    with sync_playwright() as p:
        context, cleanup = get_browser_context(p)
        try:
            if args.action == "search":
                result, context, cleanup = search_rooms(
                    context,
                    room_type=args.room_type,
                    building=args.building,
                    floor=args.floor,
                    date=args.date,
                    start_time=args.from_time,
                    end_time=args.to_time,
                    min_capacity=args.min_capacity,
                    cleanup=cleanup,
                )
            elif args.action == "book":
                if not args.room_id:
                    print(json.dumps({"error": "--room-id が必要です"}, ensure_ascii=False))
                    sys.exit(1)
                result, context, cleanup = book_room(
                    context,
                    room_id=args.room_id,
                    date=args.date,
                    start_time=args.from_time,
                    end_time=args.to_time,
                    room_type=args.room_type,
                    building=args.building,
                    floor=args.floor,
                    subject=args.subject,
                    charge_code=args.charge_code,
                    cleanup=cleanup,
                )
        except Exception as e:
            result = {"error": str(e)}
        finally:
            context.close()
            cleanup()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
