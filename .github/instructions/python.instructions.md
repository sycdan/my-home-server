---
applyTo: "**/*.py"
---

# Python Script Standards (must be followed exactly)

## Coding Style

- Refer to `pyproject.toml` for ruff configuration and follow those formatting & linting rules.

## Additional Requirements

- Executable Python scripts must have a shebang line: `#!/usr/bin/env python`.
- When running pytest, prefix the command with `PYTHONPATH=. ` to ensure the root directory is included in the module search path.
