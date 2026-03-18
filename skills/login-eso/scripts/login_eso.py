#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGIN_ESO — Accenture 社内 SSO 認証ライブラリ。

Edge のプロファイルを一時ディレクトリにコピーして msedge チャンネルで起動する。
- Edge を開いたまま実行できる（プロファイルコピーのためロック競合なし）
- msedge チャンネル使用のためマネージドデバイス認証 OK
- headless モードで起動し、SSO セッション切れ時は自動的に表示モードに切替
- SSO セッション切れ時はブラウザでそのままログインして継続

他スキルからのインポート例:
    import sys
    sys.path.insert(0, r"C:\\Users\\...\\login-eso\\scripts")
    from login_eso import get_browser_context, wait_for_login

スタンドアロン実行:
    python login_eso.py --url "https://support-places.accenture.com/places"

必要なパッケージ:
    pip install playwright
    python -m playwright install chromium
"""

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Windows 環境でも日本語を正常に出力できるようにする
if sys.stdout.encoding and sys.stdout.encoding.lower() in ('cp932', 'shift_jis', 'mbcs'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() in ('cp932', 'shift_jis', 'mbcs'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

_user = os.environ.get("USERPROFILE", "")
SCREENSHOT_DIR = Path(_user) / "AppData" / "Local" / "Temp" / "spacersv_screenshots"
DEFAULT_URL = "https://www.accenture.com"

LOGIN_DOMAINS = [
    "login.microsoftonline.com",
    "identity.accenture.com",
    "sts.accenture.com",
    "login.accenture.com",
]

# プロファイルコピー時に除外するキャッシュ系ディレクトリ
_SKIP_DIRS = {
    "Cache", "Code Cache", "GPUCache", "ShaderCache",
    "Service Worker", "CacheStorage", "DawnCache",
    "IndexedDB", "blob_storage", "databases",
    # セッション復元ファイル・ディレクトリ（タブ復元によるタイムアウト防止）
    "Sessions",
    "Last Session", "Last Tabs", "Current Session", "Current Tabs",
}


# ---------------------------------------------------------------------------
# Edge プロファイルの一時コピー
# ---------------------------------------------------------------------------

def _copy_edge_profile(edge_user_data: Path):
    """
    Edge の User Data を一時ディレクトリにコピーする。
    キャッシュ系は除外して高速化。ロック中のファイルはスキップ。

    Returns:
        (temp_user_data_path, temp_base_path) or (None, None) on failure
    """
    temp_base = Path(tempfile.mkdtemp(prefix="login_eso_"))
    temp_ud   = temp_base / "User Data"

    try:
        local_state = edge_user_data / "Local State"
        if local_state.exists():
            temp_ud.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(local_state), str(temp_ud / "Local State"))

        def _copytree_safe(src: Path, dst: Path):
            dst.mkdir(parents=True, exist_ok=True)
            for item in src.iterdir():
                if item.name in _SKIP_DIRS:
                    continue
                if item.name.startswith("Singleton"):
                    continue
                try:
                    if item.is_dir():
                        _copytree_safe(item, dst / item.name)
                    else:
                        shutil.copy2(str(item), str(dst / item.name))
                except (PermissionError, OSError):
                    pass

        _copytree_safe(edge_user_data / "Default", temp_ud / "Default")
        print("  Edge プロファイルを一時コピーしました", flush=True)
        return temp_ud, temp_base

    except Exception as e:
        print(f"  プロファイルコピー失敗: {e}", flush=True)
        shutil.rmtree(str(temp_base), ignore_errors=True)
        return None, None


# ---------------------------------------------------------------------------
# 公開 API
# ---------------------------------------------------------------------------

def get_browser_context(playwright, headless=True):
    """
    Edge プロファイルをコピーして msedge チャンネルで起動する。

    - Edge が起動中でもコピーを使うためロック競合が発生しない
    - msedge チャンネル使用のためマネージドデバイス認証 OK
    - Edge の既存 SSO セッション（Cookie）を引き継ぐため再ログイン不要
    - headless=True（デフォルト）: バックグラウンド実行、viewport=1920x1080
    - headless=False: ブラウザウィンドウ表示、フルスクリーン

    Returns:
        (context, cleanup_fn)  cleanup_fn は context.close() 後に必ず呼ぶこと
    """
    user_profile = os.environ.get("USERPROFILE", "")
    edge_ud = Path(user_profile) / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data"

    if not edge_ud.exists():
        print("エラー: Edge のユーザーデータが見つかりません。", flush=True)
        sys.exit(1)

    print("Edge プロファイルをコピーして起動します（Edge 開いたままでも OK）", flush=True)
    temp_ud, temp_base = _copy_edge_profile(edge_ud)

    if not temp_ud:
        print("エラー: Edge プロファイルのコピーに失敗しました。", flush=True)
        sys.exit(1)

    try:
        launch_args = ["--profile-directory=Default", "--no-restore-last-session"]
        if not headless:
            launch_args.append("--start-maximized")

        launch_kwargs = dict(
            channel="msedge",
            headless=headless,
            args=launch_args,
            ignore_https_errors=True,
        )
        if headless:
            launch_kwargs["viewport"] = {"width": 1920, "height": 1080}

        context = playwright.chromium.launch_persistent_context(
            str(temp_ud),
            **launch_kwargs,
        )

        # フォールバック再起動用のメタデータを保持
        context._login_eso_headless = headless
        context._login_eso_playwright = playwright

        cleanup = lambda: shutil.rmtree(str(temp_base), ignore_errors=True)
        print(f"起動: OK ({'headless' if headless else 'headed'})", flush=True)
        return context, cleanup

    except Exception as e:
        shutil.rmtree(str(temp_base), ignore_errors=True)
        print(f"起動失敗: {e}", flush=True)
        sys.exit(1)


def check_auth(page) -> bool:
    """現在の URL がログインページへのリダイレクトでないか確認する。"""
    return not any(d in page.url for d in LOGIN_DOMAINS)


def _poll_login(page, redirect_url: str, timeout_sec: int):
    """
    headed モードでユーザーの手動ログイン完了をポーリング待機する（内部関数）。

    Args:
        page: Playwright の Page オブジェクト（headed モードで開いているもの）
        redirect_url: ログイン完了後に遷移する URL
        timeout_sec: ログイン待機タイムアウト（秒）
    """
    print("SSO ログインが必要です。ブラウザでログインしてください...", flush=True)
    save_screenshot(page, "login_required")

    for _ in range(timeout_sec):
        page.wait_for_timeout(1000)
        if check_auth(page):
            break
    else:
        print("タイムアウト: ログインが完了しませんでした。", flush=True)
        raise TimeoutError("SSO ログインがタイムアウトしました。")

    print("ログイン完了。ページへ遷移します...", flush=True)
    page.goto(redirect_url, timeout=30000)
    page.wait_for_timeout(2000)


def wait_for_login(page, redirect_url: str, timeout_sec: int = 300, cleanup=None):
    """
    SSO ログイン完了まで待機し、完了後に redirect_url へ再遷移する。

    ログインページへのリダイレクトが検出された場合のみ待機する。
    すでに認証済みの場合は何もしない。

    headless モードでセッション切れを検出した場合は、自動的に headed モードで
    ブラウザを再起動し、ユーザーに手動ログインを求める。

    Args:
        page: Playwright の Page オブジェクト
        redirect_url: ログイン完了後に遷移する URL
        timeout_sec: ログイン待機タイムアウト（秒）。デフォルト 300 秒（5 分）
        cleanup: callable or None。headless フォールバック時に旧一時ディレクトリを削除するために使用

    Returns:
        None: 認証済み、または headed モードでのログイン完了（context 変更なし）
        (new_context, new_page, new_cleanup): headless→headed フォールバック発生時
    """
    if check_auth(page):
        return None  # 認証済みのため何もしない

    context = page.context
    is_headless = getattr(context, '_login_eso_headless', False)
    pw = getattr(context, '_login_eso_playwright', None)

    if is_headless and pw:
        # headless ではユーザー操作不可 → headed で再起動
        print("セッション切れ検出。表示モードで再起動します...", flush=True)
        save_screenshot(page, "login_required_headless")
        page.close()
        context.close()
        if cleanup:
            cleanup()

        new_context, new_cleanup = get_browser_context(pw, headless=False)
        new_page = new_context.new_page()
        try:
            new_page.goto(redirect_url, timeout=30000)
        except Exception:
            new_page.goto(redirect_url, wait_until="load", timeout=30000)
        new_page.wait_for_timeout(3000)

        if not check_auth(new_page):
            try:
                _poll_login(new_page, redirect_url, timeout_sec)
            except TimeoutError:
                # タイムアウト時は新 context を閉じてから例外を再送出
                new_page.close()
                new_context.close()
                new_cleanup()
                raise

        return (new_context, new_page, new_cleanup)

    # headed モード → 従来通りユーザーに手動ログインを求める
    _poll_login(page, redirect_url, timeout_sec)
    return None


def save_screenshot(page, name: str) -> str:
    """デバッグ用スクリーンショットを保存して Windows パスを返す。"""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{name}.png"
    try:
        page.screenshot(path=str(path))
        print(f"  スクリーンショット保存: {path}", flush=True)
    except Exception as e:
        print(f"  スクリーンショット失敗: {e}", flush=True)
    return str(path)


# ---------------------------------------------------------------------------
# スタンドアロン実行（認証テスト）
# ---------------------------------------------------------------------------

def _run_standalone(url: str):
    """指定 URL に SSO 認証でアクセスして開く。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context, cleanup = get_browser_context(p, headless=False)  # テスト用は常に headed
        page = context.new_page()

        print(f"\nアクセス中: {url}", flush=True)
        try:
            page.goto(url, timeout=30000)
        except Exception:
            page.goto(url, wait_until="load", timeout=30000)
        page.wait_for_timeout(3000)

        try:
            wait_for_login(page, url)
        except TimeoutError as e:
            print(str(e), flush=True)
            context.close()
            cleanup()
            sys.exit(1)

        save_screenshot(page, "login_eso_success")
        print(f"\n認証成功: {page.url}", flush=True)
        print("ブラウザを閉じると終了します。", flush=True)

        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass

        context.close()
        cleanup()

    print("完了しました。", flush=True)


def main():
    parser = argparse.ArgumentParser(description="LOGIN_ESO — Accenture 社内 SSO 認証テスト")
    parser.add_argument("--url", default=DEFAULT_URL, help="アクセスする URL")
    args = parser.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        print("エラー: playwright がインストールされていません。", flush=True)
        print("  pip install playwright", flush=True)
        print("  python -m playwright install chromium", flush=True)
        sys.exit(1)

    _run_standalone(args.url)


if __name__ == "__main__":
    main()
