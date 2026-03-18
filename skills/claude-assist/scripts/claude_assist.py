# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "customtkinter>=5.2.0",
#     "Pillow>=10.0.0",
# ]
# ///
"""Claude Assist - Multi-line Input GUI for Claude Code

A separate GUI window for composing multi-line prompts.
Launched from a terminal, it remembers that terminal's window handle
and auto-pastes text back to it.

Usage:
    # In the terminal where you will run claude:
    uv run claude_input.py        # GUI launches, terminal returns to prompt
    claude                         # start claude normally

    # The GUI is now linked to THIS terminal.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import json
import os
import subprocess
import sys

# Fix high-DPI rendering issues (blurry/broken text and borders on scaled displays)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # fallback for older Windows
    except Exception:
        pass

# Fix cp932 encoding errors on Windows terminals (emoji in window titles etc.)
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(errors="replace")
    except Exception:
        pass
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageGrab

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HISTORY_MAX = 50
TEMPLATE_MAX = 100
APP_TITLE = "Claude Assist"
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 680
FONT_FAMILY = "Meiryo UI"
FONT_MONO = "Consolas"

# Elegant glossy purple light theme
COLORS = {
    "bg_dark": "#F4F1F8",      # Page background (soft lavender tint)
    "bg_mid": "#FFFFFF",       # Card / input area background (white)
    "bg_light": "#EDE8F5",     # Button background (light purple wash)
    "fg": "#2A2438",           # Primary text (deep purple-black)
    "fg_dim": "#7A7190",       # Secondary text (muted purple-gray)
    "fg_input": "#352E45",     # Input text
    "accent": "#B189F9",       # Glossy purple (luminous base)
    "accent_hover": "#C4A4FF", # Purple hover (brighter, shiny)
    "accent_dark": "#9A6FE8",  # Deeper purple for contrast elements
    "purple": "#B189F9",       # Primary purple
    "green": "#4CAF7C",        # Fresh success green
    "red": "#E05572",          # Soft coral-red
    "orange": "#D4943A",       # Warm amber for KB accent
    "border": "#DED6EB",       # Border (purple-tinted gray)
    "shadow": "#CEC5DB",       # Shadow color (purple undertone)
    "card_shadow": "#E5DFEE",  # Subtle card shadow (lavender)
}

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
I18N = {
    "ja": {
        "ready": "準備完了",
        "input": "入力",
        "shortcuts_header": "Ctrl+Enter: 送信  |  Ctrl+H: 履歴  |  Ctrl+T: テンプレ",
        "send_btn": "送信  Ctrl+Enter",
        "history_btn": "履歴",
        "file_btn": "添付",
        "clear_btn": "クリア",
        "terminal_label": "ターミナル:",
        "not_linked": "  未接続",
        "linked": "  接続済み",
        "knowledge_base": "参照情報",
        "select_folder": "フォルダ追加",
        "select_file": "ファイル追加",
        "not_configured": "未設定",
        "auto_paste": "ターミナルへ自動送信",
        "lines": "行",
        "chars": "文字",
        "status_bar": "  Ctrl+Enter: 送信  |  Ctrl+H: 履歴  |  Ctrl+L: クリア  |  ファイルのドラッグ&ドロップ対応",
        "input_empty": "入力が空です",
        "sending": "ターミナルに送信中...",
        "sent": "ターミナルに送信しました！",
        "no_terminal": "ターミナル未接続 - クリップボードにコピーしました",
        "copied": "クリップボードにコピーしました！",
        "disconnected": "  切断 (ターミナルが閉じた？)",
        "image_pasted": "画像を貼り付けました！",
        "kb_set": "参照情報を設定しました！",
        "history_title": "入力履歴",
        "select_all": "全選択",
        "delete_selected": "選択を削除",
        "no_history": "履歴がありません",
        "use_btn": "使用",
        "attach_files_title": "ファイルを添付",
        "select_kb_title": "参照フォルダを選択",
        "select_kb_file_title": "参照ファイルを選択",
        "kb_clear": "全解除",
        "kb_cleared": "参照情報を解除しました",
        "kb_count": "件",
        "template_btn": "テンプレ",
        "template_title": "テンプレート",
        "template_save": "保存",
        "template_save_short": "テンプレ保存",
        "template_new": "+ 新規作成",
        "template_name_placeholder": "テンプレート名を入力...",
        "template_saved": "テンプレートを保存しました！",
        "template_no_items": "テンプレートがありません",
        "template_name_empty": "テンプレート名を入力してください",
        "template_content_empty": "入力欄が空です",
        "template_delete_confirm": "削除しますか？",
        "template_edit": "編集",
        "template_edit_title": "テンプレート編集",
        "template_name_label": "名前:",
        "template_content_label": "内容:",
        "template_update": "更新",
        "template_updated": "テンプレートを更新しました！",
        "help_btn": "?",
        "help_title": "使い方ガイド",
        "help_subtitle": "Claude Code に複数行の指示を快適に送信するための入力補助ツール",
        "help_sections": [
            {
                "icon": "1",
                "title": "基本の使い方",
                "desc": "3ステップですぐ使える",
                "items": [
                    ("Step 1", "ターミナルで claude を起動する"),
                    ("Step 2", "この画面の入力欄に指示を書く"),
                    ("Step 3", "Ctrl+Enter で送信 → 自動ペースト！"),
                ],
            },
            {
                "icon": "2",
                "title": "キーボードショートカット",
                "desc": "覚えると操作が格段に速くなります",
                "items": [
                    ("Ctrl+Enter", "入力内容をターミナルに送信"),
                    ("Ctrl+H", "入力履歴を表示して再利用"),
                    ("Ctrl+T", "テンプレート一覧を表示"),
                    ("Ctrl+L", "入力欄をクリア"),
                    ("Ctrl+V", "テキスト or 画像を貼り付け"),
                    ("Ctrl+A", "入力欄を全選択"),
                ],
            },
            {
                "icon": "3",
                "title": "添付・履歴・画像",
                "desc": "ファイルや画像も送れます",
                "items": [
                    ("添付ボタン", "ファイルの @パス をClaudeに送信し"
                     "中身を読ませます（実ファイルの転送ではありません）"),
                    ("対応形式", "Claudeが読めるファイルなら何でもOK"
                     "(テキスト/画像/PDF/Excel/Word等)"),
                    ("履歴ボタン", "過去の入力を再利用（最大50件）"),
                    ("画像貼付", "Ctrl+V でスクショ等を添付"),
                ],
            },
            {
                "icon": "KB",
                "title": "参照情報",
                "desc": "参照フォルダ・ファイルを設定してAIの回答精度UP",
                "items": [
                    ("フォルダ追加", "フォルダの中身をClaudeが読んで回答"),
                    ("ファイル追加", "特定ファイルをClaudeが読んで回答"),
                    ("対応形式", "Claudeが読めるファイルなら何でもOK"
                     "(テキスト/画像/PDF/Excel/Word等)"),
                    ("複数登録OK", "フォルダ・ファイルを何個でも追加可"),
                    ("個別削除", "各項目の × ボタンで削除"),
                    ("仕組み", "送信時に @パス を自動付与し"
                     "Claudeが中身を必ず読んで回答生成"),
                ],
            },
            {
                "icon": "T",
                "title": "テンプレート",
                "desc": "よく使う指示文を保存して再利用",
                "items": [
                    ("保存", "入力欄に指示を書き、テンプレ画面で名前をつけて保存"),
                    ("使用", "一覧から「使用」ボタンで入力欄に貼り付け"),
                    ("編集", "「編集」ボタンで名前・内容を修正"),
                    ("削除", "× ボタンで個別に削除"),
                    ("ショートカット", "Ctrl+T でテンプレート一覧を表示"),
                ],
            },
            {
                "icon": "⚙",
                "title": "各ボタンの説明",
                "desc": "画面上のボタンと機能一覧",
                "items": [
                    ("送信", "入力欄の内容をClaudeに送信（Ctrl+Enter）"),
                    ("履歴", "過去に送信した指示文の一覧を表示・再利用"),
                    ("テンプレ", "よく使う指示文を保存・呼び出し（Ctrl+T）"),
                    ("添付", "ファイルの @パス をClaudeに送信し中身を読ませる"),
                    ("クリア", "入力欄と添付画像をすべてクリア（Ctrl+L）"),
                    ("?", "このヘルプ画面を表示"),
                    ("JA / EN", "表示言語を日本語／英語に切り替え"),
                    ("参照情報", "毎回自動でClaudeに読ませるフォルダ・ファイルを設定"),
                    ("自動送信", "ONでターミナルに直接送信 / OFFでクリップボードにコピー"),
                ],
            },
            {
                "icon": "!",
                "title": "知っておくと便利なこと",
                "desc": "",
                "items": [
                    ("ターミナル固定", "GUIは起動元のターミナル専用です"),
                    ("別ターミナル", "別窓で使うには再度起動してください"),
                    ("手動モード", "「自動送信」OFFでコピーのみ"),
                ],
            },
        ],
        "help_close": "閉じる",
    },
    "en": {
        "ready": "Ready",
        "input": "Input",
        "shortcuts_header": "Ctrl+Enter: Send  |  Ctrl+H: History  |  Ctrl+T: Template",
        "send_btn": "Send  Ctrl+Enter",
        "history_btn": "History",
        "file_btn": "File",
        "clear_btn": "Clear",
        "terminal_label": "Terminal:",
        "not_linked": "  Not linked",
        "linked": "  Linked",
        "knowledge_base": "References",
        "select_folder": "Add Folder",
        "select_file": "Add File",
        "not_configured": "Not configured",
        "auto_paste": "Auto-paste to terminal",
        "lines": "Lines",
        "chars": "Chars",
        "status_bar": "  Ctrl+Enter: Send  |  Ctrl+H: History  |  Ctrl+L: Clear  |  Drag & drop files supported",
        "input_empty": "Input is empty",
        "sending": "Sending to terminal...",
        "sent": "Sent to terminal!",
        "no_terminal": "No terminal linked - copied to clipboard",
        "copied": "Copied to clipboard!",
        "disconnected": "  Disconnected (terminal closed?)",
        "image_pasted": "Image pasted!",
        "kb_set": "Reference set!",
        "history_title": "Input History",
        "select_all": "Select All",
        "delete_selected": "Delete Selected",
        "no_history": "No history yet",
        "use_btn": "Use",
        "attach_files_title": "Attach files",
        "select_kb_title": "Select Reference Folder",
        "select_kb_file_title": "Select Reference File",
        "kb_clear": "Clear All",
        "kb_cleared": "References cleared",
        "kb_count": "items",
        "template_btn": "Template",
        "template_title": "Templates",
        "template_save": "Save",
        "template_save_short": "Save tmpl",
        "template_new": "+ New Template",
        "template_name_placeholder": "Enter template name...",
        "template_saved": "Template saved!",
        "template_no_items": "No templates yet",
        "template_name_empty": "Please enter a template name",
        "template_content_empty": "Input area is empty",
        "template_delete_confirm": "Delete?",
        "template_edit": "Edit",
        "template_edit_title": "Edit Template",
        "template_name_label": "Name:",
        "template_content_label": "Content:",
        "template_update": "Update",
        "template_updated": "Template updated!",
        "help_btn": "?",
        "help_title": "How to Use",
        "help_subtitle": "A companion tool for sending multi-line prompts to Claude Code",
        "help_sections": [
            {
                "icon": "1",
                "title": "Getting Started",
                "desc": "Up and running in 3 steps",
                "items": [
                    ("Step 1", "Start claude in your terminal"),
                    ("Step 2", "Type your prompt in the input area"),
                    ("Step 3", "Ctrl+Enter to send → auto-pasted!"),
                ],
            },
            {
                "icon": "2",
                "title": "Keyboard Shortcuts",
                "desc": "Speed up your workflow",
                "items": [
                    ("Ctrl+Enter", "Send input to the terminal"),
                    ("Ctrl+H", "Show and reuse input history"),
                    ("Ctrl+T", "Show templates"),
                    ("Ctrl+L", "Clear the input area"),
                    ("Ctrl+V", "Paste text or image"),
                    ("Ctrl+A", "Select all text"),
                ],
            },
            {
                "icon": "3",
                "title": "Attach, History & Images",
                "desc": "Send files and images too",
                "items": [
                    ("File button", "Sends @path to Claude so it reads the file "
                     "(the file itself is not transferred)"),
                    ("Supported", "Any file Claude can read"
                     " (text/images/PDF/Excel/Word etc)"),
                    ("History button", "Reuse past inputs (up to 50)"),
                    ("Image paste", "Attach screenshots via Ctrl+V"),
                ],
            },
            {
                "icon": "KB",
                "title": "References",
                "desc": "Give Claude reference material for better answers",
                "items": [
                    ("Add Folder", "Claude reads folder contents for context"),
                    ("Add File", "Claude reads specific files for context"),
                    ("Supported", "Any file Claude can read"
                     " (text/images/PDF/Excel/Word etc)"),
                    ("Multiple OK", "Add as many folders/files as you need"),
                    ("Remove each", "Click x on each item to remove"),
                    ("How it works", "Sends @path with your prompt so "
                     "Claude reads the content automatically"),
                ],
            },
            {
                "icon": "T",
                "title": "Templates",
                "desc": "Save and reuse frequent prompts",
                "items": [
                    ("Save", "Type a prompt, open templates, name it and save"),
                    ("Use", "Click 'Use' to paste into the input area"),
                    ("Edit", "Click 'Edit' to modify name or content"),
                    ("Delete", "Click x to remove a template"),
                    ("Shortcut", "Ctrl+T to open the template list"),
                ],
            },
            {
                "icon": "⚙",
                "title": "Button Guide",
                "desc": "What each button does",
                "items": [
                    ("Send", "Send your input to Claude (Ctrl+Enter)"),
                    ("History", "Browse and reuse past prompts"),
                    ("Template", "Save and recall frequent prompts (Ctrl+T)"),
                    ("File", "Send @path to Claude so it reads the file"),
                    ("Clear", "Clear the input area and pasted images (Ctrl+L)"),
                    ("?", "Show this help page"),
                    ("JA / EN", "Switch display language"),
                    ("References", "Set folders/files for Claude to read with every prompt"),
                    ("Auto-paste", "ON: send directly to terminal / OFF: copy to clipboard"),
                ],
            },
            {
                "icon": "!",
                "title": "Good to Know",
                "desc": "",
                "items": [
                    ("Terminal link", "GUI is linked to its launch terminal"),
                    ("Other terminal", "Launch again from that terminal"),
                    ("Manual mode", "Turn off 'Auto-paste' to copy only"),
                ],
            },
        ],
        "help_close": "Close",
    },
}


# ---------------------------------------------------------------------------
# Data persistence
# ---------------------------------------------------------------------------
def _data_dir() -> Path:
    # scripts/ 内に配置された場合は親の親（スキルフォルダ）、
    # それ以外は同階層の data/ を使う
    base = Path(__file__).resolve().parent
    if base.name == "scripts":
        base = base.parent
    d = base / "data"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _history_path() -> Path:
    return _data_dir() / "history.json"


def _config_path() -> Path:
    return _data_dir() / "config.json"


def _load_history() -> list[str]:
    p = _history_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data[:HISTORY_MAX]
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_history(history: list[str]) -> None:
    p = _history_path()
    p.write_text(
        json.dumps(history[:HISTORY_MAX], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _template_path() -> Path:
    return _data_dir() / "templates.json"


def _load_templates() -> list[dict]:
    """Load templates as list of {name: str, content: str}."""
    p = _template_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data[:TEMPLATE_MAX]
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_templates(templates: list[dict]) -> None:
    p = _template_path()
    p.write_text(
        json.dumps(templates[:TEMPLATE_MAX], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _load_config() -> dict:
    p = _config_path()
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_config(cfg: dict) -> None:
    p = _config_path()
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")



# ---------------------------------------------------------------------------
# Windows API helpers
# ---------------------------------------------------------------------------
def _get_foreground_hwnd() -> int:
    """Get the foreground window handle (= the terminal the user is looking at
    when they run this command)."""
    return ctypes.windll.user32.GetForegroundWindow()


def _get_console_hwnd() -> int:
    """Get the console window handle. Try foreground window first (works with
    Windows Terminal), fall back to GetConsoleWindow (works with cmd.exe)."""
    # GetForegroundWindow returns the actual visible window (works with Windows Terminal)
    fg = _get_foreground_hwnd()
    if fg and _is_window_valid(fg):
        title = _get_window_title(fg)
        # Verify it looks like a terminal window
        terminal_keywords = ["cmd", "powershell", "terminal", "bash", "mintty", "conemu", "claude"]
        if any(kw.lower() in title.lower() for kw in terminal_keywords) or not title:
            return fg

    # Fallback: GetConsoleWindow (works for classic cmd.exe)
    return ctypes.windll.kernel32.GetConsoleWindow()


def _get_window_title(hwnd: int) -> str:
    """Get the title text of a window."""
    buf = ctypes.create_unicode_buffer(512)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, 512)
    return buf.value


def _is_window_valid(hwnd: int) -> bool:
    """Check if a window handle is still valid."""
    user32 = ctypes.windll.user32
    user32.IsWindow.argtypes = [ctypes.c_void_p]
    user32.IsWindow.restype = ctypes.c_int
    return bool(user32.IsWindow(hwnd))


def _set_clipboard(text: str) -> None:
    """Set clipboard text using Windows API."""
    CF_UNICODETEXT = 13
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # 64-bit Windows: must set proper types for pointer-sized values
    kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = ctypes.c_void_p
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]

    user32.OpenClipboard(0)
    user32.EmptyClipboard()

    data = text.encode("utf-16-le") + b"\x00\x00"
    h = kernel32.GlobalAlloc(0x0042, len(data))
    p = kernel32.GlobalLock(h)
    ctypes.memmove(p, data, len(data))
    kernel32.GlobalUnlock(h)
    user32.SetClipboardData(CF_UNICODETEXT, h)
    user32.CloseClipboard()


# ---------------------------------------------------------------------------
# Debug log (written to data/_debug.log, only when --debug flag is present)
# ---------------------------------------------------------------------------
_DEBUG_ENABLED = "--debug" in sys.argv


def _debug_log(msg: str) -> None:
    """Append a debug message to the log file (only if --debug flag is set)."""
    if not _DEBUG_ENABLED:
        return
    try:
        log_path = _data_dir() / "_debug.log"
        with open(log_path, "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"[{datetime.now():%H:%M:%S}] {msg}\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# WriteConsoleInput approach — bypasses all UI permission issues
# ---------------------------------------------------------------------------
class KEY_EVENT_RECORD(ctypes.Structure):
    _fields_ = [
        ("bKeyDown", ctypes.c_int),
        ("wRepeatCount", ctypes.c_ushort),
        ("wVirtualKeyCode", ctypes.c_ushort),
        ("wVirtualScanCode", ctypes.c_ushort),
        ("UnicodeChar", ctypes.c_wchar),
        ("dwControlKeyState", ctypes.c_ulong),
    ]


class _EventUnion(ctypes.Union):
    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("_pad", ctypes.c_byte * 16),  # ensure union is large enough
    ]


class INPUT_RECORD(ctypes.Structure):
    _fields_ = [
        ("EventType", ctypes.c_ushort),
        ("Event", _EventUnion),
    ]





def _make_key_event(ch: str, down: bool = True, vk: int = 0, ctrl: int = 0):
    """Create a single KEY_EVENT INPUT_RECORD."""
    rec = INPUT_RECORD()
    rec.EventType = 0x0001  # KEY_EVENT
    rec.Event.KeyEvent.bKeyDown = down
    rec.Event.KeyEvent.wRepeatCount = 1
    rec.Event.KeyEvent.wVirtualKeyCode = vk
    rec.Event.KeyEvent.UnicodeChar = ch
    rec.Event.KeyEvent.dwControlKeyState = ctrl
    return rec


def _build_records(text: str) -> list:
    """Build KEY_EVENT records for normal (non-slash) text + Enter."""
    records = []
    clean = text.replace("\n", " ").replace("\r", "")
    for ch in clean:
        records.append(_make_key_event(ch, down=True))
        records.append(_make_key_event(ch, down=False))
    # Enter
    records.append(_make_key_event("\r", down=True, vk=0x0D))
    records.append(_make_key_event("\r", down=False, vk=0x0D))
    return records


def _paste_via_clipboard(hwnd: int, text: str) -> bool:
    """Paste text via clipboard + Ctrl+V for slash commands.

    Clipboard paste sends the entire string at once, avoiding per-character
    autocomplete interference that happens with WriteConsoleInputW.
    After paste, user can press Enter manually to submit.
    """
    import time

    user32 = ctypes.windll.user32
    clean = text.replace("\n", " ").replace("\r", "")

    _debug_log(f"_paste_via_clipboard: hwnd={hwnd}, text_len={len(clean)}")

    try:
        # 1. Set clipboard
        _set_clipboard(clean)

        # 2. Focus terminal window
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.15)

        # 3. Ctrl+V → wait → Enter
        _KEYBD_PROTO = ctypes.WINFUNCTYPE(
            None, ctypes.c_byte, ctypes.c_byte, ctypes.c_ulong, ctypes.c_size_t
        )
        _keybd = _KEYBD_PROTO(("keybd_event", ctypes.windll.user32))

        # Ctrl+V to paste
        _keybd(0x11, 0, 0, 0)         # Ctrl down
        _keybd(0x56, 0, 0, 0)         # V down
        _keybd(0x56, 0, 0x0002, 0)    # V up
        _keybd(0x11, 0, 0x0002, 0)    # Ctrl up

        # Wait for paste to complete, then Enter to submit
        # Longer text needs more time for the terminal to process the paste
        wait = max(0.3, min(2.0, len(clean) / 2000))
        _debug_log(f"  paste wait: {wait:.2f}s for {len(clean)} chars")
        time.sleep(wait)
        _keybd(0x0D, 0, 0, 0)         # Enter down
        _keybd(0x0D, 0, 0x0002, 0)    # Enter up

        _debug_log("  _paste_via_clipboard: Ctrl+V + Enter sent")
        return True

    except Exception as e:
        _debug_log(f"  _paste_via_clipboard ERROR: {e}")
        return False


def _write_to_console(pid: int, text: str) -> bool:
    """Write text directly to a console's input buffer via WriteConsoleInputW."""
    kernel32 = ctypes.windll.kernel32

    _debug_log(f"_write_to_console: pid={pid}, text_len={len(text)}")

    kernel32.FreeConsole()

    ok = kernel32.AttachConsole(pid)
    _debug_log(f"  AttachConsole({pid}) = {ok}")
    if not ok:
        _debug_log(f"  AttachConsole FAILED, GetLastError={kernel32.GetLastError()}")
        return False

    try:
        h_stdin = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
        _debug_log(f"  GetStdHandle = {h_stdin}")
        if h_stdin in (0, -1):
            return False

        records = _build_records(text)

        # Send all in one call for maximum speed
        arr = (INPUT_RECORD * len(records))(*records)
        written = ctypes.c_ulong()
        kernel32.WriteConsoleInputW(h_stdin, arr, len(records), ctypes.byref(written))

        _debug_log(f"  WriteConsoleInputW total_written={written.value}")
        return written.value > 0

    except Exception as e:
        _debug_log(f"  Exception: {e}")
        return False

    finally:
        kernel32.FreeConsole()


def _paste_to_console(console_pid: int, text: str, hwnd: int = 0) -> bool:
    """Send text to the target terminal.

    - Slash commands (/foo ...): clipboard paste via Ctrl+V to avoid autocomplete
    - Normal text: WriteConsoleInputW for direct, reliable delivery
    """
    _debug_log(f"_paste_to_console: console_pid={console_pid}, hwnd={hwnd}")

    if not console_pid and not hwnd:
        _debug_log("  No console PID and no HWND")
        return False

    # If no console PID but we have HWND, use clipboard paste for everything
    if not console_pid:
        _debug_log("  No console PID -> clipboard paste mode")
        return _paste_via_clipboard(hwnd, text)

    clean = text.replace("\n", " ").replace("\r", "")
    is_slash = clean.lstrip().startswith("/")

    if is_slash and hwnd:
        # Slash commands: clipboard paste avoids per-char autocomplete
        _debug_log("  Slash command detected -> clipboard paste")
        return _paste_via_clipboard(hwnd, text)

    # Normal text: WriteConsoleInputW (proven reliable)
    try:
        _set_clipboard(clean)
    except Exception:
        pass
    return _write_to_console(console_pid, text)




# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
class ClaudeInputApp(ctk.CTk):
    """Modern GUI for composing multi-line input for Claude Code."""

    def __init__(self, target_hwnd: int = 0, console_pid: int = 0):
        super().__init__()

        # Target terminal
        self.target_hwnd: int = target_hwnd
        self.console_pid: int = console_pid
        self.target_title: str = ""
        _debug_log(f"GUI __init__: target_hwnd={target_hwnd}, console_pid={console_pid}")
        if target_hwnd:
            valid = _is_window_valid(target_hwnd)
            _debug_log(f"GUI __init__: _is_window_valid({target_hwnd}) = {valid}")
            if valid:
                self.target_title = _get_window_title(target_hwnd)
                _debug_log(f"GUI __init__: target_title={self.target_title!r}")


        # State
        self.history: list[str] = _load_history()
        self.templates: list[dict] = _load_templates()
        self.config: dict = _load_config()
        self.attached_files: list[Path] = []
        self.pasted_images: list[Image.Image] = []
        self.history_window: ctk.CTkToplevel | None = None
        self.template_window: ctk.CTkToplevel | None = None
        self.lang: str = self.config.get("lang", "ja")

        # Window setup
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(500, 400)
        self.configure(fg_color=COLORS["bg_dark"])

        try:
            self.iconbitmap(default="")
        except Exception:
            pass


        self._build_ui()
        self._bind_shortcuts()

        self.after(100, lambda: self.input_text.focus_set())

    # ── UI Construction ────────────────────────────────────────────────

    def _build_ui(self):
        # Helper: create a card with shadow effect
        def _card(parent, **kwargs):
            """Create a white card with a subtle drop-shadow frame underneath."""
            wrapper = ctk.CTkFrame(parent, fg_color="transparent")
            # Shadow layer (offset down-right by 2px)
            ctk.CTkFrame(
                wrapper, fg_color=COLORS["shadow"], corner_radius=10,
            ).place(relx=0, rely=0, relwidth=1, relheight=1, x=2, y=2)
            # Main card layer
            card = ctk.CTkFrame(
                wrapper, fg_color=COLORS["bg_mid"], corner_radius=10,
                border_color=COLORS["border"], border_width=1,
                **kwargs,
            )
            card.place(relx=0, rely=0, relwidth=1, relheight=1)
            return wrapper, card

        # ── Title bar (glossy purple gradient effect) ──
        title_outer = ctk.CTkFrame(self, fg_color="#9A6FE8", height=48, corner_radius=0)
        title_outer.pack(fill="x")
        title_outer.pack_propagate(False)

        # Glossy highlight strip at top of title bar
        ctk.CTkFrame(title_outer, fg_color="#C4A4FF", height=2, corner_radius=0).pack(fill="x", side="top")

        ctk.CTkLabel(
            title_outer,
            text="  Claude Assist",
            font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"),
            text_color="#FFFFFF",
            anchor="w",
        ).pack(side="left", padx=14, pady=8)

        self.status_label = ctk.CTkLabel(
            title_outer, text=self._t("ready"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color="#E8DDFF",
        )
        self.status_label.pack(side="right", padx=14, pady=8)

        lang_label = "EN" if self.lang == "ja" else "JA"
        lang_btn = ctk.CTkButton(
            title_outer, text=lang_label, width=36, height=24,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color="#8360D0", hover_color="#7450C0",
            text_color="#F0E8FF", corner_radius=12,
            command=self._toggle_lang,
        )
        lang_btn.pack(side="right", padx=(0, 4), pady=8)

        help_btn = ctk.CTkButton(
            title_outer, text="?", width=28, height=24,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#8360D0", hover_color="#7450C0",
            text_color="#F0E8FF", corner_radius=12,
            command=self._on_help,
        )
        help_btn.pack(side="right", padx=(0, 2), pady=8)

        # Glossy accent line under title bar (bright highlight)
        ctk.CTkFrame(self, fg_color=COLORS["accent"], height=2, corner_radius=0).pack(fill="x")

        # ── Main content area ──
        content = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=16, pady=(12, 8))

        # ── Terminal link bar ──
        link_frame = ctk.CTkFrame(content, fg_color="transparent", height=24)
        link_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            link_frame, text=self._t("terminal_label"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        if self.console_pid or self.target_hwnd:
            if self.target_title:
                link_text = f"  {self.target_title}"
            else:
                link_text = f"  {self._t('linked')}"
            link_color = COLORS["green"]
        else:
            link_text = self._t("not_linked")
            link_color = COLORS["red"]

        self.link_label = ctk.CTkLabel(
            link_frame, text=link_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=link_color,
        )
        self.link_label.pack(side="left", padx=(4, 0))

        # ── Input card (dark editor style with shadow) ──
        input_card_wrapper, input_card = _card(content)
        input_card_wrapper.pack(fill="both", expand=True, pady=(0, 4))
        # Override card bg to dark for the editor feel
        input_card.configure(fg_color="#1E1B2E")

        # Input header inside card (dark bg)
        input_header = ctk.CTkFrame(input_card, fg_color="transparent")
        input_header.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            input_header, text=self._t("input"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color="#B189F9",
        ).pack(side="left")

        ctk.CTkLabel(
            input_header,
            text=self._t("shortcuts_header"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color="#C0B8D0",
        ).pack(side="right")

        # Input text area (dark background, white text)
        self.input_text = ctk.CTkTextbox(
            input_card, height=200,
            font=ctk.CTkFont(family=FONT_MONO, size=13),
            fg_color="#252237", text_color="#E8E4F0",
            border_color="#3A3550", border_width=1,
            corner_radius=8, wrap="word",
            scrollbar_button_color="#3A3550",
            scrollbar_button_hover_color="#B189F9",
            insertborderwidth=0,
        )
        self.input_text.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # Attachments area
        self.attach_frame = ctk.CTkFrame(content, fg_color="transparent", height=0)
        self.attach_frame.pack(fill="x", pady=(0, 2))
        self.attach_frame.pack_propagate(False)
        self._attachment_labels: list[ctk.CTkFrame] = []

        # ── Action buttons (web-app style) ──
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(4, 6))

        # Primary CTA - Send (glossy gradient-like purple)
        self.send_btn = ctk.CTkButton(
            btn_frame, text=self._t("send_btn"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#9A6FE8", hover_color="#B189F9",
            text_color="#FFFFFF", height=42, corner_radius=21,
            command=self._on_send,
        )
        self.send_btn.pack(side="left", padx=(0, 10))

        # Secondary buttons - ghost/outline style
        for label, width, cmd in [
            (self._t("history_btn"), 80, self._on_history),
            (self._t("template_btn"), 80, self._on_template),
            (self._t("file_btn"), 70, self._on_attach_file),
        ]:
            ctk.CTkButton(
                btn_frame, text=label, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                fg_color="transparent", hover_color=COLORS["bg_light"],
                text_color=COLORS["accent"], width=width, height=42,
                corner_radius=21, border_color=COLORS["accent"], border_width=1,
                command=cmd,
            ).pack(side="left", padx=(0, 6))

        # Danger/tertiary - Clear (subtle, no border)
        ctk.CTkButton(
            btn_frame, text=self._t("clear_btn"), font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent", hover_color="#F5E0E5",
            text_color=COLORS["red"], width=70, height=42,
            corner_radius=21,
            command=self._on_clear,
        ).pack(side="right")

        # ── References card (with shadow) ──
        kb_wrapper, kb_card = _card(content)
        kb_wrapper.pack(fill="x", pady=(0, 4), ipady=0)

        kb_header = ctk.CTkFrame(kb_card, fg_color="transparent")
        kb_header.pack(fill="x", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            kb_header, text=self._t("knowledge_base"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS["orange"],
        ).pack(side="left")

        self.kb_count_label = ctk.CTkLabel(
            kb_header, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLORS["fg_dim"],
        )
        self.kb_count_label.pack(side="left", padx=(6, 0))

        self.kb_clear_btn = ctk.CTkButton(
            kb_header, text=self._t("kb_clear"), font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            fg_color="transparent", hover_color="#F5E0E5",
            text_color=COLORS["red"], width=55, height=26,
            corner_radius=13, command=self._on_clear_kb,
        )

        kb_file_btn = ctk.CTkButton(
            kb_header, text=self._t("select_file"), font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            fg_color="transparent", hover_color=COLORS["bg_light"],
            text_color=COLORS["orange"], width=80, height=26,
            corner_radius=13, border_color=COLORS["orange"], border_width=1,
            command=self._on_select_kb_file,
        )
        kb_file_btn.pack(side="right", padx=(4, 0))

        kb_folder_btn = ctk.CTkButton(
            kb_header, text=self._t("select_folder"), font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            fg_color="transparent", hover_color=COLORS["bg_light"],
            text_color=COLORS["orange"], width=90, height=26,
            corner_radius=13, border_color=COLORS["orange"], border_width=1,
            command=self._on_select_kb_folder,
        )
        kb_folder_btn.pack(side="right")

        # KB items (chip list)
        self.kb_items_frame = ctk.CTkFrame(kb_card, fg_color="transparent")
        self.kb_items_frame.pack(fill="x", padx=12, pady=(2, 8))
        self._kb_chip_widgets: list[ctk.CTkFrame] = []

        # Migrate old single-path config to list
        old_kb = self.config.get("knowledge_base")
        if isinstance(old_kb, str):
            self.config["knowledge_base"] = [old_kb] if old_kb else []
            _save_config(self.config)
        elif not isinstance(old_kb, list):
            self.config["knowledge_base"] = []

        # Placeholder label (shown when no KB items)
        self.kb_label = ctk.CTkLabel(
            self.kb_items_frame, text=self._t("not_configured"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLORS["fg_dim"], anchor="w",
        )

        self._refresh_kb_chips()

        # ── Mode options ──
        mode_frame = ctk.CTkFrame(content, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(6, 0))

        self.auto_send_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            mode_frame, text=self._t("auto_paste"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLORS["fg_dim"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            border_color=COLORS["border"], checkmark_color="#FFFFFF",
            variable=self.auto_send_var,
        ).pack(side="left")

        self.newline_label = ctk.CTkLabel(
            mode_frame, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLORS["fg_dim"],
        )
        self.newline_label.pack(side="right")
        self._update_line_count()

        # ── Bottom status bar (subtle) ──
        status_bar = ctk.CTkFrame(self, fg_color="#E8E4F0", height=28, corner_radius=0)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        ctk.CTkLabel(
            status_bar,
            text=self._t("status_bar"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color="#8A839A", anchor="w",
        ).pack(side="left", padx=10)

    # ── Key bindings ───────────────────────────────────────────────────

    def _bind_shortcuts(self):
        self.input_text.bind("<Control-Return>", lambda e: self._on_send())
        self.input_text.bind("<Control-h>", lambda e: self._on_history())
        self.input_text.bind("<Control-l>", lambda e: self._on_clear())
        self.input_text.bind("<Control-t>", lambda e: self._on_template())
        self.input_text.bind("<Control-a>", self._select_all)
        self.input_text.bind("<KeyRelease>", lambda e: self._update_line_count())
        self.input_text.bind("<Control-v>", self._on_paste)

        # Drag & drop: tkdnd if available
        try:
            self.tk.eval("package require tkdnd")
            self._setup_dnd()
        except tk.TclError:
            pass

    def _select_all(self, event=None):
        self.input_text.tag_add("sel", "1.0", "end-1c")
        return "break"

    def _cleanup_paste_files(self):
        """Remove temporary _paste_*.png files from data dir."""
        for f in _data_dir().glob("_paste_*.png"):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass

    def _on_paste(self, event=None):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                self._cleanup_paste_files()
                self._add_pasted_image(img)
                return "break"
        except Exception:
            pass
        return None

    def _setup_dnd(self):
        try:
            self.tk.eval(f"tkdnd::drop_target register {self.input_text._textbox} *")
            self.input_text._textbox.bind("<<Drop>>", self._on_drop_tkdnd)
        except Exception:
            pass

    def _on_drop_tkdnd(self, event=None):
        """Handle tkdnd drops — attach files."""
        if not (event and event.data):
            return
        raw = event.data.strip()
        if raw.startswith("{"):
            files = [raw.strip("{}")]
        else:
            files = raw.split()
        for f in files:
            p = Path(f)
            if p.exists():
                self.attached_files.append(p)
        self._refresh_attachments()

    # ── Actions ────────────────────────────────────────────────────────

    def _on_send(self):
        text = self.input_text.get("1.0", "end-1c").strip()
        if not text:
            self._flash_status(self._t("input_empty"), "#FFD700")
            return

        full_prompt = self._build_prompt(text)

        # Save to history
        if text in self.history:
            self.history.remove(text)
        self.history.insert(0, text)
        _save_history(self.history)

        can_send = self.auto_send_var.get() and (self.console_pid or self.target_hwnd)
        if can_send:
            self._flash_status(self._t("sending"), "#FFFFFF")

            def do_paste():
                ok = _paste_to_console(self.console_pid, full_prompt, self.target_hwnd)
                self.after(0, lambda: self._after_send(ok))

            threading.Thread(target=do_paste, daemon=True).start()
        else:
            _set_clipboard(full_prompt)
            if not self.console_pid and not self.target_hwnd:
                self._flash_status(self._t("no_terminal"), "#FFD700")
            else:
                self._flash_status(self._t("copied"), "#90EE90")

        # Clear input
        self.input_text.delete("1.0", "end")
        self.attached_files.clear()
        self.pasted_images.clear()
        self._refresh_attachments()
        self._update_line_count()

    def _after_send(self, success: bool):
        if success:
            self._flash_status(self._t("sent"), "#90EE90")
            self.after(500, self._refocus)
        else:
            self._flash_status(self._t("no_terminal"), "#FFD700")
            self.link_label.configure(
                text=self._t("disconnected"),
                text_color=COLORS["red"],
            )

    def _refocus(self):
        self.lift()
        self.focus_force()
        self.input_text.focus_set()

    def _build_prompt(self, text: str) -> str:
        # Reference paths (参照情報) — these get the hint text
        kb_refs = []
        kb_paths = self.config.get("knowledge_base", [])
        if isinstance(kb_paths, str):
            kb_paths = [kb_paths] if kb_paths else []
        for kb in kb_paths:
            p = Path(kb)
            if p.exists():
                kb_refs.append(f"@{kb}")

        # Attached files and pasted images — no hint text needed
        file_refs = []
        for f in self.attached_files:
            file_refs.append(f"@{f}")
        for i, img in enumerate(self.pasted_images):
            tmp_path = _data_dir() / f"_paste_{i}.png"
            img.save(str(tmp_path))
            file_refs.append(f"@{tmp_path}")

        if not kb_refs and not file_refs:
            return text

        parts = [text]

        # Hint text only for 参照情報
        if kb_refs:
            if self.lang == "ja":
                ref_hint = "以下の資料を熟読した上で指示を遂行せよ: "
            else:
                ref_hint = "Read the following material thoroughly, then carry out the instructions: "
            parts.append(ref_hint + " ".join(kb_refs))

        # Attached files / images — just append @paths
        if file_refs:
            parts.append(" ".join(file_refs))

        return " // ".join(parts)

    def _on_clear(self):
        self.input_text.delete("1.0", "end")
        self.attached_files.clear()
        self.pasted_images.clear()
        self._refresh_attachments()
        self._update_line_count()
        self.input_text.focus_set()

    # ── Templates ──────────────────────────────────────────────────────

    def _on_template(self):
        if self.template_window and self.template_window.winfo_exists():
            self.template_window.lift()
            return

        self.template_window = ctk.CTkToplevel(self)
        self.template_window.title(self._t("template_title"))
        self.template_window.geometry("620x500")
        self.template_window.configure(fg_color=COLORS["bg_dark"])
        self.template_window.transient(self)

        # -- New template button --
        ctk.CTkButton(
            self.template_window, text=self._t("template_new"),
            height=34, width=200,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF", corner_radius=8,
            command=self._tmpl_new,
        ).pack(padx=8, pady=(8, 4))

        # -- Template list --
        self._tmpl_scroll = ctk.CTkScrollableFrame(
            self.template_window, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["bg_light"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        self._tmpl_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._tmpl_build_list()

    def _tmpl_new(self):
        """Open dialog to create a new template with name and content."""
        dialog = ctk.CTkToplevel(self.template_window or self)
        dialog.title(self._t("template_new"))
        dialog.geometry("500x480")
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.transient(self.template_window or self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=self._t("template_name_label"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=COLORS["fg"],
        ).pack(padx=16, pady=(16, 4), anchor="w")

        name_entry = ctk.CTkEntry(
            dialog, placeholder_text=self._t("template_name_placeholder"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_mid"], border_color=COLORS["border"],
            text_color=COLORS["fg"],
        )
        name_entry.pack(fill="x", padx=16, pady=(0, 8))
        name_entry.focus_set()

        ctk.CTkLabel(
            dialog, text=self._t("template_content_label"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=COLORS["fg"],
        ).pack(padx=16, pady=(0, 4), anchor="w")

        content_text = ctk.CTkTextbox(
            dialog, font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_mid"], border_color=COLORS["border"],
            text_color=COLORS["fg"], border_width=1, corner_radius=6,
        )
        content_text.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        def do_save():
            name = name_entry.get().strip()
            content = content_text.get("1.0", "end-1c").strip()
            if not name:
                self._flash_status(self._t("template_name_empty"), "#FFD700")
                return
            if not content:
                self._flash_status(self._t("template_content_empty"), "#FFD700")
                return
            self.templates = [t for t in self.templates if t.get("name") != name]
            self.templates.insert(0, {"name": name, "content": content})
            _save_templates(self.templates)
            self._flash_status(self._t("template_saved"), "#90EE90")
            dialog.destroy()
            self._tmpl_build_list()

        ctk.CTkButton(
            dialog, text=self._t("template_save"), height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF", corner_radius=8,
            command=do_save,
        ).pack(fill="x", padx=16, pady=(0, 16))

    def _tmpl_build_list(self):
        """Build (or rebuild) the template item list."""
        for w in self._tmpl_scroll.winfo_children():
            w.destroy()

        if not self.templates:
            ctk.CTkLabel(
                self._tmpl_scroll, text=self._t("template_no_items"),
                text_color=COLORS["fg_dim"], font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            ).pack(pady=20)
            return

        for tmpl in self.templates:
            name = tmpl.get("name", "")
            content = tmpl.get("content", "")
            preview = content.replace("\n", " | ")
            if len(preview) > 80:
                preview = preview[:77] + "..."

            item_frame = ctk.CTkFrame(
                self._tmpl_scroll, fg_color=COLORS["bg_mid"], corner_radius=6,
            )
            item_frame.pack(fill="x", pady=2)

            # Name label (bold)
            ctk.CTkLabel(
                item_frame, text=f"  {name}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                text_color=COLORS["accent"], anchor="w",
            ).pack(fill="x", padx=6, pady=(6, 0))

            # Preview label
            ctk.CTkLabel(
                item_frame, text=f"  {preview}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLORS["fg_dim"], anchor="w",
            ).pack(fill="x", padx=6, pady=(0, 2))

            # Button row
            btn_row = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_row.pack(fill="x", padx=6, pady=(0, 6))

            ctk.CTkButton(
                btn_row, text=self._t("use_btn"), width=50, height=26,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color="#FFFFFF", corner_radius=4,
                command=lambda c=content: self._tmpl_use(c),
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                btn_row, text=self._t("template_edit"), width=50, height=26,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color="transparent", hover_color=COLORS["bg_light"],
                text_color=COLORS["accent"], corner_radius=4,
                border_color=COLORS["accent"], border_width=1,
                command=lambda n=name, c=content: self._tmpl_edit(n, c),
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                btn_row, text="\u2715", width=30, height=26,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color="transparent", hover_color="#F5E0E5",
                text_color=COLORS["red"], corner_radius=4,
                command=lambda n=name: self._tmpl_delete(n),
            ).pack(side="right")

    def _tmpl_use(self, content: str):
        """Insert template content into the input area."""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", content)
        self._update_line_count()
        if self.template_window and self.template_window.winfo_exists():
            self.template_window.destroy()
        self.input_text.focus_set()

    def _tmpl_delete(self, name: str):
        """Delete a template by name."""
        self.templates = [t for t in self.templates if t.get("name") != name]
        _save_templates(self.templates)
        self._tmpl_build_list()

    def _tmpl_edit(self, old_name: str, old_content: str):
        """Open an edit dialog for a template."""
        dialog = ctk.CTkToplevel(self.template_window or self)
        dialog.title(self._t("template_edit_title"))
        dialog.geometry("560x420")
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.transient(self.template_window or self)
        dialog.grab_set()

        # Name field
        name_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        name_frame.pack(fill="x", padx=12, pady=(12, 4))

        ctk.CTkLabel(
            name_frame, text=self._t("template_name_label"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=(0, 8))

        name_entry = ctk.CTkEntry(
            name_frame,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLORS["bg_mid"], text_color=COLORS["fg"],
            border_color=COLORS["border"], height=32, corner_radius=6,
        )
        name_entry.pack(side="left", fill="x", expand=True)
        name_entry.insert(0, old_name)

        # Content label
        ctk.CTkLabel(
            dialog, text=self._t("template_content_label"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLORS["accent"], anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 2))

        # Content editor
        content_box = ctk.CTkTextbox(
            dialog, height=250,
            font=ctk.CTkFont(family=FONT_MONO, size=13),
            fg_color="#252237", text_color="#E8E4F0",
            border_color="#3A3550", border_width=1,
            corner_radius=8, wrap="word",
        )
        content_box.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        content_box.insert("1.0", old_content)

        # Update button
        def _do_update():
            new_name = name_entry.get().strip()
            new_content = content_box.get("1.0", "end-1c").strip()
            if not new_name:
                self._flash_status(self._t("template_name_empty"), "#FFD700")
                return
            if not new_content:
                self._flash_status(self._t("template_content_empty"), "#FFD700")
                return

            # Update in-place: find old template by old_name, replace it
            for i, t in enumerate(self.templates):
                if t.get("name") == old_name:
                    self.templates[i] = {"name": new_name, "content": new_content}
                    break
            else:
                # Not found (shouldn't happen) — prepend
                self.templates.insert(0, {"name": new_name, "content": new_content})

            _save_templates(self.templates)
            self._flash_status(self._t("template_updated"), "#90EE90")
            dialog.destroy()
            self._tmpl_build_list()

        ctk.CTkButton(
            dialog, text=self._t("template_update"), height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#FFFFFF", corner_radius=18,
            command=_do_update,
        ).pack(fill="x", padx=12, pady=(0, 12))

    def _on_history(self):
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.lift()
            return

        self.history_window = ctk.CTkToplevel(self)
        self.history_window.title(self._t("history_title"))
        self.history_window.geometry("620x450")
        self.history_window.configure(fg_color=COLORS["bg_dark"])
        self.history_window.transient(self)

        # -- Top toolbar: Select All checkbox + Delete Selected button --
        toolbar = ctk.CTkFrame(self.history_window, fg_color=COLORS["bg_dark"], height=36)
        toolbar.pack(fill="x", padx=8, pady=(8, 0))

        self._hist_select_all_var = ctk.BooleanVar(value=False)
        self._hist_checkboxes: list[tuple[ctk.BooleanVar, str]] = []

        ctk.CTkCheckBox(
            toolbar, text=self._t("select_all"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLORS["fg"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            border_color=COLORS["border"], checkmark_color="#FFFFFF",
            variable=self._hist_select_all_var,
            command=self._hist_toggle_all,
        ).pack(side="left", padx=(4, 12))

        ctk.CTkButton(
            toolbar, text=self._t("delete_selected"), width=120, height=28,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color=COLORS["red"], hover_color="#ff9e9e",
            text_color="#FFFFFF", corner_radius=6,
            command=self._hist_delete_selected,
        ).pack(side="right", padx=4)

        # -- Scrollable list --
        scroll_frame = ctk.CTkScrollableFrame(
            self.history_window, fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["bg_light"],
            scrollbar_button_hover_color=COLORS["accent"],
        )
        scroll_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self._hist_scroll_frame = scroll_frame

        if not self.history:
            ctk.CTkLabel(
                scroll_frame, text=self._t("no_history"),
                text_color=COLORS["fg_dim"], font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            ).pack(pady=20)
            return

        self._hist_build_list()

    def _hist_build_list(self):
        """Build (or rebuild) the history item list."""
        for w in self._hist_scroll_frame.winfo_children():
            w.destroy()
        self._hist_checkboxes.clear()
        self._hist_select_all_var.set(False)

        if not self.history:
            ctk.CTkLabel(
                self._hist_scroll_frame, text=self._t("no_history"),
                text_color=COLORS["fg_dim"], font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            ).pack(pady=20)
            return

        for i, entry in enumerate(self.history[:30]):
            preview = entry.replace("\n", " | ")
            if len(preview) > 90:
                preview = preview[:87] + "..."

            item_frame = ctk.CTkFrame(
                self._hist_scroll_frame, fg_color=COLORS["bg_mid"], corner_radius=6,
            )
            item_frame.pack(fill="x", pady=2)

            var = ctk.BooleanVar(value=False)
            self._hist_checkboxes.append((var, entry))

            ctk.CTkCheckBox(
                item_frame, text="", width=24,
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                border_color=COLORS["border"], checkmark_color="#FFFFFF",
                variable=var,
            ).pack(side="left", padx=(6, 0), pady=4)

            ctk.CTkLabel(
                item_frame, text=f"{i + 1}. {preview}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLORS["fg"],
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=6, pady=6)

            ctk.CTkButton(
                item_frame, text=self._t("use_btn"), width=50, height=26,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                text_color="#FFFFFF", corner_radius=4,
                command=lambda e=entry: self._use_history(e),
            ).pack(side="right", padx=(0, 6), pady=4)

            ctk.CTkButton(
                item_frame, text=self._t("template_save_short"), width=60, height=26,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                fg_color="#5B9BD5", hover_color="#4A8AC4",
                text_color="#FFFFFF", corner_radius=4,
                command=lambda e=entry: self._save_history_as_template(e),
            ).pack(side="right", padx=(0, 4), pady=4)

    def _hist_toggle_all(self):
        val = self._hist_select_all_var.get()
        for var, _ in self._hist_checkboxes:
            var.set(val)

    def _hist_delete_selected(self):
        to_delete = {entry for var, entry in self._hist_checkboxes if var.get()}
        if not to_delete:
            return
        self.history = [h for h in self.history if h not in to_delete]
        _save_history(self.history)
        self._hist_build_list()

    def _save_history_as_template(self, text: str):
        """Open a small dialog to name and save a history entry as template."""
        dialog = ctk.CTkToplevel(self.history_window or self)
        dialog.title(self._t("template_save"))
        dialog.geometry("400x150")
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.transient(self.history_window or self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=self._t("template_name_label"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLORS["fg"],
        ).pack(padx=16, pady=(16, 4), anchor="w")

        name_entry = ctk.CTkEntry(
            dialog, placeholder_text=self._t("template_name_placeholder"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=COLORS["bg_mid"], border_color=COLORS["border"],
            text_color=COLORS["fg"],
        )
        name_entry.pack(fill="x", padx=16, pady=(0, 12))
        name_entry.focus_set()

        def do_save():
            name = name_entry.get().strip()
            if not name:
                self._flash_status(self._t("template_name_empty"), "#FFD700")
                return
            self.templates.insert(0, {"name": name, "content": text})
            _save_templates(self.templates)
            self._flash_status(self._t("template_saved"), "#90EE90")
            dialog.destroy()

        ctk.CTkButton(
            dialog, text=self._t("template_save"), height=34,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#5B9BD5", hover_color="#4A8AC4",
            text_color="#FFFFFF", corner_radius=8,
            command=do_save,
        ).pack(fill="x", padx=16)

        name_entry.bind("<Return>", lambda e: do_save())

    def _use_history(self, text: str):
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", text)
        self._update_line_count()
        if self.history_window and self.history_window.winfo_exists():
            self.history_window.destroy()
        self.input_text.focus_set()

    def _on_attach_file(self):
        files = filedialog.askopenfilenames(
            title=self._t("attach_files_title"),
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Text", "*.txt *.md *.py *.js *.ts *.json *.yaml *.yml"),
            ],
        )
        for f in files:
            self.attached_files.append(Path(f))
        self._refresh_attachments()

    def _add_pasted_image(self, img: Image.Image):
        self.pasted_images.append(img)
        self._refresh_attachments()
        self._flash_status(self._t("image_pasted"), "#90EE90")

    def _refresh_attachments(self):
        for w in self._attachment_labels:
            w.destroy()
        self._attachment_labels.clear()

        items = []
        for f in self.attached_files:
            items.append(("file", f.name, f))
        for i, _ in enumerate(self.pasted_images):
            items.append(("image", f"Pasted image {i + 1}", i))

        if not items:
            self.attach_frame.configure(height=0)
            return

        self.attach_frame.configure(height=32)
        for kind, name, ref in items:
            chip = ctk.CTkFrame(self.attach_frame, fg_color=COLORS["bg_light"], corner_radius=12, height=26)
            chip.pack(side="left", padx=(0, 4), pady=3)

            icon = "img" if kind == "image" else "file"
            ctk.CTkLabel(chip, text=f" {icon}: {name} ", font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLORS["fg"]).pack(side="left", padx=(6, 0))

            def _remove(k=kind, r=ref):
                if k == "file":
                    self.attached_files.remove(r)
                else:
                    self.pasted_images.pop(r)
                self._refresh_attachments()

            ctk.CTkButton(
                chip, text="x", width=20, height=20, font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                fg_color="transparent", hover_color=COLORS["red"],
                text_color=COLORS["fg_dim"], corner_radius=10, command=_remove,
            ).pack(side="right", padx=(0, 2))
            self._attachment_labels.append(chip)

    def _on_select_kb_folder(self):
        folder = filedialog.askdirectory(title=self._t("select_kb_title"))
        if folder:
            kb_list = self.config.get("knowledge_base", [])
            if folder not in kb_list:
                kb_list.append(folder)
                self.config["knowledge_base"] = kb_list
                _save_config(self.config)
            self._refresh_kb_chips()
            self._flash_status(self._t("kb_set"), "#90EE90")

    def _on_select_kb_file(self):
        files = filedialog.askopenfilenames(title=self._t("select_kb_file_title"))
        if files:
            kb_list = self.config.get("knowledge_base", [])
            for f in files:
                if f not in kb_list:
                    kb_list.append(f)
            self.config["knowledge_base"] = kb_list
            _save_config(self.config)
            self._refresh_kb_chips()
            self._flash_status(self._t("kb_set"), "#90EE90")

    def _on_clear_kb(self):
        self.config["knowledge_base"] = []
        _save_config(self.config)
        self._refresh_kb_chips()
        self._flash_status(self._t("kb_cleared"), "#90EE90")

    def _remove_kb_item(self, path: str):
        kb_list = self.config.get("knowledge_base", [])
        if path in kb_list:
            kb_list.remove(path)
            self.config["knowledge_base"] = kb_list
            _save_config(self.config)
        self._refresh_kb_chips()

    def _refresh_kb_chips(self):
        """Rebuild KB chip list in the UI."""
        for w in self._kb_chip_widgets:
            w.destroy()
        self._kb_chip_widgets.clear()

        kb_list = self.config.get("knowledge_base", [])

        # Update count label and clear button visibility
        if kb_list:
            self.kb_count_label.configure(text=f"({len(kb_list)} {self._t('kb_count')})")
            self.kb_clear_btn.pack(side="right", padx=(4, 0))
            self.kb_label.pack_forget()
        else:
            self.kb_count_label.configure(text="")
            self.kb_clear_btn.pack_forget()
            self.kb_label.pack(fill="x")
            return

        for path_str in kb_list:
            p = Path(path_str)
            is_dir = p.is_dir()
            display = p.name if not is_dir else f"{p.name}/"
            icon = "\U0001F4C1" if is_dir else "\U0001F4C4"  # folder / file emoji

            chip = ctk.CTkFrame(
                self.kb_items_frame, fg_color=COLORS["bg_light"],
                corner_radius=8,
            )
            chip.pack(fill="x", pady=(2, 0))

            ctk.CTkLabel(
                chip, text=f" {icon} {display}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLORS["fg"], anchor="w",
            ).pack(side="left", padx=(6, 0), fill="x", expand=True)

            # Tooltip-like: show full path on label
            ctk.CTkLabel(
                chip, text=path_str,
                font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                text_color=COLORS["fg_dim"], anchor="w",
            ).pack(side="left", padx=(4, 0))

            _p = path_str  # capture for lambda
            ctk.CTkButton(
                chip, text="\u2715", width=22, height=22,
                font=ctk.CTkFont(size=11), fg_color="transparent",
                hover_color="#F5E0E5", text_color=COLORS["red"],
                corner_radius=11,
                command=lambda pp=_p: self._remove_kb_item(pp),
            ).pack(side="right", padx=(0, 4), pady=2)

            self._kb_chip_widgets.append(chip)

    # ── Helpers ────────────────────────────────────────────────────────

    def _t(self, key: str) -> str:
        return I18N.get(self.lang, I18N["en"]).get(key, key)

    def _update_line_count(self):
        text = self.input_text.get("1.0", "end-1c")
        lines = text.count("\n") + 1
        chars = len(text)
        self.newline_label.configure(
            text=f"{self._t('lines')}: {lines}  {self._t('chars')}: {chars}"
        )

    def _flash_status(self, msg: str, color: str = "#E8DDFF"):
        self.status_label.configure(text=msg, text_color=color)
        self.after(3000, lambda: self.status_label.configure(
            text=self._t("ready"), text_color="#E8DDFF",
        ))


    def _make_help_section(self, parent, sec, color):
        """Build a single help section (header + items) directly into parent."""
        # Section header: badge + title + desc on one line
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(12, 2))

        ctk.CTkLabel(
            header, text=f" {sec['icon']} ", width=30, height=24,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color="#FFFFFF", fg_color=color, corner_radius=6,
        ).pack(side="left", padx=(0, 8))

        title_text = sec["title"]
        if sec["desc"]:
            title_text += f"    {sec['desc']}"
        ctk.CTkLabel(
            header, text=title_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLORS["fg"], anchor="w",
        ).pack(side="left")

        # Items — formatted as aligned table using tk.Text for performance
        # Find max key width for alignment
        max_key_len = max((len(k) for k, _ in sec["items"]), default=0)

        lines = []
        for key, val in sec["items"]:
            padded_key = key.ljust(max_key_len)
            lines.append(f"  {padded_key}    {val}")
        items_text = "\n".join(lines)

        ctk.CTkLabel(
            parent, text=items_text,
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            text_color=COLORS["fg"], anchor="nw", justify="left",
        ).pack(fill="x", padx=(40, 4), pady=(2, 0))

        # Divider line
        ctk.CTkFrame(
            parent, fg_color=COLORS["border"], height=1,
        ).pack(fill="x", padx=8, pady=(10, 0))

    def _on_help(self):
        """Show a visually rich help dialog with 2-column card layout."""
        W = 780
        H = 700
        dialog = ctk.CTkToplevel(self)
        dialog.title(self._t("help_title"))
        dialog.geometry(f"{W}x{H}")
        dialog.minsize(640, 520)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=COLORS["bg_dark"])

        # ── Header bar ──
        header = ctk.CTkFrame(dialog, fg_color="#9A6FE8", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkFrame(header, fg_color="#C4A4FF", height=2, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(
            header, text=self._t("help_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=17, weight="bold"),
            text_color="#FFFFFF", anchor="w",
        ).pack(fill="x", padx=24, pady=(10, 0))
        ctk.CTkLabel(
            header, text=self._t("help_subtitle"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color="#FFFFFF", anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 10))

        # ── Scrollable single-column content ──
        scroll = ctk.CTkScrollableFrame(
            dialog, fg_color="#FFFFFF", corner_radius=10,
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color="#B189F9",
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=(12, 0))

        icon_colors = {
            "1": "#B189F9",
            "2": "#7CB3F7",
            "3": "#4CAF7C",
            "KB": "#E0873E",
            "T": "#5B9BD5",
            "⚙": "#8E8E93",
            "!": "#D4943A",
        }

        sections = self._t("help_sections")
        for sec in sections:
            color = icon_colors.get(sec["icon"], "#B189F9")
            self._make_help_section(scroll, sec, color)

        # ── Close button ──
        btn_frame = ctk.CTkFrame(dialog, fg_color=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=20, pady=(4, 14))
        ctk.CTkButton(
            btn_frame, text=self._t("help_close"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#9A6FE8", hover_color="#B189F9",
            text_color="#FFFFFF", height=38, corner_radius=19,
            command=dialog.destroy,
        ).pack(fill="x")

        # Center on screen
        dialog.update_idletasks()
        sx = dialog.winfo_screenwidth()
        sy = dialog.winfo_screenheight()
        x = (sx - W) // 2
        y = max(0, (sy - H) // 2 - 20)
        dialog.geometry(f"+{max(0, x)}+{y}")

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "ja" else "ja"
        self.config["lang"] = self.lang
        _save_config(self.config)
        # Rebuild entire UI with new language
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()
        self._bind_shortcuts()
        self.input_text.focus_set()


# ---------------------------------------------------------------------------
# Terminal window discovery (for skill mode / ConPTY environments)
# ---------------------------------------------------------------------------
def _find_terminal_window() -> int:
    """Find the terminal window by scanning all visible windows.

    In ConPTY environments (Windows Terminal), the terminal window is owned by
    WindowsTerminal.exe, which is NOT in the parent process chain.
    Instead, we enumerate all visible windows and score them by likelihood
    of being the terminal hosting Claude Code.
    """
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    def get_process_name(pid: int) -> str:
        try:
            h = kernel32.OpenProcess(0x1000, False, pid)
            if h:
                buf = ctypes.create_unicode_buffer(260)
                size = ctypes.c_ulong(260)
                kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size))
                kernel32.CloseHandle(h)
                return buf.value
        except Exception:
            pass
        return ""

    # Enumerate all visible windows and score them
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int))
    candidates = []  # list of (hwnd, title, process_name, score)

    def enum_callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        title = _get_window_title(hwnd)
        if not title:
            return True

        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        pname = get_process_name(pid.value)
        pname_lower = pname.lower()
        title_lower = title.lower()

        score = 0

        # Process name scoring — terminal host processes
        if "windowsterminal" in pname_lower:
            score += 50
        elif "cmd.exe" in pname_lower and title:
            score += 30
        elif "powershell" in pname_lower or "pwsh" in pname_lower:
            score += 30
        elif "mintty" in pname_lower or "conemu" in pname_lower:
            score += 30
        elif "wezterm" in pname_lower or "alacritty" in pname_lower:
            score += 30

        # Title keyword scoring
        if "claude" in title_lower:
            score += 40
        if any(kw in title_lower for kw in ["terminal", "powershell", "cmd",
                                              "bash", "command prompt"]):
            score += 20

        if score > 0:
            candidates.append((hwnd, title, pname, score))

        return True

    cb = WNDENUMPROC(enum_callback)
    user32.EnumWindows(cb, 0)

    # Sort by score descending
    candidates.sort(key=lambda x: -x[3])

    for hwnd, title, pname, score in candidates:
        _debug_log(f"  candidate: hwnd={hwnd}, title={title!r}, "
                    f"proc={Path(pname).name!r}, score={score}")

    if candidates:
        best = candidates[0]
        _debug_log(f"  SELECTED: hwnd={best[0]}, title={best[1]!r}, score={best[3]}")
        return best[0]

    _debug_log("  _find_terminal_window: no terminal window found")
    return 0


# ---------------------------------------------------------------------------
# Launcher logic: detach from terminal and pass HWND
# ---------------------------------------------------------------------------
def _get_console_pids() -> list[int]:
    """Get the list of process IDs attached to the current console.
    This includes cmd.exe, powershell, python, etc."""
    kernel32 = ctypes.windll.kernel32
    # First call to get count
    buf = (ctypes.c_ulong * 64)()
    count = kernel32.GetConsoleProcessList(buf, 64)
    if count == 0:
        return []
    if count > 64:
        buf = (ctypes.c_ulong * count)()
        count = kernel32.GetConsoleProcessList(buf, count)
    return [buf[i] for i in range(count)]


def _find_shell_pid(pids: list[int]) -> int:
    """From a list of console PIDs, find the shell (cmd.exe / powershell)."""
    import os

    our_pid = os.getpid()
    # Try to identify shell process by name
    # Use tasklist to get process names for the PIDs
    shell_names = {"cmd.exe", "powershell.exe", "pwsh.exe", "bash.exe"}

    for pid in pids:
        if pid == our_pid:
            continue
        try:
            # Use ctypes to get process name
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if handle:
                try:
                    buf = ctypes.create_unicode_buffer(260)
                    size = ctypes.c_ulong(260)
                    ctypes.windll.kernel32.QueryFullProcessImageNameW(
                        handle, 0, buf, ctypes.byref(size)
                    )
                    name = Path(buf.value).name.lower()
                    if name in shell_names:
                        return pid
                finally:
                    ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            continue

    # Fallback: return the first PID that isn't us
    for pid in pids:
        if pid != our_pid:
            return pid
    return 0


def _launch_gui(hwnd: int, console_pid: int):
    """Relaunch this script as a GUI process with the target HWND and console PID.

    Uses CREATE_NO_WINDOW so no console window appears at all.
    The console_pid is the actual cmd.exe/shell PID (not the window manager PID).
    """
    CREATE_NO_WINDOW = 0x08000000

    script = str(Path(__file__).resolve())
    cmd = [
        sys.executable, script,
        "--gui", "--hwnd", str(hwnd), "--pid", str(console_pid),
    ]

    subprocess.Popen(
        cmd,
        creationflags=CREATE_NO_WINDOW,
    )


def _parse_int_arg(name: str) -> int:
    """Parse an integer argument like --hwnd 12345 from sys.argv."""
    if name in sys.argv:
        idx = sys.argv.index(name)
        if idx + 1 < len(sys.argv):
            try:
                return int(sys.argv[idx + 1])
            except ValueError:
                pass
    return 0


def main():
    # --gui mode: we are the GUI process (launched with CREATE_NO_WINDOW)
    if "--gui" in sys.argv:
        hwnd = _parse_int_arg("--hwnd")
        console_pid = _parse_int_arg("--pid")

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        app = ClaudeInputApp(target_hwnd=hwnd, console_pid=console_pid)
        app.mainloop()
        app._cleanup_paste_files()
        return

    # --skill mode: launched from Claude Code skill (detached, non-blocking)
    if "--skill" in sys.argv:
        _debug_log("=== SKILL MODE START ===")
        print("[claude-assist] Detecting terminal window...")

        # In ConPTY (Windows Terminal), GetConsoleWindow() returns 0.
        # Walk the process tree to find the terminal window instead.
        terminal_hwnd = _find_terminal_window()
        _debug_log(f"  terminal_hwnd={terminal_hwnd}")

        if terminal_hwnd:
            title = _get_window_title(terminal_hwnd)
            print(f"[claude-assist] Terminal found: {title or '(untitled)'}")
        else:
            print("[claude-assist] WARNING: No terminal window found. GUI will run in clipboard-only mode.")

        # console_pid=0 forces clipboard paste mode (no WriteConsoleInputW)
        print("[claude-assist] Launching GUI...")
        _debug_log(f"  Launching GUI with hwnd={terminal_hwnd}, pid=0 (clipboard mode)")
        _launch_gui(terminal_hwnd, 0)
        print("[claude-assist] GUI launched successfully.")
        _debug_log("=== SKILL MODE END (GUI launched) ===")
        sys.exit(0)

    # Normal launch: capture console HWND, relaunch detached, exit
    console_hwnd = _get_console_hwnd()

    # Use safe print to avoid cp932 encoding errors with special chars in window titles
    def safe_print(s: str):
        try:
            print(s)
        except UnicodeEncodeError:
            print(s.encode("ascii", errors="replace").decode("ascii"))

    if console_hwnd:
        title = _get_window_title(console_hwnd)
        # Sanitize title for console output
        safe_title = title.encode("cp932", errors="replace").decode("cp932") if title else ""
        safe_print("")
        safe_print("  ========================================")
        safe_print("   Claude Assist GUI launched!")
        safe_print("   Linked to this terminal.")
        if safe_title:
            safe_print(f"   ({safe_title})")
        safe_print("")
        safe_print("   Run 'claude' command next.")
        safe_print("  ========================================")
        safe_print("")
    else:
        safe_print("")
        safe_print("  ========================================")
        safe_print("   Claude Assist GUI launched!")
        safe_print("   No terminal detected.")
        safe_print("")
        safe_print("   Please run this command from")
        safe_print("   the terminal you want to use.")
        safe_print("  ========================================")
        safe_print("")

    # Get the actual shell PID (cmd.exe) from the current console session
    # This is critical: GetWindowThreadProcessId returns Windows Terminal's PID,
    # but AttachConsole needs the actual cmd.exe PID.
    console_pids = _get_console_pids()
    shell_pid = _find_shell_pid(console_pids)

    _launch_gui(console_hwnd, shell_pid)
    sys.exit(0)


if __name__ == "__main__":
    main()
