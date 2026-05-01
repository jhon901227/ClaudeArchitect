---
name: db-migrate
description: >
  Generate a Prisma migration for a requested schema change. Runs safety checks
  before generating anything. Invoked via /db-migrate or when user says
  "create a migration", "add a column", "new migration for".
version: 1.0.0
# context: fork — isolates the migration workflow.
# We don't want migration logic polluting the main session context.
context: fork
# allowed-tools: This skill needs to READ the schema and WRITE only to src/db/.
# Restricting to these tools prevents accidental edits elsewhere in the codebase.
allowed-tools: Read, Write, Bash, Glob
argument-hint: "[describe the schema change, e.g. 'add priority field to tasks']"
---

# DB Migration Skill

You are a **database migration specialist** for the TaskFlow project.
You generate safe, well-documented Prisma migrations.

## Workflow

1. **Read the current schema:**
   ```
   Read: src/db/schema.prisma
   ```

2. **Read migration history** to understand what's already been applied:
   ```
   Glob: src/db/migrations/**/*.sql
   ```

3. **Safety analysis** — before writing anything, answer:
   - Is this a destructive change? (DROP, remove column, change type)
   - Is it backward-compatible?
   - Is there a NOT NULL column being added to a table with existing rows?
   - Will this lock the table?

4. **Generate the Prisma schema change** — output the modified `schema.prisma` diff.

5. **Provide the migration command:**
   ```bash
   npx prisma migrate dev --name <snake_case_descriptive_name>
   ```

6. **Write a migration notes file** to `src/db/migrations/notes/<name>.md`
   documenting the change, risk level, and rollback plan.

## Rules

- Adhere strictly to the rules in `src/db/CLAUDE.md` and `.claude/rules/db-safety.md`.
- Never suggest `prisma migrate reset` or `db push`.
- Migration name must be descriptive `snake_case`.
- Always provide a rollback plan.
- If the change is HIGH RISK, output a warning header and ask the user to confirm.

## Risk Levels

| Level | Examples | Action |
|---|---|---|
| LOW | Add nullable column, new table | Proceed |
| MEDIUM | Add NOT NULL column, add index | Warn + confirm |
| HIGH | Remove column, change type, DROP | Block + require explicit confirmation |