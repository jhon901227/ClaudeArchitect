---
description: Rules for API route files — loaded only when Claude edits src/api/routes/**
paths:
  - src/api/routes/**
---

# API Route Rules

These rules apply automatically whenever Claude reads or edits any file
under `src/api/routes/`. They are NOT loaded for other files (lazy-loaded).

## Route Structure Template

Every route file must follow this pattern:

```ts
import { Router } from 'express';
import { authenticate } from '../middleware/auth';
import { validate } from '../middleware/validate';
import { createTaskSchema } from '../schemas/task';
import { TaskController } from '../controllers/task.controller';

const router = Router();
const ctrl = new TaskController();

// Public routes (explicitly marked)
router.get('/health', ctrl.health);

// Protected routes (default for all API endpoints)
router.use(authenticate);

router.get('/',        ctrl.list);
router.post('/',       validate(createTaskSchema), ctrl.create);
router.get('/:id',     ctrl.get);
router.patch('/:id',   validate(updateTaskSchema), ctrl.update);
router.delete('/:id',  ctrl.remove);

export default router;
```

## Required Patterns

- **Every handler must be async** and wrapped with `asyncHandler()` or
  declared with try/catch using `AppError`.
- **Input validation before controller** — never validate inside the controller.
- **HTTP status codes:**
  - `200` GET success, `201` POST created, `204` DELETE no-content
  - `400` validation error, `401` unauthenticated, `403` forbidden, `404` not found
- **Never return raw DB objects** — always pass through a serializer/DTO.

## Forbidden in Route Files

- Direct Prisma/DB calls (use the service layer)
- Business logic (belongs in `src/api/services/`)
- Hard-coded user IDs, magic strings, or feature flags