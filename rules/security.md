# Security Rules

Always apply these rules regardless of context. Synthesizes ECC `security.md` with the existing baseline.

## Mandatory Pre-Commit Checks

- [ ] No hardcoded secrets (API keys, passwords, tokens, connection strings)
- [ ] All user inputs validated
- [ ] SQL injection prevention (parameterized queries / ORM only)
- [ ] XSS prevention (sanitized HTML, escape output)
- [ ] CSRF protection enabled
- [ ] Authentication/authorization verified on every protected endpoint
- [ ] Rate limiting on all public endpoints
- [ ] Error messages don't leak sensitive data (stack traces, internal IDs, secrets)

## Secret Management

- **NEVER** hardcode secrets in source code
- **ALWAYS** use environment variables or a secret manager
- Validate that required secrets are present at startup (fail fast if missing)
- Rotate any secret that may have been exposed (commit history, logs, screenshots, chat)
- Run `git diff --staged` before commit to catch accidental secret commits

## Input Validation
- Validate all external input (user input, API responses, file content)
- Sanitize before database queries (parameterized queries only)
- Escape output for XSS prevention
- Use schema validation (Zod / Pydantic) at every system boundary

## Authentication & Authorization
- Never store passwords in plain text — bcrypt / argon2 only
- Verify authorization on every protected operation (not just route entry)
- Apply principle of least privilege
- Validate JWT signatures + expiration on every request
- Session tokens: secure / httpOnly / sameSite

## Security Response Protocol

If a security issue is found:
1. **STOP immediately** — don't continue the current task
2. Use the **security-reviewer** agent to scope the issue
3. Fix CRITICAL issues before continuing anything else
4. **Rotate any exposed secrets** (don't just remove them — rotate)
5. Search the entire codebase for similar issues (one occurrence often means more)
6. If secrets reached the remote: rewrite history with caution and force-push only with explicit user approval

## Common Vulnerabilities (Quick Reference)

| Class | Watch for |
|-------|-----------|
| Injection | String concatenation in queries; `eval`, `exec`, dynamic shell strings |
| Broken Auth | Weak hashing; tokens without expiration; sessions over HTTP |
| Sensitive Data | HTTP for credentials; PII in logs; secrets in env files committed |
| XXE | XML parsers with external entities enabled |
| Broken Access | Missing auth check on protected route; CORS too permissive |
| Misconfiguration | Default creds; debug mode in prod; missing security headers |
| Vulnerable Deps | `npm audit` / `pip-audit` not run before release |
| Logging | Logging request bodies/headers without redaction |

## Specialist Delegation

For deep dives, use the **security-reviewer** agent (Phase 2) — runs `npm audit`, `eslint-plugin-security`, OWASP Top 10 checks, secret scanning.
