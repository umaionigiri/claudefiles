#!/bin/bash
# Auto-sync: regenerate dashboard + commit + push to main
# Called from PostToolUse hook via stdin (jq pipe)

# Resolve .claude directory for both macOS and Windows
if [ -d "/Users/so/.claude" ]; then
  CLAUDE_DIR="/Users/so/.claude"
elif [ -d "$USERPROFILE/.claude" ]; then
  CLAUDE_DIR="$USERPROFILE/.claude"
elif [ -d "$HOME/.claude" ]; then
  CLAUDE_DIR="$HOME/.claude"
else
  exit 0
fi

FILE=$(node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{console.log(JSON.parse(d).tool_input.file_path||'')}catch{}})")

# Only trigger for config files
echo "$FILE" | grep -qE '(\.claude/(CLAUDE\.md|settings\.json|agents/.*\.md|skills/.*/SKILL\.md|commands/.*\.md|\.gitignore))$' || exit 0

# Regenerate dashboard
node "$CLAUDE_DIR/scripts/generate-dashboard.mjs" || exit 0

# Commit and push to main
cd "$CLAUDE_DIR"
git add -A
git diff --cached --quiet && exit 0
git commit -m "chore: auto-sync config changes"
git push origin main
