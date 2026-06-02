# 子スキル引き渡し (loose coupling handoff) パターン

## いつ使う / 使わない

- **使う**: あるスキルが別スキルを後段で呼び出し、構造化データを引き渡す必要がある場合 (例: `transcribe-meeting` → `word-minutes`)。スキル間で別チームが独立進化できる。
- **使わない**: 単一スキル内で完結する処理、後段が無い終端スキル。

## 設計原則

### 1. JSON + `schema_version` 必須

```json
{
  "schema_version": "1.0",
  "source_skill": "transcribe-meeting",
  ...
}
```

`schema_version` は **major.minor** のセマンティック表記。互換性を破る変更は major を上げる (1.0 → 2.0)。
受け側は `schema_version` を見て分岐できる。

### 2. 受け側は未知 schema を graceful degrade

受け側スキルが想定外の `schema_version` を受け取った場合の振る舞い:

- **やる**: 警告を出した上で、構造化データを諦めて raw markdown / transcript を平文として再解釈する。
- **やらない**: 即座に exit してユーザーをブロックする (進化を止めてしまう)。

```python
if data.get("schema_version") not in SUPPORTED_VERSIONS:
    print(f"[WARN] 未対応 schema {data.get('schema_version')}, 平文 fallback", file=sys.stderr)
    return parse_as_plain_text(data.get("summary_md_path"))
```

### 3. 送り側は構造化 JSON + raw markdown 両方を提供

送り側 (transcribe-meeting) は次の二系統を成果物として渡す:

- **構造化 JSON**: `handoff_word_minutes.json` — 意思決定/Action/参加者をフィールドで持つ。
- **Raw markdown / transcript**: パスを `transcript_path` / `summary_md_path` で参照。受け側が JSON を解釈できなくても markdown を読めば最低限の情報は得られる。

これにより**スキーマ進化と互換性の両立**ができる: 送り側が新フィールドを足しても、古い受け側は raw markdown 経由で動作可能。

## 実装例

`~/.claude/skills/transcribe-meeting/templates/handoff_word_minutes.json` を `schema_version 1.0` で `word-minutes` に渡す:

```json
{
  "schema_version": "1.0",
  "source_skill": "transcribe-meeting",
  "meeting": {"name": "...", "date": "2026-04-02", "duration_seconds": 5292},
  "attendees": [{"label": "A", "name": "山田", "org": "PMO事務局", "role": "司会"}],
  "agenda":   [{"title": "...", "start_ms": 0, "end_ms": 1234567, "summary": "..."}],
  "decisions":[{"text": "...", "owner": "A", "due": "2026-05-01", "evidence_ms": 4123000}],
  "actions":  [{"text": "...", "owner": "B", "due": "2026-05-15", "evidence_ms": 4567000}],
  "feedback": [{"text": "...", "speaker": "A", "evidence_ms": 1234000}],
  "next_meeting": {"date": "(未確認)", "agenda_hint": "..."},
  "transcript_path": "/abs/path/to/transcript_full.txt",
  "summary_md_path": "/abs/path/to/summary.md"
}
```

### フィールド設計のポイント

- **絶対パス必須**: `transcript_path` / `summary_md_path` は `/abs/path/...` 形式。受け側 cwd に依存しない。
- **`evidence_ms`**: タイムスタンプ (ミリ秒) で発話の typedef を担保 (受け側が音声ファイルへ jump back できる)。
- **`label` vs `name`**: 話者は `label: "A"` の機械 ID と `name: "山田"` の表示名を分離 (匿名化も可能)。
- **`(未確認)` リテラル**: 不明値は `null` ではなく `(未確認)` の固定文字列で送る (受け側がそのまま転記可能)。

## バージョン互換ポリシー

| 変更 | バージョン bump | 受け側影響 |
|---|---|---|
| 既存フィールドに optional field を追加 | minor (1.0 → 1.1) | 旧版でも動作 |
| 既存フィールドの型変更・削除 | major (1.0 → 2.0) | 旧版は graceful degrade |
| 新しい必須フィールド追加 | major | 同上 |

## チェックリスト

- [ ] handoff JSON に `schema_version` と `source_skill` を含む
- [ ] 構造化データと raw markdown を両系統で提供
- [ ] パスは絶対パスで送る
- [ ] 受け側は未知 schema で fallback できる
- [ ] 不明値は固定リテラル (`(未確認)`) で送る
- [ ] バージョン bump ポリシーを README に明記
