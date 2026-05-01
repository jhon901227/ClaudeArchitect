---
description: Testing rules — loaded when Claude works in src/tests/** or *.test.ts files
paths:
  - src/tests/**
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
---

# Testing Rules

Loaded automatically whenever Claude touches any test or spec file.

## Test Structure (mandatory)

```ts
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('TaskService', () => {
  let service: TaskService;

  beforeEach(() => {
    // Reset all mocks before each test — NEVER share state between tests
    vi.clearAllMocks();
    service = new TaskService(mockPrisma);
  });

  describe('createTask()', () => {
    it('creates a task and returns the serialized DTO', async () => {
      // Arrange
      mockPrisma.task.create.mockResolvedValue(fakeTask);
      // Act
      const result = await service.createTask({ title: 'Test' }, userId);
      // Assert
      expect(result).toMatchObject({ id: fakeTask.id, title: 'Test' });
    });

    it('throws AppError(400) when title is empty', async () => {
      await expect(service.createTask({ title: '' }, userId))
        .rejects.toThrow(AppError);
    });
  });
});
```

## Mocking Rules

- Use `vi.mock()` at the top of the file, outside `describe`.
- Mock **at the boundary** (DB, HTTP, file system) — never mock internal functions.
- Use typed mocks: `vi.mocked(prisma.task.create)` not `(prisma.task.create as any)`.
- Snapshot tests (`toMatchSnapshot`) are **banned** — use explicit assertions.

## Coverage Requirements

- Lines: ≥ 80% (enforced by CI)
- Branches: ≥ 75%
- Do not use `/* c8 ignore */` to game coverage without a comment explaining why.

## Forbidden

- `console.log` in tests (use `expect` assertions)
- `setTimeout` or real timers (use `vi.useFakeTimers()`)
- Tests that depend on execution order (each test must be independent)
- `it.only` or `describe.only` in committed code