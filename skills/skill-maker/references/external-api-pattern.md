# 外部 API スキル設計パターン

## いつ使う / 使わない

- **使う**: スキルが外部 API (Azure / OpenAI / GitHub / Slack 等) を呼び出し、認証、リトライ、レート制限、秘匿情報を扱う必要がある場合。
- **使わない**: ローカル処理のみで完結するスキル、API 呼び出しが 1 箇所しか無くシンプルなもの。

## 認証優先順位 (env key → DefaultCredential → fail)

ユーザー環境の柔軟性を確保するため、以下の順で試行する:

1. **環境変数 API key** (`<SERVICE>_API_KEY` 等): 最速・社内ロール権限が無い時のフォールバック。
2. **DefaultAzureCredential / OAuth Token**: `az login` ベース、ロール付与済み環境向け。
3. **Fail-fast**: 上記が両方失敗したら `exit code 2` で `az login` 等の手順を案内。

## リトライマトリクス

| HTTP Status | 動作 | 備考 |
|---|---|---|
| 200 | 成功 | retry_log に success を記録 |
| 429 | retry (backoff) | `Retry-After` ヘッダを尊重 |
| 502/503/504 | retry (backoff) | exponential: 1, 2, 4, 8, 16 秒 |
| 400/404/415 | fail-fast | リクエスト不正・URL 誤り |
| 401/403 | fail-fast (code 2) | 認証/認可エラー |
| 413 | fail-fast | ペイロード過大 (事前検証で防ぐ) |

最大リトライ回数: 5 回。ネットワーク例外も同様にリトライ対象。

## Rate-limit 検出

- 429 受信時は `Retry-After` ヘッダを最優先 (秒数 or HTTP-date)。
- ヘッダが無ければ固定 backoff schedule にフォールバック。
- すべての試行を `_run/retry_log.json` に記録 (attempt / status / wait_seconds / result)。

## 秘匿情報の扱い

- `.env` ファイルは `chmod 600` を強制、`.gitignore` で除外。
- `.env.example` のみコミットし、`<value>` プレースホルダのみを置く。
- レスポンス body をログに残す前に `_redact_secrets()` で `Bearer xxx` / `key=xxx` を `***` 置換。
- エラーメッセージにキー値そのものを含めない (識別子のみ)。

## 実装例

`~/.claude/skills/transcribe-meeting/scripts/azure_fast_transcribe.py:130-160` の `acquire_auth_headers()` を参照。

```python
def acquire_auth_headers() -> tuple[dict[str, str], str]:
    """1. env API key  2. DefaultAzureCredential  3. fail-fast (code 2)"""
    api_key = os.environ.get("AZURE_SPEECH_KEY", "").strip()
    if api_key:
        return {"Ocp-Apim-Subscription-Key": api_key}, "API key"
    try:
        token = DefaultAzureCredential().get_token(TOKEN_SCOPE)
        return {"Authorization": f"Bearer {token.token}"}, "DefaultAzureCredential"
    except ClientAuthenticationError as exc:
        fail("Azure 認証に失敗しました。AZURE_SPEECH_KEY を .env に設定するか "
             "`az login` を実行してください。", code=2)
```

リトライ実装は同ファイル `call_api()` (line 205-330) を参照。`RETRYABLE_STATUS = {429, 502, 503, 504}` と `FAIL_FAST_STATUS = {400, 401, 403, 404, 413, 415}` を集合で管理して `if status in ...` で分岐するのが明快。

## チェックリスト

- [ ] 認証は 2 段以上のフォールバックを持つ
- [ ] retryable / fail-fast の status を集合で明示
- [ ] `Retry-After` ヘッダを尊重
- [ ] retry_log を JSON に persist
- [ ] body snippet を redact してから保存
- [ ] `.env` は 600 perm + gitignore
