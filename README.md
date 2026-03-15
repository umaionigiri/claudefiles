# claudefiles

Configuration files for Claude Code (`~/.claude/`).

## Structure

```
~/.claude/
├── .gitignore             # Exclude runtime data
├── CLAUDE.md              # Global instructions (all projects)
├── settings.json          # Permissions, hooks, env vars, MCP config
├── agents/                # Custom agents (6 types)
├── commands/              # Slash commands
│   ├── slash-guide.md
│   └── kiro/              # Spec-driven development workflow (11 commands)
└── skills/                # Custom skills (7 types)
    ├── development-rules/
    ├── testing-rules/
    ├── git-workflow/
    ├── gemini-research/
    ├── serena-codebase/
    ├── document-converter/
    └── rough-estimate/
```

## CLAUDE.md

Global instruction file applied to all projects.

- **Language**: Respond in Japanese; code in English
- **Style**: Conclusion-first, concise and casual
- **Principles**: Only do what's asked; minimize file creation

## settings.json

### Permissions

Allows git read operations (`status`, `diff`, `log`, `branch`, `worktree`), `npm run`, `pnpm`, MCP tools (Context7, Azure, o3), etc.

### Hooks

| Hook | Description |
|------|-------------|
| **PreToolUse** | Block dangerous commands (`rm -rf`, etc.) and `git push --force` |
| **PostToolUse** | Auto-format `.js/.ts/.jsx/.tsx` files with prettier on save |
| **Stop** | Notification on task completion |
| **Notification** | Desktop notification via terminal-notifier |

### Environment

| Variable | Value | Description |
|----------|-------|-------------|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `70` | Auto-compaction at 70% context |

### MCP Integrations

- **Azure** — Azure resource operations and documentation
- **Context7** — Library documentation search
- **o3** — OpenAI o3 model integration
- **Serena** — Semantic code analysis
- **Playwright** — Browser automation
- **GitHub** — GitHub API integration
- **Notion** — Notion API integration
- **Gemini** — Google Gemini integration

## Agents

| Agent | Purpose |
|-------|---------|
| `estimation-agent` | Project estimation and quotation |
| `senior-consultant-reviewer` | Requirements, design, and estimate review |
| `code-reviewer` | Code quality and security review |
| `test-runner` | Test execution and code verification |
| `task-decomposer` | Project breakdown and task planning |
| `devops-problem-solver` | Error response, incidents, debugging |

## Commands

### `/slash-guide`

Explains all Claude Code slash commands in Japanese.

### `/kiro/*` — Spec-Driven Development Workflow

| Command | Purpose |
|---------|---------|
| `spec-init` | Initialize specification |
| `spec-requirements` | Generate requirements |
| `spec-design` | Create technical design |
| `spec-tasks` | Generate implementation tasks |
| `spec-impl` | Execute implementation via TDD |
| `spec-status` | Check specification progress |
| `steering` / `steering-custom` | Manage project knowledge |
| `validate-design` | Review technical design |
| `validate-gap` | Gap analysis between requirements and implementation |
| `validate-impl` | Validate implementation |

## Skills

| Skill | Purpose |
|-------|---------|
| `development-rules` | SOLID/DRY/KISS-based development rules |
| `testing-rules` | TDD cycle-based testing rules |
| `git-workflow` | Branch management with worktree requirement |
| `gemini-research` | External research via Gemini MCP |
| `serena-codebase` | Code exploration via Serena MCP |
| `document-converter` | Markdown → Word/Excel/PDF conversion |
| `rough-estimate` | Rough estimate creation (Scibit LLC) |

## Setup

```bash
git clone git@github.com:umaionigiri/claudefiles.git ~/.claude
```

If `~/.claude/` already exists, copy or symlink individual files:

```bash
git clone git@github.com:umaionigiri/claudefiles.git /tmp/claudefiles
ln -sf /tmp/claudefiles/CLAUDE.md ~/.claude/CLAUDE.md
ln -sf /tmp/claudefiles/settings.json ~/.claude/settings.json
ln -sf /tmp/claudefiles/agents ~/.claude/agents
ln -sf /tmp/claudefiles/commands ~/.claude/commands
ln -sf /tmp/claudefiles/skills ~/.claude/skills
```
