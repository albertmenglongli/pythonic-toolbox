# Guidance for AI contributors

This repository hosts **pythonic-toolbox**, a small Python utility package with decorators and helper functions.  The goal of this note is to help future AI contributors understand the project layout, constraints, and preferred practices.

## Repository layout
- `pythonic_toolbox/` contains the source code organized by feature:
  - `decorators/`: decorator helpers (e.g., `retry`, `ignore_unexpected_kwargs`) with async/sync support utilities.
  - `utils/`: standalone helpers for dict/list/deque processing, functional helpers, simple context managers, and string utilities.
  - `version.py` and `__init__.py` expose the package version.
- `tests/` contains pytest suites that double as usage documentation.  `tests/generate_readme_markdown.py` rebuilds the README from the tests.
- `README.md` is auto-generated from the tests—**do not edit it directly**; instead, update tests and regenerate.

## Coding style and expectations
- Favor small, single-purpose helpers with full type hints.  Existing code leans on `funcy` for helpers like `first` and `identity` rather than reimplementing basics.
- Keep decorators compatible with both synchronous and asynchronous callables when feasible; see `decorators.decorator_utils.decorate_sync_async` for the existing pattern.
- Preserve backwards-compatible behavior and explicit error messages (e.g., validating inputs for duplicates, type mismatches).
- Avoid adding broad exception handling around imports; keep imports at module top as currently practiced.

## Testing and verification
- Use `python -m pytest` from the repository root.  The suite runs quickly and covers the public surface area.
- When README content must change, run `python tests/generate_readme_markdown.py` to regenerate it before committing.

## Contribution tips
- New helpers should come with targeted pytest coverage mirroring the style in `tests/` and demonstrating usage.
- Prefer extending existing utility modules when adding related functionality rather than creating new scattered files.
- Keep public API imports in `pythonic_toolbox/__init__.py` and `pythonic_toolbox/utils/__init__.py` synchronized with new additions so that consumers can import from the package root.

Following these notes will help maintain a consistent, well-tested toolbox for future contributors.
