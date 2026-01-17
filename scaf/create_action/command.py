from dataclasses import dataclass


@dataclass
class CreateActionCommand:
  name: str
  """The name of the action to create (e.g. Do Stuff)."""
