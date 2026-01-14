---
applyTo: "**/*.py"
---

# Python Script Standards (must be followed exactly)

## Coding Style

- Refer to `pyproject.toml` for ruff configuration and follow those formatting & linting rules.
- All imports should be placed at the top of the file, except in special cases where doing so causes problems (e.g a circular dependency).
- Do not add return type hints to function definitions, allowing the type checker to infer them.
- Do add type hints for function parameters.
- Do add type hints for local arrays that will be returned from functions.

## Additional Requirements

- Executable Python scripts must have a shebang line: `#!/usr/bin/env python` and be marked as executable.
- When running pytest, prefix the command with `PYTHONPATH=. ` to ensure the root directory is included in the module search path.

## Notes

- Any directory within `./mhs` that contains a `logic.py` file is considered an "action" (the filename must be an exact match).
