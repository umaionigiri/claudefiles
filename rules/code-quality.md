# Code Quality Rules

Always apply these rules when writing or reviewing code.

## Naming
- Use meaningful, descriptive names
- Follow project conventions (camelCase for JS/TS, snake_case for Python)
- Boolean variables: prefix with is/has/can/should

## Functions
- Single responsibility per function
- Max 50 lines per function; extract if longer
- Pure functions preferred; minimize side effects

## Error Handling
- Handle errors at the appropriate level
- Never swallow exceptions silently
- Provide actionable error messages

## Comments
- Explain "why", not "what"
- Delete commented-out code (use git history instead)
- Japanese supplementary comments are acceptable
