# Performance Optimization

Adapted from Everything Claude Code (`rules/common/performance.md`).

## Model Selection Strategy

| Model | When to use |
|-------|-------------|
| **Haiku 4.5** (90% Sonnet capability, ~3x cheaper) | Lightweight subagents, frequent invocation, code generation pair, worker agents in multi-agent systems |
| **Sonnet 4.6** (best coding model) | Default for main development, multi-agent orchestration, complex coding |
| **Opus 4.7** (deepest reasoning) | Architectural decisions, ambiguous requirements, research/analysis |

## Context Window Management

Avoid the **last 20% of the context window** for:
- Large-scale refactoring
- Multi-file feature implementation
- Debugging complex interactions

Lower context-sensitivity tasks (safe to operate near the edge):
- Single-file edits
- Independent utility creation
- Documentation updates
- Simple bug fixes

When approaching the edge: run `/compact <focus>` proactively to free tokens, or `/fork` to branch the session.

## Extended Thinking + Plan Mode

Extended thinking is enabled by default and reserves up to 31,999 tokens for internal reasoning.

Control:
- **Toggle**: Option+T (macOS) / Alt+T (Windows/Linux)
- **Config**: `alwaysThinkingEnabled` in `~/.claude/settings.json`
- **Budget cap**: `export MAX_THINKING_TOKENS=10000`
- **Verbose mode**: Ctrl+O to inspect thinking output

For complex tasks needing deep reasoning:
1. Confirm extended thinking is on
2. Enable Plan Mode (Shift+Tab×2) for structured approach
3. Use multiple critique rounds for thorough analysis
4. Use split-role subagents for diverse perspectives

## Cost Awareness

- Subagents in `task-dispatch.md` should default to **haiku** for research (cheap parallel exploration), **sonnet** for moderate work
- Don't run **opus** parallel teams unless reasoning depth is the actual bottleneck
- Use `cost-tracker` hook (when Phase 3 is in) to retrospect token spend per session

## Build Troubleshooting

If a build fails:
1. Use the **devops-problem-solver** agent (or ECC `build-error-resolver` once Phase 2 is in)
2. Read the error output literally before guessing
3. Fix incrementally — one error class at a time
4. Verify after each fix
