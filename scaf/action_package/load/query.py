from dataclasses import dataclass


@dataclass
class LoadQuery:
  action_path: str
  """Relative to the project root."""
