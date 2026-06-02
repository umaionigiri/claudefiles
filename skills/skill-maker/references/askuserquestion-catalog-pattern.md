# AskUserQuestion カタログ一元化パターン

## いつ使う / 使わない

- **使う**: スキルが対話中に **3 個以上** の `AskUserQuestion` を発する場合。文言・選択肢が SKILL.md / scripts に散ると改修コストが膨らむ。
- **使わない**: 質問が 1-2 個で完結する小規模スキル、完全自動化スキル。

## カタログのスキーマ (YAML 推奨)

`references/questions.md` (もしくは `questions.yaml`) に質問を一元化する:

```yaml
- id: speaker_count
  phase: 1_input
  prompt: "話者数は何人ですか?"
  rationale: "diarization の maxSpeakers パラメータに使う (1-35)"
  options:
    - {value: "2", label: "2人 (1on1)"}
    - {value: "4", label: "3-4人 (小規模 MTG)"}
    - {value: "8", label: "5-8人 (標準会議)"}
    - {value: "auto", label: "自動 (既定)"}
  default: "auto"
  skip_if: "input_type == 'monologue'"

- id: glossary_apply
  phase: 2_preprocess
  prompt: "用語集を適用しますか?"
  rationale: "誤認識を後処理で置換するための判断"
  options:
    - {value: "yes", label: "適用する"}
    - {value: "no",  label: "スキップ"}
  default: "yes"
```

各 field の役割:

- `id`: スクリプトから参照する一意キー
- `phase`: ワークフロー段階 (実行順を可視化)
- `prompt`: ユーザーに見せる文言
- `rationale`: なぜこの質問が必要か (将来の保守者向け)
- `options`: AskUserQuestion の選択肢 (value / label)
- `default`: 自動モード時のデフォルト
- `skip_if`: 質問をスキップする条件式 (任意)

## 利点

1. **A/B テスト**: 文言を質問カタログだけ差し替えればスキル本体は不変。
2. **文言改善**: SKILL.md / scripts のコード行を触らずに済む (PR diff が読みやすい)。
3. **多言語化**: `prompt_ja` / `prompt_en` を並べる拡張が容易。
4. **Auto モード**: `default` 値で全質問を自動応答する dry-run が組める。
5. **ドキュメント化**: ユーザーが事前に「何を聞かれるか」を 1 ファイルで把握できる。

## 実装例

`~/.claude/skills/transcribe-meeting/references/questions.md` を参照。本スキルでは次の 5 質問を一元化:

1. 入力ファイルパス
2. 用語集の選択
3. 話者ラベル → 名前マッピング
4. 要約テンプレート選択
5. word-minutes へのハンドオフ可否

実装パターン:

```python
import yaml
catalog = yaml.safe_load(open("references/questions.yaml"))
for q in catalog:
    if should_skip(q.get("skip_if"), context):
        continue
    answer = ask_user_question(q["prompt"], q["options"], default=q["default"])
    context[q["id"]] = answer
```

## チェックリスト

- [ ] 質問が 3 個以上ならカタログ化を検討
- [ ] 各質問に `id` / `rationale` / `default` を必須記載
- [ ] `skip_if` で条件分岐をデータ駆動に
- [ ] SKILL.md からは「詳細は references/questions.md」とリンクのみ
- [ ] 自動モード時の挙動を `default` で定義
