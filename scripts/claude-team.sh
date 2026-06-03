#!/usr/bin/env bash
# Launch Claude Code inside a tmux session so Agent Teams split-pane mode works.
set -euo pipefail
SESSION_NAME="${CLAUDE_TEAM_TMUX_SESSION:-claude-team}"
if [ -z "${TMUX:-}" ]; then
  exec tmux new-session -A -s "$SESSION_NAME" "claude $*"
else
  exec claude "$@"
fi
