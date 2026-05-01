# TaskFlow API — Claude Code Configuration

> **Hierarchy level:** Project root (shared with team via git)
> Loaded by Claude Code for every session in this repo.
> More specific CLAUDE.md files in subdirectories EXTEND this file.

---

## Project Overview

TaskFlow is a task-management REST API with a React dashboard.

- **Backend:** Node.js + Express, PostgreSQL via Prisma ORM
- **Frontend:** React 18, TypeScript, Tailwind CSS
- **Tests:** Vitest (unit), Playwright (e2e)
- **CI:** GitHub Actions
- **Monorepo layout:** `src/api/`, `src/frontend/`, `src/db/`, `src/tests/`

---

## Non-Negotiable Rules

1. **Never commit secrets.** `.env`, `.env.*`, `secrets/` are off-limits — always.
2. **Every public function needs a JSDoc/TSDoc comment.**
3. **No `console.log` in production code.** Use the logger at `src/api/lib/logger.ts`.
4. **Database migrations live in `src/db/migrations/` only.** Never alter the schema inline.
5. **All API endpoints require auth middleware** unless explicitly marked `public`.

---

## Git Conventions

- Branch naming: `feat/`, `fix/`, `chore/`, `docs/`
- Commit format: `type(scope): short description` (Conventional Commits)
- PR title = first commit message
- Never force-push to `main` or `develop`

---

## Code Style

- TypeScript strict mode everywhere (`"strict": true` in tsconfig)
- Single quotes, 2-space indent, trailing commas (enforced by Prettier)
- Imports: external → internal → relative (enforced by ESLint import/order)
- Prefer `async/await` over raw Promise chains
- Error handling: always use the typed `AppError` class, not raw `new Error()`

---

## Testing Standards

- Unit tests mirror source structure: `src/api/routes/tasks.ts` → `src/tests/unit/routes/tasks.test.ts`
- Minimum 80% line coverage enforced in CI
- Use `describe` + `it` (not `test`) for clarity
- Mock external services; never hit the real DB or network in unit tests

---

## What NOT to Do

- Do not install new npm packages without confirming with the team
- Do not edit `package-lock.json` manually
- Do not rename database columns directly — always use a migration
- Do not add inline styles in React components (use Tailwind classes)

---

## Useful Commands

```bash
npm run dev          # start API + frontend in watch mode
npm run test         # run all unit tests
npm run test:e2e     # run Playwright e2e tests
npm run migrate      # run pending DB migrations
npm run lint         # ESLint + Prettier check
npm run type-check   # tsc --noEmit
```

---

## Key Files

| File | Purpose |
|---|---|
| `src/api/lib/logger.ts` | Winston logger — use this, not console |
| `src/db/schema.prisma` | Single source of truth for DB schema |
| `src/api/middleware/auth.ts` | Auth middleware — attach to all protected routes |
| `.env.example` | Template for local env (never commit `.env`) |
| `docs/api-spec.md` | OpenAPI spec — keep in sync with code |