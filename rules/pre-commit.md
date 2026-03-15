# Pre-Commit Rules

Apply before every commit.

- [ ] Tests pass (`npm test` / `pytest` / project-specific command)
- [ ] Lint and type checks pass
- [ ] `git diff --staged` shows only intended changes
- [ ] No secrets (.env, credentials, API keys) in staged files
- [ ] No debug code (console.log, debugger, print statements)
- [ ] Commit message follows Conventional Commits format
