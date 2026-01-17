AND = "AND"
OR = "OR"


def validate_action_package_contents(filenames: list[str] | set[str]):
  filenames = set(filenames)

  rules = [
    (AND, ["__init__.py", "handler.py"]),
    (OR, ["command.py", "query.py"]),
  ]

  missing = []

  for mode, files in rules:
    if mode == AND:
      missing.extend(f for f in files if f not in filenames)

    elif mode == OR:
      if not any(f in filenames for f in files):
        missing.append(" or ".join(files))

  if missing:
    raise RuntimeError(f"Action package is missing required files: {', '.join(missing)}")
