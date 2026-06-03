# コスト報告パターン

## いつ使う / 使わない

- **使う**: 外部 API (Azure / AOAI / OpenAI / Anthropic 等) を呼び出すスキルで、ユーザーが従量課金を負担する場合。終了時に実コストを可視化する。
- **使わない**: ローカル処理のみ、または無料枠で完結する処理。

## cost_report.json スキーマ

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-05-10T12:34:56+00:00",
  "input": {
    "audio_seconds": 5292.0,
    "prompt_tokens": 28431,
    "completion_tokens": 3210
  },
  "rates": {
    "<service>_usd_per_<unit>": 0.36,
    "usdjpy": 155.0,
    "usdjpy_source": "cache | default",
    "usdjpy_cached_at": "2026-05-09T00:00:00+00:00",
    "last_verified_date": "2026-05-10"
  },
  "breakdown_usd": {"<line_item>": 0.123, "total": 0.456},
  "breakdown_jpy": {"<line_item>": 19, "total": 71}
}
```

`schema_version` は将来の互換性確保のため必須。`rates.*` には適用した単価をすべて記録 (再現性確保)。

## コンソール pretty-print (固定幅整形)

ユーザーが終了時に必ず目にする要件。固定幅で揃えて読みやすくする。

```
=========================================================
  Azure コスト見積り — transcribe-meeting
=========================================================
  音声尺              : 1h 28m 12s
  Fast Transcription  : $ 0.529   (¥  82)
  GPT-4o input        :  28,431 tok → $ 0.071  (¥ 11)
  GPT-4o output       :   3,210 tok → $ 0.032  (¥  5)
---------------------------------------------------------
  合計                : $ 0.632   (¥  98)
  単価レート           : 1 USD = ¥155.00 (cached 2026-05-09)
=========================================================
```

## USDJPY キャッシュ

- 場所: `~/.claude/cache/usdjpy.json` (全スキル共有)。
- スキーマ: `{"rate": 155.0, "cached_at": "ISO8601"}`。
- TTL: **30 日**。期限切れまたは破損時は既定値 (例 `155.0`) にフォールバックし、`stderr` に警告を出す。
- `usdjpy_source` を `"cache" | "default"` で記録し、ユーザーがどちらを使ったか追跡できるようにする。

## 90 日陳腐化警告

- 料金表は変動するので、スクリプト内に `LAST_VERIFIED_DATE` 定数を持つ。
- 起動時に `(today - LAST_VERIFIED_DATE).days > 90` なら警告:
  > `[compute_cost] 警告: 料金表 (2026-05-10) が 95 日経過しています. references/cost-model.md を更新してください.`
- `references/cost-model.md` に料金根拠 URL と最終確認日を必ず記載。

## 実装例

`~/.claude/skills/transcribe-meeting/scripts/compute_cost.py` を参照。要点:

- `compute_breakdown()` は純粋関数 (副作用無し、I/O 無し): テストしやすい。
- `load_usdjpy()` はキャッシュ読み込み + 期限判定を一括処理し `(rate, source, cached_at)` の tuple を返す。
- `warn_if_pricing_stale()` は単独で呼べる (CLI / orchestrator どちらからも使える)。
- `compute_and_report()` は計算 → コンソール出力 → JSON 書き出しを一括実行する高レベル wrapper。
- スモークテスト (`_smoke()`) を `__main__` に同梱、引数無しで実行すると典型値で動作確認可能。

## チェックリスト

- [ ] `cost_report.json` に `schema_version` を含む
- [ ] 適用したすべての単価を `rates` に記録
- [ ] USDJPY キャッシュは TTL 30 日
- [ ] 料金表に `last_verified_date` と参照 URL
- [ ] 90 日陳腐化で warning
- [ ] コンソール pretty-print は固定幅整形
- [ ] `compute_breakdown()` は純粋関数
