---
applyTo: "**/*.py"
---

# Python Script Standards (must be followed exactly)

## Coding Style

- Refer to `pyproject.toml` for ruff configuration and follow those formatting & linting rules.
- All imports should be placed at the top of the file, grouped in the following order with a blank line between each group:
  1. Standard library imports
  2. Third-party imports
  3. Local application/library-specific imports
  - The only exceptions would be to avoid circular dependencies, or other extenuating circumstances.
- Do not add return type hints to function definitions, allowing the type checker to infer them.
- Do add type hints for function parameters.
- Do add type hints for local arrays that will be returned from functions.

## Additional Requirements

- Executable Python scripts must have a shebang line: `#!/usr/bin/env python`.
- When running pytest, prefix the command with `PYTHONPATH=. ` to ensure the root directory is included in the module search path.
