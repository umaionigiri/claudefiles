---
name: claude-assist
description: "複数行入力GUIを起動してClaudeのチャット欄に送信する入力支援ツール。長文の指示、テンプレート活用、ファイル参照付き指示の作成に便利。Use when the user wants to compose a multi-line prompt via GUI."
allowed-tools: "Bash(uv *)"
---

# Claude Assist - 複数行入力支援GUI

Claude Codeのチャット欄への入力を支援するGUIツールを起動します。

## 実行手順

1. 以下のコマンドを実行してGUIを起動する:

```bash
uv run ${CLAUDE_SKILL_DIR}/scripts/claude_assist.py --skill
```

2. コマンドの出力に `GUI launched successfully` と表示されたことを確認してから、ユーザーに「GUIを起動しました」と伝える。
3. 初回実行時は依存パッケージ（customtkinter, Pillow）のインストールに時間がかかる場合がある。コマンドの出力をそのまま表示し、完了を待つこと。

## 注意事項

- **重要**: コマンドの出力に `GUI launched successfully` が含まれるまで「起動しました」と伝えてはいけない。
- コマンドが完了するまで待機すること（初回は依存パッケージのインストールに数十秒かかる場合がある）。
- ユーザーがGUIから送信したテキストは自動的にClaudeのチャット欄に入力される。
- このコマンド実行後、追加の説明は不要。
