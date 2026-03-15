#!/bin/bash
# Auto-sync: regenerate dashboard + commit + push to main
# Called from PostToolUse hook via stdin (jq pipe)

FILE=$(jq -r '.tool_input.file_path // empty')

# Only trigger for config files
echo "$FILE" | grep -qE '/Users/so/.claude/(CLAUDE\.md|settings\.json|agents/.*\.md|skills/.*/SKILL\.md|commands/.*\.md|\.gitignore)$' || exit 0

# Regenerate dashboard
node /Users/so/.claude/scripts/generate-dashboard.mjs || exit 0

# Commit and push to main
cd /Users/so/.claude
git add -A
git diff --cached --quiet && exit 0
git commit -m "chore: auto-sync config changes"
git push origin main
