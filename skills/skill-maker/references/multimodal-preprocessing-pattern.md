# Multimodal 前処理パターン (video / audio / 画像 → canonical 形式)

## いつ使う / 使わない

- **使う**: 入力が動画・音声・画像など多形式で、API が要求する canonical 形式 (例: 16kHz mono PCM WAV、特定解像度 PNG) に変換する必要がある場合。
- **使わない**: 入力がすでに canonical 形式、または単純な拡張子変換で済む場合。

## ffmpeg レシピ (動画/音声 → 16kHz mono PCM WAV)

Azure Speech / OpenAI Whisper など多くの ASR API が推奨する形式:

```bash
ffmpeg -y -hide_banner -nostats -i "$INPUT" \
  -vn -ar 16000 -ac 1 -c:a pcm_s16le \
  "$OUTPUT.wav"
```

| Flag | 意味 |
|---|---|
| `-vn` | 映像トラックを破棄 |
| `-ar 16000` | サンプリングレート 16kHz |
| `-ac 1` | mono (1 チャネル) |
| `-c:a pcm_s16le` | 16bit signed PCM little-endian (圧縮なし) |

## 二段 loudnorm (推奨)

長尺会議は音量がバラついて Azure の音響モデルが揺らぐので、EBU R128 ベースの正規化を強く推奨。

**pass1 (測定のみ)**:
```bash
ffmpeg -y -i "$INPUT" \
  -af "loudnorm=I=-23:TP=-2:LRA=7:print_format=json" \
  -f null - 2> pass1.log
```

stderr 末尾の JSON ブロックから `input_i` / `input_tp` / `input_lra` / `input_thresh` / `target_offset` を抽出。

**pass2 (適用 + 出力)**:
```bash
ffmpeg -y -i "$INPUT" \
  -af "loudnorm=I=-23:TP=-2:LRA=7:measured_I=$M_I:measured_TP=$M_TP:measured_LRA=$M_LRA:measured_thresh=$M_TH:offset=$T_OFF:linear=true" \
  -vn -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

**なぜ二段か**: 一段 (single-pass) は実時間アルゴリズムで局所判断するため長尺で過補正が起きやすい。二段なら全尺の統計に基づく `linear=true` が使え、一貫した正規化になる。

## なぜ denoise (afftdn) を避けるか

- Azure Speech / OpenAI Whisper は学習データに軽度ノイズを織り込み済み。
- afftdn の過剰なノイズ除去は子音 (s/k/t) のフォルマントを削り、認識精度を**下げる**。
- Microsoft Fast Transcription ベストプラクティスでも「extra denoising 不要」と明記。
- → loudnorm のみ採用、denoise は入れない。

## 入力サイズ事前検証 (API 上限早期検出)

API call 前に必ず: ファイルサイズ + duration を計測し、上限超過なら exit code 3 で fail-fast。

```python
MAX_FILE_BYTES = 500 * 1024 * 1024  # 500 MB
MAX_DURATION_SECONDS = 2 * 60 * 60  # 2h

size = wav_path.stat().st_size
duration = get_wav_duration_seconds(wav_path)  # wave.open() ヘッダから
if size > MAX_FILE_BYTES:
    fail(f"{size} bytes > {MAX_FILE_BYTES}", code=3)
if duration and duration > MAX_DURATION_SECONDS:
    fail(f"{duration}s > {MAX_DURATION_SECONDS}s", code=3)
```

事前検証によってネットワークアップロードを節約 (大きなファイルで 413 を返されてから気づくのは無駄)。

## 実装例

`~/.claude/skills/transcribe-meeting/scripts/preprocess_audio.sh` を参照。

- 一段目で `print_format=json` を `stderr` に出力させ、`re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}")` で JSON ブロックを抽出。
- 二段目で `linear=true` を付けることで pass1 値に基づく決定論的補正を実行。
- 出力 WAV のサイズを `stat -c '%s'` で確認、空ファイルなら exit 1。

`~/.claude/skills/transcribe-meeting/scripts/azure_fast_transcribe.py:182-202` の `validate_input()` も併せて参照。

## チェックリスト

- [ ] 出力は API が要求する canonical 形式 (16kHz mono PCM WAV 等)
- [ ] 二段 loudnorm を適用 (pass1 測定 → pass2 linear=true)
- [ ] denoise は入れない (ASR 精度を下げる)
- [ ] API call 前にサイズ + duration を事前検証
- [ ] 上限超過は exit code 3 で fail-fast
- [ ] pass1 の測定 JSON を成果物として保存 (再現性)
