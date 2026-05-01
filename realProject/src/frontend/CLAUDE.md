# Frontend — Claude Code Configuration

> **Hierarchy level:** `src/frontend/` subdirectory
> This file EXTENDS (not replaces) the root CLAUDE.md.
> Rules here apply only when Claude is working in `src/frontend/`.

---

## Frontend-Specific Context

This is a **React 18 + TypeScript + Tailwind CSS** SPA that talks to the
TaskFlow REST API via `/api/v1/`. Routing is handled by React Router v6.

State management: **Zustand** (no Redux). Server state: **TanStack Query**.

---

## Component Rules

- Prefer **functional components** with hooks — no class components.
- File naming: `PascalCase.tsx` for components, `camelCase.ts` for utilities.
- Each component lives in its own directory with an `index.ts` barrel:
  ```
  src/frontend/components/TaskCard/
    index.ts         ← re-exports TaskCard
    TaskCard.tsx     ← component
    TaskCard.test.tsx
    TaskCard.stories.tsx  (if Storybook story exists)
  ```
- Keep components under **150 lines**. Split if larger.
- Use `cn()` from `lib/utils.ts` to merge Tailwind classes — never string concat.

---

## Styling

- Tailwind utility classes only — no CSS modules, no inline styles.
- Color tokens live in `tailwind.config.ts` — do not hardcode hex values.
- Dark mode via `dark:` prefix — always test both modes.

---

## Data Fetching

```ts
// CORRECT — use TanStack Query
const { data, isLoading } = useQuery({ queryKey: ['tasks'], queryFn: fetchTasks });

// WRONG — never fetch directly in component body
const tasks = await fetch('/api/v1/tasks');
```

---

## Do Not Touch (frontend scope)

- `src/frontend/generated/` — auto-generated from OpenAPI spec, do not edit manually.
- `src/frontend/lib/api-client.ts` — central HTTP client, changes need team review.