# Version Check Rules

At the start of each session (first prompt), silently perform:

## 1. Check Current Version
Run `claude --version` to get installed version.

## 2. Check for Updates
Search for latest Claude Code release via WebSearch: `"Claude Code latest version changelog"`

## 3. If New Version Available
- Report version diff to user (current → latest)
- Summarize new features in Japanese
- Evaluate each new feature against current config:
  - New settings available? → Add to `settings.json`
  - New hook types? → Evaluate for `hooks` section
  - New slash commands? → Update Context Management techniques
  - New agent/skill capabilities? → Update relevant definitions
  - Breaking changes? → Flag and plan migration

## 4. If Up to Date
- Silently continue (do not report unless asked)
