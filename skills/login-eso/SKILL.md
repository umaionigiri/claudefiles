---
name: login-eso
description: Accenture 社内システム（ESO/SSO）への認証スキル。Edge のプロファイルをコピーして msedge チャンネルで起動し、マネージドデバイス認証を通す。他のスキルから import して使う基盤認証ライブラリ。
---

# LOGIN_ESO — Accenture 社内 SSO 認証スキル

## Overview

Accenture 社内システムへの SSO 認証を行う共通ライブラリスキル。

- Edge を開いたまま実行できる（プロファイルを一時コピーするためロック競合なし）
- `channel="msedge"` 使用のためマネージドデバイス認証 OK
- SSO セッション切れ時はブラウザでそのままログインして継続

---

## 使い方（他スキルからのインポート）

```python
import sys
sys.path.insert(0, r"C:\Users\masaki.hayashi\.claude\skills\login-eso\scripts")
from login_eso import get_browser_context, check_auth, wait_for_login, save_screenshot

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context, cleanup = get_browser_context(p)
    page = context.new_page()
    page.goto("https://support-places.accenture.com/places")
    wait_for_login(page, "https://support-places.accenture.com/places")
    # ... 以降の操作
    context.close()
    cleanup()
```

---

## スタンドアロン実行（認証確認）

```powershell
# 認証テスト（URL を指定して開く）
python "$env:USERPROFILE\.claude\skills\login-eso\scripts\login_eso.py" --url "https://support-places.accenture.com/places"

# デフォルト（Accenture ポータル）
python "$env:USERPROFILE\.claude\skills\login-eso\scripts\login_eso.py"
```

---

## 提供する関数

| 関数 | 説明 |
|------|------|
| `get_browser_context(playwright)` | Edge プロファイルコピー＋msedge 起動。`(context, cleanup)` を返す |
| `check_auth(page)` | ログインページへのリダイレクトでないか確認 |
| `wait_for_login(page, url, timeout_sec=300)` | SSO ログイン完了まで待機し、完了後に url へ再遷移 |
| `save_screenshot(page, name)` | デバッグ用スクリーンショットを保存 |

スクリーンショット保存先: `%TEMP%\spacersv_screenshots\`

---

## 前提条件

```bash
pip install playwright
python -m playwright install chromium
```
