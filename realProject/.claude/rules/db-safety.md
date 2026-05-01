---
description: Safety rules for database migration files — highest-risk files in the repo
paths:
  - src/db/migrations/**
  - src/db/schema.prisma
---

# Database Migration Safety Rules

⚠️  These files are **production-critical**. Claude should be highly conservative.

## Read-Only by Default

Unless the user has explicitly asked Claude to write or edit a migration,
Claude should treat all files matching these paths as **read-only for analysis**.

Preferred response: explain what the migration does, identify risks, suggest
improvements — but do not write or propose schema changes unless asked.

## Before Suggesting Any Change

Claude MUST address all of these in its response:

1. **Is this change backward-compatible?** (Can old code run against the new schema?)
2. **Is there a rollback plan?** (Can this migration be reversed?)
3. **Is there a data migration needed?** (Adding a NOT NULL column to a table with rows?)
4. **What is the estimated lock duration?** (ALTER TABLE on large tables can block reads)

## Forbidden Actions

Claude must NOT:
- Suggest `DROP TABLE` without an explicit user request AND confirmation prompt
- Suggest `prisma migrate reset` — this wipes the database
- Add `@@ignore` to the Prisma schema to hide a table from the ORM
- Propose removing a column that appears in any `src/api/` or `src/frontend/` file

## Approved Safe Operations

- Adding nullable columns
- Adding new tables
- Adding indexes (with `CREATE INDEX CONCURRENTLY` for large tables)
- Renaming via new column + backfill + drop old pattern (documented in `docs/migration-guide.md`)