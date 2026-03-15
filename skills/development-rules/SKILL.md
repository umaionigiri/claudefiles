---
name: development-rules
description: |
  コード実装・レビュー時の開発ルールを適用。
  Context7 による事前リサーチを必須とし、最新のベストプラクティスに基づいた実装を行う。
  トリガー: 「機能を実装」「コードを書く」「コード品質レビュー」
---

# Development Rules

## Step 1: Context7 Research (Required)

Always check latest API/patterns before implementation:

```
mcp__context7__resolve-library-id({ libraryName: "framework-name" })
mcp__context7__query-docs({ libraryId: "/lib/xxx", topic: "implementation pattern" })
```

## Step 2: Design Considerations

- Clarify requirements
- Verify consistency with existing code (search existing patterns via Grep/Glob)
- Identify impact scope
- Parallelize independent tasks with Task tool

## Step 3: Code Quality

→ See `rules/code-quality.md` for standards (naming, functions, error handling, comments)
→ See `rules/security.md` for security checks

## Verification Checklist

**Pre-implementation:**
- [ ] Context7 research completed
- [ ] Existing code patterns reviewed
- [ ] Impact scope identified

**Post-implementation:**
- [ ] Each function/class has single responsibility
- [ ] No unnecessary features added
- [ ] Simplest possible solution
- [ ] Tests present with adequate coverage
- [ ] `rules/security.md` criteria satisfied
