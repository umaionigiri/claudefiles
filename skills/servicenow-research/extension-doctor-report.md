# extension-doctor 監査レポート / Audit Report

対象 / Target: `/home/shokenohshiro/.claude/skills/servicenow-research`
形式 / Form: `skill`

## 検出事項 / Findings

### [P2] 🟡 警告 / WARN — Python の依存関係マニフェストが見つかりません

_(EN: Python dependency manifest not found)_

**JA**: `*.py` ファイルが 9 件見つかりましたが、`pyproject.toml` または `requirements.txt` がありません。再現性確保のため追加してください。**推奨は `uv` ＋ `pyproject.toml` ＋ `uv.lock`** です（`uv add <dep>` で 1 コマンド）。`uv` 未導入の場合は <https://docs.astral.sh/uv/> を参照、またはレガシー形式の `requirements.txt` で代替可能。

**EN**: Found 9 *.py files but no pyproject.toml or requirements.txt. Add one for reproducibility. **Preferred: `uv` + `pyproject.toml` + `uv.lock`** (one command via `uv add <dep>`). If `uv` is not installed, see <https://docs.astral.sh/uv/>, or fall back to the legacy `requirements.txt` format.

### [P9] 🔵 情報 / INFO — 非標準のレイアウトです（root の SKILL.md）

_(EN: Non-canonical layout (root SKILL.md))_

**JA**: `repackage` Skill で `skills/<slug>/SKILL.md` 形式に再構成できます。Claude Hub アップロード時に同じ処理が行われます。

**EN**: `repackage` skill will move it to `skills/<slug>/SKILL.md`. Claude Hub does the same on upload.

