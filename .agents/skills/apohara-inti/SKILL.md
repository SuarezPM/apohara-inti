```markdown
# apohara-inti Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill documents the core development patterns, coding conventions, and workflows used in the `apohara-inti` repository. The project is primarily written in Python (backend) with a TypeScript/React frontend, and emphasizes clean code, conventional commits, and robust testing. It provides step-by-step guides for implementing features, writing tests, and updating documentation, ensuring consistency and quality across contributions.

## Coding Conventions

### File Naming
- Use **snake_case** for Python files.
  - Example: `data_loader.py`, `test_utils.py`
- Use **PascalCase** or **camelCase** for TypeScript/React components.
  - Example: `MyComponent.tsx`, `dataFetcher.ts`

### Import Style
- Use **alias imports** in Python.
  ```python
  import numpy as np
  import pandas as pd
  ```
- In TypeScript, use standard ES module imports.
  ```typescript
  import React from "react";
  import { fetchData } from "./lib/data_fetcher";
  ```

### Export Style
- Use **named exports** in TypeScript/JavaScript.
  ```typescript
  // lib/math.ts
  export function add(a: number, b: number) {
    return a + b;
  }
  ```

### Commit Messages
- Follow **Conventional Commits** with prefixes:
  - `feat`: New features
  - `fix`: Bug fixes
  - `docs`: Documentation changes
- Example:
  ```
  feat: add user authentication to backend API
  fix: correct typo in data_loader.py
  docs: update README with setup instructions
  ```

## Workflows

### Feature Implementation with Tests
**Trigger:** When adding a new backend or frontend feature that requires testing  
**Command:** `/new-feature-with-tests`

1. Implement the feature logic in the appropriate source files:
    - Backend: `packages/backend/*.py`
    - Frontend: `packages/frontend/src/*.tsx` or `*.ts`
2. Add or update corresponding test files:
    - Backend: `packages/backend/tests/test_*.py`
    - Frontend: `packages/frontend/src/lib/*.test.ts`
3. Update related files as needed (API routes, helpers, UI components).
4. Run tests to verify correctness.
    - Backend: Use `pytest` or your preferred runner.
    - Frontend: Use `vitest`.
5. Commit changes with a conventional commit message.

**Example:**
```python
# packages/backend/user_manager.py
def create_user(username, password):
    # implementation here
    pass
```
```python
# packages/backend/tests/test_user_manager.py
def test_create_user():
    assert create_user("alice", "secret") is not None
```
```typescript
// packages/frontend/src/lib/user.test.ts
import { createUser } from "./user";
test("creates a user", () => {
  expect(createUser("bob", "pass")).toBeTruthy();
});
```

---

### Feature Documentation Update
**Trigger:** When documenting a new feature, workflow, or architectural decision  
**Command:** `/update-docs`

1. Edit `README.md` to describe new features or usage.
2. Edit `AUDIT.md` to record audit trail or security/feature decisions.
3. Document rationale, usage, and edge cases.
4. Commit documentation changes with a `docs:` prefix.

**Example:**
```markdown
# README.md

## New Feature: User Authentication
- Users can now register and log in using email/password.
- See API docs for endpoints.
```

## Testing Patterns

- **Backend (Python):**
  - Test files are named `test_*.py` and located in `packages/backend/tests/`.
  - Use standard Python testing frameworks (e.g., `pytest`).
  - Example:
    ```python
    # packages/backend/tests/test_math.py
    def test_add():
        assert add(2, 3) == 5
    ```

- **Frontend (TypeScript):**
  - Test files follow the pattern `*.test.ts` and are located in `packages/frontend/src/lib/`.
  - Use `vitest` as the testing framework.
  - Example:
    ```typescript
    // packages/frontend/src/lib/math.test.ts
    import { add } from "./math";
    test("adds numbers", () => {
      expect(add(1, 2)).toBe(3);
    });
    ```

## Commands

| Command                  | Purpose                                                      |
|--------------------------|--------------------------------------------------------------|
| /new-feature-with-tests  | Implement a new feature with corresponding tests             |
| /update-docs             | Update documentation files (README, AUDIT) for new features |

```