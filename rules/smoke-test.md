# Smoke Test Mode for Large Tasks

For "大きな作業" (high-impact / multi-step / hard-to-revert tasks), insert checkpoint
confirmations between logical steps so errors are caught early and any damage is
contained to one step.

## When to apply

Trigger smoke-test mode when **any one** of these is true:

- 3+ chained file/folder creations or edits
- Modifying formatted Office files (xlsx, docx, pptx) where format break is hard to detect
- Writes into production folders, shared drives, or any path the user cares about
  beyond the local repo
- External-system writes (Slack, GitHub PR/issue, ticketing system, deploy)
- Multi-stage data transforms where each stage feeds the next
- Any user instruction that names "smoke test", "段階的に", "一段階ずつ確認" etc.

## When NOT to apply

- Single-file edits in the local repo
- Read-only investigation
- Trivial one-shot changes (rename, typo fix, single config tweak)
- Operations the user has already explicitly authorized to run end-to-end

## How to apply

1. Decompose the task into logical steps. Each step should:
   - Produce a visible result (path, file, output) the user can confirm
   - Be self-contained — abandoning here leaves the system in a coherent state
2. Execute step N. Print or summarize what was created / modified.
3. Call `AskUserQuestion` with options like:
   - **次の作業（<step N+1 の内容>）に進む**
   - **中断して内容を確認したい**
   - **修正してから再実行したい**
4. Only proceed to step N+1 after the user picks "進む".
5. If the user picks "中断" or "修正", stop and report what's already been done so
   the user can decide whether to roll back.

## Goal

Local errors instead of cascading damage. The user pays one extra prompt per step
in exchange for catching mistakes before they propagate through 5 more steps.
