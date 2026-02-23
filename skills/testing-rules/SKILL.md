---
name: testing-rules
description: |
  テスト作成・レビュー時のテストルールを適用。TDDサイクルに基づく。
  テストファースト開発、品質基準、カバレッジ目標を定義。
  トリガー: 「テストを書く」「TDD」「テストカバレッジ」「テスト品質レビュー」
---

# テストルール

## TDD サイクル

1. **RED**: 失敗するテストを書く → テスト失敗を確認
2. **GREEN**: テストを通す最小限の実装
3. **REFACTOR**: テストが通る状態を維持しつつコード改善

## テスト命名規則

| パターン | 例 |
|----------|-----|
| should + 期待動作 | `should return user when id exists` |
| when + 条件 | `when input is empty, should throw error` |
| given/when/then | `given valid input, when submitted, then saves data` |

## カバレッジ目標

| 種別 | 目標 |
|------|------|
| Statements | 80% |
| Branches | 75% |
| Functions | 80% |
| Lines | 80% |

## モック使用基準

| 対象 | モック |
|------|--------|
| 外部API | Yes |
| データベース | Yes（ユニットテスト） |
| 時間 | Yes（`Date.now` 等） |
| 内部ロジック | No |

## 検証チェックリスト

**テストコード品質:**
- [ ] テスト名が振る舞いを説明している
- [ ] 1テスト = 1アサーション（原則）
- [ ] AAA パターン（Arrange-Act-Assert）に従っている
- [ ] 実装ではなく振る舞いをテスト
- [ ] テストが独立している（順序依存なし）

**プッシュ前:**
- [ ] 全テスト通過
- [ ] カバレッジ目標達成
- [ ] Lint エラーなし
- [ ] 型チェック通過
- [ ] ビルド成功
