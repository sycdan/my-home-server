from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


@dataclass
class ActionPackage:
  action_dir: Path
  """The path to the domain action folder (which contains __init__.py)"""
  action_package: ModuleType
  """The module loaded from the action_dir (__init__.py)"""
  action_file: Path
  """The path to the action_file (command.py or query.py)"""
  action_module: ModuleType
  """The module loaded from the action_file (command.py or query.py)"""
  action_hash: str
  """The hash of the full path to the domain folder."""
