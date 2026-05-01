# Database — Claude Code Configuration

> **Hierarchy level:** `src/db/` subdirectory
> Extends root CLAUDE.md. Applies only when Claude touches `src/db/`.

---

## Migration Rules (CRITICAL)

Migrations are **irreversible in production**. Follow these rules exactly:

1. **Always use `npx prisma migrate dev --name <name>`** — never write raw SQL migrations by hand.
2. **One concern per migration.** Never combine schema changes with data backfills.
3. Migration names must be `snake_case` and descriptive: `add_due_date_to_tasks`, not `update1`.
4. **All migrations must be reviewed by a second engineer before merging.**
5. Every destructive operation (DROP, column removal) must have a rollback plan documented in the PR.

---

## Schema Design Conventions

- Primary keys: `id UUID DEFAULT gen_random_uuid()` — never auto-increment integers.
- Timestamps: every table has `created_at` and `updated_at` managed by Prisma.
- Soft deletes: use `deleted_at TIMESTAMP` — never hard DELETE records.
- Foreign keys: always explicit with `ON DELETE RESTRICT` unless the team agrees otherwise.

---

## Safe Operations Only

When working in this directory, Claude should:
- Read schema files and migration history freely.
- Suggest migration SQL or Prisma schema changes.
- **Never run `prisma migrate reset`** — this drops the database.
- **Never run `prisma db push`** in this project — we use migrate, not push.