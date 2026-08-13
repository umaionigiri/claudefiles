#!/usr/bin/env bash
# Launch Claude Code inside a tmux session so Agent Teams split-pane mode works.
set -euo pipefail
SESSION_NAME="${CLAUDE_TEAM_TMUX_SESSION:-claude-team}"
# Always launch with Opus 4.8 (1M context) at max reasoning effort.
# These are CLI flags, which outrank the organization default model (Sonnet 4.6),
# so they also sidestep the "Managed settings pins Sonnet 4.6" restart warning.
# settings.json ("model"/"effortLevel") stays as the fallback for a bare `claude`.
if [ -z "${TMUX:-}" ]; then
  exec tmux new-session -A -s "$SESSION_NAME" "claude --model 'claude-opus-4-8[1m]' --effort max $*"
else
  exec claude --model 'claude-opus-4-8[1m]' --effort max "$@"
fi
