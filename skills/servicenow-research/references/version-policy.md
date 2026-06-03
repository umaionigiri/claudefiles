# Version Policy — リリース判定と AskUserQuestion 発火条件

## ServiceNow リリースファミリー

ServiceNow は半年に1度メジャーリリースを行い、各リリースは **都市名のアルファベット順** で命名される。

| 順 | リリース名 | GA時期 (概算) | ServiceNowDocs ブランチ |
|----|-----------|--------------|----------------------|
| ... | (older) | | (削除済) |
| - | Xanadu | 2024 後半 | `xanadu` |
| - | Yokohama | 2025 前半 | `yokohama` |
| - | Zurich | 2025 後半 | `zurich` |
| - | **Australia** (latest) | 2026 前半 | `australia` |

ServiceNowDocs は **最新3 + Early Access** のみ保持する。最古ブランチは GA 時に削除される (ローリング保持)。

## ALLOWED_BRANCHES (現時点)

`scripts/raw_fetch.py` の `ALLOWED_BRANCHES` 定数:
```
{"australia", "zurich", "yokohama", "xanadu"}
```

新リリース GA 時はこの定数を更新し、最古ブランチを除外する。

## バージョン判定アルゴリズム

```
1. 質問テキストを小文字化
2. 以下の語彙が含まれているか判定:
   - "australia" / "オーストラリア" → branch="australia"
   - "zurich" / "チューリッヒ" → branch="zurich"
   - "yokohama" / "横浜" / "ヨコハマ" → branch="yokohama"
   - "xanadu" / "ザナドゥ" → branch="xanadu"
   - "latest" / "最新" / "最新版" → branch="australia" (現時点の最新)
3. 該当なし → AskUserQuestion で確認 (下記参照)
```

## AskUserQuestion の発火タイミング

**質問テキストにバージョン語が一切含まれない場合のみ** AskUserQuestion を呼ぶ。これは制約「対象バージョンが不明なら聞く」の機械的判定。

質問例:
```
"対象の ServiceNow リリースはどれですか? (新機能や仕様はリリースによって異なります)"

選択肢:
- Australia (最新)  ← 推奨
- Zurich
- Yokohama
- Xanadu
- リリース不問 / 共通
```

「リリース不問」が選ばれた場合は **`australia` を採用** し、回答末尾の補足に「リリース不問の質問のため最新版で調査しました」と明記する。

## バージョン語が含まれる場合の挙動

質問例: 「Yokohama リリースで MID Server を構成する手順」

→ AskUserQuestion はスキップし、`branch="yokohama"` で直接調査開始する。
回答冒頭で「対象リリース: Yokohama」をフッタに表示する。

## 複数バージョン跨ぎの質問

質問例: 「Australia と Zurich で Now Assist の振る舞いがどう違うか?」

→ 2ブランチで並列に調査し、差分を比較形式で回答する:
```markdown
## 結論
両リリースの差分は以下のとおり: ...

## 理由 / 背景
### Australia (最新)
<内容>([Now Assist Australia](URL_australia))

### Zurich
<内容>([Now Assist Zurich](URL_zurich))
```

## 削除済みリリース (xanadu より古い) を聞かれたら

「該当リリースは公式ドキュメントリポジトリの保持対象外です。最新3リリース (Australia / Zurich / Yokohama) または Xanadu の中から対象を選んでください」と返答し、再質問を促す。

## デフォルト動作 (制約整合)

ユーザ制約:
> 調査対象のバージョン (Australia等) が不明な場合は AskQuestion で質問すること

→ **明示無し → 必ず AskUserQuestion** を発火させる (デフォルトで Australia に倒さない)。
これにより、ユーザが意図せず古いリリース固有の話を聞いていた場合の取り違いを防げる。
