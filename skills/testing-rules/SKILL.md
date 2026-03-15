---
name: testing-rules
description: |
  テスト作成・レビュー時のテストルールを適用。TDDサイクルに基づく。
  テストファースト開発、品質基準、カバレッジ目標を定義。
  トリガー: 「テストを書く」「TDD」「テストカバレッジ」「テスト品質レビュー」
---

# Testing Rules

## TDD Cycle

1. **RED**: Write a failing test → Confirm test failure
2. **GREEN**: Minimum implementation to pass the test
3. **REFACTOR**: Improve code while keeping tests green

## Test Naming Convention

| Pattern | Example |
|---------|---------|
| should + expected behavior | `should return user when id exists` |
| when + condition | `when input is empty, should throw error` |
| given/when/then | `given valid input, when submitted, then saves data` |

## Coverage Targets

| Type | Target |
|------|--------|
| Statements | 80% |
| Branches | 75% |
| Functions | 80% |
| Lines | 80% |

## Mock Usage Criteria

| Target | Mock? |
|--------|-------|
| External API | Yes |
| Database | Yes (unit tests) |
| Time | Yes (`Date.now`, etc.) |
| Internal logic | No |

## Verification Checklist

**Test code quality:**
- [ ] Test names describe behavior
- [ ] 1 test = 1 assertion (principle)
- [ ] Follows AAA pattern (Arrange-Act-Assert)
- [ ] Tests behavior, not implementation
- [ ] Tests are independent (no order dependency)

**Pre-push:**
- [ ] All tests pass
- [ ] Coverage targets met
- [ ] No lint errors
- [ ] Type check passes
- [ ] Build successful
