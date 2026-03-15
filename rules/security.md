# Security Rules

Always apply these rules regardless of context.

## Secrets
- NEVER hardcode API keys, passwords, tokens, or connection strings
- Use environment variables or secret managers
- Check `git diff --staged` for accidental secret commits

## Input Validation
- Validate all external input (user input, API responses, file content)
- Sanitize before database queries (parameterized queries only)
- Escape output for XSS prevention

## Authentication & Authorization
- Never store passwords in plain text
- Verify authorization on every protected operation
- Use principle of least privilege
