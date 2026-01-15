from dataclasses import dataclass


@dataclass
class RunScriptCommand:
  executable_path: str
  root_directory: str | None = None
  create_root: bool = False
  debug: bool = False
