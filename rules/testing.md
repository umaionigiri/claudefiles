# Testing Requirements

Adapted from Everything Claude Code (`rules/common/testing.md`).

## Minimum Coverage: 80%

Test types (all required for a feature to be "done"):
1. **Unit tests** — individual functions, utilities, components
2. **Integration tests** — API endpoints, database operations
3. **E2E tests** — critical user flows (Playwright for web, language-appropriate framework otherwise)

## Test-Driven Development (TDD)

Mandatory cycle for new code:
1. **RED** — Write the test first
2. Run the test — it should fail
3. **GREEN** — Write the minimal implementation to pass
4. Run the test — it should pass
5. **IMPROVE** — Refactor while keeping tests green
6. Verify coverage ≥ 80%

## Troubleshooting Test Failures

1. Use the **tdd-guide** agent (after Phase 2 adoption) to facilitate the cycle
2. Check test isolation (no shared state, no test order dependencies)
3. Verify mocks/fixtures are correct
4. Fix the implementation, not the test — unless the test expectation is itself wrong

## Test Structure (AAA Pattern)

Prefer Arrange-Act-Assert structure:

```typescript
test('calculates similarity correctly', () => {
  // Arrange
  const vector1 = [1, 0, 0]
  const vector2 = [0, 1, 0]

  // Act
  const similarity = calculateCosineSimilarity(vector1, vector2)

  // Assert
  expect(similarity).toBe(0)
})
```

```python
def test_calculates_similarity_correctly():
    # Arrange
    vector1 = [1, 0, 0]
    vector2 = [0, 1, 0]

    # Act
    similarity = calculate_cosine_similarity(vector1, vector2)

    # Assert
    assert similarity == 0
```

## Test Naming

Names must describe the behavior, not the function:

```
GOOD: returns empty array when no markets match query
GOOD: throws error when API key is missing
GOOD: falls back to substring search when Redis is unavailable

BAD:  testSearch
BAD:  test_function_1
BAD:  it works
```

## Test Behavior, Not Implementation

Per CLAUDE.md core philosophy: test what users observe, not internal implementation. Refactoring should not break tests.

## Agent Support

| Agent | When to use |
|-------|-------------|
| **tdd-guide** (Phase 2) | Use PROACTIVELY for new features — enforces tests-first |
| **pr-test-analyzer** (Phase 2) | After PR is ready — checks behavioral coverage and gap severity |
| **test-runner** (existing) | Running test suites and interpreting failures |
