---
name: testing-rules
description: |
  テスト作成・レビュー時のテストルールを適用。TDDサイクルに基づく。
  テストファースト開発、品質基準、カバレッジ目標を定義。
  トリガー: 「テストを書く」「TDD」「テストカバレッジ」「テスト品質レビュー」
---

# Testing Rules

TDDに基づくテスト開発ルールスキル。

## ワークフロー

```mermaid
flowchart TD
    A[機能要件確認] --> B[テストケース設計]
    B --> C[RED: 失敗テスト作成]
    C --> D[テスト実行]
    D --> E{テスト失敗?}
    E -->|No| F[テストを修正]
    F --> D
    E -->|Yes| G[GREEN: 最小実装]
    G --> H[テスト実行]
    H --> I{テスト成功?}
    I -->|No| J[実装を修正]
    J --> H
    I -->|Yes| K{リファクタ必要?}
    K -->|Yes| L[REFACTOR: コード改善]
    L --> M[テスト実行]
    M --> N{テスト成功?}
    N -->|No| L
    N -->|Yes| O{次のテスト?}
    K -->|No| O
    O -->|Yes| C
    O -->|No| P[完了]
```

## Step 1: テストケース設計

機能要件から必要なテストケースを洗い出す。

| 観点 | 内容 |
|------|------|
| 正常系 | 期待通りの入力で期待通りの出力 |
| 境界値 | 最小値、最大値、境界付近 |
| 異常系 | 不正入力、エラーケース |
| エッジケース | 空配列、null、特殊文字 |

## Step 2: RED - 失敗するテストを書く

```javascript
// Good: 振る舞いを記述
it('should return empty array when no items match filter')
it('should throw ValidationError when input is invalid')

// Bad: 曖昧な命名
it('test1')
it('works')
```

**テスト構造: AAA パターン**

```javascript
it('should calculate total price with discount', () => {
  // Arrange - 準備
  const cart = new Cart();
  cart.addItem({ price: 100, quantity: 2 });

  // Act - 実行
  const total = cart.calculateTotal(0.1); // 10% discount

  // Assert - 検証
  expect(total).toBe(180);
});
```

## Step 3: GREEN - 最小限の実装

- テストを通すための最小限のコードを書く
- 「きれいな」コードは後回し
- ハードコードでもOK

## Step 4: REFACTOR - コード改善

- テストが通った状態を維持
- 重複を除去
- 命名を改善
- 設計を改善

## クイックリファレンス

### テスト実行コマンド

| タイミング | コマンド |
|------------|----------|
| 開発中 | `npm test -- --watch` |
| コミット前 | `npm test` |
| プッシュ前 | `npm test -- --coverage` |
| CI | `npm run test:ci` |

### 全チェック（コミット前）

```bash
npm test && npm run lint && npm run type-check && npm run build
```

### カバレッジ目標

| 種別 | 目標 |
|------|------|
| Statements | 80% |
| Branches | 75% |
| Functions | 80% |
| Lines | 80% |

### テスト命名規則

| パターン | 例 |
|----------|-----|
| should + 期待動作 | `should return user when id exists` |
| when + 条件 | `when input is empty, should throw error` |
| given/when/then | `given valid input, when submitted, then saves data` |

### モック使用基準

| 対象 | モック |
|------|--------|
| 外部API | Yes |
| データベース | Yes（ユニットテスト） |
| 時間 | Yes（`Date.now`等） |
| 内部ロジック | No |

## 検証チェックリスト

### テスト作成前チェック

- [ ] 要件を理解している
- [ ] テストケースを洗い出した
- [ ] 正常系/異常系/境界値を網羅

### テストコード品質チェック

- [ ] テスト名が振る舞いを説明している
- [ ] 1テスト = 1アサーション（原則）
- [ ] AAA パターンに従っている
- [ ] 実装ではなく振る舞いをテスト
- [ ] テストが独立している（順序依存なし）
- [ ] テストデータが明確

### TDD サイクルチェック

- [ ] RED: テストが正しく失敗する
- [ ] GREEN: 最小限の実装で通過
- [ ] REFACTOR: リファクタ後もテスト通過

### プッシュ前チェック

- [ ] 全テスト通過
- [ ] カバレッジ目標達成
- [ ] Lint エラーなし
- [ ] 型チェック通過
- [ ] ビルド成功

## 重要事項

- **テストファースト**: 実装前にテストを書く
- **振る舞いをテスト**: 実装詳細ではなく振る舞いを検証
- **独立したテスト**: 他のテストに依存しない
- **読みやすい命名**: テスト名は仕様書として機能する
