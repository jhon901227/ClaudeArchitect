# Claude Code Configuration — Certification Practice

Hands-on project covering every concept in the
**"Configure Claude Code for a real project"** certification scenario.

---

## What You Will Practice

| Concept | Files | Exercise |
|---|---|---|
| CLAUDE.md hierarchy (root + subdirs) | `CLAUDE.md`, `src/*/CLAUDE.md` | 1 |
| Path-specific rules (lazy-loaded) | `.claude/rules/*.md` | 2 |
| Custom skills with frontmatter | `.claude/skills/*/SKILL.md` | 3 |
| `context: fork` (subagent isolation) | `review-pr`, `db-migrate` skills | 3B |
| `allowed-tools` restriction | All skill files | 3C |
| MCP server integration | `.mcp.json` | 4 |
| Settings & permissions | `.claude/settings.json` | 5 |

---

## Project Structure

```
claude-code-config/                     ← Simulated real project
│
├── CLAUDE.md                           ← Root: loaded every session
│
├── .mcp.json                           ← MCP server definitions
│
├── .claude/
│   ├── settings.json                   ← Project permissions (committed)
│   ├── settings.local.json             ← Personal overrides (gitignored)
│   ├── rules/
│   │   ├── api-routes.md               ← Lazy: paths: src/api/routes/**
│   │   ├── testing.md                  ← Lazy: paths: **/*.test.ts
│   │   ├── db-safety.md                ← Lazy: paths: src/db/migrations/**
│   │   └── ci-scripts.md              ← Lazy: paths: .github/** scripts/**
│   ├── skills/
│   │   ├── review-pr/SKILL.md          ← context: fork | Read,Glob,Grep only
│   │   ├── db-migrate/SKILL.md         ← context: fork | Read,Write,Bash
│   │   ├── gen-component/SKILL.md      ← main context | Read,Write,Glob
│   │   └── security-audit/SKILL.md     ← context: fork | Read,Glob,Grep,Bash
│   └── agents/
│       └── db-expert.md               ← Specialized subagent for db-migrate
│
└── src/
    ├── api/
    ├── frontend/
    │   └── CLAUDE.md                   ← Subdir: extends root, frontend rules
    ├── db/
    │   └── CLAUDE.md                   ← Subdir: extends root, migration rules
    └── tests/
```

---

## Setup on Linux VM

### 1. Install Claude Code

```bash
# Requires Node.js 18+
node --version

# Install Claude Code globally
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

### 2. Authenticate

```bash
claude login
# Opens browser for OAuth with your Anthropic account
```

### 3. Clone this practice project

```bash
git clone https://github.com/YOUR_USER/claude-code-config.git
cd claude-code-config
```

### 4. Install MCP server dependencies (Exercise 4 prep)

```bash
# The MCP servers in .mcp.json use npx — they auto-install on first use.
# Pre-install them to avoid delays:
npx -y @modelcontextprotocol/server-github --help
npx -y @modelcontextprotocol/server-filesystem --help

# Set env vars for MCP servers
export GITHUB_TOKEN="ghp_..."         # GitHub PAT with repo scope
export DATABASE_URL="postgresql://localhost:5432/taskflow_dev"
```

---

## Exercise 1 — CLAUDE.md Hierarchy

**Goal:** Understand how CLAUDE.md files stack and merge.

### 1A. Inspect what Claude loads

```bash
cd claude-code-config
claude

# In the Claude Code session, ask:
> What are the rules for this project?
> What are the rules specifically for the frontend?
> What are the database migration rules?
```

**Expected behavior:**
- Claude references rules from `CLAUDE.md` (root) for general questions.
- Claude references `src/frontend/CLAUDE.md` rules when asked about frontend.
- The subdirectory file EXTENDS the root — both apply simultaneously.

### 1B. Test hierarchy priority

```bash
# Open two terminal sessions:
# Terminal 1: start claude in the root
cd claude-code-config && claude

# Terminal 2: start claude in src/frontend/
cd claude-code-config/src/frontend && claude

# Compare what each session knows about:
> What are the component rules here?
```

The frontend session has BOTH root + frontend rules loaded.
The root session only has root rules (no frontend-specific ones).

### 1C. Add your own rules

Edit `CLAUDE.md` and add a rule about your preferred logging format.
Then open a new Claude Code session and ask: *"How should I log errors?"*

### Key Facts for Certification

```
~/.claude/CLAUDE.md         → User-level (all your projects)
<project>/CLAUDE.md         → Project root (shared via git)
<project>/src/*/CLAUDE.md   → Subdirectory (scope-limited, extends parent)
.claude/CLAUDE.md           → Also loaded (supplement to root CLAUDE.md)
```

Loading order: user → project root → subdirectory (each extends, not replaces)

---

## Exercise 2 — Path-Specific Rules (`.claude/rules/`)

**Goal:** Understand how rules are lazy-loaded only when relevant files are touched.

### 2A. Observe lazy loading in action

```bash
claude

# Rule NOT loaded yet — ask about API routes:
> What are the route conventions for this project?
# Answer: Claude uses CLAUDE.md only (no extra route rules yet)

# Now open an API route file to trigger lazy loading:
> Read src/api/routes/tasks.ts and explain the structure
# NOW the api-routes.md rule is loaded because you touched src/api/routes/**
> What are the route conventions?
# Answer: Claude now has the detailed api-routes.md rules available
```

### 2B. Inspect a rule file

```bash
cat .claude/rules/api-routes.md
```

Notice the YAML frontmatter:
```yaml
---
description: Rules for API route files — loaded only when Claude edits src/api/routes/**
paths:
  - src/api/routes/**
---
```

The `paths:` field is the key. Without it, rules load into every session (like CLAUDE.md).
With `paths:`, rules are **lazy-loaded** — only when Claude accesses a matching file.

### 2C. Create your own path-specific rule

```bash
cat > .claude/rules/docs.md << 'EOF'
---
description: Rules for documentation files
paths:
  - docs/**
  - "**/*.md"
---

# Documentation Rules

- Use British English spelling (colour, not color)
- Every code block must specify the language
- Maximum heading depth: 3 levels (###)
- All internal links must use relative paths
EOF
```

Test it:
```bash
claude
> Read the README and check if it follows documentation rules
```

### Key Facts for Certification

```
.claude/rules/*.md without frontmatter  → Loaded every session (like CLAUDE.md)
.claude/rules/*.md with paths: frontmatter → LAZY loaded (only when paths match)

Rules complement CLAUDE.md — they're additive, not a replacement.
```

---

## Exercise 3 — Custom Skills with Frontmatter

**Goal:** Master the SKILL.md format, `context: fork`, and `allowed-tools`.

### 3A. Invoke a skill manually

```bash
claude
> /review-pr main
```

Or let auto-invocation work:
```bash
> Review my PR for the feat/add-due-dates branch
# Claude auto-invokes the review-pr skill based on description matching
```

### 3B. Understand `context: fork`

```bash
cat .claude/skills/review-pr/SKILL.md | head -20
```

See:
```yaml
context: fork
allowed-tools: Read, Glob, Grep, WebSearch
```

**What `context: fork` does:**
- Spawns a **subagent** with a fresh context window
- The subagent does the work (reading the PR diff, analyzing)
- Results are returned to your main session
- The main session's context is NOT polluted by the PR diff (could be huge)

**What happens WITHOUT `context: fork`:**
- The skill runs inline — all PR diff content goes into YOUR current context
- For large PRs, this can fill the context window quickly

### 3C. Understand `allowed-tools` restriction

Compare two skills:

```bash
# review-pr: READ ONLY (no side effects)
grep "allowed-tools" .claude/skills/review-pr/SKILL.md
# allowed-tools: Read, Glob, Grep, WebSearch

# db-migrate: needs to READ and WRITE migration files
grep "allowed-tools" .claude/skills/db-migrate/SKILL.md
# allowed-tools: Read, Write, Bash, Glob
```

**Why restrict tools?**
- `review-pr` should NEVER write files — it's analysis only
- Restricting to Read/Grep makes this guarantee explicit and enforced
- Without restriction, Claude could theoretically edit files during a review

### 3D. Test auto vs manual invocation

```bash
# Auto-invocation (Claude decides to use the skill):
> Generate a new React component for displaying a task list

# Manual invocation (you control):
> /gen-component TaskList displays a paginated list of tasks with filters
```

### 3E. Create your own skill

```bash
mkdir -p .claude/skills/changelog
cat > .claude/skills/changelog/SKILL.md << 'EOF'
---
name: changelog
description: >
  Generate a CHANGELOG.md entry for recent commits.
  Invoked when user says "update changelog" or "generate changelog".
version: 1.0.0
context: fork
allowed-tools: Read, Write, Bash
argument-hint: "[version number, e.g. v1.2.0]"
---

# Changelog Generator

1. Run: `git log --oneline -20` to get recent commits
2. Read: `CHANGELOG.md` to understand the existing format
3. Group commits by type: Features, Bug Fixes, Breaking Changes
4. Write the new entry at the top of CHANGELOG.md

Format:
## [<version>] - <today's date>
### Added
### Fixed
### Breaking Changes
EOF
```

Test it:
```bash
claude
> Update changelog for v1.3.0
```

### Key Facts for Certification

```
context: fork     → Runs skill as isolated subagent (fresh context, results returned)
                    Use for: large inputs, read-only tasks, context isolation

context: (absent) → Runs inline in main context
                    Use for: write tasks where user will iterate immediately

allowed-tools     → Comma-separated tool allowlist for this skill
                    Claude cannot use tools not listed, even if normally allowed

user-invocable: false   → Hides from /menu, still auto-invokable
disable-model-invocation: true → Manual only (/slash), never auto-invoked
```

---

## Exercise 4 — MCP Server Integration

**Goal:** Configure and use an MCP server; understand the three scopes.

### 4A. Understand MCP scopes

```
local scope   → .claude/mcp.json or per-session   (private, not committed)
project scope → .mcp.json                          (shared with team via git)  ← this project
user scope    → ~/.claude/mcp.json                 (available across all projects)
```

### 4B. Inspect `.mcp.json`

```bash
cat .mcp.json
```

You'll see three servers:
- **github** — reads PRs, issues, branches (used by `review-pr` skill)
- **postgres** — read-only DB inspection
- **filesystem** — scoped file access

### 4C. Start Claude Code and verify MCP servers load

```bash
# Set required env vars
export GITHUB_TOKEN="ghp_your_token_here"
export DATABASE_URL="postgresql://localhost:5432/taskflow_dev"

claude

# Ask Claude what tools it has:
> What MCP tools do you have available?
# Should list tools from github and postgres servers
```

### 4D. Use the GitHub MCP server

```bash
claude
> List the open PRs in this repository
> What issues are labeled 'bug'?
> Show me the diff for PR #5
```

The `review-pr` skill uses these GitHub tools automatically.

### 4E. Add an MCP server at user scope (available to all your projects)

```bash
# Add to user-level MCP config
claude mcp add sequential-thinking \
  --command npx \
  --args "-y @modelcontextprotocol/server-sequential-thinking"

# Verify
claude mcp list
```

### 4F. Temporarily disable an MCP server for one session

```bash
# Start Claude without postgres (e.g., no DB running locally)
claude --disable-mcp postgres
```

### Key Facts for Certification

```
.mcp.json (project)      → version-controlled, shared with team
~/.claude/mcp.json (user) → personal, all projects
Per-session              → --mcp-server flag or /mcp add in session

MCP tool naming in Claude: mcp__<servername>__<toolname>
MCP prompts become slash commands: /mcp__github__create_issue

Context window impact: every connected MCP server adds its tool schemas to context
  → Disable unused servers to save context tokens
```

---

## Exercise 5 — Settings & Permissions

**Goal:** Understand the `settings.json` hierarchy and permission system.

### 5A. Inspect project settings

```bash
cat .claude/settings.json
```

Notice the structure:
- **allow list**: explicit bash commands Claude can run without prompting
- **deny list**: commands Claude cannot run at all (even if asked)
- **env**: environment variables injected into every session

### 5B. Test deny rules

```bash
claude
> Run prisma migrate reset
# Claude should refuse — this is in the deny list
> Delete the src/ directory with rm -rf
# Claude should refuse — rm -rf * is denied
```

### 5C. Understand settings hierarchy

```
Managed (org admin)    ← highest priority, cannot be overridden
User (~/.claude/settings.json)
Project (.claude/settings.json)    ← this file (committed)
Local (.claude/settings.local.json) ← lowest priority, gitignored
```

Later levels ADD to earlier ones. Deny rules ALWAYS win (checked first).

### 5D. Add a personal override in settings.local.json

```bash
cat > .claude/settings.local.json << 'EOF'
{
  "env": {
    "DATABASE_URL": "postgresql://localhost:5432/taskflow_MY_LOCAL_NAME"
  }
}
EOF
```

This overrides DATABASE_URL for your local session without touching the committed settings.

---

## Certification Checklist

**CLAUDE.md Hierarchy**
- [ ] Know the three CLAUDE.md locations (user, project, subdirectory)
- [ ] Explain how subdirectory files extend (not replace) parent files
- [ ] Understand that `.claude/CLAUDE.md` is also loaded alongside root CLAUDE.md

**Path-Specific Rules**
- [ ] Explain the difference between rules with and without `paths:` frontmatter
- [ ] Know that `paths:` rules are lazy-loaded (only when files match)
- [ ] Know that rules without `paths:` load every session (same as CLAUDE.md)

**Skills**
- [ ] Write a valid SKILL.md with all frontmatter fields
- [ ] Explain `context: fork` — what it does, when to use it
- [ ] Explain `allowed-tools` — what it restricts, why it matters
- [ ] Know the difference between `user-invocable: false` and `disable-model-invocation: true`
- [ ] Know skills live in `.claude/skills/<name>/SKILL.md`

**MCP Servers**
- [ ] Explain the three MCP scopes (local, project, user)
- [ ] Know that `.mcp.json` = project scope (committed)
- [ ] Understand MCP tool naming: `mcp__<server>__<tool>`
- [ ] Know that MCP servers consume context tokens even when idle
- [ ] Know how to disable a server: `claude --disable-mcp <name>`

**Settings & Permissions**
- [ ] Explain the 4-level settings hierarchy (managed → user → project → local)
- [ ] Know that deny rules always win (checked before allow)
- [ ] Know `.claude/settings.local.json` is gitignored by Claude Code automatically
- [ ] Use env vars in settings.json to inject configuration into every session

---

## Push to GitHub

```bash
git init
git add .
# Do NOT add settings.local.json (already gitignored by Claude Code)
git commit -m "chore: add Claude Code configuration for TaskFlow"
git remote add origin https://github.com/YOUR_USER/claude-code-config.git
git push -u origin main
```