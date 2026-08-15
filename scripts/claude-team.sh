#!/usr/bin/env bash
# Launch Claude Code inside a tmux session so Agent Teams split-pane mode works.
set -euo pipefail
SESSION_NAME="${CLAUDE_TEAM_TMUX_SESSION:-claude-team}"
# Always launch with the latest Opus alias (currently Opus 5, native 1M) at max reasoning effort.
# These are CLI flags, which outrank the organization default model (Sonnet 4.6),
# so they also sidestep the "Managed settings pins Sonnet 4.6" restart warning.
# settings.json ("model"/"effortLevel") stays as the fallback for a bare `claude`.
if [ -z "${TMUX:-}" ]; then
  exec tmux new-session -A -s "$SESSION_NAME" "claude --model opus --effort max $*"
else
  exec claude --model opus --effort max "$@"
fi
