# Skills 改善計画

rough-estimate スキルと公式ベストプラクティスを基準に、他のスキルを改善する計画。

---

## 現状分析

### rough-estimate の優れた構造

| 要素 | 内容 |
|------|------|
| description | 複数行、トリガーフレーズ含む |
| フローチャート | Mermaid で可視化 |
| ステップ手順 | Step 1〜6 の明確なワークフロー |
| クイックリファレンス | 早見表で即座に参照可能 |
| 参照ファイル | references/, assets/ に分離 |
| 検証チェックリスト | 出力前の確認項目 |
| 言語指定 | Important Notes で日本語出力を明記 |

### 他スキルの問題点

| スキル | 問題 |
|--------|------|
| development-rules | ワークフローなし、単なるルール羅列 |
| testing-rules | TDDサイクルあるが実行手順なし |
| git-workflow | 手順あるがフローチャートなし |
| serena-codebase | ツール呼び出し例あるが段階的手順不足 |
| gemini-research | 使用例あるがワークフローなし |
| document-converter | 手順あるが検証ステップなし |

---

## 改善方針

公式ベストプラクティスに基づく改善:

### 1. description の改善

**Before:**
```yaml
description: Apply development rules when writing or reviewing code. Triggers on "implement feature", "write code"...
```

**After:**
```yaml
description: |
  コード実装・レビュー時の開発ルールを適用。SOLID、YAGNI、DRY、KISS原則に基づく。
  トリガー: 「機能を実装」「コードを書く」「コード品質レビュー」「SOLID原則を適用」
```

### 2. 共通構造テンプレート

```markdown
---
name: skill-name
description: |
  スキルの目的と機能の説明（日本語）
  トリガー: 「〇〇」「△△」「□□」
---

# スキル名

簡潔な概要（1-2行）

## ワークフロー

```mermaid
flowchart TD
    A[開始] --> B[ステップ1]
    B --> C[ステップ2]
    C --> D[完了]
```

## ステップ

### Step 1: 〇〇
具体的な手順...

### Step 2: △△
具体的な手順...

## クイックリファレンス

| 項目 | 値 |
|------|-----|
| ... | ... |

## 検証チェックリスト

- [ ] 確認項目1
- [ ] 確認項目2

## 重要事項

- 出力は日本語
- その他の注意点
```

---

## 各スキルの改善内容

### 1. development-rules

**追加要素:**
- Mermaid フローチャート（実装前リサーチ → 設計 → 実装 → レビュー）
- Step 形式のワークフロー
- クイックリファレンス（原則の早見表）
- コードレビューチェックリスト

### 2. testing-rules

**追加要素:**
- TDD サイクルの Mermaid 図
- Step 形式（RED → GREEN → REFACTOR）
- テスト実行コマンドのクイックリファレンス
- テスト品質チェックリスト

### 3. git-workflow

**追加要素:**
- ブランチフローの Mermaid 図
- PR 作成ワークフローの Step 化
- コミット前チェックリスト
- 安全性確認チェックリスト

### 4. serena-codebase

**追加要素:**
- 探索戦略の Mermaid フローチャート
- 段階的アプローチの Step 化
- トークン最適化のクイックリファレンス

### 5. gemini-research

**追加要素:**
- リサーチワークフローの Mermaid 図
- 効果的なプロンプト作成 Step
- ユースケース別クイックリファレンス

### 6. document-converter

**追加要素:**
- 変換ワークフローの Mermaid 図
- 変換前後の検証チェックリスト
- フォーマット別クイックリファレンス

---

## 実装計画

### Phase 1: 基本構造の統一
1. 全スキルの description を複数行に変更（日本語 + トリガーフレーズ）
2. 概要セクションを追加

### Phase 2: ワークフロー追加
1. 各スキルに Mermaid フローチャートを追加
2. Step 形式のワークフローを作成

### Phase 3: リファレンス・チェックリスト
1. クイックリファレンス（早見表）を追加
2. 検証チェックリストを追加
3. 重要事項セクションで言語設定を明記

---

## 対象ファイル

- `/Users/so/.claude/skills/development-rules/SKILL.md`
- `/Users/so/.claude/skills/testing-rules/SKILL.md`
- `/Users/so/.claude/skills/git-workflow/SKILL.md`
- `/Users/so/.claude/skills/serena-codebase/SKILL.md`
- `/Users/so/.claude/skills/gemini-research/SKILL.md`
- `/Users/so/.claude/skills/document-converter/SKILL.md`

---

## 検証方法

1. Claude Code を新規セッションで起動
2. 各スキルのトリガーフレーズで呼び出し確認
3. ワークフローが適切に実行されるか確認
4. 出力が日本語であることを確認
