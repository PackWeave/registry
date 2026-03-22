## Python Development Context

You are assisting with Python development. Apply these best practices consistently:

### Type annotations
- Annotate all function signatures: parameters and return types. Use `-> None` for functions that return nothing.
- Use `from __future__ import annotations` for forward references in Python 3.9 and below.
- Prefer built-in generics (`list[str]`, `dict[str, int]`, `tuple[int, ...]`) over `typing.List`, `typing.Dict` (Python 3.9+).
- Use `Optional[T]` only when needed; prefer `T | None` (Python 3.10+).
- Use `TypeAlias` for complex type aliases; use `TypeVar` and `Generic` for reusable generic types.
- Run `mypy --strict` to validate types. Fix all errors; do not use `# type: ignore` without an explanation comment.

### Code style
- Follow PEP 8. Use `ruff` for linting and `black` for formatting.
- Maximum line length: 88 characters (black default).
- Use f-strings for string interpolation; avoid `%` formatting and `.format()` unless required.
- Name constants in `UPPER_SNAKE_CASE`; classes in `PascalCase`; everything else in `snake_case`.

### Error handling
- Catch specific exceptions, not bare `except:` or `except Exception:`.
- Use custom exception classes for domain errors; inherit from `Exception`, not `BaseException`.
- Use `contextlib.suppress` only for intentionally ignored exceptions, with a comment explaining why.
- Always clean up resources with `with` statements (context managers) or `try/finally`.

### Project structure and imports
- Organise imports: standard library, third-party, local — separated by blank lines (`isort` enforces this).
- Avoid circular imports; if they occur, move shared types to a dedicated `types.py` or `models.py` module.
- Use `__all__` in public modules to define the public API explicitly.

### Testing
- Use `pytest`. Test files go in `tests/` mirroring the source layout.
- Use `pytest.mark.parametrize` for data-driven tests.
- Use `pytest-cov` to track coverage; aim for >80% on business logic.
- Mock external dependencies (`requests`, databases, file I/O) with `unittest.mock` or `pytest-mock`.

### Dependencies and packaging
- Pin direct dependencies in `pyproject.toml` with minimum versions (`>=`); let the lockfile (Poetry/pip-tools) pin transitive deps.
- Use virtual environments; never install packages globally.
- Prefer `pathlib.Path` over `os.path` for all file operations.
