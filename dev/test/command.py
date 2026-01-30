from dataclasses import dataclass


@dataclass
class Test:
  """Run tests using pytest."""

  def execute(self):
    from dev.test.handler import handle

    return handle(self)
