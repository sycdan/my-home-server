from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


@dataclass
class ActionPackage:
  """A domain action loaded from the filesystem."""

  action_dir: Path
  """Domain action folder (containing handler.py)."""
  init_module: ModuleType
  """Loaded from the __init__.py in the action folder."""
  shape_module: ModuleType
  """Loaded from command.py or query.py."""
  logic_module: ModuleType
  """Loaded from handler.py."""
  action_hash: str
  """The hash of the full path to the domain action folder."""
